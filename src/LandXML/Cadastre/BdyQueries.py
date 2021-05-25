'''
Set of functions and methods to query a boundary point
'''
from LandXML import Connections, RemoveCalculatedConnections, BDY_Connections, RemoveDeadEnds
import CadastreClasses as DataObjects
from LandXML.Easements import RemoveEasements
from timer import Timer

def main(LandXML_Obj, PntRefNum, gui, Query, RM_Connection):
    '''
    Coordinates 
    :param LandXML_Obj: 
    :param PntRefNum: 
    :param Query: 
    :return: 
    '''
    #if PntRefNum == "65":
    #    print("Stop")
        
    # Get connections from PntRefNum
    Observations = Connections.AllConnections(PntRefNum, LandXML_Obj)
    # Remove already calculated connections
    Observations = RemoveCalculatedConnections.main(Observations, gui.CadastralPlan,
                                                             DataObjects.Traverse(False, "RM"),
                                                             LandXML_Obj.TraverseProps,
                                                             PntRefNum)
    Observations  = RemoveCalculatedConnections.CheckTargetPoint(Observations,
                                                                 gui.CadastralPlan,
                                                                 PntRefNum,
                                                                 LandXML_Obj)
    #Remove Easements
    RemoveEasObj = RemoveEasements.RemoveEasementObservations(Observations,
                                                              PntRefNum,
                                                              LandXML_Obj)
    Observations = RemoveEasObj.SearchObservations()
    if len(Observations.__dict__.keys()) == 0:
        #gui.CadastralPlan.Points.PointList.remove(PntRefNum)
        return PntRefNum
    
    # Loop through available observations
    #tObj = Timer()
    if RM_Connection:
        #tests connections to the RM connection
        return TestTargetObservations(Observations, LandXML_Obj, gui, Query, PntRefNum, False)
        #tObj.start()

        #tObj.stop("RM searches")
    else:
        #tests connections to PntRefNum
        #tObj.start()
        RunQueryObj = RunQuery(Observations, LandXML_Obj, Query, PntRefNum, gui.CadastralPlan, 
                               False)#, RM_Connection)
        if RunQueryObj.CoordinateQuery():
            return True

        #tObj.stop("Non RM start query")
            

    return False

def TestTargetObservations(Observations, LandXML_Obj, gui, Query, PntRefNum, GetStart):
    '''
    Tests Observations from Target of Observation
    :return:
    '''
    for key in Observations.__dict__.keys():
        Observation = Observations.__getattribute__(key)
        if GetStart:
            #when called from external module need to assign starting point
            PntRefNum = GetStartPoint(gui.CadastralPlan, Observation, LandXML_Obj.TraverseProps)

        desc = Observation.get("desc")

        if desc == "Connection" or desc == "Road Extent" or \
                desc == "Reference":
            # Get TargetID for Observation
            TargetID = Connections.GetTargetID(Observation, PntRefNum, LandXML_Obj.TraverseProps)
        else:
            continue

        # Get Connections to TargetID
        TargetObservations = Connections.AllConnections(TargetID, LandXML_Obj)
        TargetObservations = RemoveCalculatedConnections.main(TargetObservations, gui.CadastralPlan,
                                                              DataObjects.Traverse(False, "RM"),
                                                              LandXML_Obj.TraverseProps,
                                                              TargetID)

        # remove observation to TargetID
        TargetObservations = RemoveParentObservation(TargetObservations, TargetID, PntRefNum,
                                                     LandXML_Obj)
        if TargetObservations is None:
            continue
        # run Query
        RunQueryObj = RunQuery(TargetObservations, LandXML_Obj, Query, TargetID, gui.CadastralPlan, 
                               GetStart)  # , RM_Connection)

        if RunQueryObj.CoordinateQuery():
            if GetStart:
                return PntRefNum
            else:
                return True

    return False

def GetStartPoint(CadastralPlan, Observation, TraverseProps):
    '''
    Determines the starting point of an observation
    based on the which end is already calculated in CadastralPlan
    :param CadastralPlan:
    :param Observation:
    :return:
    '''

    setupID = Observation.get("setupID").replace(TraverseProps.tag, "")
    targetID = Observation.get("targetSetupID").replace(TraverseProps.tag, "")
    
    if hasattr(CadastralPlan.Points, setupID):
        return setupID
    else:
        return targetID
    
    
def RemoveParentObservation(Observations, TargetID, PntRefNum, LandXML_Obj):
    '''
    Removes the parent connection between PntRefNum and TargetID from
        Observations
    :param Observations:
    :param TargetID:
    :param PntRefNum:
    :return:
    '''

    for key in Observations.__dict__.keys():
        Observation = Observations.__getattribute__(key)

        TargetOfTarget = Connections.GetTargetID(Observation, TargetID, LandXML_Obj.TraverseProps)

        if TargetOfTarget == PntRefNum:
            delattr(Observations, key)
            return Observations

class RunQuery:
    def __init__(self, Observations, LandXML_Obj, Query, PntRefNum, CadastralPlan, GetStart):#, RmConnection):
        self.Observations = Observations
        self.LandXML_Obj = LandXML_Obj
        self.Query = Query
        self.PntRefNum = PntRefNum
        self.CadastralPlan = CadastralPlan
        self.GetStart = GetStart
        #self.RmConnection = RmConnection

    def CoordinateQuery(self):
        '''
        Check what query is to be performed and calls the appropriate query function
        :param Observations:
        :param LandXML_Obj:
        :param Query:
        :return:
        '''

        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            
            if self.GetStart:
                self.PntRefNum = GetStartPoint(self.CadastralPlan, Observation, self.LandXML_Obj.TraverseProps)

            if self.Query == "RoadParcel" or self.Query == "KnownPointRoadParcel"\
                    or self.Query == "ConnectionRoadParcel" or self.Query == "RoadExtent":
                if self.RoadFrontageParcel(Observation):
                    return True
            elif self.Query == "Road" or self.Query == "KnownPointRoad":
                if self.RoadFrontage(Observation):
                    return True
            elif self.Query == "RmAndBdy" or self.Query == "KnownPointAndBdy":
                if self.BdyObservations(Observation):
                    return True
                
            elif self.Query == "Any":
                if self.AnyObservations(Observation):
                    return True
                


        return False

    def RoadFrontageParcel(self, Observation):
        '''
        Checks if Observation is on road frontage and is a parcel from the
            plans subdivision
        :param LandXML_Obj:
        :param PntRefNum:
        :return:
        '''

        #Get target ID for Observation
        TargetID = Connections.GetTargetID(Observation, self.PntRefNum,
                                           self.LandXML_Obj.TraverseProps)
        #Check if its a boundary of parcel from subdivision
        ObservationChecker = BDY_Connections.CheckBdyConnection(TargetID, self.LandXML_Obj)
        if not (ObservationChecker.BdyConnection(TargetID) and
                ObservationChecker.BdyConnection(self.PntRefNum)):
            return False

        
        if self.Query == "RmAndBdy" or self.Query == "KnownPointAndBdy":
            #when just looking for boundary connections ignore looking for road
            return True
        else: #check if Observation is road frontage
            desc = Observation.get("desc")
            if desc == "Road":
                return True

        return False


    def RoadFrontage(self, Observation):
        '''
        Checks if PntRefNum is on road frontage and part of a road parcel
        :param LandXML_Obj:
        :param PntRefNum:
        :return:
        '''
        #Set target ID for observation
        TargetID = Connections.GetTargetID(Observation, self.PntRefNum,
                                           self.LandXML_Obj.TraverseProps)
        #loop through parcels to find road parcels
        for parcel in self.LandXML_Obj.RoadParcels:
            if self.CheckParcelLines(parcel, TargetID) and \
                        self.CheckParcelLines(parcel, self.PntRefNum):
                    return True

        return False

    def BdyObservations(self, Observation):
        '''
        Checks if point has a Bdy to Bdy observation
        :param Observation:
        :return:
        '''
        # Get target ID for Observation
        TargetID = Connections.GetTargetID(Observation, self.PntRefNum,
                                           self.LandXML_Obj.TraverseProps)
        # Check if its a boundary of parcel from subdivision
        ObservationChecker = BDY_Connections.CheckBdyConnection(TargetID, self.LandXML_Obj)
        if (ObservationChecker.BdyConnection(TargetID) and \
                ObservationChecker.BdyConnection(self.PntRefNum)) and \
                Observation.get("desc") == "Boundary":
            return True
        
        return False
    
    def AnyObservations(self, Observation):
        '''
        Allows any observation unless a dead end
        :param Observation: 
        :return: 
        '''
        
        TargetID = Connections.GetTargetID(Observation, self.PntRefNum, self.LandXML_Obj.TraverseProps)

        TargObs = Connections.AllConnections(TargetID, self.LandXML_Obj)
        if len(TargObs.__dict__.keys()) > 1:
            return True
        return False

    def CheckParcelLines(self, parcel, TargetID):
        '''
        Checks linework in parcel to see if any vertexes match TargetID
        :param parcel:
        :param TargetID:
        :param kwargs:
        :return:
        '''

        # get lines out of parcel
        lines = parcel.find(self.LandXML_Obj.TraverseProps.Namespace + "CoordGeom")
        # loop through line to check vertexes
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "Start").get("pntRef")
                endRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "End").get("pntRef")
                # check if startRef or endRef are TargetID
                if startRef == TargetID or endRef == TargetID:
                    return True

        return False

    
    