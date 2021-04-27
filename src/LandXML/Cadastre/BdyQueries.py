'''
Set of functions and methods to query a boundary point
'''
from LandXML import Connections, RemoveCalculatedConnections, BDY_Connections
import CadastreClasses as DataObjects

def main(LandXML_Obj, PntRefNum, gui, Query, RM_Connection):
    '''
    Coordinates 
    :param LandXML_Obj: 
    :param PntRefNum: 
    :param Query: 
    :return: 
    '''

    # Get connections from PntRefNum
    Observations = Connections.AllConnections(PntRefNum, LandXML_Obj)
    # Remove already calculated connections
    Observations = RemoveCalculatedConnections.main(Observations, gui.CadastralPlan,
                                                             DataObjects.Traverse(False, "RM"),
                                                             LandXML_Obj.TraverseProps,
                                                             PntRefNum)
    # Loop through available observations
    if RM_Connection:
        #tests connections to the RM connection
        for key in Observations.__dict__.keys():
            Observation = Observations.__getattribute__(key)

            #Get TargetID for Observation
            TargetID = Connections.GetTargetID(Observation, PntRefNum, LandXML_Obj.TraverseProps)

            #Get Connections to TargetID
            TargetObservations = Connections.AllConnections(TargetID, LandXML_Obj)
            TargetObservations = RemoveCalculatedConnections.main(TargetObservations, gui.CadastralPlan,
                                               DataObjects.Traverse(False, "RM"),
                                               LandXML_Obj.TraverseProps,
                                               TargetID)

            #remove observation to TargetID
            TargetObservations = RemoveParentObservation(TargetObservations, TargetID, PntRefNum,
                                                         LandXML_Obj)
            #run Query
            RunQueryObj = RunQuery(TargetObservations, LandXML_Obj, Query, TargetID, RM_Connection)

            if RunQueryObj.CoordinateQuery():
                return True
    else:
        #tests connections to PntRefNum
        RunQueryObj = RunQuery(Observations, LandXML_Obj, Query, PntRefNum, RM_Connection)
        if RunQueryObj.CoordinateQuery():
            return True
            

    return False

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
    def __init__(self, Observations, LandXML_Obj, Query, PntRefNum, RmConnection):
        self.Observations = Observations
        self.LandXML_Obj = LandXML_Obj
        self.Query = Query
        self.PntRefNum = PntRefNum
        self.RmConnection = RmConnection

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

            if self.Query == "RoadParcel" or self.Query == "KnownPointRoadParcel"\
                    or self.Query == "ConnectionRoadParcel":
                if self.RoadFrontageParcel(Observation):
                    return True
            elif self.Query == "Road" or self.Query == "KnownPointRoad":
                if self.RoadFrontage(Observation):
                    return True
            elif self.Query == "RmAndBdy" or self.Query == "KnownPointAndBdy":
                if self.BdyObservations(Observation):
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
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")

            if parcelClass == "Road":
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

    
    