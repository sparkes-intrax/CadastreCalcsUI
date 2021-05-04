'''
Workflow and decision tree to find connection for traverse
'''
from LandXML.RefMarks import FilterNonRMs
from LandXML.Cadastre import CadastreTraverseFilter
from LandXML import TraverseClose, Connections, RemoveDeadEnds, \
    RemoveCalculatedConnections, NoConnection, BDY_Connections, BranchOperations, \
    FinalConnectionFilter

import CadastreClasses as DataObjects
from TraverseOperations import CopyTraverseInstance

from copy import copy


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
        self.RmOnly = RmOnly #if true only looking for Rms - remove non-RM connections not prioritise
        Obs = self.FilterConnections()

    def FilterConnections(self):
        '''
        Runs a set of slection criteria to filter connections
        Different criteria run depending on traverse type (RM or BDY)
        Easement traverses will not be sent here as a different routine is performed
        Any remove filter calls NoConnectionHandler as it could end up with no observations left in self.Observations
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

        # 3) Remove dead ends if looking for closes - add dead ends to removed lines
        self.DeadEnds()  # remove filter

        self.NoConnectionHandler()
        if self.Observations is None:
            return None

        # 4) Prioritise RM-RM connections
        if not self.LandXML_Obj.TraverseProps.MixedTraverse:
            self.Observations = FilterNonRMs.RemoveNonRM_Connections(self.Observations,
                                                                     self.LandXML_Obj, self.PntRefNum,
                                                                     "Remove")
            self.NoConnectionHandler()
            if self.Observations is None:
                return None
        else:
            self.Observations = FilterNonRMs.RemoveNonRM_Connections(self.Observations,
                                                                     self.LandXML_Obj, self.PntRefNum,
                                                                     "Priority")

        #if more than one observation remaining set SecondaryBranch to True
        if len(self.Observations.__dict__.keys()) > 1:
            self.SecondaryBranch = True
        '''
        # 3) Check whether a traverse close is possible - only RMs or BDY traverse
        # TraverseClose object to check for closes
        self.CloseCheck = TraverseClose.CloseChecker(self.TraverseProps)
        self.CloseConnection = self.CloseCheck.RM_Close(self.CadastralPlan,
                                                        self.traverse, self.Observations)
        if self.CloseCheck.Close:
            # Close operations
            # print("Close found")
            self.TraverseClose = self.CloseCheck.Close
            self.Observations = Connections.KeepConnection(self.Observations, self.CloseConnection)
            return None
        '''
        #Filter observations if mixed traverse encountered
        self.MixedTraverse() #priority filter
        
        # 5) Check for boundary connections if still looking for boundary connections
        # defined by whether RMs in LandXML have not been calculated  that have a BDY connection
        # LandXML_Obj.Traverse_Props.BdyConnections
        # remove non-boundary connected RMs only if there is choice of one with a BDY connection
        self.BdyConnections()

        # if more than one observation remaining set SecondaryBranch to True
        if len(self.Observations.__dict__.keys()) > 1:
            self.PrimaryBranch = True

        

        # 6) More than 1 connection - ie a branch was in the traverse was found
        self.FinalSelection()

        # Create branch instance if required
        self.BranchFunction()

        return None

    def TraverseCloseCheck(self):
        '''
        Checks whether a close can be found from one of the observations
        :return: True if close is found and Observation is selectec
        '''

        self.CloseCheck = TraverseClose.CloseChecker(self.LandXML_Obj,
                                                self.Observations,
                                                self.traverse,
                                                self.CadastralPlan)
        self.CloseConnection = self.CloseCheck.RM_Close()
        if self.CloseCheck.Close:
            # Close operations
            # print("Close found")
            self.TraverseClose = self.CloseCheck.Close
            self.Observations = Connections.KeepConnection(self.Observations, self.CloseConnection)
            return True

        return False

    def BranchFunction(self):
        '''
        Determines whether there is a branch and which list it is to be added to
            - Primary or Secondary
        :return:
        '''
        #print("PntRefNum: " + self.PntRefNum)
        #print(len(self.Observations.__dict__.keys()))
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            break
            
        AddBranchObj = BranchOperations.AddBranch(self, self.Branches, self.traverse, 
                                                  self.PntRefNum, self.LandXML_Obj, Observation)
        self.Branches, self.traverse = AddBranchObj.AddBranchInstance()
        '''
        if self.PrimaryBranch or \
                (self.SecondaryBranch and self.LandXML_Obj.TraverseProps.MixedTraverse):
            self.traverse.PrimaryBranches = self.AddBranch(self.traverse.PrimaryBranches)
        elif self.SecondaryBranch:
            self.traverse.SecondaryBranches = self.AddBranch(self.traverse.SecondaryBranches)
        elif self.NonRmBranch and not self.RmOnly:
            self.traverse.NonRmBranches = self.AddBranch(self.traverse.NonRmBranches)
        '''

    def NoConnectionHandler(self):
        '''
        Handles when filters all connections
        Goes back to last branch
        :return:
        '''
        
        #try primary branches in traverse first
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
                self.LandXML_Obj.TraverseProps.MixedTraverse:
            self.traverse.NonRmBranches = self.FindBranch(self.traverse.NonRmBranches)

        if len(self.Observations.__dict__.keys()) == 0:

            self.Observations = None


    def FindBranch(self, BranchList):
        '''
        Finds a new branch of thee travers from the BranchList
        :param BranchList:
        :return:
        '''
        self.Observations, self.PntRefNum, self.traverse,\
            BranchList = \
            NoConnection.main(BranchList, self.Observations,
                              self.gui, self.traverse,
                              self.Branches, self.RmOnly, self.LandXML_Obj)
        return BranchList
    
    def MixedTraverse(self):
        '''
        Checks if traverse is mixed type and select observation accordingly
        :return: 
        '''
        if self.LandXML_Obj.TraverseProps.MixedTraverse:
            self.traverse.MixedTraverse = True
            self.Observations = CadastreTraverseFilter.main(self.Observations, self.PntRefNum,
                                                            self.LandXML_Obj, self.gui,
                                                    self.traverse)
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
        

    def BdyConnections(self):
        '''
        Prioritises Observations where end point has a boundary connection
        :return: 
        '''
        
        if self.LandXML_Obj.TraverseProps.BdyConnections and \
                not self.LandXML_Obj.TraverseProps.MixedTraverse:
            # create instance of Boundary checker
            ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)
            self.Observations = ConnectionChecker.FilterBdyConnection(self.Observations)
            
    def AddBranch(self, BranchList):
        '''
        Creates branch instance
        :return:
        '''

        # Record branch and create new traverse instance in branches - referenced by PntNum of Branch
        #Check if branhc instance already exists
        exists = False
        BranchLabel = None
        for key in self.Branches.__dict__.keys():
            Branch = self.Branches.__getattribute__(key)
            try:
                if key == "FirstBranch" or Branch.__class__.__name__ == "list" or \
                        Branch.__class__.__name__ == "BranchSubClass" or key == "CurrentBranch":
                    continue
                BranchPnts = Branch.refPnts

                if BranchPnts == self.traverse.refPnts:
                    exists = True
                    break
            except AttributeError:
                pass

        if not exists:
            BranchLabel = self.GetTraverseBranchNumber()
            BranchList.append(BranchLabel)
            # create a traverse copy instance and add to Branches
            travCopy = CopyTraverseInstance.TraverseCopy(self.traverse)
            # Add name of parent traverse branch
            setattr(travCopy, "ParentBranch", self.traverse.BranchName)
            # get reference number for branch
            setattr(self.Branches, BranchLabel, travCopy)
        #elif self.traverse.BranchName == self.Branches.FirstBranch and \
        #    self.Branches.FirstBranch not in BranchList:
        #    BranchList.append(self.Branches.FirstBranch)

        return BranchList

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

    def GetTraverseBranchNumber(self):
        '''
        In the case of multiple branches from a single point,
            gets an increment number and adds it to the traverse reference in Branches
        :return:
        '''

        counter = 0
        for key in self.Branches.__dict__.keys():
            if key == self.PntRefNum and counter == 0:
                counter = 1
            elif self.PntRefNum == key.split("_")[0]:
                increment = int(key.split("_")[1])
                if counter <= increment:
                    counter = increment + 1

        if counter == 0:
            return self.PntRefNum
        else:
            return (self.PntRefNum + "_" + str(counter))


    def CurrentTraverseBranchNumber(self):
        '''
        Branch name in current traverse branch list
        :return:
        '''

        counter = 0
        counter = 0
        for branchNum in self.traverse.Branches:
            if branchNum == self.PntRefNum and counter == 0:
                counter = 1
            elif self.PntRefNum == branchNum.split("_")[0]:
                increment = int(branchNum.split("_")[1])
                if counter <= increment:
                    counter = increment + 1

        if counter == 0:
            return self.PntRefNum
        else:
            return (self.PntRefNum + "_" + str(counter))




class FinalFilter:
    def __init__(self, traverse, TraverseProps):
        '''
        Filters used when other prioritisation methods have not selected
            a single connection
        Contains methods to filter by bearing or distance
        :param traverse: traverse data object
        '''
        self.traverse = traverse
        self.TraverseProps = TraverseProps

    def SimilarBearingConnection(self, Observations):
        '''
        Finds a Observations with a bearing within 45 dgrees of last connection
        if first connection returns all Observations
        :param Observations: Set of Observations to be queried
        :param traverse: traverse data object
        :return: Observations
        '''

        # Check if first connection
        if len(self.traverse.refPnts) == 1:
            return Observations

        # get bearing of last connection
        LastBearing, EndRefNum = self.FindLastConnectionBearing()
        # Find Observations within 45 degrees of LastBearing
        ConnectionList = self.ObservationsWithinBearing(LastBearing, Observations, EndRefNum)
        # if find Observations within 45 degrees, delete other bearings
        if len(ConnectionList) < len(Observations.__dict__.keys()):
            Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations

    def FindLastConnectionBearing(self):
        '''
        Finds the bearing of last connection in the traverse
        :return:
        '''

        StartRefNum = self.traverse.refPnts[-2]
        EndRefNum = self.traverse.refPnts[-1]
        # get line bearing of lasat connection
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            Line = self.traverse.Lines.__getattribute__(key)
            if Line.StartRef == StartRefNum and Line.EndRef == EndRefNum:
                return float(Line.Bearing), EndRefNum

    def ObservationsWithinBearing(self, LastBearing, Observations, PntRefNum):
        '''
        Finds the Observation in Observations object that are within 45 degrees
            of LastBearing
        :param LastBearing: Bearing of last connection in traverese
        :param Observations: Set of Observations from LandXML to query
        :param PntRefNum: Starting point reference of all Observations to be queried
        :return: ConnectionList (List of Observations that pass query)
        '''

        # Create a list to store Observations to remove - only when 1 or more Observations pass
        # bearing query
        ConnectionList = []
        # Loop through Observations and check if their bearings are within 45 degrees
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            # Get Observations bearing - normalised to same orientation as lat traverse connection
            # that is setupiD (Last connection) = TargetID (queried connection)

            if connection.get("setupID").replace(self.TraverseProps.tag, "") == PntRefNum:
                azimuth = float(Connections.GetObservationAzimuth(connection))
            else:
                azimuth = self.FlipBearing(float(Connections.GetObservationAzimuth(connection)))

            # test of bearing with 45 degrees
            if abs(LastBearing - azimuth) > 45:
                ConnectionList.append(key)

        return ConnectionList

    def FlipBearing(self, Bearing):
        '''
        Flips bearing by 180 degrees
        :param Bearing:
        :return:
        '''

        Bearing = Bearing + 180
        if Bearing >= 360:
            Bearing = Bearing - 360

        return Bearing

    def DeleteConnections(self, Connections, ConnectionsList):
        '''
        Deletes Connection that are not in Connection list
        :param Connections:
        :param ConnectionsList:
        :return:
        '''

        for key in Connections.__dict__.keys():
            connection = Connections.__getattribute__(key)
            if connection not in ConnectionsList:
                delattr(Connections, key)

        return Connections

    def FilterByDistance(self, Observations):
        '''
        Filters the Observations for the line with the shortest distance
        :param Observations:
        :return:
        '''

        ShortestDistance = 10000
        ConnectionList = []
        # Loop through Observations
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            distance = float(Connections.GetObservationDistance(connection))
            if distance < ShortestDistance:
                KeepConnection = key
                ShortestDistance = distance

        # delete all but shortest side
        for key in Observations.__dict__.keys():
            if key != KeepConnection:
                ConnectionList.append(key)
        Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations

'''
def TraverseCopy(traverse):
    
    Creates a copy of traverse in new instance
    :param traverse:
    :return:
    

    TraverseCopy = DataObjects.Traverse(traverse.FirstTraverse, traverse.type)
    for key in traverse.__dict__.keys():
        attr = copy(traverse.__getattribute__(key))
        setattr(TraverseCopy, key, attr)

    return TraverseCopy
'''
class TraverseCopyObj(object):
    pass


class CreateClassCopy(object):

    def __init__(self, traverse):
        '''
        creates a new class instance of traverse by
            recursively adding attributes
        :param traverse:
        '''
        super().__init__()

        for key in traverse.__dict__.keys():
            attr = traverse.__getattribute__(key)
            object.__setattr__(self, key, attr)

    def __copy__(self, traverse):
        return CreateClassCopy(traverse)

