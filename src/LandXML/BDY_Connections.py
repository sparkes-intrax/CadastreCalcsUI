'''
Workflow for checking if a point is connected to a vertex of a parcel
from the proposed subdivision

defined by:
    Class=Lot
    State=Proposed
    Area < 10000m2 - this avoids public reserves being included
'''

from LandXML import Connections

class CheckBdyConnection:
    def __init__(self, PntRefNum, LandXML_Obj):
        '''
        Checks if the pntRefNUm is connected to a vertex from a parcel in the proposed subdivision
        :param PntRefNum:
        :param LandXML_Obj:
        :param Observations: Set of Reduced observations from LandXML file
                                to check for a boundary connection
        :return: boolean defining if connected to parcel or not
        '''
        self.PntRefNum = PntRefNum
        self.LandXML_Obj = LandXML_Obj        
        self.FindConnection = False
        self.FilterConnection = False
        self.LargeLots = LandXML_Obj.TraverseProps.LargeLots #when True allows connections to large lots
        self.ExistingLots = LandXML_Obj.TraverseProps.ExistingLots #when True allows connections to existing lots

    def CycleObservations(self):
        '''
        Loop method to cycle through observations        '''

        #loop through found connections and see if any end points are parcel vertexes
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            #assign the refNum that PointRefNum is connected to
            TargetID = self.GetTargetID(Observation, self.PntRefNum)

            #Check if TargetID is a parcel vertex
            if self.FindConnection and self.BdyConnection(TargetID):
                return True
            elif self.FilterConnection and not self.TestConnections(TargetID):
                # when prioritising connections without a BDY connection
                self.RemoveConnections.append(key)


        return False

    def GetTargetID(self, Observation, PntRefNum):
        '''
        Gets the target ID from Observation
        Assumes PntRefNUm is the start of the connection
        :param Observation:
        :param PntRefNum:
        :return: TargetID
        '''

        if Observation.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "") == \
                PntRefNum:
            TargetID = Observation.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        else:
            TargetID = Observation.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")

        return TargetID


    def FindBdyConnection(self, Observations):
        '''
        Method called when want to find if PntRefNum has any BDY connection
        :return: Boolean
        '''
        self.Observations = Observations
        self.FindConnection = True
        return self.CycleObservations()

    def FilterBdyConnection(self, Observations):
        '''
        Method to filter Observations for one that have BDY connections
        Does nothing if there are not Boundary Connections
        :return: filtered self.Observations
        '''

        self.Observations = Observations
        self.FilterConnection = True
        self.RemoveConnections = []
        Connected = self.CycleObservations()

        #if found boundary connection remove other connections
        if len(self.RemoveConnections) != len(self.Observations.__dict__.keys()) and \
                len(self.RemoveConnections) != 0:
            Observations = Connections.RemoveSelectedConnections(self.Observations,
                                                                 self.RemoveConnections)

        return Observations



        ####################################################################
    #methods to query whether connection has a BDY connection
    def BdyConnection(self, TargetID):
        '''
        Runs boundary vertex test for TargetID
        :param TargetID:
        :param LandXML_Obj:
        :return:
        '''

        #Loop through parcels in landXML file
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")
            try:
                parcelArea = float(parcel.get("area"))
                #filter for large public reserves
                if parcelArea > 10000 and not self.LargeLots:
                    continue
            except TypeError:
                continue
            #filter for class and state attributes which define a proposed lot in subdivision
            if (parcelClass == "Lot" and parcelState == "proposed") or\
                    (parcelClass == "Road" and self.LandXML_Obj.TraverseProps.RoadConnections) or \
                    (parcelClass == "Lot" and parcelState == "adjoining" and self.ExistingLots):
                #check if Target ID is in the parcels linework vertexes
                if self.CheckParcelLines(parcel, TargetID, self.LandXML_Obj.TraverseProps):
                    return True

        return False

    def CheckParcelLines(self, parcel, TargetID, TraverseProps):
        '''
        Checks linework in parcel to see if any vertexes match TargetID
        :param parcel:
        :param TargetID:
        :param kwargs:
        :return:
        '''

        #get lines out of parcel
        lines = parcel.find(TraverseProps.Namespace+"CoordGeom")
        #loop through line to check vertexes
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(TraverseProps.Namespace + "Start").get("pntRef")
                endRef = line.find(TraverseProps.Namespace + "End").get("pntRef")
                #check if startRef or endRef are TargetID
                if startRef == TargetID or endRef == TargetID:
                    return True

        return False

    def TestConnections(self, PntRefNum):
        '''
        Checks if connections to PntRefNUm have a boundary connections
        Used when searching for connections to the endpoint of a queried connection from
            self.PntRefNum
        :param PntRefNum:
        :return:
        '''
        # get all connections for TargetID
        TargetConnections = Connections.AllConnections(PntRefNum, self.LandXML_Obj)
        # check if any of the connections from TargetID are connected to a BDY
        for keyTarg in TargetConnections.__dict__.keys():
            TargetConnection = TargetConnections.__getattribute__(keyTarg)
            Target = self.GetTargetID(TargetConnection, PntRefNum)
            # check if Target is a boundary
            if self.BdyConnection(Target):
                return True

        return False