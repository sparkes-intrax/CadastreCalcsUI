'''
Set of functions and methods to process Traverse operations
'''

import CadastreClasses as DataObjects
from numpy import sqrt
from PyQt5 import QtCore
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QDialog, QPushButton, QLabel, QLineEdit, QComboBox
from DrawingObjects import LinesPoints
import genericFunctions as funcs
from DrawingObjects import Arcs
import MessageBoxes
from GUI_Objects import ObjectStyleSheets, Fonts, GroupBoxes

def NewTraverse(layer, StartRefPnt, FirstTraverse, point):
    '''
    creates a new traverse object or resets current traverse
    :param traverse:
    :return:
    '''

    traverse = DataObjects.Traverse(FirstTraverse, layer)
    traverse.StartRefPnt = StartRefPnt
    traverse.refPnts.append(StartRefPnt)
    setattr(traverse.Points, StartRefPnt, point)

    return traverse


class CommitTraverse:
    def __init__(self, gui):
        '''
        Adds traverse to traverses object
        Adds points, lines, and arcs to CadastralPlan
        :param CadastralPlan: 
        :param Traverse: traverse object to be added and to draw objects from for
                            CadastralPlan
        '''

        # change Traverse line/point colours back to layer colours
        gui.traverse.Points = self.SetPointColours(gui.traverse.Points)
        gui.traverse.Lines = self.SetLineColours(gui.traverse.Lines, gui.traverse.Points, "Line")
        #gui.traverse.Arcs = self.SetLineColours(gui.traverse.Arcs, gui.traverse.Points, "Arc")

        #add traverse to data objects
        gui.CadastralPlan.Traverses = self.AddTraverse(gui.CadastralPlan.Traverses, gui.traverse)
        gui.CadastralPlan = self.AddCadastralData(gui.CadastralPlan, gui.traverse)

        
    def AddTraverse(self, Traverses, Traverse):
        '''
        Adds Traverse to Traverses
        :param Traverses: 
        :param Traverse: 
        :return: 
        '''
        
        #get number of traverses in Traverses
        TravNum = str(len(Traverses.__dict__.keys()))
        setattr(Traverses, ("Traverse_" + TravNum), Traverse)
        
        return Traverses
    
    def AddCadastralData(self, CadastralPlan, Traverse):
        '''
        Adds drawing objects to CadastralPlan classes
        :param CadastralPlan: 
        :param Traverse: 
        :return: 
        '''
        
        #add point objects
        CadastralPlan = self.AddPointObjects(Traverse.Points, CadastralPlan)
        #add lines
        CadastralPlan = self.AddLineObjects(Traverse.Lines, CadastralPlan)
        #add Arcs
        #CadastralPlan = self.AddArcObjects(Traverse.Arcs, CadastralPlan)

        return CadastralPlan

        
    def AddPointObjects(self, Points, CadastralPlan):
        '''
        Adds point objects from Points to CadastralPlan
        :param Points: 
        :param CadastralPlan: 
        :return: 
        '''
        
        for key in Points.__dict__.keys():
            if key == "PointList":
                continue
            Point = Points.__getattribute__(key)
            setattr(CadastralPlan.Points, Point.PntNum, Point)
            
        return CadastralPlan

    def AddLineObjects(self, Lines, CadastralPlan):
        '''
        Adds Line objects from Points to CadastralPlan
        :param Lines: 
        :param CadastralPlan: 
        :return:

        '''

        for key in Lines.__dict__.keys():
            if key == "LineNum":
                continue
            Line = Lines.__getattribute__(key)
            #CadastralClasses = DataObjects.CadastralPlan()
            #if Line.__class__.__name__ == "Line":
            lineNum = str(len(CadastralPlan.Lines.__dict__.keys()))
            setattr(CadastralPlan.Lines, ("Line" + lineNum), Line)

        return CadastralPlan
    
    def AddArcObjects(self, Arcs, CadastralPlan):
        '''
        Adds Arc objects from Points to CadastralPlan
        :param Arcs: 
        :param CadastralPlan: 
        :return: 
        '''

        for key in Arcs.__dict__.keys():
            Arc = Arcs.__getattribute__(key)
            if Arc.__class__.__name__ == "Arc":
                arcNum = str(len(CadastralPlan.Arcs.__dict__.keys()))
                setattr(CadastralPlan.Arcs, ("Arc_" + arcNum), Arc)

        return CadastralPlan

    def SetPointColours(self, Points):
        '''
        For each points sets it colours to what is defined by its layer
        :param Points:
        :return:
        '''

        for key in Points.__dict__.keys():
            if key == "PointList":
                continue
            point = Points.__getattribute__(key)
            Layer = point.Layer
            PointProps = LinesPoints.LinePointProperties()
            Colour, Pen, Brush = PointProps.SetPointProperties(Layer)
            point.GraphicsItems.Point.setPen(Pen)
            point.GraphicsItems.Point.setBrush(Brush)
            setattr(Points, point.PntNum, point)
        return Points

    def SetLineColours(self, Lines, Points, LineType):
        '''
        For each points sets it colours to what is defined by its layer
        :param Points:
        :return:
        '''

        for key in Lines.__dict__.keys():
            if key == "LineNum" or key == "ArcNum":
                continue

            Line = Lines.__getattribute__(key)
            SrcPoint = Line.StartRef
            SrcPointLayer = Points.__getattribute__(SrcPoint).Layer
            EndPoint = Line.EndRef
            EndPointLayer = Points.__getattribute__(EndPoint).Layer
            LineProps = LinesPoints.LinePointProperties()
            Pen, Layer, colour = LineProps.SetLineProperties(EndPointLayer, SrcPointLayer)
            if LineType == "Line":
                Line.GraphicsItems.Line.setPen(Pen)
            else:
                Line.GraphicsItems.Arc.setPen(Pen)
            setattr(Lines, key, Line)
        return Lines

class CheckTraverseClose:

    def __init__(self, point, traverse, CadastralPlan):
        """
        Checks whether calculated point is near any already
        calculated points:
        Checks traverse.Points objects
        Checks CadastralPlan.Points objects
        Has 100mm tolerance
        """

        #check Traverse object for close points
        CloseError, ClosePointRefNum, EastError, NorthError = \
            self.CheckObject(point, traverse)
        #if no point within close point tolerance in TraverseObject check already committed points
        if CloseError is None:
            CloseError, ClosePointRefNum, EastError, NorthError = \
                self.CheckObject(point, CadastralPlan)

        #set object attributes
        if CloseError is not None:
            self.Close = True
            self.CloseError = CloseError
            self.ClosePointRefNum = ClosePointRefNum
            self.EastError = EastError
            self.NorthError = NorthError
        else:
            self.Close = False


    def CheckObject(self, point, object):
        '''
        Checks  object.Points whether any points are within close tolerance
        to point
        :param point:
        :param traverse:
        :return: ClosePointRefNum, closeError
        '''

        CloseError = None

        for key in object.Points.__dict__.keys():
            if key == 'PointList':
                continue
            ClosePoint = object.Points.__getattribute__(key)
            CloseError = self.Distance(point.E, ClosePoint.E,
                                            point.N, ClosePoint.N)
            EastError = point.E - ClosePoint.E
            NorthError = point.N - ClosePoint.N

            #check if TravPoint is within 100mm of point
            if CloseError < 0.25 and point.PntNum != key:
                return CloseError, key, EastError, NorthError

        return None, None, None, None


    def Distance(self, E1, E2, N1, N2):
        """
        Calculates distance between 2 points
        :param E1:
        :param E2:
        :param N1:
        :param N2:
        :return: DistanceToPoint
        """

        return sqrt((E2-E1)**2 + (N2-N1)**2)


class ColourTraverseObjects:
    def __init__(self, gui, lineWidth, Colour):
        '''
        Colours graphitems in traverse object
        :param gui: contains traverse object
        :param lineWidth:
        :param Colour:
        '''

        # lines
        if len(gui.traverse.Lines.__dict__.keys()) > 1:
            self.ColourLines(gui, lineWidth, Colour)

        # Points
        if len(gui.traverse.Points.__dict__.keys()) > 0:
            self.ColourPoints(gui, lineWidth, Colour)

        # Arcs
        #if len(gui.traverse.Arcs.__dict__.keys()) > 0:
        #    self.ColourArcs(gui, lineWidth, Colour)

    def ColourLines(self, gui, lineWidth, Colour):
        '''
        Colours lines in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''

        for key in gui.traverse.Lines.__dict__.keys():
            if key != "LineNum":
                line = gui.traverse.Lines.__getattribute__(key)
                lineItem = line.GraphicsItems.Line
                self.SetObjectPen(lineItem, Colour, lineWidth)
                gui.view.scene.update()

    def ColourPoints(self, gui, lineWidth, Colour):
        '''
        Colours points in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''

        for key in gui.traverse.Points.__dict__.keys():
            if key == "PointList":
                continue
            point = gui.traverse.Points.__getattribute__(key)
            PointItem = point.GraphicsItems.Point
            self.SetObjectPen(PointItem, Colour, lineWidth)
            self.SetObjectBrush(PointItem, Colour)
            gui.view.scene.update()

    def ColourArcs(self, gui, lineWidth, Colour):
        '''
        Colourts arcs in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''
        for key in gui.traverse.Arcs.__dict__.keys():
            if key != "ArcNum":
                arc = gui.traverse.Arcs.__getattribute__(key)
                ArcItem = arc.GraphicsItems.Arc
                self.SetObjectPen(ArcItem, Colour, lineWidth)

    def SetObjectPen(self, item, colour, linewidth):
        '''
        Sets colour of item pen
        :param line:
        :return:
        '''
        # QtGui.QColor.
        Pen = QPen(colour)
        Pen.setWidth(linewidth)
        item.setPen(Pen)

    def SetObjectBrush(self, item, colour):
        '''
        Sets colour ofitem brush
        :param line:
        :return:
        '''
        # QtGui.QColor.
        Brush = QBrush(colour)
        item.setBrush(Brush)

def CheckTraverseExists(gui):
    '''
    Checks if a Traverse object exists for gui object
    :param gui:
    :return:
    '''

    if hasattr(gui, "traverse"):
        return True
    else:
        return False

def RemoveCurrentTraverseFromGui(gui):
    '''
    Removes the current traverse from gui
    :param gui:
    :return:
    '''

    #delete points
    for key in gui.traverse.Points.__dict__.keys():
        if key == "PointList":
            continue
        Point = gui.traverse.Points.__getattribute__(key)
        #remove the graphicsItems
        GraphicsItems = Point.GraphicsItems
        RemoveGraphicsItems(GraphicsItems, gui)

    #delete Lines
    for key in gui.traverse.Lines.__dict__.keys():
        Line = gui.traverse.Lines.__getattribute__(key)
        # remove the graphicsItems
        if hasattr(Line, "GraphicsItems"):
            GraphicsItems = Line.GraphicsItems
            RemoveGraphicsItems(GraphicsItems, gui)
    '''
    #delete Arcs
    for key in gui.traverse.Arcs.__dict__.keys():
        Arc = gui.traverse.Arcs.__getattribute__(key)
        # remove the graphicsItems
        if hasattr(Arc, "GraphicsItems"):
            GraphicsItems = Arc.GraphicsItems
            RemoveGraphicsItems(GraphicsItems, gui)
    '''

def RemoveGraphicsItems(GraphicsItems, gui):
    '''
    Removes items held in GraphicsItems Objects from GUI
    :param GraphicsItems:
    :return:
    '''

    for key in GraphicsItems.__dict__.keys():
        item = GraphicsItems.__getattribute__(key)
        if key != "Label":
            gui.view.scene.removeItem(item)

class RedrawTraverse:

    def __init__(self, gui):
        '''
        Redraws traverse with adjusted coorindates for points
        '''

        #remove items
        RemoveCurrentTraverseFromGui(gui)

        #remove last point and create a line closing traverse
        if gui.ApplyTraverseAdjust:
            self.UpdateTraverseEnding(gui)

        #draw points
        self.DrawPoints(gui)

        #draw lines
        self.DrawLines(gui)

    def UpdateTraverseEnding(self, gui):
        '''
        ONce traverse is adjusted the last point is a duplicate
        Remove last point and join traverse onto the known close point
        :param gui:
        :return:
        '''

        #remove last point
        delattr(gui.traverse.Points, gui.traverse.refPnts[-1])
        del gui.traverse.refPnts[-1]
        #change the last lines end point ref to the traverse end point
        for key in gui.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            line = gui.traverse.Lines.__getattribute__(key)
            if line.StartRef == gui.traverse.refPnts[-1]:
                setattr(line, "EndRef", gui.traverse.EndRefPnt)
                if not gui.traverse.FirstTraverse:
                    point = gui.CadastralPlan.Points.__getattribute__(gui.traverse.EndRefPnt)
                    setattr(gui.traverse.Points, gui.traverse.EndRefPnt, point)


    def DrawPoints(self, gui):
        '''
        Draws point in traverse
        :param gui:
        :return:
        '''

        for key in gui.traverse.Points.__dict__.keys():
            if key == "PointList":
                continue
            point = gui.traverse.Points.__getattribute__(key)
            LinesPoints.AddPointToScene(gui.view, point, point.Layer)

    def DrawLines(self, gui):
        '''
        Draws point in traverse
        :param gui:
        :return:
        '''

        #draw lines in traverse object
        for key in gui.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            Line = gui.traverse.Lines.__getattribute__(key)

            #get start and end points
            PointS = gui.traverse.Points.__getattribute__(Line.StartRef)
            PointE = gui.traverse.Points.__getattribute__(Line.EndRef)

            # Get Line Props
            LineProps = LinesPoints.LinePointProperties()
            LinePen, Layer, colour = LineProps.SetLineProperties(PointE.Layer,
                                                         PointS.Layer)

            if Line.type == "Line":
                GraphLine = self.AddLine(Line, LinePen, PointS, PointE, gui)
                setattr(Line, "BoundingRect", GraphLine.boundingRect())
            else:
                GraphLine = self.AddArc(Line, LinePen, PointS, PointE, gui)
                setattr(Line, "BoundingRect", GraphLine.boundingRect())


    def AddLine(self, Line, LinePen, PointS, PointE, gui):
        '''
        Adds Line to graphicsview
        :param Line:
        :param LinePen:
        :param PointS:
        :param PointE:
        :return:
        '''

        GraphLine = gui.view.Line(int(PointS.E*1000), int(PointS.NorthingScreen*1000),
                                  int(PointE.E*1000), int(PointE.NorthingScreen*1000), LinePen)
        setattr(Line.GraphicsItems, "Line", GraphLine)

        return GraphLine

    def AddArc(self, Line, LinePen, PointS, PointE, gui):
        '''
        Adds an arc to graphcisview
        :param Line:
        :param LinePen:
        :param PointS:
        :param PointE:
        :param gui:
        :return:
        '''

        CentreArcCoords = funcs.ArcCentreCoords(PointS, PointE, Line.Radius, Line.Rotation)

        #Update arc object
        Line.CentreEast = CentreArcCoords.CentreEasting
        Line.CentreNorthing = CentreArcCoords.CentreNorthing

        #get arc path object
        Params = ArcParams(Line.Radius, Line.Rotation)
        ArcPath = Arcs.DrawArc(PointS, PointE, CentreArcCoords, Params)
        #add Arc Path to GUI
        ArcLine = gui.view.scene.addPath(ArcPath.arcPath, LinePen)
        ArcLine.setFlag(QGraphicsItem.ItemIsSelectable, True)
        Line.BoundingRect = ArcLine.boundingRect()
        #add Arc GraphItem
        setattr(Line.GraphicsItems, "Line", ArcLine)

        return ArcLine




class ArcParams:
    def __init__(self, radius, rotation):
        self.Radius = radius
        self.ArcRotation = rotation



