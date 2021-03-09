'''
Methods to retreive connections for a given point in the Land XML file
'''

class AllConnections:

    def __init__(self, PntRefNum, LandXML_Obj):
        '''
        Looks for connections containing PntRefNUm in ReducedObservations
        :param PntRefNum: Integer refNum to pointsin the LandXML file
        :param ReducedObs: LandXML element from the Survey parent element
        '''
        #Counter for number of connections for PntRefNum
        ConnectionNum = 0
        
        # loop through observations
        for ob in LandXML_Obj.ReducedObs.getchildren():
            #check if observation contains PntRefNum
            attrib = ob.attrib
            if "targetSetupID" in attrib.keys():
                SetupID = ob.get("setupID").replace(LandXML_Obj.TraverseProps.tag, "")
                TargetID = ob.get("targetSetupID").replace(LandXML_Obj.TraverseProps.tag, "")
                if PntRefNum == SetupID or PntRefNum == TargetID:
                    # pntRef in ob -> add to Obs
                    ConnectionNum += 1
                    setattr(self, ("connection" + str(ConnectionNum)), ob)


def RemoveSelectedConnections(Observations, RemoveObs):
    '''
    Removes Observations in RemoveObs
    :param Observations: List of connections that are to be analysed
    :param RemoveObs: list of keys of Observations to remove
    :return: Observations
    '''

    for Obs in RemoveObs:
        delattr(Observations, Obs)

    return Observations

        

        