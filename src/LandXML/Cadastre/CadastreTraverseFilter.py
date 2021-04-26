'''
Workflow to filter a set of Observations to prioritise
conditions for a Cadastre traverse determined from LandXML

Priority is to Observations with road frontage - desc="Road"
Then a boundary - desc = "Boundary"
Leaving Connections between Boundaries of different lots (ie across roads) desc="Connection"

Connection to RMs of DHW. GIP, CB type are not allowed. These are calculated
after all other connections have been calc'd
'''
from LandXML import Connections, RemoveDeadEnds
from LandXML.RefMarks import RefMarkQueries


def main(Observations, PntRefNum, LandXML_Obj, gui, traverse):
    '''
    Coordinates the workflow
    :param Observations:
    :param PntRefNum:
    :param LandXML_Obj:
    :return: filtered Observations
    '''

    #create filter object
    FilterObj = CadastreObsFilter(PntRefNum, LandXML_Obj)

    #remove any unwanted RM connections (DHW etc)
    if LandXML_Obj.TraverseProps.TraverseClose:
        Observations = RemoveDeadEnds.main(PntRefNum, Observations,
                                                LandXML_Obj, gui, traverse)
    #Observations = FilterObj.RemoveRmConnections(Observations)

    #prioritise road frontage
    Observations = FilterObj.RoadFrontage(Observations)

    #prioritise boundary observation
    if not FilterObj.RoadFrontageFound:
        Observations = FilterObj.Bdy(Observations)

    return Observations


class CadastreObsFilter:

    def __init__(self, PntRefNum, LandXML_Obj):
        self.PntRefNum = PntRefNum
        self.LandXML_Obj = LandXML_Obj
        self.RoadFrontageFound = False

    def RemoveRmConnections(self, Observations):
        '''
        Removes any connection to a RM of GIP, DHW, CB type
        :return:
        '''
        RemoveObs = [] #List of observations to be removed
        for key in Observations.__dict__.keys():
            Obs = Observations.__getattribute__(key)

            #Get reference number of Target from PntRefNum
            TargetID = Connections.GetTargetID(Obs, self.PntRefNum, self.LandXML_Obj.TraverseProps)

            #checks if TargetID is an accepted reference mark - ie on a connection or BDY corner
            if RefMarkQueries.CheckIfConnectionMark(self.LandXML_Obj, TargetID):
                continue
            #check if ref mark
            if RefMarkQueries.FindMarkType(self.LandXML_Obj, TargetID) is not None and \
                    not RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, TargetID):
                RemoveObs.append(key)

        if len(RemoveObs) > 0:
            Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)

        return Observations

    def RoadFrontage(self, Observations):
        '''
        Prioritises Road Frontage observations
        If finds observations with road frontage, observations without are removed
        If no observations with road frontage nothing happens
        :param Observations:
        :return:
        '''

        Observations = self.ObservationFilter(Observations, "Road")

        return Observations

    def Bdy(self, Observations):
        '''
        Prioritises Boundary observations
        :param Observations:
        :return:
        '''

        Observations = self.ObservationFilter(Observations, "Boundary")

        return Observations


    def ObservationFilter(self, Observations, Search):
        '''
        Prioritises Observations with desc = Search
        If finds observations with "Search", observations without are removed
        If no observations with "Search" nothing happens
        :param Observations:
        :param Search: "Road", "Boundary"
        :return:
        '''

        RemoveObs = [] # list to store observations without Search
        for key in Observations.__dict__.keys():
            Obs = Observations.__getattribute__(key)
            Desc = Obs.get("desc")

            if Desc != Search:
                RemoveObs.append(key)

        #check if any Search found
        if len(RemoveObs) != len(Observations.__dict__.keys()):
            Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)
            if Search == "Road":
                self.RoadFrontageFound = True

        return Observations


