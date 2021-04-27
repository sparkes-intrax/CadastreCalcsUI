'''
Workflow to determine what to do about when there is no boundary connection
to RMs.
For RM traverse only
'''

from LandXML import Connections, BDY_Connections, NoConnection
from LandXML.RefMarks import FilterNonRMs


def NoBdy(Observations, PntRefNum, LandXML_Obj, TraverseProps,
          CadastralPlan, traverse, gui):
    '''
    Operation is defined by how many consecutive traverse sides have occurred
    without a boundary connection
    Counter is in TraverseProps
    1) Check if any targets of Observations have a boundary connection
    2) if there are no boundary connections, check if RMs with 
            boundary connections still need to be calculated
    3) If still to be calculated use counter define operation pathway
    :param Observations: Set of observatons to query
    :return: 
    '''
    #Set up objects
    ConnectionChecker = BDY_Connections.CheckBdyConnection(PntRefNum, LandXML_Obj)
    NoBdyObj = NoBdyMethods(Observations, PntRefNum, LandXML_Obj, TraverseProps,
          CadastralPlan, traverse, ConnectionChecker, gui)
    
    # Check if any observation's targets have connection to BDY
    if NoBdyObj.CheckForBdyConnections():
        TraverseProps.PointsSinceBdy = 0
        return TraverseProps, Observations, PntRefNum
    
    # Check if Boundary Connections remain
    if not NoBdyObj.QueryRefMarks():
        return TraverseProps, Observations, PntRefNum
    
    #Use counter to define operation
    if TraverseProps.PointsSinceBdy < 5:
        TraverseProps.PointsSinceBdy += 1
    elif len(TraverseProps.Branches) > 0:
        #Current traverse side number
        TraverseSides = len(traverse.Points.__dict__.keys())
        #reverse up to branch if exists
        Observations, BranchRefNum = NoConnection.main(TraverseProps, LandXML_Obj,
                                                       traverse, gui,
                                                       CadastralPlan)
        PntRefNum = BranchRefNum
        Observations = FilterNonRMs.RemoveNonRM_Connections(Observations,
                                                            traverse,
                                                            LandXML_Obj,
                                                            PntRefNum)
        #Calc how many sides have been deleted
        DeletedSides = TraverseSides - len(traverse.Points.__dict__.keys())
        TraverseProps.PointsSinceBdy =TraverseProps.PointsSinceBdy - DeletedSides

    return TraverseProps, Observations, PntRefNum
        
    
class NoBdyMethods:
    def __init__(self, Observations, PntRefNum, LandXML_Obj, TraverseProps,
          CadastralPlan, traverse, ConnectionChecker, gui):
        
        self.Observations = Observations
        self.PntRefNum = PntRefNum
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = TraverseProps
        self.CadastralPlan = CadastralPlan
        self.traverse = traverse
        self.ConnectionChecker = ConnectionChecker
        self.gui = gui
        
        
        
    def CheckForBdyConnections(self):
        '''
        Checks whether any of self.Obs targets are connected to a BDY
        :return: True if Boundary Connection found
        '''
        
        for key in self.Observations.__dict__.keys():
            observation = self.Observations.__getattribute__(key)
            TargetID = self.ConnectionChecker.GetTargetID(observation, self.PntRefNum)
            if self.ConnectionChecker.TestConnections(TargetID):
                return True
            else:
                return False


    def QueryRefMarks(self):
        '''
        Looking for RMs not calculated but with boundary connection
        Queries all reference marks whether they have been calculated (in traverse
        or CadastralPlan) and whether they have a boundary connection
        :return: Boolean
        '''

        for monument in self.LandXML_Obj.Monuments.getchildren():
            MarkType = monument.get("type")
            if MarkType == "SSM" or MarkType == "PM":
                ID = monument.get("pntRef")
                if not self.CheckPntIsCalculated(ID):
                    #get all connections for ID
                    Observations = Connections.AllConnections(ID, self.LandXML_Obj)
                    self.FindConnection = True
                    if self.CheckObservations(ID, Observations):
                        return True

        return False


    def CheckPntIsCalculated(self, ID):
        '''
        Checkes if point (ID) has been calculated already
        :param CadastralPlan:
        :param traverse:
        :param ID:
        :return:
        '''

        if hasattr(self.CadastralPlan.Points, ID) or hasattr(self.traverse.Points, ID):
            return True
        else:
            return False

    def CheckObservations(self, ID, Observations):
        '''
        Loop method to cycle through observations looking for
        connections to a boundary
        '''

        #loop through found connections and see if any end points are parcel vertexes
        for key in Observations.__dict__.keys():
            Observation = Observations.__getattribute__(key)
            #assign the refNum that PointRefNum is connected to
            TargetID = self.ConnectionChecker.GetTargetID(Observation, ID)

            #Check if TargetID is a parcel vertex
            if self.ConnectionChecker.BdyConnection(TargetID):
                return True


        return False