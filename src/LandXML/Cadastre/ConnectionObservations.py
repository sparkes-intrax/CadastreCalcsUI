'''
Retrieves observations that are of specific type (Query),
haven't been calculated and
that one of the end points is in CadastralPlan.Points
'''

from LandXML import Connections
from LandXML import RemoveDeadEnds

def main(CadastralPlan, LandXMLObj, Query):
    '''
    Calls methods to query observation type
    :param CadastralPlan: HOlds Calculated cadastral data
    :param LandXMLObj: holds LandXML file data and software properties
    :param Query: Type of observation to query
    :return:
    '''

    ConnectionQueryObs = ConnectionQuery(CadastralPlan, LandXMLObj, Query)
    Observations = ConnectionQueryObs.ExtractObservations()
    
    return Observations
    

class ConnectionQuery:

    def __init__(self, CadastralPlan, LandXMLObj, Query):
        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXMLObj
        self.Query = Query

    def ExtractObservations(self):
        '''
        Coordinates observation query
        :return: Observations
        '''
        
        if self.Query == "Any":
            Observations = ObservationObj(self.LandXML_Obj.ReducedObs)
        else:
            Observations = self.GetAllObs()
        Observations = self.RemoveObservations(Observations)
        Observations = self.RemoveDeadEnds(Observations)
        
        return Observations

    def GetAllObs(self):
        '''
        Returns all obs of query type
        :return:
        '''

        ns = self.LandXML_Obj.lxml.getroot().nsmap
        ObsType = self.Query

        tag = "//ReducedObservation"
        Query = tag + "[@desc='" + ObsType + "']"
        Observations = self.LandXML_Obj.lxml.findall(Query, ns)
        Observations = ObservationObj(Observations)

        return Observations

    def RemoveObservations(self, Observations):
        '''
        Removes alread calculated observations and observations
        :param Observations:
        :return:
        '''

        # Remove already calculated connections
        RemoveObs = []
        for key in Observations.__dict__.keys():
            Ob = Observations.__getattribute__(key)
            ObsName = Ob.get("name")
            try:
                setupID = Ob.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
                targetID = Ob.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            except AttributeError:
                RemoveObs.append(key)
                Ob.getparent().remove(Ob)
                continue

            if hasattr(self.CadastralPlan.Lines, ObsName) or\
                    hasattr(self.CadastralPlan.TriedConnections, ObsName):
                RemoveObs.append(key)
            elif hasattr(self.CadastralPlan.Points, setupID) and \
                hasattr(self.CadastralPlan.Points, targetID):
                RemoveObs.append(key)
            elif not hasattr(self.CadastralPlan.Points, setupID) and \
                not hasattr(self.CadastralPlan.Points, targetID):
                RemoveObs.append(key)


        if len(RemoveObs) > 0:
            Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)

        return Observations


    def GetArcObs(self):
        ns = LandXML_Obj.lxml.getroot().nsmap
        ObsType = self.LandXML_Obj.TraverseProps.tag + self.Query

        tag = "//ReducedArcObservation"
        Query = tag + "[@desc='" + ObsID + "']"
        Observations = LandXML_Obj.lxml.findall(Query, ns)
        Observations = ObservationObj(Observations)

        return Observations

    def RemoveDeadEnds(self, Observations):
        '''
        Removes dead end observations
        :param Observations:
        :return:
        '''

        RemoveObs = []
        for key in Observations.__dict__.keys():
            Ob = Observations.__getattribute__(key)
            try:
                TargetID = self.GetStart(Ob)
            except AttributeError:
                continue

            #Remove already calc'd Traget Obs
            TargObs = Connections.AllConnections(TargetID, self.LandXML_Obj)
            RemoveTargObs = []
            for key in TargObs.__dict__.keys():
                Obs = TargObs.__getattribute__(key)
                ObsName = Obs.get("name")
                if hasattr(self.CadastralPlan.Lines, ObsName):
                    RemoveTargObs.append(key)
                    if len(RemoveTargObs) > 0:
                        TargObs = Connections.RemoveSelectedConnections(TargObs, RemoveTargObs)

            if len(TargObs.__dict__.keys()) == 1 and key not in RemoveObs:
                RemoveObs.append(key)

        if len(RemoveObs) > 0:
            Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)


        return Observations

    def GetStart(self, Observation):
        '''
        Gets start point of observation
        :param Observation:
        :return:
        '''

        setupID = Observation.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        targetID = Observation.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")

        if hasattr(self.CadastralPlan.Points, setupID):
            return targetID
        else:
            return setupID

class ObservationObj:
    def __init__(self, Observations):
        '''
        Converts Observations to a class instance
        :param Observations:
        '''

        for Ob in Observations:
            if Ob.text is None:
                setattr(self, Ob.get("name"), Ob)