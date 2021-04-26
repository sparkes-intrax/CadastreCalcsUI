'''
Methods to check for traverse close

Called for each new connection selection - only from RM and BOundary Connection
'''
from LandXML import Connections

class CloseChecker:
    '''
    class with methods to check for a close in RM and Boundary traverses
    '''
    
    def __init__(self, TraverseProps):
        
        self.Close = False #Boolean defining whether a close was possible
        self.CloseConnection = None
        self.TraverseProps = TraverseProps

    def RM_Close(self, CadastralPlan, traverse, Observations):
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
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            #Get connection start and end point reference numbers
            SetupID = self.TraverseProps.PntRefNum
            TargetSetupID = self.GetTargetID(connection, SetupID)
            #check if either end of the connection closes on first point of traverse
            if TargetSetupID == traverse.refPnts[0]:
                #up date close params
                self.CloseConnections = connection
                self.Close = True
                CloseConnections.append(key)
                
            #check if connection closes onto an already calculated point - only if not first traverse
            if (hasattr(CadastralPlan.Points, TargetSetupID)) and \
                    not self.TraverseProps.FirstTraverse:
                self.CloseConnections = connection
                self.Close = True
                CloseConnections.append(key)

        if self.Close and len(CloseConnections) > 1:
            #get shortest connection
            return self.shortestConnection(CloseConnections, Observations)
        elif self.Close:
            return Observations.__getattribute__(CloseConnections[0])

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

    def shortestConnection(self, CloseConnections, Observations):
        '''
        Checke which of multiple closes is shortest
        :param CloseConnections:
        :param Connections:
        :return:
        '''
        shortestConnection = 1e10
        shortestConnectionKey = None
        for Connection in CloseConnections:
            Obs = Observations.__getattribute__(Connection)
            distance = Connections.GetObservationDistance(Obs)
            if distance < shortestConnection:
                shortestConnection = distance
                shortestConnectionKey = Connection

        return Observations.__getattribute__(shortestConnectionKey)
