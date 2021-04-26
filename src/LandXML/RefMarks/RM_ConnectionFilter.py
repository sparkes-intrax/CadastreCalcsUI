'''
Workflow to filter Connections for a RM traverse
'''
from LandXML.RefMarks import RefMarkQueries, TraverseNoBdy, FilterNonRMs
from LandXML import BDY_Connections, Connections, NoConnection


def FilterObservations(Observations, traverse, CadastralPlan, 
                       LandXML_Obj, PntRefNum, gui):
    '''
    Perfroms specific filtering criteria to Connections for A RM traverse
    :param Connections: Set of connections to be queried - from LandXML
    :param traverse: current traverse data object
    :param CadastralPlan: CadastralPlan data object
    :param LandXML_Obj: Data object from LandXML file
    :return: Connections
    '''

    #1) Remove connections not between RMs and dead ends when no more closes to find
    Observations = FilterNonRMs.RemoveNonRM_Connections(Observations, traverse, 
                                                        LandXML_Obj, PntRefNum)
    if len(Observations.__dict__.keys()) == 0:
        # deal with no connection
        Observations, PntRefNum = NoConnection.main(LandXML_Obj.TraverseProps,
                                                              LandXML_Obj,
                                                              traverse,
                                                              gui, CadastralPlan)
        setattr(LandXML_Obj.TraverseProps, "PntRefNum", PntRefNum)
        Observations = FilterNonRMs.RemoveNonRM_Connections(Observations, 
                                                            traverse, LandXML_Obj, 
                                                            PntRefNum)

    #2) Check for boundary connections if still looking for boundary connections
    # defined by whether RMs in LandXML have not been calculated  that have a BDY connection
    # LandXML_Obj.Traverse_Props.BdyConnections
    # remove non-boundary connected RMs only if there is choice of one with a BDY connection

    if LandXML_Obj.TraverseProps.BdyConnections:
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(PntRefNum, LandXML_Obj)
        Observations = ConnectionChecker.FilterBdyConnection(Observations)

    #Query remaining observations for boundary connections to determine
            #next operation
    LandXML_Obj.TraverseProps, Observations, PntRefNum = \
        TraverseNoBdy.NoBdy(Observations, PntRefNum, LandXML_Obj,
                            LandXML_Obj.TraverseProps, CadastralPlan, traverse, gui)

    setattr(LandXML_Obj.TraverseProps, "PntRefNum", PntRefNum)

    # 3) More than 1 connection - select connections with bearing within 45 degrees.
    if len(Observations.__dict__.keys()) > 1:
        LandXML_Obj.TraverseProps.Branches.append(PntRefNum)
        FinalConnectionFilter = FinalFilter(traverse, LandXML_Obj.TraverseProps)
        Observations =  FinalConnectionFilter.SimilarBearingConnection(Observations)
    # 4) if still more than one connection (or no connections) select shortest connection
    if len(Observations.__dict__.keys()) > 1:
        Observations = FinalConnectionFilter.FilterByDistance(Observations)

    #return connection
    for key in Observations.__dict__.keys():
        return Observations.__getattribute__(key)
    


def TraverseBranches(PntRefNum, ):
    '''
    Checks if there are branches at PntRefNum and what to do about it 
    :return: 
    '''


class FinalFilter:
    def __init__(self, traverse, TraverseProps):
        '''
        Filters used when other prioritisation methods have not selected
            a single connection
        Contains methods to filter by bearing or distance
        :param traverse: traverse data object
        '''
        self.traverse = traverse
        self.TraverseProps = TraverseProps


    def SimilarBearingConnection(self, Observations):
        '''
        Finds a Observations with a bearing within 45 dgrees of last connection
        if first connection returns all Observations
        :param Observations: Set of Observations to be queried
        :param traverse: traverse data object
        :return: Observations
        '''

        #Check if first connection
        if len(self.traverse.refPnts) == 1:
            return Observations

        #get bearing of last connection
        LastBearing, EndRefNum = self.FindLastConnectionBearing()
        #Find Observations within 45 degrees of LastBearing
        ConnectionList = self.ObservationsWithinBearing(LastBearing, Observations, EndRefNum)
        #if find Observations within 45 degrees, delete other bearings
        if len(ConnectionList) < len(Observations.__dict__.keys()):
            Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations

    def FindLastConnectionBearing(self):
        '''
        Finds the bearing of last connection in the traverse
        :return:
        '''
        StartRefNum = self.traverse.refPnts[-2]
        EndRefNum = self.traverse.refPnts[-1]
        #get line bearing of lasat connection
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            Line = self.traverse.Lines.__getattribute__(key)
            if Line.StartRef == StartRefNum and Line.EndRef == EndRefNum:
                return float(Line.Bearing), EndRefNum

    def ObservationsWithinBearing(self, LastBearing, Observations, PntRefNum):
        '''
        Finds the Observations in Observations object that are within 45 degrees
            of LastBearing
        :param LastBearing: Bearing of last connection in traverese
        :param Observations: Set of Observations from LandXML to query
        :param PntRefNum: Starting point reference of all Observations to be queried
        :return: ConnectionList (List of Observations that pass query)
        '''

        #Create a list to store Observations to remove - only when 1 or more Observations pass
            #bearing query
        ConnectionList = []
        #Loop through Observations and check if their bearings are within 45 degrees
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            #Get Observations bearing - normalised to same orientation as lat traverse connection
                #that is setupiD (Last connection) = TargetID (queried connection)
            if connection.get("setupID").replace(self.TraverseProps.tag, "") == PntRefNum:
                azimuth = float(connection.get("azimuth"))
            else:
                azimuth = self.FlipBearing(float(connection.get("azimuth")))

            #test of bearing with 45 degrees
            if abs(LastBearing - azimuth) > 45:
                ConnectionList.append(key)

        return ConnectionList

    def FlipBearing(self, Bearing):
        '''
        Flips bearing by 180 degrees
        :param Bearing:
        :return:
        '''

        Bearing = Bearing + 180
        if Bearing >= 360:
            Bearing = Bearing - 360

        return Bearing

    def DeleteConnections(self, Connections, ConnectionsList):
        '''
        Deletes Connection that are not in Connection list
        :param Connections:
        :param ConnectionsList:
        :return:
        '''

        for key in Connections.__dict__.keys():
            connection = Connections.__getattribute__(key)
            if connection not in ConnectionsList:
                delattr(Connections, key)

        return Connections


    def FilterByDistance(self, Observations):
        '''
        Filters the Observations for the line with the shortest distance
        :param Observations:
        :return:
        '''

        ShortestDistance = 10000
        ConnectionList = []
        #Loop through Observations
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            distance  = float(connection.get("horizDistance"))
            if distance < ShortestDistance:
                KeepConnection = key
                ShortestDistance = distance


        #delete all but shortest side
        for key in Observations.__dict__.keys():
            if key != KeepConnection:
                ConnectionList.append(key)
        Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations


    
    