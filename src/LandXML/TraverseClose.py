'''
Methods to check for traverse close

Called for each new connection selection - only from RM and BOundary Connection
'''

class CloseChecker:
    '''
    class with methods to check for a close in RM and Boundary traverses
    '''
    
    def __init__(self):
        
        self.Close = False #Boolean defining whether a close was possible
        self.CloseConnection = None

    def RM_Close(self, TraverseProps, CadastralPlan, traverse, Connections):
        '''
        Checks if a close can be found meeting the TraverseProps criteria
        :param TraverseProps: Properties for travserse
        :param CadastralPlan: CadastralPlan data object
        :param traverse: current traverse data object
        :param Connections: list of connections to query
        :return: None. Updates self.Close and self.Connections
        '''

        #loop through connections
        for key in Connections.__dict__.keys():
            connection = Connections.__getattribute__(key)
            #Get connection start and end point reference numbers
            SetupID = connection.get("setupID").replace(TraverseProps.tag, "")
            TargetSetupID = connection.get("targetSetupID").replace(TraverseProps.tag, "")
            #check if either end of the connection closes on first point of traverse
            if (SetupID == traverse.refPnts[0] or TargetSetupID == traverse.refPnts[0]) and \
                    len(traverse.refPnts) > 1:
                #up date close params
                self.CloseConnections = connection
                self.Close = True
                break
                
            #check if connection closes onto an already calculated point - only if not first traverse
            if (hasattr(CadastralPlan.Points, SetupID) or \
                    hasattr(CadastralPlan.Points, TargetSetupID)) and \
                TraverseProps.FirstTraverse:
                self.CloseConnections = connection
                self.Close = True
                break