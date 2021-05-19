'''
Mops up the remaining connections that were not calculated by traverse
Draws lines between existing points
Does not calculate Easements - these are filtered
Checks if both ends of the Observation to be drawn are calc'd otherwise observation is not drawn
'''

import genericFunctions as funcs
from LandXML.RefMarks import RefMarkQueries
from LandXML.Easements import RemoveEasements
from LandXML import PointClass, SharedOperations, TraverseSideCalcs
from DrawingObjects import LinesPoints, Arcs

import CadastreClasses as DataObjects

def main(gui, LandXML_Obj):
    '''
    Coordinates calculation of remaining connections
    Should be all single connections
    Either draws the connection (if connects to already calculated points)
        - trigger error when too different to calc'd point
    :param CadastralPlan: contains the calculated Cadastral data
    :param LandXML_Obj: contains observations to mop up
    :return Cadastral Plan
    '''

    #Create Connection Mopper Object
    ConnectionMop = ObservationMop(gui, LandXML_Obj)

    for obs in LandXML_Obj.ReducedObs:
        #ignore Easements
        if CheckIfEasement(LandXML_Obj, obs):
            continue

        ConnectionMop.ObservationCalculator(obs)

    print("Observations left after connection mopper: " + str(len(LandXML_Obj.ReducedObs)))

def CheckIfEasement(LandXML_Obj, Observation):
    '''
    Checks if observation is an easment
    :param LandXML_Obj:
    :param Observation:
    :return:
    '''
    try:
        PntRefNum = Observation.get("setupID").replace(LandXML_Obj.TraverseProps.tag, "")
        TargetID = Observation.get("targetSetupID").replace(LandXML_Obj.TraverseProps.tag, "")
        RemoveEasObj = RemoveEasements.RemoveEasementObservations(Observation,
                                                                  PntRefNum,
                                                                  LandXML_Obj)
        if RemoveEasObj.CheckLotParcel(TargetID):
            return False
        elif RemoveEasObj.SearchEasementParcels(TargetID):
            return True
        else:
            return False
    except AttributeError:
        return False



class ObservationMop:

    def __init__(self, gui, LandXML_Obj):
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan
        self.LandXML_Obj = LandXML_Obj

    def ObservationCalculator(self, Observation):
        '''
        Coordinates the seach for observation not drawn on the UI
        or added to the Cadastral Plan
        These will be the only connections remaining in LandXML_Obj.ReducedObs
        :return:
        '''
        #get observation name
        self.ObsName = Observation.get("name")
        #Set whether observation is arc or line
        if Observation.tag.replace(self.LandXML_Obj.TraverseProps.Namespace,"") == \
                'ReducedObservation':
            self.Arc = False
        else:
            self.Arc = True
        #Get start and end point of Observation
        self.StartRef, self.EndRef, Flip, self.connection = self.FindEndPoint(Observation)
        if self.StartRef is not None:
            self.SrcPoint = self.CadastralPlan.Points.__getattribute__(self.StartRef)
            #create a traverse object to store connection
            TravStart = SharedOperations.TraverseStartPoint(self.StartRef, self.CadastralPlan)
            self.traverse = SharedOperations.initialiseTraverse(TravStart, TravStart.Layer, False)
            self.distance = self.GetDistance(Observation)
            self.bearing = self.GetBearing(Observation, Flip)
            #calculate point
            self.PointCalculation(Observation)
            self.LineObj(Flip)
            self.DrawObservation()
            Observation.getparent().remove(Observation)


        #print("Done")

    def FindEndPoint(self, Observation):
        '''
        Determines what the start end point of the observation is
        If both end and start of Observation are already calculated - just takes setupID
        If RM with no end not calc'd - sets already calc'd point as startpoint
        :return:
        '''
        try:
            SetupID = Observation.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            TargetID = Observation.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        except AttributeError:
            Observation.getparent().remove(Observation)
            return None, None, None, None

        if hasattr(self.CadastralPlan.Points, SetupID) and \
            hasattr(self.CadastralPlan.Points, TargetID):
            #Observation between 2 already calc'd points
            return SetupID, TargetID, False, True
        elif hasattr(self.CadastralPlan.Points, SetupID):
            #CadastralPlan only contains the setupid point
            return SetupID, TargetID, False, False
        elif hasattr(self.CadastralPlan.Points, TargetID):
            #Contains
            return TargetID, SetupID, True, False
        else:
            return None, None, None, None



    def GetDistance(self, Observation):
        '''
        Gets distance for obs
        If arc true, calculates chord distance. LandXML gives the arc
        :return:
        '''
        if not self.Arc:
            return Observation.get("horizDistance")
        else:
            ArcLength = Observation.get("length")
            self.radius = Observation.get("radius")
            self.rotation = Observation.get("rot")
            return funcs.CalcChordLength(self.radius, ArcLength)

    def GetBearing(self, Observation, Flip):
        '''
        Gets bearing of obs, rotates if targetID is start of connection
        :param Observation:
        :return:
        '''
        #retrieve bearing of observation
        if self.Arc:
            bearing = Observation.get("chordAzimuth")
        else:
            bearing = Observation.get("azimuth")

        #Flip bearing if required
        if Flip:
            bearing = str(funcs.FlipBearing(float(bearing)))
            if len(bearing.split(".")[1]) == 1 or \
                    len(bearing.split(".")[1]) == 3:
                bearing += "0"

        return bearing

    def PointCalculation(self, Observation):
        '''
        Calculates the end point of the connection
        :return: 
        '''

        self.PointObj = PointClass.Points(self.LandXML_Obj, self.CadastralPlan.Points)
        self.point = self.PointObj.CalcPoints(self.bearing, self.distance,
                                         self.StartRef, self.EndRef,
                                         Observation)
        #create line object
        
    def LineObj(self, Flip):
        '''
        Creates a Line object between the start and end point
        :return: 
        '''
        
        # get line properties
        self.SetLinePointGuiProps()
        
        if not self.Arc:
            self.line = DataObjects.Line(self.StartRef, self.EndRef,
                                     self.LineLayer, self.distance,
                                     self.PointObj.deltaE, self.PointObj.deltaN,
                                     self.bearing, self.LineColour)
        else:
            self.CreateArcLine(Flip)

    def CreateArcLine(self, Flip):

        # set rotation
        ArcObjCls = Arcs.ArcClass(self.rotation)
        if Flip:
            self.rotation = ArcObjCls.SetArcRotation(True)
        else:
            self.rotation = ArcObjCls.SetArcRotation(False)
        # get coordinates for centre of the arc
        CentreArcCoords = funcs.ArcCentreCoords(self.SrcPoint, self.point,
                                           self.radius, self.rotation)


        #create arc object
        self.line = DataObjects.Arc(self.StartRef, self.EndRef,
                          self.LineLayer, self.radius,
                          CentreArcCoords, self.rotation, self.distance,
                          self.bearing, self.PointObj.deltaE,
                            self.PointObj.deltaN, self.LineColour)
    
    def CheckClose(self):
        '''
        For when calculation is between 2 points already calc'd
        Throw message when >5mm. Colour and show
        :return: 
        '''
        
    def DrawObservation(self):
        '''
        Draws the Observation in gui and adds it to the Cadastral Plan
        :return:
        '''
        
        if self.connection:
            self.DrawLineMeth()
        else:
            self.DrawPoint()
            setattr(self.CadastralPlan.Points, self.EndRef, self.point)
            self.DrawLineMeth()
        
        setattr(self.CadastralPlan.Lines, self.ObsName, self.line)
            
    def DrawPoint(self):  
        '''
        Draws point on UI
        '''
        pointObj = LinesPoints.AddPointToScene(self.gui.view, self.point,
                                               self.point.Layer)
        
    def DrawLineMeth(self):
        '''
        Draw Line coordination method
        :return: 
        '''
        
        
        if not self.Arc:
            self.DrawLine()
        else:
            self.DrawArc()
            
    def DrawLine(self):
        '''
        Draws line in UI
        '''
        self.GraphLine = self.gui.view.Line(self.SrcPoint.E*1000, self.SrcPoint.NorthingScreen*1000,
                                            self.point.E*1000, self.point.NorthingScreen*1000,
                                            self.LinePen)

        # add QGraphicsLine to line.GraphicsItems
        setattr(self.line.GraphicsItems, "Line", self.GraphLine)
        self.line.BoundingRect = self.GraphLine.boundingRect()
        
    def DrawArc(self):
        '''
        Draws arc defined by SrcPoint and EndPoint coords on drawing canvas
        '''
        #Get Arc drawing params
        ArcParamsObj = ArcParams(self.line)
        #create path object to draw arc
        # get arc path object
        ArcPath = Arcs.DrawArc(self.SrcPoint, self.point, self.line.CentreCoords, ArcParamsObj)
        #draw arc
        ArcLine = self.gui.view.scene.addPath(ArcPath.arcPath, self.LinePen)
        self.line.BoundingRect = ArcLine.boundingRect()
        
    def SetLinePointGuiProps(self):
        '''
        Sets properties of line and points to be drawn on the drawing canvas
        '''

        #get line props
        LineProps = LinesPoints.LinePointProperties()

        self.LinePen, self.LineLayer, \
        self.LineColour = LineProps.SetLineProperties(self.SrcPoint.Layer,
                                                      self.point.Layer)
        
        
class ArcParams:
    def __init__(self, ArcObject):
        self.Radius = ArcObject.Radius
        self.ArcRotation = ArcObject.Rotation