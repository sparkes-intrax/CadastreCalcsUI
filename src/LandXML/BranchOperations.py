'''
Set of procedures to deal with branches
'''
from TraverseOperations import CopyTraverseInstance

class BranchCopy:
    def __init__(self, BranchName, Branches):      
        '''
        Makes a copy of branch instance
        Removes branches if same as BranchName PntRefNum
        :param BranchName: Name of branch in Branches
        :param Branches:
        '''
        self.Branches = Branches
        self.BranchName = BranchName
    
    def GetCopy(self):

        #get branch instance from Branches
        Branch = self.Branches.__getattribute__(self.BranchName)
        #make a copy of branch
        Branch = CopyTraverseInstance.TraverseCopy(Branch)
        
        #set PntRefNum
        PntRefNum = self.BranchName.split("_")[0]
        
        #remove branches corresponding to BranchName or PntRefNum
        Branch = self.CleanUpBranches(Branch, PntRefNum)
        
        return Branch, PntRefNum
        
    def CleanUpBranches(self, traverse, PntRefNum):
        '''
        removes branches from primary, secondary and NonRM lists if they are
            equal to PntRefNum or BranchName
        :param traverse: 
        :param PntRefNum: 
        :param BranchName: 
        :return: traverse
        '''
        
        #primary branches
        traverse.PrimaryBranches = self.removeBranches(traverse.PrimaryBranches,
                                                  PntRefNum)
        # secondary branches
        traverse.SecondaryBranches = self.removeBranches(traverse.SecondaryBranches,
                                                  PntRefNum)
        # primary branches
        traverse.NonRmBranches = self.removeBranches(traverse.NonRmBranches,
                                                  PntRefNum)
        
        return traverse
        
    def removeBranches(self, BranchList, PntRefNum):
        
        if PntRefNum in BranchList:
            BranchList.remove(PntRefNum)
        elif self.BranchName in BranchList:
            BranchList.remove(self.BranchName)
            
        return BranchList
    
def GetTraverseBranchNumber(Branches, PntRefNum):
    '''
    In the case of multiple branches from a single point,
        gets an increment number and adds it to the traverse reference in Branches
    :return:
    '''

    counter = 0
    for key in Branches.__dict__.keys():
        if key == PntRefNum and counter == 0:
            counter = 1
        elif PntRefNum == key.split("_")[0]:
            increment = int(key.split("_")[1])
            if counter <= increment:
                counter = increment + 1

    if counter == 0:
        return PntRefNum
    else:
        return (PntRefNum + "_" + str(counter))

class RemoveTriedBranches:
    def __init__(self, Branches, BranchName):
        self.Branches = Branches
        self.BranchName = BranchName

    def RemoveBranchInstance(self):
        '''
        Loops through all Branches in self.Branches and removes BranchName from
            primaryBranches
        :return:
        '''

        for key in self.Branches.__dict__.keys():
            Branch = self.Branches.__getattribute__(key)
            if key == "FirstBranch" or Branch.__class__.__name__ == "list" or \
                Branch.__class__.__name__ == "BranchSubClass" or key == "CurrentBranch":
                continue #not a Branch instance - descriptive attributes of Branch class
            
            if self.BranchName in Branch.PrimaryBranches:
                Branch.PrimaryBranches.remove(self.BranchName)

        return self.Branches
    
class AddBranch:
    def __init__(self, ConnectionFinder, Branches, traverse, PntRefNum, 
                 LandXML_Obj, Observation):
        '''
        Checks if branch should be created and added to Branches
        Updates Branch Lists
        :param ConnectionFinder: 
        :param Branches: 
        '''
        
        self.ConnectionFinder = ConnectionFinder
        self.Branches = Branches
        self.traverse = traverse
        self.PntRefNum = PntRefNum
        self.LandXML_Obj = LandXML_Obj
        self.Observation = Observation
        
    def AddBranchInstance(self):
        
        if not self.CheckBranchExists():
            if self.ConnectionFinder.PrimaryBranch or \
                    (self.ConnectionFinder.SecondaryBranch and self.LandXML_Obj.TraverseProps.MixedTraverse):
                self.traverse.PrimaryBranches = self.CreateBranch(self.traverse.PrimaryBranches)
            elif self.ConnectionFinder.SecondaryBranch:
                self.traverse.SecondaryBranches = self.CreateBranch(self.traverse.SecondaryBranches)
            elif self.ConnectionFinder.NonRmBranch and self.LandXML_Obj.TraverseProps.MixedTraverse:
                self.traverse.NonRmBranches = self.CreateBranch(self.traverse.NonRmBranches)
            
        return self.Branches, self.traverse
    
    def CheckBranchExists(self):
        #Check if branch instance already exists
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
                    #self.AddObservationTrying()
                    return True
                    break
            except AttributeError:
                pass
            
        return False
    
    
    def CreateBranch(self, BranchList):
        '''
        Creates a branch instance in slef.Branches
        :return: 
        '''

        BranchLabel = GetTraverseBranchNumber(self.Branches, self.PntRefNum)
        BranchList.append(BranchLabel)
        # create a traverse copy instance and add to Branches
        travCopy = CopyTraverseInstance.TraverseCopy(self.traverse)
        # Add name of parent traverse branch
        setattr(travCopy, "ParentBranch", self.traverse.BranchName)
        setattr(travCopy, "TriedObservation", self.Observation)
        # get reference number for branch
        setattr(self.Branches, BranchLabel, travCopy)
        
        return BranchList
            
            
        

