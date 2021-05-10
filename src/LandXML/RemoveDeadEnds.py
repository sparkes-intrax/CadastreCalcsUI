'''
Removes dead ends from Observation list
'''
from LandXML import Connections, TraverseSideCalcs
from LandXML.RefMarks import RefMarkQueries
import CadastreClasses as DataObjects

def main(PntRefNum, Observations, LandXML_Obj, gui, traverse):
    '''
    Coordinates the removal of dead end observations
    :param PntRefNum: Reference Number for start of all connections in Obsevations
    :param Observations: Set Observations to test
    :return: Updated Observations with dead ends removed
    '''
    
    #create RemoveTraverseDeadEnds instance
    RemoveObs = RemoveTraverseDeadEnds(PntRefNum, LandXML_Obj, gui, traverse)
    #get a list of dead end connections
    DeadEnds = RemoveObs.TestForDeadEnds(Observations)

    #remove Dead Ends if found
    if len(DeadEnds) > 0:
        Observations = Connections.RemoveSelectedConnections(Observations, DeadEnds)

    return Observations
    

class RemoveTraverseDeadEnds:

    def __init__(self, PntRefNum, LandXML_Obj, gui, traverse):
        '''
        methods to remove dead end observations from a observations connected
        to PntRefNum
        :param PntRefNum: Start point for all connections to be tested
        '''

        self.PntRefNum = PntRefNum
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.LandXML_Obj = LandXML_Obj
        self.gui = gui
        self.traverse = traverse

    def TestForDeadEnds(self, Observations):
        '''
        Tests all connections in Observations for DeadEnds
        :return: list of dead end connections - DeadEnds
        '''
        
        #create empty list to store dead ends
        DeadEnds = []
        #loop through connections to test for dead ends
        for key in Observations.__dict__.keys():
            Observation = Observations.__getattribute__(key)
            #get end point reference number
            TargetID = self.GetTargetID(Observation)
            #get all Observations to TargetID
            TargObs = Connections.AllConnections(TargetID, self.LandXML_Obj)
            #remove connection to self.PntRefNum
            TargObs = self.RemoveCurrentObservation(TargetID, TargObs)
            
            #check if the TargObs has more than one observations - if not  = dead end
            if len(TargObs.__dict__.keys()) == 0:
                #if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, TargetID):
                #self.AddRmDeadEndToTriedConecctions(Observation)


                DeadEnds.append(key)

        return DeadEnds
    
    def GetTargetID(self, Observation):
        '''
        Queries connection for the end reference number
        End can't be equal to self.PntRefNum
        :param Observation: 
        :return: End Point reference Number
        '''
        
        # Get TargetID PnteRef
        if Observation.get("setupID").replace(self.TraverseProps.tag, "") == \
                self.PntRefNum:
            return Observation.get("targetSetupID").replace(self.TraverseProps.tag, "")
        else:
            return Observation.get("setupID").replace(self.TraverseProps.tag, "")
        
    def RemoveCurrentObservation(self, PntRefNum, Observations):
        '''
        Removes the connection between self.PntRefNum and PntRefNum from Observations 
        :param TargetID: 
        :param Observations: 
        :return: 
        '''
        
        for key in Observations.__dict__.keys():
            Observation = Observations.__getattribute__(key)
            
            #get observation endpoint reference numbers
            SetUpID = Observation.get("setupID").replace(self.TraverseProps.tag, "")
            TargetID = Observation.get("targetSetupID").replace(self.TraverseProps.tag, "")
            
            #check if the connection is to self.PntRefNum
            if (SetUpID == self.PntRefNum and TargetID == PntRefNum) or \
                    (SetUpID == PntRefNum and TargetID == self.PntRefNum):
                break
                
        #delete selected connection from Observations
        delattr(Observations, key)
        
        return Observations

    def AddRmDeadEndToTriedConecctions(self, Observation):
        '''
        Creates a line object and adds it to TriedConnections
        '''

        #Create dummy traverse object to store line
        traverse = DataObjects.Traverse(False, None)
        #add source point to traverse
        SrcPoint = self.traverse.Points.__getattribute__(self.PntRefNum)
        setattr(traverse.Points, self.PntRefNum, SrcPoint)
        #create traverse sideObj and run the work flow
        sideObj = TraverseSideCalcs.TraverseSide(self.PntRefNum, traverse, Observation,
                                                 self.gui, self.LandXML_Obj)

        #add line to tried connections - CadastralPlan
        LineNum = self.gui.CadastralPlan.TriedConnections.__getattribute__("LineNum")
        LineName = "Line" + str(LineNum+1)
        setattr(self.gui.CadastralPlan.TriedConnections, LineName, sideObj.line)
        setattr(self.gui.CadastralPlan.TriedConnections, "LineNum", (LineNum + 1))
        # add line to tried connections - Traverse
        LineNum = self.traverse.TriedConnections.__getattribute__("LineNum")
        LineName = "Line" + str(LineNum + 1)
        setattr(self.traverse.TriedConnections, LineName, sideObj.line)
        setattr(self.traverse.TriedConnections, "LineNum", (LineNum + 1))
            

