'''
Coordinates branch creation and traverse path selection
'''
from LandXML import Connections, TraverseSideCalcs, SharedOperations
from LandXML.Cadastre import BdySideSelection
import CadastreClasses as DataObjects
from timer import Timer
from DrawingObjects import DrawTraverse



class TraverseCalcs:

    def __init__(self, gui, LandXML_Obj, PntRefNum):
        '''
        Methods to calculate a traverse path from PntRefNum to a close
            onto an already calculated point in CadastralPlan
        :param traverse:
        :param gui:
        :param LandXML_Obj:
        :param PntRefNum:
        '''

        #self.traverse = traverse
        self.TriedConnections = DataObjects.Lines()
        self.CadastralPlan = gui.CadastralPlan
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.PntRefNum = PntRefNum
        self.Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
        self.tObj = Timer()
        setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)
        
    def FindPath(self, traverse):
        '''
        Coordinates path solution for traverse
        Finds a close otherwise returns None
        :return: 
        '''
        
        #create a branches object to store traverse branches
        #For boundary traverses - new branches only tried when a
            #close can't be found
        self.Branches = BranchesObj(self.PntRefNum, traverse)
        setattr(self.Branches, "CurrentBranch", traverse)
        setattr(self.Branches.CurrentBranch, "ParentName", self.PntRefNum)
        setattr(self.Branches.CurrentBranch, "BranchName", self.PntRefNum)
        #TRack whether TRaversePath found
        TraverseFinished = False

        #tObj = Timer()
        #tObj.start()
        #finds sides until closed
        while (not TraverseFinished):

            setattr(self.Branches.CurrentBranch, "NextStartPnt", None)
            #select observation from self.Observations - apply priorities
            #self.tObj.start()
            ObservationObj = BdySideSelection.SideSelection(self.Observations, 
                                                            self.Branches.CurrentBranch, 
                                                         self.LandXML_Obj, 
                                                         self.gui.CadastralPlan, 
                                                         self.PntRefNum,
                                                            self.Branches, self.gui,
                                                            self.TriedConnections)
            Observation = ObservationObj.PrioritiseObservations()
            #self.tObj.stop("Bdy Side Selection")
            #check if an observation was selected
            if Observation is None:
                if len(self.TriedConnections.__dict__.keys()) > 1:
                    self.AddTriedConnections()
                elif not self.LandXML_Obj.TraverseProps.TraverseClose:
                    return self.Branches.CurrentBranch
                break

            self.Branches.CurrentBranch = ObservationObj.traverse
            self.PntRefNum = self.LandXML_Obj.TraverseProps.PntRefNum
            #Add side to traverse
            point = TraverseSideCalcs.TraverseSide(self.PntRefNum,
                                                   self.Branches.CurrentBranch,
                                                   Observation,
                                                   self.gui,
                                                   self.LandXML_Obj)

            #set PntRefNum for next traverse side and get observations from PntRefNum
            self.PntRefNum = point.TargPntRefNum
            setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)

            #Handle a close when its found
            if ObservationObj.TraverseClose:
                #tObj.stop("CloseFound", len(self.Branches.CurrentBranch.refPnts))
                self.Branches.CurrentBranch.EndRefPnt = self.PntRefNum
                if not self.CloseHandler():
                    return self.Branches.CurrentBranch
                #else:
                    #tObj.start()

            self.Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
    
    def CloseHandler(self):
        '''
        Determines what to do when a traverse is found
        :return: 
        '''
        
        if self.Branches.CurrentBranch.NextStartPnt is not None:
            # start next traverse from same spot and run normal close operations
            # add traverse to Cadadastral Plan and gui
            DrawTraverse.main(self.gui, self.Branches.CurrentBranch, self.LandXML_Obj)
            self.gui = SharedOperations.ApplyCloseAdjustment(self.Branches.CurrentBranch,
                                                             self.LandXML_Obj,
                                                             self.gui)
            #create new traverse  and set PntRefNum
            StartPointObj = StartPoint(self.gui, self.Branches.CurrentBranch.NextStartPnt)
            self.PntRefNum = StartPointObj.PntRefNum
            traverse = SharedOperations.initialiseTraverse(StartPointObj, "BOUNDARY", False)
            self.Branches = BranchesObj(self.PntRefNum, traverse)
            setattr(self.Branches.CurrentBranch, "NextStartPnt", None)
            setattr(self.LandXML_Obj.TraverseProps, "PntRefNum", self.PntRefNum)
            return True
        else:
            return False

    def AddTriedConnections(self):
        '''
        when a close can't be found the tried connections
        are add to Cadastral Plan
        :return:
        '''

        for key in self.TriedConnections.__dict__.keys():
            Obs = self.TriedConnections.__getattribute__(key)
            if Obs.__class__.__name__ != "Line":
                if Obs.__class__.__name__ != "Arc":
                    continue
            '''
            #set pntrefNum - always from start of traverse
            PntRefNum = self.Branches.CurrentBranch.ParentBranch
            # Calculate the side of the tried connection and its line oject
            SideObj = TraverseSideCalcs.TraverseSide(PntRefNum,
                                                   self.Branches.CurrentBranch,
                                                   Obs,
                                                   self.gui,
                                                   self.LandXML_Obj)
            '''
            #check Observation hasn't already been added to tried Observations
            if not hasattr(self.CadastralPlan.TriedConnections, key):
                setattr(self.CadastralPlan.TriedConnections, key, Obs)
                print("added tried connection")



class StartPoint:
    def __init__(self, gui, PntRefNum):
        point = gui.CadastralPlan.Points.__getattribute__(PntRefNum)
        self.PntRefNum = PntRefNum
        self.Code = point.Code
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Layer = point.Layer

class BranchesObj:
    def __init__(self, PntRefNum, traverse):
        self.CurrentBranch = traverse
        setattr(self.CurrentBranch, "BranchName", PntRefNum)
        setattr(self.CurrentBranch, "ParentBranch", PntRefNum)