'''
Grabs the next traverse branch to try
Stripped down of version applied to RM traverses as Bdy's are less complex 
'''
from TraverseOperations import CopyTraverseInstance
from LandXML import Connections, RemoveCalculatedConnections

def main(BranchList, Observations, CadastralPlan, traverse, 
         Branches, LandXML_Obj, ConnectionFinder):
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

    FindBranchObj = FindBranch(CadastralPlan, BranchList, traverse, Branches,
                               LandXML_Obj, ConnectionFinder)
    PntRefNum = None
    NewTraverse = CopyTraverseInstance.TraverseCopy(traverse)
    while (len(Observations.__dict__.keys()) == 0):
        try:
            Branch = BranchList[-1]

            Observations, PntRefNum, NewTraverse, BranchList = \
                FindBranchObj.RetrieveBranch(Branch)
        except IndexError:
            break

    return Observations, PntRefNum, NewTraverse, BranchList

class FindBranch:
    def __init__(self, CadastralPlan, BranchList,
                 traverse, Branches, LandXML_Obj, ConnectionFinder):

        self.CadastralPlan = CadastralPlan
        self.BranchList = BranchList
        self.traverse = traverse
        self.Branches = Branches
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.ConnectionFinder = ConnectionFinder
        
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
        setattr(self.NewTraverse, "BranchName", self.PntRefNum)

        #remove start of branch from any branch lists
        if len(self.NewTraverse.PrimaryBranches) > 0:
            self.NewTraverse.PrimaryBranches.remove(self.Branch)
        else:
            self.NewTraverse.SecondaryBranches.remove(self.Branch)


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