'''
Removes connections from Observation list that have already been calculated:
- In Traverse
- In CadastralPlan
'''
from LandXML import Connections
from timer import Timer


def main(Observations, CadastralPlan, traverse, TraverseProps, PntRefNum):
    '''
    Calls methods to remove already calculated lines Observations from
        Observations
    :param Observations: List of Observations to query
    :param CadastralPlan: Committed calculations to query
    :param traverse: current traverse
    :param TraverseProps: Properties of current traverse
    :return: Observations
    '''

    RemoveObj = RemoveConnections(Observations, CadastralPlan, traverse,
                                  TraverseProps, PntRefNum)
    Observations = RemoveObj.RemoveCalculatedObservations()

    return Observations

class RemoveConnections:
    def __init__(self, Observations, CadastralPlan,
                 traverse, TraverseProps, PntRefNum):
        self.Observations = Observations
        self.CadastralPlan = CadastralPlan
        self.traverse =traverse
        self.TraverseProps = TraverseProps
        self.PntRefNum = PntRefNum
    def RemoveCalculatedObservations(self):
        '''
        Checks if any of the Observations have already been calculated
            Removes ones that have
        Checks in current traverse and CadastralPlan
        Also remove connecxtions where the end point of the connection is
            a mid point of the current traverse
        :param Observations: Set of Observations to query
        :param traverse: current traverse data object
        :param CadastralPlan: CadastralPlan data object
        :return: updated Observations
        '''

        # loop through Observations
        RemoveObs = []
        for key in self.Observations.__dict__.keys():
            connection = self.Observations.__getattribute__(key)
            # check if cadastralPlan contains connection
            if self.CheckLinesObject(connection, self.CadastralPlan.Lines, key):
                RemoveObs.append(key)
            # check if traverse already contains connection or end point is traverse midpoint
            #elif self.traverse is not None:
            elif self.CheckLinesObject(connection, self.traverse.Lines, key):
                    RemoveObs.append(key)

            #Check cadastral plan point objects
            # stops taking a single connection traverse close
            elif self.CheckPointsObject(connection, self.CadastralPlan.Points):
                RemoveObs.append(key)

            elif self.TraverseProps.TraverseClose:
                #if self.traverse is not None:
                if self.CheckLinesObject(connection, self.traverse.TriedConnections, key):
                    RemoveObs.append(key)
                elif self.CheckLinesObject(connection, self.CadastralPlan.TriedConnections, key):
                    RemoveObs.append(key)
            # check
        # remove any observation collected in RemoveObs(Already calc'd)
        if len(RemoveObs) > 0:
            self.Observations = Connections.RemoveSelectedConnections(self.Observations, RemoveObs)

        return self.Observations


    def CheckLinesObject(self, connection, Lines, LineKey):
        '''
        Checks Lines data object if it contains connection
        :param connection:
        :param Lines:
        :return:
        '''

        # define setup and traget ID points
        if self.PntRefNum == connection.get("setupID").replace(self.TraverseProps.tag, ""):
            SetupID = connection.get("setupID").replace(self.TraverseProps.tag, "")
            TargetSetupID = connection.get("targetSetupID").replace(self.TraverseProps.tag, "")
        else:
            SetupID = connection.get("targetSetupID").replace(self.TraverseProps.tag, "")
            TargetSetupID = connection.get("setupID").replace(self.TraverseProps.tag, "")
        

        if hasattr(Lines, LineKey):
            return True
        elif TargetSetupID in self.traverse.refPnts and \
             TargetSetupID != self.traverse.refPnts[0]:
            return True

        '''
        # Check if connection has already been calculated or
        tObj = Timer()
        tObj.start()
        for key in Lines.__dict__.keys():
            if key == "LineNum":
                continue

            line = Lines.__getattribute__(key)
            StartRef = line.__getattribute__("StartRef")
            EndRef = line.__getattribute__("EndRef")
            # remove *_# tag from point numbers
            if len(StartRef.split("_")) > 1:
                StartRef = StartRef.split("_")[0]
            if len(EndRef.split("_")) > 1:
                EndRef = EndRef.split("_")[0]
        # checks connection = line (ie already calculated)
            if (SetupID == StartRef and TargetSetupID == EndRef) or \
                    (SetupID == EndRef and TargetSetupID == StartRef):
                tObj.stop("Loop line checker")
                return True
            #
            #elif self.traverse is not None:
            elif TargetSetupID in self.traverse.refPnts and \
                TargetSetupID != self.traverse.refPnts[0]:
                tObj.stop("Loop line checker")
                return True

        tObj.stop("Loop line checker")
        '''

        return False

    def CheckPointsObject(self, connection, Points):
        '''
        Checks if any connection end points are already in Points
        :param connection:
        :param Points:
        :return:
        '''
        TargetID = Connections.GetTargetID(connection, self.PntRefNum, self.TraverseProps)
        #if self.traverse is not None:
        if hasattr(Points, TargetID) and len(self.traverse.refPnts) == 1:
            return True

        return False
    
def CheckTargetPoint(Observations, CadastralPlan, PntRefNum, LandXML_Obj):
    '''
    Checks observations if they are to a already calculated point
    Removes these observations from Observations list
    :param Observations: 
    :param CadastralPlan: 
    :return: 
    '''
    RemoveObs = []
    for key in Observations.__dict__.keys():
        Observation = Observations.__getattribute__(key)
        
        TargetID = Connections.GetTargetID(Observation, PntRefNum, LandXML_Obj.TraverseProps)
        if hasattr(CadastralPlan.Points, TargetID):
            RemoveObs.append(key)
            
    if len(RemoveObs) > 0:
        Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)
        
    return Observations



