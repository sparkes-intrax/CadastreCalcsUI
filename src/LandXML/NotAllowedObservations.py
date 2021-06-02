'''
Removes observations from a set that are not allowed for traverses
'''
from LandXML import Connections

def main(Observations, TraverseProps):
    '''
    Loop through observation and check if in not allowed list
    :param Observations: 
    :param TraverseProps: 
    :return: 
    '''
    
    RemoveObs = []
    for Obs in Observations:
        ObType = Obs.get("desc")
        
        #loop through not allow list
        for NotAllowedType in TraverseProps.NotAllowedObs:
            if NotAllowedType == ObType:
                RemoveObs.append(Obs)
                
    #remove observations in RemoveObs
    for Obs in RemoveObs:
        Observations.remove(Obs)
        
    return Observations
        