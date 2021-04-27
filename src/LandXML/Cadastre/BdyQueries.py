'''
Set of functions and methods to query a boundary point
'''
from LandXML import Connections

def main(LandXML_Obj, PntRefNum, Query):
    '''
    Coordinates 
    :param LandXML_Obj: 
    :param PntRefNum: 
    :param Query: 
    :return: 
    '''

    # Get connections from PntRefNum
    Observations = Connections.AllConnections(PntRefNum, LandXML_Obj)
    # Remove already calculated connections
    Observ
    # Loop through available observations 
    for key in Observations.__dict__.keys():
        Observation = Observations.__getattribute__(key)
        
        #Get TargetID for Observation
        TargetID = Connections.GetTargetID(Observation, PntRefNum, LandXML_Obj.TraverseProps)
        #Get Connections

def RoadFrontageParcel(LandXML_Obj, PntRefNum):
    '''
    Checks if PntRefNum is on road frontage and is a parcel from the 
        plans subdivision
    :param LandXML_Obj: 
    :param PntRefNum: 
    :return: 
    '''
    
    
    
    
    
def RoadFrontage(LandXML_Obj, PntRefNum):
    '''
    Checks if PntRefNum is on road frontage and part of a road parcel
    :param LandXML_Obj: 
    :param PntRefNum: 
    :return: 
    '''