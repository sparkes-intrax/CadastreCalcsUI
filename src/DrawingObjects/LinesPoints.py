'''
Draws lines and points on graphics scene
Functions to convert coordinates to scene coordinates and show objects
'''
from PyQt5.QtGui import QBrush, QPen, QFont, QPainter, QPainterPath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsItem

import genericFunctions as funcs
import CadastreClasses as dataObjects
from DrawingObjects import Arcs
from GUI_Objects import GraphicsView

from numpy import sin, cos, radians


class AddPointToScene:
    def __init__(self, view, point, Layer):
        '''
        Adds a point to scene object (added as an ellipse)
        Updates the point object to include graphics items
        :param scene:
        :param point:
        :param layer:
        :return:
        '''

        #set Pen and Brush props
        PointProps = LinePointProperties()
        self.Colour, self.Pen, self.Brush = PointProps.SetPointProperties(Layer)

        #set scene coords for point
        E = float(point.E) * 1000
        N = float(point.NorthingScreen) * 1000

        #add point object to scene
        self.point, self.PointObj = self.AddPointObject(view, point, E, N)

        #add point number label to scene
        if Layer != "EASEMENT":
            self.AddPointNumLabel(E, N, view)

        #Add code label if itbeen entered
        if self.point.Code != "":
            self.AddCodeLabel(E, N, view)



    def AddPointObject(self, view, point, E, N):
        '''
        Adds the point to scene (as ellipse
        :param scene:
        :param point:
        :return:
        '''

        #add point to scene
        PointObj = view.Point(E, N, 200, self.Pen, self.Brush)
        #   PointObj.setFlag(QGraphicsItem.ItemIsSelectable, True)

        #Get point scene bounding rect
        point.BoundingRect = PointObj.boundingRect()
        #add point Obj to points graphicsItems
        setattr(point.GraphicsItems, "Point", PointObj)

        return point, PointObj

    def AddPointNumLabel(self, E, N, view):
        '''
        Adds the point Number Label to the point
        :param E:
        :param N:
        :return:
        '''

        PntNumLabel = view.scene.addText(self.point.PntNum)
        PntNumLabel.setPos(int(E), int(N + 1000))
        PntNumLabel.setDefaultTextColor(self.Colour)
        PntNumLabel.setFont(QFont('Arial', 1500, QFont.Light))
        PntNumLabel.setFlag(QGraphicsItem.ItemIsSelectable, True)

        #add label to points grpahics Items
        setattr(self.point.GraphicsItems, "PointNumLabel", PntNumLabel)

    def AddCodeLabel(self, E, N, view):
        '''
        Adds the code Label to the point
        :param E:
        :param N:
        :return:
        '''

        CodeLabel = view.scene.addText(self.point.Code)
        CodeLabel.setPos(int(E + 250), int(N - 4000))
        CodeLabel.setDefaultTextColor(self.Colour)
        if "SSM" in self.point.Code or "PM" in self.point.Code:
            CodeLabel.setFont(QFont('Times', 6000, QFont.Light))
        else:
            CodeLabel.setFont(QFont('Times', 1500, QFont.Light))
        CodeLabel.setRotation(-30)
        CodeLabel.resetTransform()
        CodeLabel.setFlag(QGraphicsItem.ItemIsSelectable, True)

        #add code label to Graphics items for point
        setattr(self.point.GraphicsItems, "CodeLabel", CodeLabel)




class LineObjects:
    def __init__(self, pointObj, gui):
        '''
        Draws linework for pointObj onto scene object
        :param pointObj:
        :param scene:
        '''

        #calls different methods depending on whether the line is an arc or not
        if gui.RadiusInput.InputObj.text() != "":
            self.drawArc(pointObj, gui)
        else:
            self.drawLine(pointObj, gui)

    def drawLine(self, pointObj, gui):
        '''
        Adds linework to data objects and dsiplays on
        :return:
        '''

        # Get src point coordinates
        SrcPoint = gui.traverse.Points.__getattribute__(pointObj.Params.SrcPntNum)
        SrcEasting = float(SrcPoint.E) * 1000
        SrcNorthing = float(SrcPoint.NorthingScreen) * 1000

        #Get Line Props
        LineProps = LinePointProperties()
        self.LinePen, Layer, Colour = LineProps.SetLineProperties(pointObj.Params.Layer,
                                                          SrcPoint.Layer)

        #create line object
        line = dataObjects.Line(pointObj.Params.SrcPntNum, pointObj.Params.PntNum,
                                Layer, pointObj.Params.Distance,
                                pointObj.deltaE, pointObj.deltaN, pointObj.Params.Bearing, Colour)
        #Screen Coords
        E = pointObj.point.E * 1000
        N = pointObj.point.NorthingScreen*1000
        #draw line and get its bounding rect
        GraphLine = gui.view.Line(SrcEasting, SrcNorthing, E, N, self.LinePen)
        setattr(line.GraphicsItems, "Line", GraphLine)
        line.BoundingRect = GraphLine.boundingRect()
        #get traverse lineNum and add line to traverse object
        lineNum = gui.CadastralPlan.Lines.LineNum + 1
        setattr(gui.traverse.Lines, ("line"+str(lineNum)), line)
        if pointObj.point.Code in gui.CodeList:
            setattr(gui.CadastralPlan.Lines, ("line"+str(lineNum)), line)

        #Add bearings and distances on line
        if abs(float(line.Distance)) > 50:
            label = self.LinePropsLabel(line, SrcPoint, pointObj, gui)
            setattr(line.GraphicsItems, "Label", label)

        gui.CadastralPlan.Lines.LineNum += 1
        gui.traverse.Lines.LineNum += 1



    def drawArc(self, pointObj, gui):
        '''
        Draws an ar using qpainter
        :return:
        '''

        # Get src point coordinates
        SrcPoint = gui.traverse.Points.__getattribute__(pointObj.Params.SrcPntNum)

        # set pen/brush colour
        LineProps = LinePointProperties()
        self.LinePen, Layer, Colour = LineProps.SetLineProperties(pointObj.Params.Layer, SrcPoint.Layer)

        #get coordinates for centre of the arc
        CentreArcCoords = funcs.ArcCentreCoords(SrcPoint, pointObj.point,
                                                     pointObj.Params.Radius, pointObj.Params.ArcRotation)

        #create Arc Object
        arc = dataObjects.Arc(pointObj.Params.SrcPntNum, pointObj.Params.PntNum,
                              Layer, pointObj.Params.Radius,
                              CentreArcCoords, pointObj.Params.ArcRotation, pointObj.Params.Distance,
                              pointObj.Params.Bearing, pointObj.deltaE, pointObj.deltaN, Colour)

        #get arc path object
        ArcPath = Arcs.DrawArc(SrcPoint, pointObj.point, CentreArcCoords, pointObj.Params)
        #add Arc Path to GUI
        ArcLine = gui.view.scene.addPath(ArcPath.arcPath, self.LinePen)
        ArcLine.setFlag(QGraphicsItem.ItemIsSelectable, True)
        arc.BoundingRect = ArcLine.boundingRect()
        #add Arc GraphItem
        setattr(arc.GraphicsItems, "Line", ArcLine)
        #add Arc to Traverse object        line.BoundingRect = GraphLine.boundingRect()
        #get traverse lineNum and add line to traverse object
        LineNum = gui.CadastralPlan.Lines.LineNum + 1
        setattr(gui.traverse.Lines, ("Line"+str(LineNum)), arc)

        gui.CadastralPlan.Lines.LineNum += 1
        gui.traverse.Lines.LineNum += 1

    def LinePropsLabel(self, line, SrcPoint, pointObj, gui):
        '''
        Determine line properties to display bearings and distances
        :param line:
        :param SrcPoint:
        :param pointObj:
        :return:
        '''

        if len(line.Bearing.split(".")) == 1:
            bearingStr = line.Bearing + eval(r'"\u00B0"')
        elif len(line.Bearing.split(".")[1]) == 2:
            bearingStr = line.Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         line.Bearing.split(".")[1][0:2] + "'"
        else:
            bearingStr = line.Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         line.Bearing.split(".")[1][0:2] + "' " + \
                         line.Bearing.split(".")[1][2:] + "\""

        Distance = abs(float(line.Distance))
        LinePropsStr = bearingStr + " ~ " + str(Distance)
        LineMidEasting = (SrcPoint.E + pointObj.point.E) / 2
        LineMidNorthing = (SrcPoint.NorthingScreen + pointObj.point.NorthingScreen)/2
        bearing = funcs.bearing2_dec(line.Bearing)
        rotation = self.LabelRotation(bearing)

        #get line equation
        #m, b = funcs.calcLineEquation(SrcPoint.E, pointObj.point.E, SrcPoint.N, pointObj.point.N)
        #perpencidular line equation
        #m_perp = -1/m
        #b_perp = m_perp*LineMidEasting - LineMidNorthing

        LineLabel = gui.view.Text(LineMidEasting, LineMidNorthing, rotation, LinePropsStr)

        return LineLabel


    def LabelRotation(self, bearing):
        '''
        Sets rotation of line props label in QT space
        :param bearing:
        :return:
        '''

        if bearing >= 180:
            rotation = bearing - 270
        else:
            rotation = bearing - 90

        return rotation


class CalculatePoint:

    def __init__(self, gui, traverse):
        '''
        Calculates a new point
        - gets info from gui (source point, bearing & distances ect)
        - calculates points and adds them to the scene
        :param gui: gui interface with objects
        :param traverse: traverse object with line/point objects already calculated
        '''

        #get calculation params from GUI
        self.Params = CalcInfo(gui)
        #calculate point coordinates
        self.point = self.CalcPoint(traverse)

    def CalcPoint(self, traverse):
        '''
        Calculate point from parameter info
        :return:
        '''

        #convert bearing to decimal
        BearingDec = funcs.bearing2_dec(self.Params.Bearing)
        #Return angle for point calculate and its sign for Easting and Northing
        angle, deltaE, deltaN = funcs.bearing2angle(BearingDec)
        # calculate change in coordinates
        self.deltaE = float(self.Params.Distance) * sin(radians(angle)) * deltaE
        self.deltaN = float(self.Params.Distance) * cos(radians(angle)) * deltaN
        #get source point object from traverse object
        SrcPoint = traverse.Points.__getattribute__(self.Params.SrcPntNum)
        #calculate new coordinates
        E = float(SrcPoint.E) + self.deltaE
        N = float(SrcPoint.N) + self.deltaN
        N_Screen = float(SrcPoint.NorthingScreen) - self.deltaN

        # create new point object
        point = dataObjects.Point(self.Params.PntNum, E, N, N_Screen,
                                  self.Params.Elev, self.Params.Code, self.Params.Layer)

        return point

        
class CalcInfo:
    def __init__(self, gui):
        '''
        retrieves info from GUI
        :param gui: 
        :return: 
        '''

        self.Bearing = gui.BearingToCalcPoint.InputObj.text()
        self.Distance = gui.DistanceToCalcPoint.InputObj.text()
        self.PntNum = gui.PointNumber.InputObj.text()
        self.SrcPntNum = gui.SrcPoint.InputObj.text()
        self.Elev = gui.PointElevation.InputObj.text()
        self.Radius = gui.RadiusInput.InputObj.text()
        self.ArcRotation = gui.ArcRotationDirection.InputObj.currentText()
        self.Code = gui.PointCode.InputObj.text()
        self.Layer = gui.PointLayer.InputObj.currentText()
        PointProps = LinePointProperties()
        self.PointColour, self.PointPen, self.PointBrush = \
            PointProps.SetPointProperties(self.Layer)



class LinePointProperties:

    def SetPointProperties(self, Layer):

        # set pen colour
        if Layer == "BOUNDARY":
            Colour = Qt.cyan
        elif Layer == "REFERENCE MARKS":
            Colour = Qt.white
        elif Layer == "EASEMENT":
            Colour = Qt.green

        Pen = QPen(Colour)
        Pen.setWidth(1000)
        Brush = QBrush(Colour)

        return Colour, Pen, Brush

    def SetLineProperties(self, Layer, SrcLayer):

        if Layer == "REFERENCE MARKS" or SrcLayer == "REFERENCE MARKS":
            Colour = Qt.white
            Layer = "REFERENCE MARKS"
        elif Layer == "EASEMENT" or SrcLayer == "EASEMENT":
            Colour = Qt.green
            Layer = "EASEMENT"
        else:
            Colour = Qt.cyan


        Pen = QPen(Colour)
        Pen.setWidth(200)
        if Layer == "EASEMENT":
            Pen.setStyle(Qt.DashLine)

        return Pen, Layer, Colour
