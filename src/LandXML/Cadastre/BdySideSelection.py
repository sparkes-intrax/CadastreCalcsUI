'''
Methods to select an observation from the LandXML file that
    will be the next side of the traverse
'''
from LandXML import RemoveCalculatedConnections, TraverseClose, Connections, \
                    FinalConnectionFilter, BranchOperations, NoConnection, BDY_Connections, \
                    RemoveDeadEnds
from LandXML.Cadastre import BdyQueries, BdyNextBranch
from LandXML.Easements import RemoveEasements
from timer import Timer


class SideSelection:
    def __init__(self, Observations, traverse, LandXML_Obj,
                 CadastralPlan, PntRefNum, Branches, gui):
        '''
        Finds a side after filtering based on priorities
        :param Observations:
        :param traverse:
        :param LandXML_Obj:
        :param CadastralPlan:
        :param PntRefNum:
        '''

        self.Observations = Observations
        self.traverse = traverse
        self.LandXML_Obj = LandXML_Obj
        self.CadastralPlan = CadastralPlan
        self.PntRefNum = PntRefNum
        self.Branches = Branches
        self.gui = gui
        self.TraverseClose = False
        self.PrimaryBranch = False
        self.tObj = Timer()

    def PrioritiseObservations(self):
        '''
        Calls a set of operations to prioritise observation type
        :return: Observation
        '''

        #1) Remove already calculated Observations
        #self.tObj.start()
        self.Observations = RemoveCalculatedConnections.main(self.Observations, 
                                                             self.CadastralPlan,
                                                             self.traverse,
                                                             self.LandXML_Obj.TraverseProps,
                                                             self.PntRefNum)
        #self.tObj.stop("Remove Already Calculated Connections")

        #self.tObj.start()
        self.Observations = RemoveDeadEnds.main(self.PntRefNum, 
                                                self.Observations, 
                                                self.LandXML_Obj, 
                                                self.gui, 
                                                self.traverse)
        #self.tObj.stop("Remove DeadEnds")
        #remove Easement boundaries
        RemoveEasObj = RemoveEasements.RemoveEasementObservations(self.Observations,
                                                                  self.PntRefNum,
                                                                  self.LandXML_Obj)
        self.Observations = RemoveEasObj.SearchObservations()
        #Check to see if any observations are road frontage or boundary
        #for when close found, starts next traverse fromm same spot
        #self.tObj.start()
        if self.RoadsAndBoundaries():
            setattr(self.traverse, "NextStartPnt", self.PntRefNum)
        #self.tObj.stop("Road and Boundary check for branches")
            
        #2) Check for close to RM (can't close on starting point??)
        #self.tObj.start()
        if self.TraverseCloseCheck("RM"):
            return ObservationObj(self.Observations, self.PntRefNum)
        #self.tObj.stop("RM Close check")
        #3) Check for close to connection
        #self.tObj.start()
        if self.TraverseCloseCheck("Connection"):
            return ObservationObj(self.Observations, self.PntRefNum)
        #self.tObj.stop("Connection Close check")
        #3a) when an old plan sometime connections are defined as Road Extent
        #self.tObj.start()
        if not self.LandXML_Obj.RefMarks:
            if self.TraverseCloseCheck("RoadExtent"):
                return ObservationObj(self.Observations, self.PntRefNum)
        #self.tObj.stop("Close for RoadExtent Connection")
        #4) Priotise a road frontage that is part of a parcel of the subdivision
        #self.tObj.start()
        self.SidePriorities("RoadParcel")
        #self.tObj.stop("Road Parcel Priority")
        #5) Check for any close
        #self.tObj.start()
        if self.TraverseCloseCheck("Any"):
            return ObservationObj(self.Observations, self.PntRefNum)
        #self.tObj.stop("Any Close check")
        #6) Check if branches and add to branch object (branches are only used when a close
            #can't be found, so cleared after close found)
        if len(self.Observations.__dict__.keys()) > 1:
            self.PrimaryBranch = True
        #self.SidePriorities("Road")
        #7) Boundary Observation (Observation desc="BOUNDARY")
        self.SidePriorities("Bdy")
        #8) Connection Observation (Observation desc="CONNECTION")
        self.SidePriorities("Connection")
        #9) Final Filter (Bearing then distance)
        if len(self.Observations.__dict__.keys()) > 1:
            self.FinalSelection()
        elif len(self.Observations.__dict__.keys()) == 0:
            if len(self.traverse.PrimaryBranches) > 0:
                self.tObj.start()
                self.GetNextBranch()
                self.tObj.stop("Next Branch")
            else:
                return None
            
        #add branch instance if found
        if self.PrimaryBranch:
            self.AddBranch()

        return ObservationObj(self.Observations, self.PntRefNum)

    def TraverseCloseCheck(self, CloseType):
        '''
        Coordinates check for a traverse close connection
        :param CloseType:
        :return:
        '''

        CloseCheck = TraverseClose.CloseChecker(self.LandXML_Obj,
                                                self.Observations,
                                                self.traverse,
                                                self.CadastralPlan)
        CloseConnection = CloseCheck.BdyTraverseClose(CloseType)
        if CloseCheck.Close:
            self.TraverseClose = True
            self.Observations = Connections.KeepConnection(self.Observations, CloseConnection)
            return True

        return False

    def SidePriorities(self, Query):
        '''
        Checks if any Observation have road frontage and part of a parcel in subdivision
        If there is, these are prioritised (other observations are removed)
        Can be more than one observation passing query
        If no road frontages, does nothing
        :return: Nothing. Updates self.Observations if required
        '''
        
        #create BdyQuery instance
        QueryObj = BdyQueries.RunQuery(self.Observations,
                                       self.LandXML_Obj,
                                       Query,
                                       self.PntRefNum)
        #List of Observations without road frontage
        RemoveObservations = []
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            if not self.TestObservation(Observation, QueryObj, Query):
                RemoveObservations.append(key)
                
        #if any road fronatage and parcel obs found, remove the rest
        if len(RemoveObservations) < len(self.Observations.__dict__.keys()):
            self.Observations = Connections.RemoveSelectedConnections(self.Observations, 
                                                                      RemoveObservations)
        
    def TestObservation(self, Observation, QueryObj, Query):
        '''
        Tests whether Observation meets Query criteria
        :param Observation:
        :param QueryObj:
        :param Query:
        :return: Bool
        '''

        if Query == "RoadParcel":
            if QueryObj.RoadFrontageParcel(Observation):
                return True
        elif Query == "Road":
            if QueryObj.RoadFrontage(Observation):
                return True
        elif Query == "Bdy":
            if QueryObj.BdyObservations(Observation):
                return True
        elif Query == "Connection":
            if Observation.get("desc") == "Connection":
                return True 
            
        return False

    def FinalSelection(self):
        '''
        If prioritising methods don't select a single
        observation, observation is selected by bearing and distance
        '''
        if len(self.Observations.__dict__.keys()) > 1:
            FinalFilterObj = FinalConnectionFilter.FinalFilter(self.traverse, self.LandXML_Obj.TraverseProps)
            self.Observations = FinalFilterObj.SimilarBearingConnection(self.Observations)
            # 7) if still more than one connection (or no connections) select shortest connection

        if len(self.Observations.__dict__.keys()) > 1:
            self.Observations = FinalFilterObj.FilterByDistance(self.Observations)

    def RoadsAndBoundaries(self):
        '''
        Checks if any connection in self.Observation is a road or boundary
        :return:
        '''
        counter = 0
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            if Observation.get("desc") == "Road" or \
                Observation.get("desc") == "Boundary":
                counter += 1

        if counter > 0 and len(self.Observations.__dict__.keys()) > 1:
            return True

        return False
    
    def AddBranch(self):
        '''
        Adds copy of current traverse at its current stage to Branches
        Adds PntRefNum to BranchOrder
        :return: 
        '''
        
        #get observation being tried
        Observation = ObservationObj(self.Observations, self.PntRefNum).Observation
        AddBranchObj = BranchOperations.AddBranch(self, self.Branches, self.traverse,
                                                  self.PntRefNum, self.LandXML_Obj, Observation)
        self.Branches, self.traverse = AddBranchObj.AddBranchInstance()
        
    def GetNextBranch(self):
        '''
        Called when a dead end is found loads up last traverse branch instance
        :return: 
        '''
        
        #while loop to keep searching until total observations are not 1
        TotalObservations = 0
        while (TotalObservations == 0):
            self.PrimaryBranch = False
            #Get next branch instance - already calc'd connections plus the branch tried
                #deleted
            self.Observations, self.PntRefNum, self.traverse,\
                BranchList = \
                BdyNextBranch.main(self.traverse.PrimaryBranches, self.Observations,
                                  self.CadastralPlan, self.traverse,
                                  self.Branches, self.LandXML_Obj)
            self.traverse.PrimaryBranches = BranchList
            
            #apply remaining filters
            self.SidePriorities("RoadParcel")
            #trigger branch
            if len(self.Observations.__dict__.keys()) > 1:
                self.PrimaryBranch = True
            self.SidePriorities("Bdy")
            # 8) Connection Observation (Observation desc="CONNECTION")
            self.SidePriorities("Connection")
            # 9) Final Filter (Bearing then distance)
            if len(self.Observations.__dict__.keys()) > 1:
                self.FinalSelection()

            # add branch instance if found
            if self.PrimaryBranch:
                self.AddBranch()
                
            TotalObservations = len(self.Observations.__dict__.keys())

        self.PrimaryBranch = False
        

class ObservationObj:
    def __init__(self, Observations, PntRefNum):
        '''
        Creates Observation insatnce with selected Observation
            and PntRefNum
        '''
        
        self.PntRefNum = PntRefNum
        
        for key in Observations.__dict__.keys():
            self.Observation = Observations.__getattribute__(key)
            break