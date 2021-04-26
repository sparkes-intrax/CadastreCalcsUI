from LandXML.RefMarks import RefMarkQueries
from LandXML import Connections

def RemoveNonRM_Connections(Observations, LandXML_Obj, PntRefNum, Action):
    '''
    Checks if any of the connectiosn are between RMs and prioritises them
    If no RM-RM connections does nothing
    param Action: whether to remove "Remove" or prioritise "Priority" RMs
    :return: 
    '''
    # list of connections to delete
    RemoveObs = []
    # loop through connections
    for key in Observations.__dict__.keys():
        connection = Observations.__getattribute__(key)

        # get point ref numbers of connection
        SetupID = connection.get("setupID").replace(LandXML_Obj.TraverseProps.tag, "")
        TargetSetupID = connection.get("targetSetupID").replace(LandXML_Obj.TraverseProps.tag, "")
        # get end point of connection
        if SetupID == PntRefNum:
            EndRefNum = TargetSetupID
        else:
            EndRefNum = SetupID

        # check if EndPoint is an RM
        if not RefMarkQueries.CheckIfRefMark(LandXML_Obj, EndRefNum):
            RemoveObs.append(key)

    # if Observations were found to delete remove them
    if len(RemoveObs) < len(Observations.__dict__.keys()) and Action == "Priority":
        Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)
    elif len(RemoveObs) == len(Observations.__dict__.keys()) and Action == "Priority":
        setattr(LandXML_Obj.TraverseProps, "MixedTraverse", True)
    elif len(RemoveObs) > 0 and Action == "Remove":
        Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)

    return Observations


def DeadEndConnection(PntRefNum, LandXML_Obj):
    '''
    Checks if PntRefNum is a dead end
    :param PntRefNum: Point to query (Point number from LandXML)
    :param LandXML_Obj: LadnXML data object
    :return:
    '''
    # Find all connections to PntRefNum - has one connection iof its a dead end
    Observations = Connections.AllConnections(PntRefNum, LandXML_Obj)
    if len(Observations.__dict__.keys()) == 1:
        return True
    return False