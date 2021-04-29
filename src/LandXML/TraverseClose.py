'''
Methods to check for traverse close

Called for each new connection selection - only from RM and BOundary Connection
'''
from LandXML import Connections
from LandXML.RefMarks import RefMarkQueries

class CloseChecker:
    '''
    class with methods to check for a close in RM and Boundary traverses
    '''
    
    def __init__(self, LandXML_Obj, Observations, traverse, CadastralPlan):
        
        self.Close = False #Boolean defining whether a close was possible
        self.CloseConnection = None
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.LandXML_Obj = LandXML_Obj
        self.Observations = Observations
        self.traverse = traverse
        self.CadastralPlan = CadastralPlan


    def RM_Close(self):
        '''
        Checks if a close can be found meeting the TraverseProps criteria
        :param TraverseProps: Properties for travserse
        :param CadastralPlan: CadastralPlan data object
        :param traverse: current traverse data object
        :param Connections: list of connections to query
        :return: None. Updates self.Close and self.Connections
        '''

        #loop through connections
        CloseConnections =[]
        for key in self.Observations.__dict__.keys():
            connection = self.Observations.__getattribute__(key)
            #Get connection start and end point reference numbers
            SetupID = self.TraverseProps.PntRefNum
            TargetSetupID = Connections.GetTargetID(connection, SetupID, self.TraverseProps)
            #check if either end of the connection closes on first point of traverse
            if TargetSetupID == self.traverse.refPnts[0]:
                #up date close params
                self.CloseConnections = connection
                self.Close = True
                CloseConnections.append(key)
                
            #check if connection closes onto an already calculated point - only if not first traverse
            if (hasattr(self.CadastralPlan.Points, TargetSetupID)) and \
                    not self.TraverseProps.FirstTraverse:
                self.CloseConnections = connection
                self.Close = True
                CloseConnections.append(key)

        if len(CloseConnections) > 0:
            return self.GetCloseObservation(CloseConnections)


    def BdyTraverseClose(self, CloseType):
        '''
        Checks if a close of CloseType can be found
        :param CloseType: Type of point a traverse can close on.
                        Accepted Values: RM, Connection, Any
        :return: Selected close observation if found
        '''

        # loop through connections
        PntRefNum = self.TraverseProps.PntRefNum
        CloseConnections = []
        for key in self.Observations.__dict__.keys():
            observation = self.Observations.__getattribute__(key)

            #get end of observation ref number
            TargetID = Connections.GetTargetID(observation, PntRefNum, self.TraverseProps)

            #Check if TargetID closes
            if self.BdyCloseCheck(observation, TargetID, CloseType):
                self.Close = True
                CloseConnections.append(key)

        if len(CloseConnections) > 0:
            return self.GetCloseObservation(CloseConnections)
        else:
            return None

    def BdyCloseCheck(self, observation, TargetID, CloseType):
        '''
        Checks if Target ID is close of CloseType
        :param observation:
        :param TargetID:
        :param CloseType:
        :return:
        '''

        if CloseType == "RM":
            if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, TargetID) and \
                hasattr(self.CadastralPlan.Points, TargetID):
                return True
        elif CloseType == "Connection":
            if observation.get("desc") == "Connection" and \
                    hasattr(self.CadastralPlan.Points, TargetID):
                return True
        elif CloseType == "RoadExtent":
            if observation.get("desc") == "Road Extent" and \
                    hasattr(self.CadastralPlan.Points, TargetID):
                return True
        else:
            if hasattr(self.CadastralPlan.Points, TargetID) or \
                self.traverse.refPnts[0] == TargetID:
                return True

        return False



    def GetTargetID(self, Observation, PntRefNum):
        '''
        Gets the target ID from Observation
        Assumes PntRefNUm is the start of the connection
        :param Observation:
        :param PntRefNum:
        :return: TargetID
        '''

        if Observation.get("setupID").replace(self.TraverseProps.tag, "") == \
                PntRefNum:
            TargetID = Observation.get("targetSetupID").replace(self.TraverseProps.tag, "")
        else:
            TargetID = Observation.get("setupID").replace(self.TraverseProps.tag, "")

        return TargetID

    def GetCloseObservation(self, CloseConnections):
        if self.Close and len(CloseConnections) > 1:
            #get shortest connection
            return self.shortestConnection(CloseConnections)
        elif self.Close:
            return self.Observations.__getattribute__(CloseConnections[0])

    def shortestConnection(self, CloseConnections):
        '''
        Checke which of multiple closes is shortest
        :param CloseConnections:
        :param Connections:
        :return:
        '''
        shortestConnection = 1e10
        shortestConnectionKey = None
        for Connection in CloseConnections:
            Obs = self.Observations.__getattribute__(Connection)
            distance = Connections.GetObservationDistance(Obs)
            if distance < shortestConnection:
                shortestConnection = distance
                shortestConnectionKey = Connection

        return self.Observations.__getattribute__(shortestConnectionKey)
