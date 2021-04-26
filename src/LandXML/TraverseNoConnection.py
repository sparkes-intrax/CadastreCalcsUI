'''
Workflow to handle when no connection could be found satisfying criteria
'''
from LandXML import Connections
def NoConnection(traverse, TraverseProps, PntRefNum, LandXML_Obj):
    '''
    Coordinates workflow to handle no connections
    :param traverse: current traverse data object
    :return: 
    '''
    
    if not TraverseProps.Close:
        #Not looking for closes anymore
        Connections = Connections.AllConnections(PntRefNum, LandXML_Obj)