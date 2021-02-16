'''
Used on click event when joining points

Only works to join commited data - ie committed traverse
'''

from numpy import sqrt
from PyQt5.QtGui import QPen, QColor, QBrush
from DrawingObjects import LinesPoints
import genericFunctions as funcs
import CadastreClasses as DataObjects

class FindPointObj:

    def __init__(self, gui, pos):

        self.gui = gui
        self.NearestPoint = self.FindPoint(pos)
        if self.NearestPoint is not None:
            self.ScreenEasting = int(self.NearestPoint.E*1000)
            self.ScreenNorthing = int(self.NearestPoint.NorthingScreen * 1000)
            self.ColourPoint()

    def FindPoint(self, pos):
        '''
        Searches for any points near pos (within a metre and then the closest)
        :param pos: scene position clicked
        :return:
        '''

        #convert clicked scene position to E/N (NorthingScreen)
        Easting = float(pos.x())/1000
        Northing = float(pos.y())/1000

        #search point object in gui.CadastralPlan if any point near pos
        NearestPoint = self.FindNearest(Easting, Northing)

        return NearestPoint

    def FindNearest(self, Easting, Northing):
        '''
        Finds CadastralPoint closest to Easting/Northing - within 1m
        :return:
        '''

        CurrentMinDistance = 20
        for key in self.gui.CadastralPlan.Points.__dict__.keys():
            point = self.gui.CadastralPlan.Points.__getattribute__(key)
            pointEasting = point.__getattribute__("E")
            pointNorthing = point.__getattribute__("NorthingScreen")

            Distance = sqrt((Easting - pointEasting)**2 + (Northing - pointNorthing)**2)
            if Distance < 1 and Distance < CurrentMinDistance:
                CurrentMinDistance = Distance
                NearestPoint = point

        if CurrentMinDistance == 20:
            return None
        else:
            return NearestPoint

    def ColourPoint(self):
        '''
        Colours point being clicked red
        :return:
        '''

        point = self.NearestPoint.GraphicsItems.__getattribute__("Point")
        PenColor = QColor("red")
        Pen = QPen(PenColor)
        Pen.setWidth(500)
        Brush = QBrush(QColor("red"))
        point.setPen(Pen)
        point.setBrush(Brush)

class DrawMouseMove:

    def __init__(self, ClickedPoint, pos, gui):
        '''
        adds a line to gui from clicked point to current position
        :param ClickedPoint:
        :param pos:
        :return:
        '''

        Pen = QPen(QColor("red"))
        Pen.setWidth(500)

        self.mouseLine = gui.view.Line(ClickedPoint.ScreenEasting,
                                            ClickedPoint.ScreenNorthing,
                                            pos.x(), pos.y(), Pen)

class DrawNewLine:

    def __init__(self, StartPoint, EndPoint, gui):
        '''
        Draws New line from start to End Points
        Colours according to layers
        Adds line to CadastralPlan object
        '''

        #Get Layer of points for Pen/Brush Properties
        StartLayer = StartPoint.__getattribute__("Layer")
        EndLayer = EndPoint.__getattribute__("Layer")

        #re-drawpoints
        self.redrawPoints(StartPoint.GraphicsItems.__getattribute__("Point"), StartLayer)
        self.redrawPoints(EndPoint.GraphicsItems.__getattribute__("Point"), EndLayer)

        #get Pen props for new line
        LineProps = LinesPoints.LinePointProperties()
        Pen, Layer, Colour = LineProps.SetLineProperties(StartLayer, EndLayer)

        #draw new line on scene
        NewLine = self.drawLine(StartPoint, EndPoint, gui, Pen)
        Bearing, Distance, deltaE, deltaN = self.CalcLineBearingDistance(StartPoint, EndPoint)
        
        #create line object
        line = DataObjects.Line(StartPoint.PntNum, EndPoint.PntNum,
                                Layer, Distance,
                                deltaE, deltaN, Bearing, Colour)

        setattr(line, "BoundingRect", NewLine.boundingRect())
        #add new line to graphics items
        setattr(line.GraphicsItems, "Line", NewLine)
        #add line object to CadastralPlan
        lineNum = gui.CadastralPlan.Lines.LineNum + 1
        setattr(gui.CadastralPlan.Lines, ("line" + str(lineNum)), line)

        # Add bearings and distances on line
        if abs(float(Distance)) > 50:
            label = self.LinePropsLabel(Bearing, Distance, StartPoint, EndPoint, gui)
            setattr(line.GraphicsItems, "Label", label)

        gui.CadastralPlan.Lines.LineNum += 1

    def redrawPoints(self, point, layer):
        '''
        recolours point according to layer properties
        :param point:
        :param layer:
        :return:
        '''

        #get pen props
        LineProps = LinesPoints.LinePointProperties()
        Colour, Pen, Brush = LineProps.SetPointProperties(layer)

        #set point properties for point
        point.setPen(Pen)
        point.setBrush(Brush)

    def drawLine(self, StartPoint, EndPoint, gui, Pen):
        '''
        Draws a new line between start and end points of scene
        '''
        
        #Get screen coordinates to draw between
        StartEasting = int(StartPoint.E * 1000)
        StartNorthing = int(StartPoint.NorthingScreen * 1000)
        EndEasting = int(EndPoint.E * 1000)
        EndNorthing = int(EndPoint.NorthingScreen * 1000)
        
        # draw line
        NewLine = gui.view.Line(StartEasting, StartNorthing,
                                EndEasting, EndNorthing, Pen)
        
        return NewLine
    
    def CalcLineBearingDistance(self, StartPoint, EndPoint):
        '''
        Calculates the new bearing and distance of line
        :param StartPoint: 
        :param EndPoint: 
        :return: 
        '''

        # Get point coordinates
        StartEasting = StartPoint.E
        StartNorthing = StartPoint.N
        EndEasting = EndPoint.E
        EndNorthing = EndPoint.N
        
        deltaE = EndEasting - StartEasting
        deltaN = EndNorthing - StartNorthing
        
        bearing = funcs.calcBearing(StartEasting, StartNorthing, EndEasting, EndNorthing)
        bearing = funcs.bearing2_DMS(bearing)
        
        distance = sqrt((StartEasting-EndEasting)**2 + (StartNorthing-EndNorthing)**2)
        
        return bearing, round(distance,3), deltaE, deltaN
    
    def LinePropsLabel(self, Bearing, Distance, StartPoint, EndPoint, gui):
        '''
        Determine line properties to display bearings and distances
        :param line:
        :param SrcPoint:
        :param pointObj:
        :return:
        '''

        if len(Bearing.split(".")) == 1:
            bearingStr = Bearing + eval(r'"\u00B0"')
        elif len(Bearing.split(".")[1]) == 2:
            bearingStr = Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         Bearing.split(".")[1][0:2] + "'"
        else:
            bearingStr = Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         Bearing.split(".")[1][0:2] + "' " + \
                         Bearing.split(".")[1][2:] + "\""


        LinePropsStr = bearingStr + " ~ " + str(abs(Distance))
        LineMidEasting = (StartPoint.E + EndPoint.E) / 2
        LineMidNorthing = (StartPoint.NorthingScreen + EndPoint.NorthingScreen)/2
        bearing = funcs.bearing2_dec(Bearing)
        rotation = self.LabelRotation(bearing)

        #get line equation
        #m, b = funcs.calcLineEquation(SrcPoint.E, pointObj.point.E, SrcPoint.N, pointObj.point.N)
        #perpencidular line equation
        #m_perp = -1/m
        #b_perp = m_perp*LineMidEasting - LineMidNorthing

        gui.view.Text(LineMidEasting, LineMidNorthing, rotation, LinePropsStr)
    
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







