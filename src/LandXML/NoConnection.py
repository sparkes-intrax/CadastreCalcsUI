'''
Handles traverse when no connections meets criteria
'''
from LandXML import Connections, RemoveCalculatedConnections, RemoveDeadEnds
from LandXML.RefMarks import FilterNonRMs
from TraverseOperations import CopyTraverseInstance

def main(BranchList, Observations, gui, traverse,
         Branches, RmOnly, LandXML_Obj):
    '''
    Coorindates workflow to find the next branch along a traverse to try
    :param BranchList:
    :return:
    '''
    #Get next branch to try from traverse
        #Gets its instance name and pntrefnum
        #add connection to  branch already tried to tried connections
    #Set new trav
    #get observations from branch

    FindBranchObj = FindBranch(gui, BranchList, traverse, Branches,
                               LandXML_Obj, RmOnly)
    PntRefNum = None
    NewTraverse = None
    while (len(Observations.__dict__.keys()) == 0):
        try:
            Branch = BranchList[-1]
    
            Observations, PntRefNum, NewTraverse, BranchList = \
                FindBranchObj.RetrieveBranch(Branch)
        except IndexError:
            break

    return Observations, PntRefNum, NewTraverse, BranchList


class FindBranch:
    def __init__(self, gui, BranchList,
                 traverse, Branches, LandXML_Obj, RmOnly):

        self.CadastralPlan = gui.CadastralPlan
        self.gui = gui
        self.BranchList = BranchList
        self.traverse = traverse
        self.Branches = Branches
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.RmOnly = RmOnly

    def RetrieveBranch(self, Branch):
        self.Branch = Branch
        self.PntRefNum = Branch.split("_")[0]
        self.TraverseProps.PntRefNum = self.PntRefNum
        self.GetNewBranchTraverseInstance()
        self.FindAndDeleteTriedBranch()
        Observations =  self.GetObservationFromNewBranch()
        return Observations, self.PntRefNum, self.NewTraverse, self.BranchList

    def GetNewBranchTraverseInstance(self):
        '''
        Retrieves the traverse instance labelled self.Branch
        and removes them from BranchList and Branches
        '''
        self.BranchList.pop(-1)
        Branch = self.Branches.__getattribute__(self.Branch)
        self.NewTraverse = CopyTraverseInstance.TraverseCopy(Branch)

        #remove start of brnach from any branch lists
        try:
            self.NewTraverse.PrimaryBranches.remove(self.PntRefNum)
        except ValueError:
            pass

        try:
            self.NewTraverse.SecondaryBranches.remove(self.PntRefNum)
        except ValueError:
            pass

        try:
            self.NewTraverse.NonRmBranches.remove(self.PntRefNum)
        except ValueError:
            pass


    def FindAndDeleteTriedBranch(self):
        '''
        Finds the observation connecting to the new branch
        Adds it to TriedConnections
        '''

        Line = self.FindLine(self.PntRefNum)
        LineNum = self.NewTraverse.TriedConnections.__getattribute__("LineNum")
        LineName = "Line" + str(LineNum+1)
        setattr(self.NewTraverse.TriedConnections, LineName, Line)
        setattr(self.NewTraverse.TriedConnections, "LineNum", (LineNum + 1))



    def GetObservationFromNewBranch(self):
        '''
        Retrieves Observations connected to branch
        - fitlers Observations already calc'd and performs RM filters as required
        '''

        # Get connections from PntRefNum
        Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
        # remove already calc'd connections
        Observations = RemoveCalculatedConnections.main(Observations,
                                                        self.CadastralPlan,
                                                        self.traverse,
                                                        self.TraverseProps,
                                                        self.PntRefNum)

        # Remove non RM-RM connections or prioritise
        if not self.LandXML_Obj.TraverseProps.MixedTraverse:
            Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                self.LandXML_Obj,
                                                                self.PntRefNum,
                                                                     "Remove")
        else:
            Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                self.LandXML_Obj,
                                                                self.PntRefNum,
                                                                     "Priority")

        #Remove dead ends when traverse close still a priority
        if self.LandXML_Obj.TraverseProps.TraverseClose:
            Observations = RemoveDeadEnds.main(self.PntRefNum, Observations,
                                               self.LandXML_Obj, self.gui,
                                               self.traverse)

        return Observations

    def FindLine(self, PntRefNum):
        '''
        finds a line in the traverse where PntRefNum is the end point
        :param PntRefNum:
        :return:
        '''

        # loop through traverse lines
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue

            line = self.traverse.Lines.__getattribute__(key)
            # get lines end point ref
            StartRef = line.__getattribute__("StartRef")
            if StartRef == PntRefNum:
                return line

        return None

'''
def FindBranch(BranchList, TraverseProps, LandXML_Obj,
               traverse, gui, CadastralPlan, RmOnly, Observations):
    
    Finds a new branch of the traverse from the BranchList
    :param BranchList:
    :return:
    

    PntRefNum = None
    while (len(Observations.__dict__.keys()) == 0):
        Branch = BranchList[-1]

        # deal with no connection
        Observations, PntRefNum = GetBranch(TraverseProps, LandXML_Obj,
                                                         traverse, gui, CadastralPlan,
                                                              RmOnly, Branch)
        setattr(LandXML_Obj.TraverseProps, "PntRefNum", PntRefNum)

        # When no branches are found
        try:
            #if no Branches left in list and no observations found
            #set everything to None so program knows that no path can found from
            #the starting point
            if len(BranchList) == 0:
                BranchList = None
                Observations = None
                break
        except TypeError:
            break

    #Clean up
    if Observations is not None:
        BranchList.pop(-1)

    return Observations, PntRefNum

def GetBranch(TraverseProps, LandXML_Obj, traverse, gui, CadastralPlan, RmOnly, Branch):
    
    Coordinates the workflow and methods to retrieve Branch and Observations from the Branch
    :param TraverseProps: Properties of the current traverse.
    :param LandXML_Obj:
    :return: Observations - new list of observations to query
    

    #Check if there are other branches of traverse to try
    BranchRefNum = Branch.split("_")[0]
    NoConnectObj = NoConnection(TraverseProps, LandXML_Obj, traverse,
                                gui, CadastralPlan, RmOnly, Branch)
    Observations = NoConnectObj.BackUpToBranch(BranchRefNum)


        
    return Observations, BranchRefNum

class NoConnection:
    def __init__(self, TraverseProps, LandXML_Obj, traverse,
                 gui, CadastralPlan, RmOnly, Branch):
        self.traverse = traverse
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = TraverseProps
        self.CadastralPlan = CadastralPlan
        self.gui = gui
        self.RmOnly = RmOnly
        self.Branch = Branch


    def BackUpToBranch(self, PntRefNum):
        
        removes lines and points from traverse and gui
        add removed connections to traverse.TriedConnections
        :param PntRefNum: Point to back up traverse to
        :return: traverse and Observations from branch point
        
        
        #gets line from traverse where PntRefNum is the startRef
            #adds it to tried connections
        LineNum = self.traverse.TriedConnections.LineNum + 1
        Line, key = self.FindLine(PntRefNum)
        setattr(self.traverse.TriedConnections, str(LineNum), Line)
        setattr(self.traverse.TriedConnections, "LineNum", LineNum+1)

        LineNum = self.gui.CadastralPlan.TriedConnections.__getattribute__("LineNum")
        LineName = "Line" + str(LineNum)
        setattr(self.gui.CadastralPlan.TriedConnections, LineName, Line)
        setattr(self.gui.CadastralPlan.TriedConnections, "LineNum", (LineNum + 1))

        
        #loop through traverse.refPnts from end to start
        i = -1
        while(i > -len(self.traverse.refPnts)):
            #check if back to branch
            if self.traverse.refPnts[i] == PntRefNum:
                break
            
            Point = self.traverse.Points.__getattribute__(self.traverse.refPnts[i])
            # delete point from GUI and its associated items            
            #GraphicsItems = Point.__getattribute__("GraphicsItems")
            #self.RemoveGraphicsItems(GraphicsItems)
            #delete point from traverse
            delattr(self.traverse.Points, self.traverse.refPnts[i])
            #find line where Point is the end point
            Line, key = self.FindLine(self.traverse.refPnts[i])
            #get line distance to remove from traverse distance
            Distance = float(Line.Distance)
            TravDistance = float(self.traverse.Distance)
            self.traverse.Distance = TravDistance - Distance
            # delete line from GUI and its associated items
            GraphicsItems = Line.__getattribute__("GraphicsItems")
            self.RemoveGraphicsItems(GraphicsItems)
            #delete line from traverse
            delattr(self.traverse.Lines, key)
            setattr(self.traverse.TriedConnections, key, Line)
            
            
            i -= 1
        
        # Delete Points from traverse.refPnts
        if i < -1:
            self.traverse.refPnts = self.traverse.refPnts[:(i + 1)]

        #Get connections from PntRefNum
        Observations = self.GetObservations(PntRefNum)
        

        return Observations


    def GetObservations(self, PntRefNum):
        
        Get connections to PntRefNUm and filters them
        :param PntRefNum:
        :return:
        
        # Get connections from PntRefNum
        Observations = Connections.AllConnections(PntRefNum, self.LandXML_Obj)
        # remove already calc'd connections
        Observations = RemoveCalculatedConnections.main(Observations,
                                                        self.CadastralPlan,
                                                        self.traverse,
                                                        self.TraverseProps,
                                                        PntRefNum)

        # Remove non RM-RM connections or prioritise
        if self.RmOnly:
            Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                     self.LandXML_Obj, PntRefNum,
                                                                     "Remove")
        else:
            Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                                     self.LandXML_Obj, PntRefNum,
                                                                     "Priority")

        return Observations
            
    def RemoveGraphicsItems(self, GraphicsItems):
        
        removes all items in Graphics items from GUI
        :param GraphicsItems: Collection of GUI Grpahics items
        :return: 
        
        keys = []
        for key in GraphicsItems.__dict__.keys():
            keys.append(key)

        for key in keys:
            item = GraphicsItems.__getattribute__(key)
            self.gui.view.scene.removeItem(item)
            
    def FindLine(self, PntRefNum):
        
        finds a line in the traverse where PntRefNum is the end point
        :param PntRefNum: 
        :return: 
        
        
        #loop through traverse lines
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
                
            line = self.traverse.Lines.__getattribute__(key)
            #get lines end point ref
            EndRef = line.__getattribute__("EndRef")
            #StartRef = line.__getattribute__("StartRef")
            #if StartRef == PntRefNum:
            #    return line, key
            if EndRef == PntRefNum:
                return line, key
            
        return None
    '''

