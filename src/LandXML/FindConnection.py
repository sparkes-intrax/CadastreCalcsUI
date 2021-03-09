'''
Workflow and decision tree to find connection for traverse
'''
from LandXML.RefMarks import RM_ConnectionFilter
from LandXML import TraverseClose

class FindNextConnection:
    def __init__(self, Observations, traverse, PntRefNum,
                 TraverseProps, CadastralPlan, LandXML_Obj):
        '''
        Finds next connection for traverse
        :param Connections:
        '''

        self.Observations = Observations
        self.traverse = traverse
        self.PntRefNum = PntRefNum
        self.TraverseProps = TraverseProps
        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj
        self.TraverseClose = False
        self.Connection = self.FilterConnections()

    def FilterConnections(self):
        '''
        Runs a set of slection criteria to filter connections
        Different criteria run depending on traverse type (RM or BDY)
        Easement traverses will not be sent here as a different routine is performed
        '''
        # 1) Remove connections already calculated and those where end point is a traverse midpoint
        # - lines in CadastralPlanObj and traverse
        self.Observations = self.RemoveCalculatedConnections(self.Observations, self.CadastralPlan)
        if len(self.Observations.__dict__.keys()) == 0:
            # deal with no connection
            TraverseNoConnection(self.traverse, self.TraverseProps, self.PntRefNum, self.LandXML_Obj)
            return None

        # 2) Check whether a traverse close is possible - only RMs or BDY traverse
        # TraverseClose object to check for closes
        self.CloseCheck = TraverseClose.CloseChecker()
        self.Close = self.CloseCheck.RM_Close(self.TraverseProps, self.CadastralPlan,
                                         self.traverse, self.Observations)
        if self.CloseCheck.Close:
            # Close operations
            print("Close found")
            self.TraverseClose = self.CloseCheck.Close
            return self.Close.Connection
        
        #3) Perform filters specific to traverse type
        if self.TraverseProps.TraverseType == "REFERENCE MARKS":
            self.Observations = RM_ConnectionFilter.FilterObservations(self.Observations,
                                                                     self.traverse, 
                                                                     self.CadastralPlan,
                                                                     self.LandXML_Obj,
                                                                     self.PntRefNum)
        elif self.TraverseProps.TraverseType == "BOUNDARY":
            # 2) Check whether a traverse close is possible
            Close = CloseCheck.RM_Close(self.LandXML_Obj.TraverseProps, self.gui.CadastralPlan,
                                        self.traverse, Observations)



    #######################################################################################
    # workflow to remove already calculated lines
    def RemoveCalculatedObservations(self, Observations, CadastralPlan):
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
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            # check if cadastralPlan contains connection
            if self.CheckLinesObject(connection, CadastralPlan.Lines, CadastralPlan.Points):
                delattr(Observations, key)
            # check if traverse already contains connection or end point is traverse midpoint
            elif self.CheckLinesObject(connection, self.traverse.Lines, self.traverse.Points):
                delattr(Observations, key)
            #check

        return Observations


    def CheckLinesObject(self, connection, Lines, Points):
        '''
        Checks Lines data object if it contains connection
        :param connection:
        :param Lines:
        :return:
        '''
        SetupID = connection.get("setupID").replace(self.TraverseProps.tag, "")
        TargetSetupID = connection.get("targetSetupID").replace(self.TraverseProps.tag, "")
        for key in Lines.__dict__.keys():
            if key == "LineNum":
                continue

            line = Lines.__getattribute__(key)
            StartRef = line.__getattribute__("StartRef")
            EndRef = line.__getattribute__("StartRef")

            if (SetupID == StartRef and TargetSetupID == EndRef) or \
                    (SetupID == EndRef and TargetSetupID == StartRef):
                return True
            elif hasattr(Points, EndRefNum):
                return True

        return False

