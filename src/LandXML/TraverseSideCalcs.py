'''
Methods and workflow to calculate new points from a connection selected from the LandXMl
Adds linework (calcs for arcs)
Adds traverse side to current traverse and gui
'''
import genericFunctions as funcs
import CadastreClasses as DataObjects
from LandXML.RefMarks import RefMarkQueries
from LandXML import Connections, BDY_Connections
from DrawingObjects import LinesPoints
from numpy import sin, cos, radians
class TraverseSide:

    def __init__(self, PntRefNum, traverse, Connection, gui, LandXML_Obj):
        '''
        Initialise class attributes
        :param PntRefNum: RefNum for start of traverse side
        :param traverse: traverse data object
        :param Connection: Connection to be added
        :param gui:
        '''
        self.PntRefNum = PntRefNum
        self.traverse = traverse
        try:
            for key in Connection.Observations.__dict__.keys():
                self.Connection = Connection.Observations.__getattribute__(key)
                break
        except AttributeError:
            try:
                self.Connection = Connection.__getattribute__("Observation")
            except AttributeError:
                self.Connection = Connection

        self.ObsName = self.Connection.get("name")
        self.traverse.Observations.append(self.Connection)
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.CalcPointCoordsWorkflow()

    def CalcPointCoordsWorkflow(self):
        '''
        Calculates the coordinates of the point at the end of the connection
        :return:
        '''
        #get Connection bearing and distance
        self.ConnectionBearing()
        self.ConnectionDistance()
        #get new points PntRefNum
        self.TargPntRefNum = self.GetTargetPointRefNum()        
        #get Point code - if RM
        self.Code = self.GetPointCode()
        if hasattr(self.traverse.Points, self.TargPntRefNum):
            self.TargPntRefNum = self.TargPntRefNum + "_1"
        self.traverse.refPnts.append(self.TargPntRefNum)
        #Calculate the coordinates of the new point - creates a point data object
        self.CalcPointCoords()
        self.AddPoint2Traverse()
        #self.AddPoint2GUI()
        if self.LineType == "Line":
            self.AddLine2Traverse()
        else:
            self.AddArc2Traverse()


    def ConnectionBearing(self):
        '''
        return connection bearing from landXML element
        Accounts for chord attributes of Arcs
        :return: bearing
        '''
        self.bearing = Connections.GetObservationAzimuth(self.Connection)

    def ConnectionDistance(self):
        '''
        return connection distance from landXML element
        Accounts for chord attributes of Arcs
        :return: distance
        '''
        self.distance = Connections.GetObservationDistance(self.Connection)
        self.LineType = Connections.GetLineType(self.Connection)

        if self.LineType == "Arc":
            self.radius = self.Connection.get("radius")
            #reverse rotation when self.PntRefNUm is the end on the Observation
            if not Connections.ObservationOrientation(self.PntRefNum, self.Connection,
                                                  self.LandXML_Obj.TraverseProps):
                self.rotation = self.SetArcRotation(self.Connection.get("rot"), True)
            else:
                self.rotation = self.SetArcRotation(self.Connection.get("rot"), False)

    def CalcChordLength(self, arcLength):
        '''
        LandXML provides the arc length for an arc connection
        This functions calculated the chord length from the arc length and radius
        :param arcLength: length of arc segeent
        :return: chord length - distance
        '''
        distance = 2 * float(self.radius) * sin(float(arcLength) / (2 * float(self.radius)))
        return distance

    def CalcPointCoords(self):
        '''
        Calculates the coordinates of the new point
        creates attributes for their E and N
        '''
        #convert bearing to decimal
        bearing = funcs.bearing2_dec(self.bearing)
        #Return angle for point calculate and its sign for Easting and Northing
        angle, deltaE, deltaN = funcs.bearing2angle(bearing)
        # calculate change in coordinates
        self.deltaE = float(self.distance) * sin(radians(angle)) * deltaE
        self.deltaN = float(self.distance) * cos(radians(angle)) * deltaN
        #get source point object from traverse object
        SrcPoint = self.traverse.Points.__getattribute__(self.PntRefNum)
        #calculate new coordinates
        self.E = float(SrcPoint.E) + self.deltaE
        self.N = float(SrcPoint.N) + self.deltaN
        self.N_Screen = float(SrcPoint.NorthingScreen) - self.deltaN
        Layer = self.EndPointType()

        # create new point object
        self.point = DataObjects.Point(self.TargPntRefNum, self.E, self.N, self.N_Screen,
                                  None, self.Code, Layer)

    def GetTargetPointRefNum(self):
        '''
        Gets the reference point number for the point to be calculated
        :return: Target
        '''
        # Get TargetID PnteRef
        if self.Connection.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "") == \
                self.PntRefNum:
            return self.Connection.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        else:
            #flip bearing
            bearing = float(self.bearing) + 180
            if bearing >= 360:
                bearing = bearing - 360

            self.bearing  = self.CheckBearingFormat(bearing)
            
            return self.Connection.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
    def CheckBearingFormat(self, bearing):
        '''
        When a bearing flip is performed the bearing format can be wrong
        :param bearing:
        :return:
        '''
        bearing = str(round(bearing,4))
        if len(bearing.split(".")) == 1:
            return bearing

        if len(bearing.split(".")[1]) == 1:
            bearing += "0"
        elif len(bearing.split(".")[1]) == 3:
            bearing += "0"

        return bearing

    def GetPointCode(self):
        '''
        Gets the point code of the point to be calculated
        Only retrieves codes for RMs
        '''
        # Get RM type - None if not RM
        MarkType = RefMarkQueries.FindMarkType(self.LandXML_Obj, self.TargPntRefNum)
        if MarkType is not None:
            Code = "RM"+MarkType

            #Check if SSM or PM
            if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, self.TargPntRefNum):
                try:
                    Code += "-" + RefMarkQueries.GetMarkNumber(self.LandXML_Obj, self.TargPntRefNum)
                except TypeError:
                    Code += "-" + RefMarkQueries.GetMarkNumberMonuments(self.LandXML_Obj, self.TargPntRefNum)
        else:
            Code = ""

        return Code

    def SetLinePointGuiProps(self):
        '''
        Sets properties of line and points to be drawn on the drawing canvas
        '''
        #get source point layer
        self.SrcPoint = self.traverse.Points.__getattribute__(self.PntRefNum)
        #get line props
        LineProps = LinesPoints.LinePointProperties()

        self.LinePen, self.LineLayer, \
        self.LineColour = LineProps.SetLineProperties(self.SrcPoint.Layer, self.point.Layer)

    def AddPoint2Traverse(self):
        '''
        Adds point object to traverse.Points
        '''
        setattr(self.traverse.Points, self.TargPntRefNum, self.point)


    def AddPoint2GUI(self):
        '''
        Adds point object to gui
        '''

        Layer = self.EndPointType(self.point)
        pointObj = LinesPoints.AddPointToScene(self.gui.view, self.point, "BOUNDARY")
        
    
    def AddLine2Traverse(self):
        '''
        Creates a line object and adds it to Traverse.Lines
        '''
        # get line drawing properties
        self.SetLinePointGuiProps()

        #create Line odata class and populate attributes
        self.line = DataObjects.Line(self.PntRefNum, self.TargPntRefNum,
                                self.LineLayer, self.distance,
                                self.deltaE, self.deltaN, self.bearing, self.LineColour)

        #add line to the GUI - adds Graphics Items to line class
        #self.AddLine2GUI()
        #LineNum = self.traverse.Lines.LineNum + 1
        setattr(self.traverse.Lines, self.ObsName, self.line)
        self.traverse.Lines.LineNum += 1

    def AddArc2Traverse(self):
        '''
        Creates an arc object and adds it to the traverse.Lines objects
        :return:
        '''

        # get line drawing properties
        self.SetLinePointGuiProps()

        # get coordinates for centre of the arc
        CentreArcCoords = funcs.ArcCentreCoords(self.SrcPoint, self.point,
                                               self.radius, self.rotation)
        
        ArcAngles = funcs.ArcAngles(self.SrcPoint, self.point, CentreArcCoords, self.rotation)

        #create arc object
        self.line = DataObjects.Arc(self.PntRefNum, self.TargPntRefNum,
                              self.LineLayer, self.radius,
                              CentreArcCoords, self.rotation, self.distance,
                              self.bearing, self.deltaE, self.deltaN, self.LineColour,
                                    ArcAngles)

        #Add arc to traverse
        #LineNum = self.traverse.Lines.LineNum + 1
        setattr(self.traverse.Lines, self.ObsName, self.line)
        self.traverse.Lines.LineNum += 1




    def AddLine2GUI(self):
        '''
        Adds line to drawing canvas
        Includes:
            using correct line properties
            Calculating screen coords
            Add bearing and distance labels onto the drawing canvas

        '''
        #get line end screen coordinates
        E = self.E * 1000
        N = self.N_Screen * 1000

        #get start of line screen coordinates coordinates
        #SrcPoint = self.traverse.Points.__getattribute__(self.PntRefNum)
        SrcEasting = self.SrcPoint.E * 1000
        SrcNorthing = self.SrcPoint.NorthingScreen * 1000

        #add line to gui and to Line graphics items
        self.GraphLine = self.gui.view.Line(SrcEasting, SrcNorthing, E, N, self.LinePen)
        #add QGraphicsLine to line.GraphicsItems
        setattr(self.line.GraphicsItems, "Line", self.GraphLine )
        self.line.BoundingRect = self.GraphLine.boundingRect()

        #add line bearing and distance label - add as graphicsItem in line.GraphicsItems
        if abs(float(self.distance)) > 30:
            self.AddLineBearingDistance2GUI(SrcPoint)

    '''
    def ArcCalcs(self):
    def AddArc2GUI(self):
    '''
    def AddLineBearingDistance2GUI(self, SrcPoint):
        '''
        Determine line properties to display bearings and distances
        Adds them to the drawing canvas and then to line data class
        '''

        if len(self.bearing.split(".")) == 1:
            bearingStr = self.bearing + eval(r'"\u00B0"')
        elif len(self.bearing.split(".")[1]) == 2:
            bearingStr = self.bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         self.bearing.split(".")[1][0:2] + "'"
        else:
            bearingStr = self.bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         self.bearing.split(".")[1][0:2] + "' " + \
                         self.bearing.split(".")[1][2:] + "\""

        Distance = abs(float(self.distance))
        LinePropsStr = bearingStr + " ~ " + str(Distance)
        LineMidEasting = (SrcPoint.E + self.point.E) / 2
        LineMidNorthing = (SrcPoint.NorthingScreen + self.point.NorthingScreen) / 2
        bearing = funcs.bearing2_dec(self.bearing)
        rotation = self.LabelRotation(bearing)

        LineLabel = self.gui.view.Text(LineMidEasting, LineMidNorthing, rotation, LinePropsStr)
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

    def SetArcRotation(self, rotation, reverse):
        '''
        Reverses rotation of arc when src point is target in alndXML Observation
        :return:
        '''

        if rotation == "ccw" and reverse:
            return "CW"
        elif rotation == "cw" and reverse:
            return "CCW"
        elif rotation == "ccw":
            return "CCW"
        else:
            return "CW"

    def EndPointType(self):
        '''
        Determines the type of point
        :return:
        '''
        
        if self.traverse.type == "EASEMENT":
            return "EASEMENT"

        desc = self.Connection.get("desc")
        if self.CheckIfBoundary():
            return "BOUNDARY"
        elif RefMarkQueries.CheckIfMonument(self.LandXML_Obj, self.TargPntRefNum.split("_")[0]) or \
            desc == "Reference":
            return "REFERENCE MARKS"
        elif desc == "Connection" or desc == "Road Extent" or desc == "IrregularLine" or \
                desc == "Road":
            return "BOUNDARY"



    def CheckIfBoundary(self):
        '''
        checks if end point is a boundary - for layer determination
        :return:
        '''

        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)
        #Loop through parcels in landXML file
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")

            if parcelClass != "Easement" or parcelClass != "Restriction On Use Of Land" or \
                    parcelClass != "Designated Area":
                if ConnectionChecker.CheckParcelLines(parcel, self.TargPntRefNum.split("_")[0],
                                                   self.LandXML_Obj.TraverseProps):
                    return True

        return False



