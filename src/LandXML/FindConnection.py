'''
Workflow and decision tree to find connection for traverse
'''
from LandXML.RefMarks import RM_ConnectionFilter
from LandXML import TraverseClose, Connections, RemoveDeadEnds, \
    RemoveCalculatedConnections, NoConnection, BranchOperations

class FindNextConnection:
    def __init__(self, Observations, traverse,
                 TraverseProps, CadastralPlan, LandXML_Obj, gui, Branches, RmOnly):
        '''
        Finds next connection for traverse
        :param Connections:
        '''

        self.Observations = Observations
        self.traverse = traverse
        self.PntRefNum = TraverseProps.PntRefNum
        self.TraverseProps = TraverseProps
        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj
        self.gui = gui
        self.Branches = Branches
        self.TraverseClose = False
        self.PrimaryBranch = False
        self.SecondaryBranch = False
        self.NonRmBranch = False
        self.RmOnly = RmOnly  # if true only looking for Rms - remove non-RM connections not prioritise
        Obs = self.FilterConnections()

    def FilterConnections(self):
        '''
        Runs a set of slection criteria to filter connections
        Different criteria run depending on traverse type (RM or BDY)
        Easement traverses will not be sent here as a different routine is performed
        '''
        # 1) Remove connections already calculated and those where end point is a traverse midpoint
        # - lines in CadastralPlanObj and traverse
        self.Observations = RemoveCalculatedConnections.main(self.Observations, 
                                                             self.CadastralPlan,
                                                             self.traverse, 
                                                             self.LandXML_Obj.TraverseProps,
                                                             self.PntRefNum)
        
        if len(self.Observations.__dict__.keys()) > 1:
            self.NonRmBranch = True

        self.NoConnectionHandler()
        if self.Observations is None:
                return None

        # 2) Check whether a traverse close is possible - only RMs or BDY traverse
        # TraverseClose object to check for closes
        if self.TraverseCloseCheck():
            return None
        
        #3) Dead ends
        self.DeadEnds()
        
        #4) RM filteres if RM traverse
        if self.TraverseProps.type == "REFERENCE MARKS":
            self.RM_Connections()
        
        #check that all Observations have not been filterd
        if self.Observations is None:
            return None
        
        #set secondary branch
        if len(self.Observations.__dict__.keys()) > 1:
            self.SecondaryBranch = True
        
        #5) Apply Cadastre Filter - Boundary traverse or mixed traverse
        self.CadastreFilter()
        
        #set primary branch 
        if len(self.Observations.__dict__.keys()) > 1:
            self.PrimaryBranch = True
            
        #6) Handle branches - create instance if required
        self.BranchFunction()
        
        #7) If still haven't made a selection - filter by bearing and distance
        self.FinalSelection()

        return None


    def TraverseCloseCheck(self):
        '''
        Checks whether a close can be found from one of the observations
        :return: True if close is found and Observation is selectec
        '''

        self.CloseCheck = TraverseClose.CloseChecker(self.TraverseProps)
        self.CloseConnection = self.CloseCheck.RM_Close(self.CadastralPlan,
                                                        self.traverse, self.Observations)
        if self.CloseCheck.Close:
            # Close operations
            # print("Close found")
            self.TraverseClose = self.CloseCheck.Close
            self.Observations = Connections.KeepConnection(self.Observations, self.CloseConnection)
            return True
        
        return False

    def DeadEnds(self):
        '''
        Checks if any observations are dead ends
        :return: 
        '''

        if self.TraverseProps.TraverseClose:
            self.Observations = RemoveDeadEnds.main(self.PntRefNum,
                                                    self.Observations,
                                                    self.LandXML_Obj, self.gui,
                                                    self.traverse)

    def NoConnectionHandler(self):
        '''
        Handles when filters all connections
        Goes back to last branch
        :return:
        '''

        # try primary branches in traverse first
        if len(self.Observations.__dict__.keys()) == 0 and \
                len(self.traverse.PrimaryBranches) > 0:
            self.traverse.PrimaryBranches = self.FindBranch(self.traverse.PrimaryBranches)
        # try SECONDARY branches in traverse
        if len(self.Observations.__dict__.keys()) == 0 and \
                len(self.traverse.SecondaryBranches) > 0:
            self.traverse.SecondaryBranches = self.FindBranch(self.traverse.SecondaryBranches)

        # when non RMs are allowed to be included in the traverse
        # try NonRmBranches
        if len(self.Observations.__dict__.keys()) == 0 and \
                len(self.traverse.NonRmBranches) > 0 and \
                not self.RmOnly:
            self.traverse.NonRmBranches = self.FindBranch(self.traverse.NonRmBranches)

        if len(self.Observations.__dict__.keys()) == 0:
            self.Observations = None

    def FindBranch(self, BranchList):
        '''
        Finds a new branch of thee travers from the BranchList
        :param BranchList:
        :return:
        '''
        self.Observations, self.PntRefNum, self.traverse, \
        BranchList = \
            NoConnection.main(BranchList, self.Observations,
                              self.gui.CadastralPlan, self.traverse,
                              self.Branches, self.RmOnly, self.LandXML_Obj)
        return BranchList

    def RM_Connections(self):
        '''
        Selects or prioritises RM connections in Observations
        Filters for bdy connections if they ara priority
        :return:
        '''
        
        #RM Connections
        if self.RmOnly:
            self.Observations = FilterNonRMs.RemoveNonRM_Connections(self.Observations,
                                                                     self.LandXML_Obj, self.PntRefNum,
                                                                     "Remove")
            self.NoConnectionHandler()
        else:
            self.Observations = FilterNonRMs.RemoveNonRM_Connections(self.Observations,
                                                                     self.LandXML_Obj, self.PntRefNum,
                                                                     "Priority")
            
        #BDY Connections
        if self.Observation is not None:
            if self.LandXML_Obj.TraverseProps.BdyConnections and \
                    not self.LandXML_Obj.TraverseProps.MixedTraverse:
                # create instance of Boundary checker
                ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)
                self.Observations = ConnectionChecker.FilterBdyConnection(self.Observations)
        
 

    def CadastreFilter(self):
        '''
        Checks if traverse is mixed type and select observation accordingly
        :return: 
        '''
        if self.TraverseProps.MixedTraverse or self.TraverseProps.type == "BOUNDARY":
            self.traverse.MixedTraverse = True
            self.Observations = CadastreTraverseFilter.main(self.Observations, self.PntRefNum,
                                                            self.LandXML_Obj, self.gui,
                                                    self.traverse)
            
    def BranchFunction(self):
        '''
        Determines whether there is a branch and which list it is to be added to
            - Primary or Secondary
        :return:
        '''
        AddBranchObj = BranchOperations.AddBranch(self, self.Branches, self.traverse, 
                                                  self.PntRefNum, self.LandXML_Obj, self.RmOnly)
        self.Branches, self.traverse = AddBranchObj.AddBranchInstance()
        

    def FinalSelection(self):
        '''
        What to do when a Branch is encountered
        '''
        if len(self.Observations.__dict__.keys()) > 1:
            FinalFilterObj = FinalConnectionFilter.FinalFilter(self.traverse, self.LandXML_Obj.TraverseProps)
            self.Observations = FinalFilterObj.SimilarBearingConnection(self.Observations)
            # 7) if still more than one connection (or no connections) select shortest connection

        if len(self.Observations.__dict__.keys()) > 1:
            self.Observations = FinalFilterObj.FilterByDistance(self.Observations)