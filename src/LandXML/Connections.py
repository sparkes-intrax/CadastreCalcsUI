'''
Methods to retreive connections for a given point in the Land XML file
'''
from LandXML import RemoveCalculatedConnections, RemoveDeadEnds, NotAllowedObservations
from LandXML.RefMarks import FilterNonRMs
from numpy import sin

from timer import Timer
class AllConnections:

    def __init__(self, PntRefNum, LandXML_Obj):
        '''
        Looks for connections containing PntRefNUm in ReducedObservations
        :param PntRefNum: Integer refNum to pointsin the LandXML file
        :param ReducedObs: LandXML element from the Survey parent element
        '''

        #Get Oobservations from pointrefNum
        Observations =self.GetQueries(PntRefNum, LandXML_Obj)
        '''
        #Counter for number of connections for PntRefNum
        #tObj = Timer()
        ConnectionNum = 0
        #tObj.start()
        ObsID = LandXML_Obj.TraverseProps.tag + PntRefNum
        ns = LandXML_Obj.lxml.getroot().nsmap
        Query = "//ReducedObservation[@setupID='" + ObsID + "']"
        Observations1 = LandXML_Obj.lxml.findall(Query, ns)
        Query = "//ReducedObservation[@targetSetupID='" + ObsID + "']"
        Observations2 = LandXML_Obj.lxml.findall(Query, ns)
        Observations = Observations1 + Observations2
        #tObj.stop("Findall lxml operation:")
        '''
        Observations = NotAllowedObservations.main(Observations, LandXML_Obj.TraverseProps)
        for ob in Observations:
            if self.CheckObs(ob):
                setattr(self, ob.get("name"), ob)
            


    def CheckObs(self, ob):
        '''
        Checks if Observation has a azimuth and a distance. Some ReducedObs don't
        :param Ob: Observation to test
        :return: bool
        '''
        #check has a bearing
        if ob.get("azimuth") is None and ob.get("chordAzimuth") is None:
            return False
        else:
            #check has a distance
            if ob.get("length") is None and ob.get("horizDistance") is None:
                return False
            else:
                return True


    def GetQueries(self, PntRefNum, LandXML_Obj):
        '''
        RUns a set of queries to extract observations with PntRefNum
        :return:
        '''

        ObsID = LandXML_Obj.TraverseProps.tag + PntRefNum
        ns = LandXML_Obj.lxml.getroot().nsmap

        #Reduced Observations
        tag = "//ReducedObservation"
        Query1 = tag + "[@setupID='" + ObsID + "']"
        Query2 = tag + "[@targetSetupID='" + ObsID + "']"
        Observations = LandXML_Obj.lxml.findall(Query1, ns) + \
                       LandXML_Obj.lxml.findall(Query2, ns)

        # Reduced ArcObservations
        tag = "//ReducedArcObservation"
        Query1 = tag + "[@setupID='" + ObsID + "']"
        Query2 = tag + "[@targetSetupID='" + ObsID + "']"
        Observations = Observations + LandXML_Obj.lxml.findall(Query1, ns) + \
                       LandXML_Obj.lxml.findall(Query2, ns)

        return Observations





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

def KeepConnection(Observations, Connection):
    '''
    Removes all but Connection from Observations
    :param Observations: List of connections that are to be analysed
    :param RemoveObs: list of keys of Observations to remove
    :return: Observations
    '''
    RemoveObs = []
    for key in Observations.__dict__.keys():
        if Observations.__getattribute__(key) != Connection:
            RemoveObs.append(key)
            
    if len(RemoveObs) > 0:
        Observations = RemoveSelectedConnections(Observations, RemoveObs)

    return Observations

def GetTargetID(Observation, PntRefNum, TraverseProps):
    '''
    Gets the target ID from Observation
    Assumes PntRefNUm is the start of the connection
    :param Observation:
    :param PntRefNum:
    :return: TargetID
    '''

    if Observation.get("setupID").replace(TraverseProps.tag, "") == \
            PntRefNum:
        TargetID = Observation.get("targetSetupID").replace(TraverseProps.tag, "")
    else:
        TargetID = Observation.get("setupID").replace(TraverseProps.tag, "")

    return TargetID

def ObservationOrientation(PntRefNum, Observation, TraverseProps):
    '''
    Checks if PntRefNum is Target or Stup of Observation
    :param PntRefNum:
    :param LandXML_Obj:
    :return:
    '''

    if Observation.get("setupID").replace(TraverseProps.tag, "") == PntRefNum:
        return True
    else:
        return False



def CheckStartingPoint(PntRefNum, LandXML_Obj, CadastralPlan, traverse, gui):
    '''
    Checks Observations whether any connections meet criteria
    - Not already calculated
    - Between RMs
    '''
    # get all connections to point
    Observations = AllConnections(PntRefNum, LandXML_Obj)
    # remove already calculated points
    Observations = RemoveCalculatedConnections.main(Observations,
                                                    CadastralPlan,
                                                    traverse,
                                                    LandXML_Obj.TraverseProps,
                                                    PntRefNum)

    '''                                               
    # Remove Dead Ends
    if LandXML_Obj.TraverseProps.TraverseClose:
        Observations = RemoveDeadEnds.main(PntRefNum,
                                                Observations,
                                                LandXML_Obj, gui,
                                                traverse)
    '''
    # remove non RM connections
    Observations = FilterNonRMs.RemoveNonRM_Connections(Observations, LandXML_Obj, PntRefNum, "Remove")

    return Observations

def GetObservationAzimuth(Observation):
    '''
    Bearing (or Azimuth) of Arc and Line connections are stored under different attributes
    in a landXML Observation
    Function retrieves bearing depending on Observation type
    :param Observation: Observation to retrieve bearing from
    :return:
    '''

    if Observation.get("azimuth") is None:
        #arc
        return Observation.get("chordAzimuth")
    else:
        #line
        return Observation.get("azimuth")

def GetObservationDistance(Observation):
    '''
    Distance of Arc and Line connections are stored under different attributes
    in a landXML Observation
    The distance for an arc stored in the length attribute of an arc is a arc distance.
        Function convert arc distance to chord distance
    :param Observation:
    :return:
    '''

    if Observation.get("horizDistance") is None:
        try:
            arcLength = Observation.get("length")
            radius = Observation.get("radius")
            return (2 * float(radius) * sin(float(arcLength) / (2 * float(radius))))
        except TypeError:
            pass
    else:
        return float(Observation.get("horizDistance"))

def GetLineType(Observation):
    '''
    Checkes whether observation is a Arc or Line
    :param Observation:
    :return:
    '''

    if Observation.get("horizDistance") is None:
        return "Arc"
    else:
        return "Line"

