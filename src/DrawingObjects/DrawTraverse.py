'''
Draws traverse selected from LandXML file
'''

from DrawingObjects import LinesPoints, Arcs
import CadastreClasses as DataObjects
import genericFunctions as funcs

def main(gui, traverse):
    '''
    Coordinates workflow to draw traverse on drawing canvas
    Calculates close
    Throws adjust message
    :param gui:
    :param traverse:
    :return:
    '''
    # get instance to add data to CadastralPlan
    DataCommitObject = DataCommit(gui.CadastralPlan, traverse)
    #DataCommitObject
    DataCommitObject.AddPoints()
    DataCommitObject.AddLines()
    DataCommitObject.AddTraverses()

    #get instance of DarwTraverse
    DrawObject = DrawTraverse(gui, traverse)
    DrawObject.DrawPoints()
    DrawObject.DrawLines()
    
class DrawTraverse:
    def __init__(self, gui, traverse):
        '''
        :param gui: drawing cnavas instance
        :param traverse: traverse object
        '''
        self.gui = gui
        self.traverse = traverse

    def DrawPoints(self):
        '''
        draws point objects in traverse and adds associated text
        - point number and codes
        '''

        #loop through refPnts list
        for i, StartRef in enumerate(self.traverse.refPnts):
            try:
                EndRef = self.traverse.refPnts[i+1]
                self.EndPoint = self.traverse.Points.__getattribute__(EndRef)
                pointObj = LinesPoints.AddPointToScene(self.gui.view, self.EndPoint, 
                                                       self.EndPoint.Layer)

            except IndexError:
                pass
                
    
    def DrawLines(self):
        '''
        Draws lines in traverse on drawing canvase 
        '''
        
        #loop through lines
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            self.line = self.traverse.Lines.__getattribute__(key)
            self.GetLineCoordinates()
            self.SetLinePointGuiProps()

            if self.line.type == "Line":
                self.DrawLine()
            else:
                self.DrawArc()
            
 
    def GetLineCoordinates(self):
        '''
        Retrieves point coordinates for start and end of line
        :return: 
        '''
        
        #get source point coordinates
        StartRef = self.line.StartRef
        self.SrcPoint = self.traverse.Points.__getattribute__(StartRef)
        self.SrcPointE = self.SrcPoint.E * 1000
        self.SrcPointN = self.SrcPoint.NorthingScreen * 1000
        
        #get end point coords
        # get source point coordinates
        EndRef = self.line.EndRef
        self.EndPoint = self.traverse.Points.__getattribute__(EndRef)
        self.EndPointE = self.EndPoint.E * 1000
        self.EndPointN = self.EndPoint.NorthingScreen *1000
        
    def SetLinePointGuiProps(self):
        '''
        Sets properties of line and points to be drawn on the drawing canvas
        '''

        #get line props
        LineProps = LinesPoints.LinePointProperties()

        self.LinePen, self.LineLayer, \
        self.LineColour = LineProps.SetLineProperties(self.SrcPoint.Layer,
                                                      self.EndPoint.Layer)
        
    def DrawLine(self):
        '''
        Draws line defined by SrcPoint and EndPoint coords on drawing canvas
        '''

        # add line to gui and to Line graphics items
        self.GraphLine = self.gui.view.Line(self.SrcPointE, self.SrcPointN,
                                            self.EndPointE, self.EndPointN,
                                            self.LinePen)

        # add QGraphicsLine to line.GraphicsItems
        setattr(self.line.GraphicsItems, "Line", self.GraphLine)
        self.line.BoundingRect = self.GraphLine.boundingRect()

        if abs(float(self.line.Distance)) > 30:
            self.AddLineBearingDistance2GUI()

    def DrawArc(self):
        '''
        Draws arc defined by SrcPoint and EndPoint coords on drawing canvas
        '''
        #Get Arc drawing params
        ArcParamsObj = ArcParams(self.line)
        #create path object to draw arc
        # get arc path object
        ArcPath = Arcs.DrawArc(self.SrcPoint, self.EndPoint, self.line.CentreCoords, ArcParamsObj)
        #draw arc
        ArcLine = self.gui.view.scene.addPath(ArcPath.arcPath, self.LinePen)
        self.line.BoundingRect = ArcLine.boundingRect()
        setattr(self.line.GraphicsItems, "Line", self.GraphLine)


    def AddLineBearingDistance2GUI(self):
        '''
        Determine line properties to display bearings and distances
        Adds them to the drawing canvas and then to line data class
        '''

        if len(self.line.Bearing.split(".")) == 1:
            bearingStr = self.line.Bearing + eval(r'"\u00B0"')
        elif len(self.line.Bearing.split(".")[1]) == 2:
            bearingStr = self.line.Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         self.line.Bearing.split(".")[1][0:2] + "'"
        else:
            bearingStr = self.line.Bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         self.line.Bearing.split(".")[1][0:2] + "' " + \
                         self.line.Bearing.split(".")[1][2:] + "\""

        Distance = abs(float(self.line.Distance))
        LinePropsStr = bearingStr + " ~ " + str(Distance)
        LineMidEasting = (self.SrcPoint.E + self.EndPoint.E) / 2
        LineMidNorthing = (self.SrcPoint.NorthingScreen +\
                           self.EndPoint.NorthingScreen) / 2
        bearing = funcs.bearing2_dec(self.line.Bearing)
        rotation = self.LabelRotation(bearing)

        LineLabel = self.gui.view.Text(LineMidEasting, LineMidNorthing, rotation,
                                       LinePropsStr)
        setattr(self.line.GraphicsItems, "LineLabel", LineLabel)

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
    '''
    def AddLineBearingLabel
        
    def AddArc
        
    def AddArcLabels
    '''

class DataCommit:

    def __init__(self, CadastralPan, traverse):

        self.CadastralPan = CadastralPan
        self.traverse = traverse
    
    #def RemoveGraphicsItems 

    def AddPoints(self):
        '''
        Adds points from traverse to Cadastral Plan
        '''
        self.GetPointNumber()
        #sequentially add points in traverse to CadastralPlan
        for key in self.traverse.Points.__dict__.keys():
            point = self.traverse.Points.__getattribute__(key)
            setattr(self.CadastralPan.Points, key, point)

    def AddLines(self):
        '''
        Add line objects to CadastralPlan
        :return:
        '''

        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            line = self.traverse.Lines.__getattribute__(key)
            LineNum = self.CadastralPan.Lines.__getattribute__("LineNum")
            setattr(self.CadastralPan.Lines, ("Line" + str(LineNum)), line)
            setattr(self.CadastralPan.Lines, "LineNum", (LineNum+1))

    def AddTraverses(self):
        '''
        Add Travers to CadstralPlan
        :return:
        '''

        TraverseNum = self.CadastralPan.Traverses.TraverseCounter
        TravName = "Traverse" +"_" + self.traverse.type + "_" +str(TraverseNum)
        setattr(self.CadastralPan.Traverses, TravName, self.traverse)
        setattr(self.CadastralPan.Traverses, "TraverseCounter", (TraverseNum+1))

    def GetPointNumber(self):
        '''
        Gets a point number for traverse close
        adds "_#" to point number if already a point
        increments as more points are added (more closes at same point)
        updates fields with new point name
        :return:
        '''

        PntNum = self.traverse.refPnts[-1]
        if hasattr(self.CadastralPan.Points, PntNum):
            counter = 0
            for key in self.CadastralPan.Points.__dict__.keys():
                if key == self.traverse.refPnts[-1]:
                    counter +=1
            
            point = self.traverse.Points.__getattribute__(self.traverse.refPnts[-1])
            delattr(self.traverse.Points, self.traverse.refPnts[-1])
            NewPntNum = self.traverse.refPnts[-1] + "_" + str(counter)
            point.PntNum = NewPntNum
            self.traverse.refPnts[-1] = NewPntNum
            setattr(self.traverse.Points, NewPntNum, point)


            #Update point reference in traverse lines
            for key in self.traverse.Lines.__dict__.keys():
                if key == "LineNum":
                    continue
                line = self.traverse.Lines.__getattribute__(key)
                if line.EndRef == str(PntNum):
                    line.EndRef = NewPntNum



        
        
        
class ArcParams:
    def __init__(self, ArcObject):
        self.Radius = ArcObject.Radius
        self.ArcRotation = ArcObject.Rotation


        

