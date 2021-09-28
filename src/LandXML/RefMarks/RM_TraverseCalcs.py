'''
Methods and workflow to calculate an RM traverse
- Calculates all possible traverse paths from a starting point
- Takes the shortest closed traverse
'''

from LandXML import Connections, TraverseClose, TraverseNoConnection, FindConnection, \
    TraverseSideCalcs, RemoveCalculatedConnections, RemoveDeadEnds, NoConnection, \
    BranchOperations, SharedOperations
from LandXML.RefMarks import FindRmConnection, FilterNonRMs, RefMark_Traverse, RefMarkQueries
from TraverseOperations import CopyTraverseInstance

import CadastreClasses as DataObjects


class Traverse:
    def __init__(self, traverse, gui, LandXML_Obj, PntRefNum):
        '''
        Contains methods to calculate a traverse
        Queries all branches found on a traverse path and selects the shortest traverse
        :param traverse: traverse object to store all traverse attributes
        :param gui: ui data object
        :param LandXML_Obj: LandXML data object
        :param PntRefNum: The starting point for the traverse. Updates with new traverse sides
        '''

        self.PntRefNum = PntRefNum
        self.Branches = BranchesObj()
        setattr(self.Branches, "CurrentBranch", traverse)
        setattr(self.Branches.CurrentBranch, "BranchName", self.PntRefNum)
        setattr(self.Branches, "FirstBranch", self.PntRefNum)
        self.NoBranches = False
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.ShortestTraverse = 1e10
        self.SelectedTraversePath = None
        self.RmOnly = True
        self.RM_CloseFound = False
        # Add PntRefNum as a TraverseProps attribute
        setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)
        
        # defines whether a finish to a traverse has been found
        # not neccesarily a close
        self.TraverseFinished = False

        #set first traverse to current traverse
        #self.CurrentTraverse = self.Branches.__getattribute__(self.PntRefNum)
        #set branch name for referencing parent branches
        #setattr(self.CurrentTraverse, "BranchName", self.PntRefNum)
        #add reference to the first branch calculated
        #if self.PntRefNum == "9":
        #   print("here")
        # find all connections for self.PntRefNum and remove any non-RM connections
        Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
        # loop to add sides to a traverse
        while (not self.TraverseFinished):

            # select connection
            connection = FindRmConnection.FindNextConnection(Observations,
                                                             self.Branches.CurrentBranch,
                                                           self.LandXML_Obj.TraverseProps,
                                                           self.gui.CadastralPlan,
                                                           self.LandXML_Obj,
                                                           self.gui, self.Branches, self.RmOnly)

            self.Branches.CurrentBranch = connection.traverse
            #if no observations found
            if connection.Observations  is None:
                Observations = self.NoObservationHandler(connection, self.Branches.CurrentBranch)
                if Observations is None:
                    self.GetShortestTraversePath()
                    break
                else:
                    continue

            if self.LandXML_Obj.TraverseProps.MixedTraverse:
                self.MixTraverse = True
            # calculate new point and create line object
            self.PntRefNum = self.LandXML_Obj.TraverseProps.__getattribute__("PntRefNum")
            if len(self.Branches.CurrentBranch.refPnts) == 1:
                for key in connection.Observations.__dict__.keys():
                    Obs = connection.Observations.__getattribute__(key)
                    break
                setattr(self.Branches.CurrentBranch, "StartObs", Obs.get("name"))
            point = TraverseSideCalcs.TraverseSide(self.PntRefNum,
                                                     self.Branches.CurrentBranch, connection,
                                                     self.gui, self.LandXML_Obj)
            #calculate cumulative traverse length
            self.Branches.CurrentBranch.Distance += float(point.distance)
                        
            #Handle close or move onto next traverse side
            if self.Branches.CurrentBranch.Distance > self.ShortestTraverse:
                #remove branch from self.Branches
                self.UpdateBranches()
                self.DeleteLongerTraverseBranches()
                Observations = self.CloseHandler()
                #self.Branches.Secondary = []  # reset secondary branchs as won't be used after finding a close
                #self.Branches.NonRmBranch = []
            elif connection.TraverseClose:
                #if RM only traverse TraverseCloseFound to True
                if not self.Branches.CurrentBranch.MixedTraverse:
                    self.RM_CloseFound = True
                
                #update shortest traverse
                #self.ShortestTraverse = self.Branches.CurrentBranch.Distance
                #self.Branches.CurrentBranch.Closed = True

                #Commit Traverse as new branch
                if self.NewRms(): #only commit if traverse path adds new RMs
                    self.Branches.CurrentBranch.EndRefPnt = point.TargPntRefNum
                    self.ShortestTraverse = self.Branches.CurrentBranch.Distance
                    self.Branches.CurrentBranch.Closed = True
                    self.CommitTraverseInstance()

                self.UpdateBranches()
                #cut off traverse search when great then 75 branches
                if len(self.Branches.Primary) > 75:
                    self.GetShortestTraversePath()
                    break
                #self.Branches.Secondary = [] #reset secondary branchs as won't be used after finding a close
                #self.Branches.NonRmBranch = []
                
                #ON update of shortest traverse delete any longer traverses in branches
                self.DeleteLongerTraverseBranches()
                Observations = self.CloseHandler()

            else:
                Observations = self.NextTraverseSide(point)

                if len(Observations.__dict__.keys()) == 0 and \
                        not self.LandXML_Obj.TraverseProps.TraverseClose:
                    break


            if self.NoBranches:
                self.GetShortestTraversePath()                
                break

    def NextTraverseSide(self, point):
        '''
        Gets connections for next side
        :param point:
        :return:
        '''
        self.PntRefNum = point.TargPntRefNum
        setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)
        Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
        Observations = RemoveCalculatedConnections.main(Observations,
                                                               self.gui.CadastralPlan,
                                                               self.Branches.CurrentBranch,
                                                               self.LandXML_Obj.TraverseProps,
                                                               self.PntRefNum)
        return Observations

    def LongTraverse(self):
        '''
        Called when a traverse branch is longer than the shortest traverse
        Deletes current branch and gets the next branch to query
        '''

        #Delete current branch

        delattr(self.Branches, self.CurrentTraverse.BranchName)
        # Get next branch
        Observations = self.CloseHandler()

        return Observations

    def CommitTraverseInstance(self):
        '''
        Creates a new traverse instance for closed traverse and adds to Branches object
        '''

        #Get new name for branch - increment if more than one branch from PntRefNum
        BranchName = self.Branches.CurrentBranch.BranchName.split("_")[0]
        TravName = BranchOperations.GetTraverseBranchNumber(self.Branches,
                                                            BranchName)
        #Copy traverseInstance
        BranchCopy = CopyTraverseInstance.TraverseCopy(self.Branches.CurrentBranch)

        setattr(self.Branches, TravName, BranchCopy)


    def DeleteLongerTraverseBranches(self):
        '''
        After finding a traverse to replace the shortest traverse
            deletes any branches already longer than shortest.
            As long as they aren't parent branch to any remaining (KeepBranches)
        '''

        #Loop through branch objects listed for query
        RemoveBranches = [] # for removing from list to test
        KeepBranches = []
        for key in self.Branches.__dict__.keys():

            if key == "FirstBranch" or self.Branches.FirstBranch == key:
                continue
            #get branch object
            branch = self.Branches.__getattribute__(key)

            try:
                #test branch length compared current shortest traverse
                if branch.Distance > self.ShortestTraverse:
                    #Add branch to list to remove
                    RemoveBranches.append(key)
                else:
                    KeepBranches.append(key)
            except AttributeError:
                pass

        #remove collected branch objects from self.Branches
        for RemoveKey in RemoveBranches:
            Keep = False
            #check if branch to be deleted is a parent to the branches to be kept
            for KeepKey in KeepBranches:
                KeepBranch = self.Branches.__getattribute__(KeepKey)
                Parent = KeepBranch.BranchName
                if Parent == RemoveKey:
                    Keep = True

            #detele if not required
            if not Keep:
                #delattr(self.Branches, RemoveKey)
                try:
                    self.Branches.Primary.remove(RemoveKey)
                except ValueError:
                    pass



    def CloseHandler(self):
        '''
        Handles a close event for a traverse
        Traverse loop finds a close and calls this event handler.
        - looks for branches, if they exist:
                gets next traverse branch instance to follow
                sets PntRefNum for following the new branch
                Sets current traverse to closed
            if no branches
                sets current traverse to closed
                Selects shortest traverse from branches
        :return:
        '''

        #Check if traverse branches exist and haven't been calculated
        RemoveBranches = [] # for removing from list to test
        DeleteBranches = [] # for branches that can't be followed
        if len(self.Branches.Primary) > 0:
            #loop through branches until find one with connections to follow
            for TravRefNum in self.Branches.Primary:
                BranchCopyObj = BranchOperations.BranchCopy(TravRefNum,
                                                self.Branches)
                self.Branches.CurrentBranch, self.PntRefNum = BranchCopyObj.GetCopy()

                #remove branch from primary list
                RemoveBranchObj = BranchOperations.RemoveTriedBranches(self.Branches, TravRefNum)
                self.Branches = RemoveBranchObj.RemoveBranchInstance()

                #remove traverse branch from list
                RemoveBranches.append(TravRefNum)
                Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
                # Remove Already calculated observations
                Observations = RemoveCalculatedConnections.main(Observations, self.gui.CadastralPlan,
                                                                self.Branches.CurrentBranch,
                                                                self.LandXML_Obj.TraverseProps,
                                                                self.PntRefNum)
                #remove any already calculated branch from new PntRefNum and non-RM connections
                Observations = self.CheckBranches(Observations,
                                                  self.Branches.CurrentBranch.TriedObservation)

                if self.LandXML_Obj.TraverseProps.MixedTraverse:
                    Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                         self.LandXML_Obj,
                                                                         self.PntRefNum, "Priority")
                else:
                    Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                        self.LandXML_Obj,
                                                                        self.PntRefNum, "Remove")
                #remove dead ends
                if self.LandXML_Obj.TraverseProps.TraverseClose:
                    Observations = RemoveDeadEnds.main(self.PntRefNum,
                                                            Observations,
                                                            self.LandXML_Obj, self.gui,
                                                            self.Branches.CurrentBranch)
                if len(Observations.__dict__.keys()) > 0:
                    break
                elif len(self.Branches.Primary) == 0:
                    self.Branches.CurrentBranch = self.GetShortestTraversePath()
                elif self.Branches.CurrentBranch.Distance > self.ShortestTraverse or \
                        len(Observations.__dict__.keys()) == 0:
                    DeleteBranches.append(TravRefNum)

        else:
            Observations = None
            self.Branches.CurrentBranch = self.GetShortestTraversePath()
            self.NoBranches = True

        #remove traverse branches from list
        for branch in RemoveBranches:
            self.Branches.Primary.remove(branch)
        for branch in DeleteBranches:
            delattr(self.Branches, branch)

        if len(self.Branches.Primary) == 0:
            self.NoBranches = True

        setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)

        return Observations

    def CheckBranches(self, Observations, TriedObservation):
        '''
        Checks all closed traverse instances in Branches if connection has already been calculated
        :param connection:
        :return:
        '''

        #Set up Remove Obs object'
        RemoveObj = RemoveCalculatedConnections.RemoveConnections(Observations,
                                                                  self.gui.CadastralPlan,
                                                                  self.Branches.CurrentBranch,
                                                                  self.LandXML_Obj.TraverseProps,
                                                                  self.PntRefNum)
        RemoveObs = []
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            if connection.get("name") == TriedObservation.get("name"):
                RemoveObs.append(key)
                continue
            try:
                for TravKey in self.Branches.__dict__.keys():
                    traverse = self.Branches.__getattribute__(TravKey)
                    if TravKey == "FirstBranch" or traverse.__class__.__name__ == "list" or \
                            traverse.__class__.__name__ == "BranchSubClass":
                        continue

                    if traverse.Closed or TravKey == self.Branches.CurrentBranch.ParentBranch:
                        if RemoveObj.CheckLinesObject(connection, traverse.Lines, key):
                            if key not in RemoveObs:
                                RemoveObs.append(key)

            except AttributeError:
                pass

        if len(RemoveObs) > 0:
            Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)

        return Observations

    def GetShortestTraversePath(self):
        '''
        Checks all possible traverses and selects the one with shortest path
        :return: sets selected traverse to self.CurrentTraverse
        '''

        ShortestPath = 1e10
        #Check number of RMs in Traverse - if any with 2 or greater
            #traverse must have at least 2
        MoreThan2RMs = self.NumberRMsInBranches()
        for key in self.Branches.__dict__.keys():
            CurrentTraverse = self.Branches.__getattribute__(key)
            if key == "FirstBranch" or CurrentTraverse.__class__.__name__ == "list" or \
                    CurrentTraverse.__class__.__name__ == "BranchSubClass" or \
                    key == "CurrentBranch":
                continue

            if not CurrentTraverse.Closed:
                continue

            if MoreThan2RMs and not self.RMsInBranch(CurrentTraverse):
                continue

            try:
                Length = CurrentTraverse.Distance
                if Length < ShortestPath and CurrentTraverse.Closed:
                    self.Branches.CurrentBranch = CurrentTraverse
            except AttributeError:
                pass

    def TraverseLength(self, CurrentTraverse):
        '''
        Calculates the length of the CurrentTraverse Path
        :param CurrentTraverse: Traberse to query its length
        :return: Length
        '''

        Length = 0
        for key in CurrentTraverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue

            Line = CurrentTraverse.Lines.__getattribute__(key)
            Length += float(line.Distance)

        return Length

    def NumberRMsInBranches(self):
        '''
        Checks how many RMs ina traverse branch
        :return:
        '''
        for key in self.Branches.__dict__.keys():
            CurrentTraverse = self.Branches.__getattribute__(key)
            if key == "FirstBranch" or CurrentTraverse.__class__.__name__ == "list" or \
                    CurrentTraverse.__class__.__name__ == "BranchSubClass" or \
                    key == "CurrentBranch":
                continue

            if self.RMsInBranch(CurrentTraverse):
                return True

        return False

    def RMsInBranch(self, CurrentTraverse):
        counter = 0
        for PointNum in CurrentTraverse.refPnts:
            if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, PointNum):
                counter += 1

        if counter >= 2:
            return True

        return False


    def NoObservationHandler(self, connection, traverse):
        '''
        called when no Observation could be found meeting a given criteria
        :param connection: connection tried
        :return:
        '''
        if not self.LandXML_Obj.TraverseProps.TraverseClose:
            Observations = None
        elif not self.LandXML_Obj.TraverseProps.MixedTraverse and not self.RM_CloseFound:
            self.LandXML_Obj.TraverseProps.MixedTraverse = True
            #starting traverse search again so remove tried connections
            self.RemoveTriedConnections()
            self.PntRefNum = self.Branches.FirstBranch
            setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)
            #get observations from PntRefNum
            Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
            #create new branches object
            self.Branches = BranchesObj()
            setattr(self.Branches, "FirstBranch", self.PntRefNum)

            #create new traverse instance
            point = traverse.Points.__getattribute__(self.PntRefNum)
            StartPoint = CreateStartPoint(point)
            FirstTraverse = traverse.FirstTraverse
            traverse = SharedOperations.initialiseTraverse(StartPoint, "REFERENCE MARKS", FirstTraverse)
            setattr(self.Branches, "CurrentBranch", traverse)
            self.Branches.CurrentBranch = traverse
            setattr(self.Branches.CurrentBranch, "BranchName", self.PntRefNum)



            '''
            self.Branches.Primary = self.Branches.Other
            #retry traverse from last possible branch in other branch list
                #now allowing boundary connections
            if len(self.Branches.Other) > 0:
                Observations, self.PntRefNum = \
                    NoConnection.FindBranch(self.Branches.Primary,
                                            self.LandXML_Obj.TraverseProps,
                                            self.LandXML_Obj,
                                            self.CurrentTraverse,
                                            self.gui,
                                            self.gui.CadastralPlan,
                                            self.RmOnly,
                                            connection.Observations)

                #Cleanup
                setattr(self.Branches, self.PntRefNum, self.CurrentTraverse)

            '''
            #else:
            #    Observations = None
        else:
            if hasattr(self.gui.CadastralPlan.Points, self.PntRefNum):
                self.TriedStarts(connection)
            Observations = None


        return Observations


    def RemoveTriedConnections(self):
        '''
        Removes lines from CadastralPlan.TriedConnections
        '''

        RemoveLines = []
        for key in self.gui.CadastralPlan.TriedConnections.__dict__.keys():
            if key == "LineNum":
                continue
            RemoveLines.append(key)

        self.gui.CadastralPlan.TriedConnections = Connections.RemoveSelectedConnections(\
                                                self.gui.CadastralPlan.TriedConnections,
                                                RemoveLines)
        self.gui.CadastralPlan.TriedConnections.LineNum = 0

    def TriedStarts(self, connection):
        '''
        Adds the first connection from a traverse to CadastralPlan.TriedConnections
        THis tell the program not try the connection again until all closes have ben found
        :return:
        '''

        if len(self.Branches.CurrentBranch.Lines.__dict__.keys())> 1:
            Line = self.Branches.CurrentBranch.Lines.__getattribute__(self.Branches.CurrentBranch.StartObs)
            LineNum = self.gui.CadastralPlan.TriedConnections.__getattribute__("LineNum")
            LineName = self.Branches.CurrentBranch.StartObs
            setattr(self.gui.CadastralPlan.TriedConnections, LineName, Line)
            setattr(self.gui.CadastralPlan.TriedConnections, "LineNum", (LineNum+1))


        else:
            #get dead end connection from starting point of traverse
            #accounts for a single connection between RMs
            Observations = Connections.CheckStartingPoint(self.PntRefNum, self.LandXML_Obj, 
                                           self.gui.CadastralPlan, self.Branches.CurrentBranch, self.gui)
            if len(Observations.__dict__.keys()) > 0:
                setattr(connection, "Observations", Observations)
                #for key in Observations.__dict__.keys():
                Observation = Observations.__getattribute__(dir(Observations)[0])
                ObsName = Observation.get("name")
                #break
                TargetID = Connections.GetTargetID(Observation, self.PntRefNum, self.LandXML_Obj.TraverseProps)

                SideObj = TraverseSideCalcs.TraverseSide(self.PntRefNum,
                                                       self.Branches.CurrentBranch, connection,
                                                       self.gui, self.LandXML_Obj)
                #Side = SideObj.CalcPointCoordsWorkflow()
                setattr(self.Branches.CurrentBranch, "StartObs", ObsName)
                Line = self.Branches.CurrentBranch.Lines.__getattribute__(self.Branches.CurrentBranch.StartObs)
                LineNum = self.gui.CadastralPlan.TriedConnections.__getattribute__("LineNum")
                LineName = self.Branches.CurrentBranch.StartObs
                setattr(self.gui.CadastralPlan.TriedConnections, ObsName, Line)
                setattr(self.gui.CadastralPlan.TriedConnections, "LineNum", (LineNum + 1))

    def UpdateBranches(self):
        '''
        Adds primary branches from the current traverse to Branches
        Called when a close traverse found
        :return:
        '''

        for branch in self.Branches.CurrentBranch.PrimaryBranches:
            self.Branches.Primary.append(branch)

    def NewRms(self):
        '''
        Checks if new Rms from Current Traverse branch will be added to CadastralPlan
        :return:
        '''
        for PntNum in self.Branches.CurrentBranch.refPnts:
            if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, PntNum) and \
                    not hasattr(self.gui.CadastralPlan.Points, PntNum):
                return True
        return False

class CreateStartPoint:
    def __init__(self, point):
        self.PntRefNum = point.PntNum
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Code = point.Code
        self.Layer = point.Layer

class BranchesObj:
    def __init__(self):
        self.Primary = []
        self.TriedBranches = BranchSubClass()
        #self.Secondary = []
        #self.NonRmBranch = []+
        
class BranchSubClass(object):
    pass