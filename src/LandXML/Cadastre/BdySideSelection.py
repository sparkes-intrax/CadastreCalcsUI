'''
Methods to select an observation from the LandXML file that
    will be the next side of the traverse
'''
from LandXML import RemoveCalculatedConnections, TraverseClose, Connections, \
                    FinalConnectionFilter, BranchOperations, NoConnection, BDY_Connections, \
                    RemoveDeadEnds, TraverseSideCalcs
from LandXML.Cadastre import BdyQueries, BdyNextBranch
from LandXML.Easements import RemoveEasements
from LandXML.RefMarks import RefMarkQueries
from timer import Timer


class SideSelection:
    def __init__(self, Observations, traverse, LandXML_Obj,
                 CadastralPlan, PntRefNum, Branches, gui, TriedConnections):
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
        self.TriedConnections = TriedConnections
        #self.SecondaryBranch = False
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


        # Remove Single Connection RefMarks
        self.RemoveSingleConnectionRms()
        #self.tObj.stop("Remove Already Calculated Connections")
        # Check to see if any observations are road frontage or boundary
        # for when close found, starts next traverse fromm same spot
        # self.tObj.start()
        if self.RoadsAndBoundaries():
            setattr(self.traverse, "NextStartPnt", self.PntRefNum)
        # self.tObj.stop("Road and Boundary check for branches")
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
        #self.tObj.start()

        #self.tObj.stop("Remove DeadEnds")
        #remove Easement boundaries
        RemoveEasObj = RemoveEasements.RemoveEasementObservations(self.Observations,
                                                                  self.PntRefNum,
                                                                  self.LandXML_Obj)
        self.Observations = RemoveEasObj.SearchObservations()        

        #3a) when an old plan sometime connections are defined as Road Extent
        #self.tObj.start()
        if not self.LandXML_Obj.RefMarks:
            if self.TraverseCloseCheck("RoadExtent"):
                return ObservationObj(self.Observations, self.PntRefNum)
        #self.tObj.stop("Close for RoadExtent Connection")

        #Add a secondary branch tracker
        if len(self.Observations.__dict__.keys()) > 1:
            self.PrimaryBranch = True
        #4) Priotise a road frontage that is part of a parcel of the subdivision
        #self.tObj.start()
        self.SidePriorities("RoadParcel")
        #self.tObj.stop("Road Parcel Priority")
        # 5) Boundary Observation (Observation desc="BOUNDARY")
        self.SidePriorities("Bdy")
        #select boundary observation of close bearing - if it exists
        if len(self.Observations.__dict__.keys()) > 1:
            self.BdyConnectionSelection()

        #6) Check for any close
        #self.tObj.start()
        if self.TraverseCloseCheck("Any"):
            return ObservationObj(self.Observations, self.PntRefNum)

        #Remove dead end connections - picks up connections missed by RM check
        if self.LandXML_Obj.TraverseProps.TraverseClose:
            self.Observations = RemoveDeadEnds.main(self.PntRefNum,
                                                self.Observations,
                                                self.LandXML_Obj,
                                                self.gui,
                                                self.traverse)

        #self.tObj.stop("Any Close check")
        #6) Check if branches and add to branch object (branches are only used when a close
            #can't be found, so cleared after close found)
        #if len(self.Observations.__dict__.keys()) > 1:
        #    self.PrimaryBranch = True
        #self.SidePriorities("Road")

        #8) Connection Observation (Observation desc="CONNECTION")
        self.SidePriorities("Connection")
        #9) Final Filter (Bearing then distance)
        if len(self.Observations.__dict__.keys()) > 1:
            self.FinalSelection()
        elif len(self.Observations.__dict__.keys()) == 0:
            #if len(self.traverse.Observations) > 0:
            #    self.AddToTriedConnections()
            if not self.LandXML_Obj.TraverseProps.TraverseClose:
                return None
            elif len(self.traverse.PrimaryBranches) > 0 or \
                    len(self.traverse.SecondaryBranches) > 0:
                #When all observations have been removed try another branch
                #Add starting branch to tried connections
                if len(self.traverse.Observations) > 0:
                    self.AddToTriedConnections()
                #self.tObj.start()
                self.NoConnectionHandler()
                #No branch can be found
                if len(self.Observations.__dict__.keys()) == 0:
                    return None
                #check for closes
                if self.CheckAllCloses():
                    return ObservationObj(self.Observations, self.PntRefNum)
                #self.tObj.stop("Next Branch")
            else:
                if len(self.traverse.Observations) > 0:
                    self.AddToTriedConnections()
                return None
            
        #add branch instance if found
        if self.PrimaryBranch:# or self.SecondaryBranch:
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
                                       self.PntRefNum, self.CadastralPlan, False)
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

    def BdyConnectionSelection(self):
        '''
        Check if more than one boundary observation remains
         - remove any other connections
         - if more than one boundary observation - select one with nearest bearing
        :return:
        '''

        #Count number of boundary connections
        BdyCounter = 0
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            if Observation.get("desc") == "Boundary":
                BdyCounter += 1

        #remove connection observations if required (when more than 1 bdy observation
        if BdyCounter > 1 and BdyCounter < len(self.Observations.__dict__.keys()):
            RemoveObs = []
            for key in self.Observations.__dict__.keys():
                Observation = self.Observations.__getattribute__(key)
                if Observation.get("desc") == "Connection":
                    RemoveObs.append(key)

            #remove observations from self.Obs
            self.Observations = Connections.RemoveSelectedConnections(self.Observations, RemoveObs)

        #Select Observation with close bearing
        if BdyCounter > 1:
            FinalFilterObj = FinalConnectionFilter.FinalFilter(self.traverse, self.LandXML_Obj.TraverseProps)
            self.Observations = FinalFilterObj.SimilarBearingConnection(self.Observations)

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

    def NoConnectionHandler(self):
        '''
        Handles when filters all connections
        Goes back to last branch
        :return:
        '''

        # try primary branches in traverse first
        if len(self.Observations.__dict__.keys()) == 0 and \
                len(self.traverse.PrimaryBranches) > 0:
            self.traverse.PrimaryBranches = self.GetNextBranch(self.traverse.PrimaryBranches)
        # try SECONDARY branches in traverse
        if len(self.Observations.__dict__.keys()) == 0 and \
                len(self.traverse.SecondaryBranches) > 0:
            self.traverse.SecondaryBranches = self.GetNextBranch(self.traverse.SecondaryBranches)
        
    def GetNextBranch(self, BranchList):
        '''
        Called when a dead end is found loads up last traverse branch instance
        :return: 
        '''
        
        #while loop to keep searching until total observations are not 1
        TotalObservations = 0
        while (TotalObservations == 0):
            #Get next branch instance - already calc'd connections plus the branch tried
                #deleted
            self.Observations, self.PntRefNum, self.traverse,\
                BranchList = \
                BdyNextBranch.main(BranchList, self.Observations,
                                  self.CadastralPlan, self.traverse,
                                  self.Branches, self.LandXML_Obj, self)


            if len(BranchList) == 0 and self.PntRefNum is None:
                return BranchList

            self.PrimaryBranch = False
            self.RemoveSingleConnectionRms()
            #self.SecondaryBranch = False
            #self.traverse.PrimaryBranches = BranchList
            if len(self.Observations.__dict__.keys()) > 1:
                self.PrimaryBranch = True
            #apply remaining filters
            self.SidePriorities("RoadParcel")
            #trigger branch
            #if len(self.Observations.__dict__.keys()) > 1:
            #    self.PrimaryBranch = True
            self.SidePriorities("Bdy")
            # 8) Connection Observation (Observation desc="CONNECTION")
            self.SidePriorities("Connection")


            # 9) Final Filter (Bearing then distance)
            if len(self.Observations.__dict__.keys()) > 1:
                self.FinalSelection()

            TotalObservations = len(self.Observations.__dict__.keys())

        # add branch instance if found
        if self.PrimaryBranch:# or self.SecondaryBranch:
            self.AddBranch()
            if len(self.traverse.refPnts) == 0:
                self.traverse.refPnts.append(self.CadastralPlan)
                

        self.PrimaryBranch = False
        self.SecondaryBranch = False

        return BranchList

    def RemoveSingleConnectionRms(self):
        '''
        Checks if any of the Observations are to dead end RMs
        :return:
        '''
        self.LandXML_Obj.TraverseProps.RoadConnections = True

        RemoveObs = []  # List of observations to be removed
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)

            TargetID = Connections.GetTargetID(Observation, self.PntRefNum, self.LandXML_Obj.TraverseProps)
            TargObs = Connections.AllConnections(TargetID, self.LandXML_Obj)
            #check if Target ID is a boundary
            ObservationChecker = BDY_Connections.CheckBdyConnection(TargetID, self.LandXML_Obj)
            ObservationChecker.ExistingLots = True

            #self.LandXML_Obj.TraverseProps.RoadConnections = False

            if RefMarkQueries.CheckIfConnectionMark(self.LandXML_Obj, TargetID) and \
                not ObservationChecker.BdyConnection(TargetID) and \
                    len(TargObs.__dict__.keys()) <= 1:
                RemoveObs.append(key)

            #if len(TargObs.__dict__.keys()) <= 1:
            #    RemoveObs.append(key)


        #Remove found connections
        if len(RemoveObs) > 0:
            self.Observations = Connections.RemoveSelectedConnections(self.Observations, RemoveObs)

    def CheckAllCloses(self):
        '''
        After finding a new branch this function is called to figure out if a close can
        be found for the branch
        :return:
        '''

        if self.TraverseCloseCheck("RM"):
            return True

        if self.TraverseCloseCheck("Connection"):
            return True

        if self.TraverseCloseCheck("Any"):
            return True

        return False


    def AddToTriedConnections(self):
        '''
        Checks if tried connections contains starting connection of traverse
        If it doesn't it is added
        :return:
        '''
        
        #check tried connections
        StartingObservation = self.traverse.Observations[0]
        if not hasattr(self.TriedConnections, StartingObservation.get("name")):
            StartRefNum = self.traverse.refPnts[0]
            SideObj = TraverseSideCalcs.TraverseSide(StartRefNum,
                                                     self.traverse, StartingObservation,
                                                     self.gui, self.LandXML_Obj)
            setattr(self.TriedConnections, StartingObservation.get("name"), SideObj.line)


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