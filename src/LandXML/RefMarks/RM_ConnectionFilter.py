'''
Workflow to filter Connections for a RM traverse
'''
from LandXML.RefMarks import RefMarkQueries
from LandXML import BDY_Connections, Connections
def FilterConnections(Observations, traverse, CadastralPlan, LandXML_Obj, PntRefNum):
    '''
    Perfroms specific filtering criteria to Connections for A RM traverse
    :param Connections: Set of connections to be queried - from LandXML
    :param traverse: current traverse data object
    :param CadastralPlan: CadastralPlan data object
    :param LandXML_Obj: Data object from LandXML file
    :return: Connections
    '''

    #1) Remove connections not between RMs and dead ends when no more closes to find
    Connections = RemoveNonRM_Connections(Observations, traverse, LandXML_Obj, PntRefNum)
    if len(Connections.__dict__.keys()) == 0:
        # deal with no connection
        TraverseNoConnection(traverse, LandXML_Obj.TraverseProps, PntRefNum, LandXML_Obj)
        return None
    #2) Check for boundary connections if still looking for boundary connections
    # defined by whether RMs in LandXML have not been calculated  that have a BDY connection
    # LandXML_Obj.Traverse_Props.BdyConnections
    # remove non-boundary connected RMs only if there is choice of one with a BDY connection
    if LandXML_Obj.TraverseProps.BdyConnections:
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(PntRefNum, LandXML_Obj)
        Observations = ConnectionChecker.FilterBdyConnection(Observations)

    # 3) More than 1 connection - select connections with bearing within 45 degrees.
    if len(Observations.__dict__.keys()) > 1:
        FinalConnectionFilter = FinalFilter(traverse, LandXML_Obj.TraverseProps)
        Observations =  FinalConnectionFilter.SimilarBearingConnection(Observations)
    # 4) if still more than one connection (or no connections) select shortest connection
    if len(Observations.__dict__.keys()) > 1:
        Observations = FinalConnectionFilter.FilterByDistance(Observations)


    #return connection
    for key in Observations.__dict__.keys():
        return Observations.__getattribute__(key)
    
def RemoveNonRM_Connections(Observations, traverse, LandXML_Obj, PntRefNum):
    '''
    Removes connections that are not between RMs
    Prioritises BDY connections for enbd point of tested connection (If still applicable)
    :return: 
    '''
    #list of connections to delete
    RemoveObs = []
    #loop through connections
    for key in Observations.__dict__.keys():
        connection = Observations.__getattribute__(key)
        
        #get point ref numbers of connection
        SetupID = connection.get("setupID").replace(LandXML_Obj.TraverseProps.tag, "")
        TargetSetupID = connection.get("targetSetupID").replace(LandXML_Obj.TraverseProps.tag, "")
        # get end point of connection
        if SetupID == PntRefNum:
            EndRefNum =  TargetSetupID
        else:
            EndRefNum = SetupID

        #check if EndPoint is an RM
        if not RefMarkQueries.CheckIfRefMark(LandXML_Obj, EndRefNum):
            RemoveObs.append(key)
            continue

        #remove dead traverses
        if DeadEndConnection(EndRefNum, LandXML_Obj) and LandXML_Obj.TraverseProps.TraverseClose:
            RemoveObs.append(key)
            continue
            
    #if Observations were found to delete remove them
    if len(RemoveObs) > 0:
        Observations = Connections.RemoveSelectedConnections(Observations, RemoveObs)

    return Observations

def DeadEndConnection(PntRefNum, LandXML_Obj):
    '''
    Checks if PntRefNum is a dead end
    :param PntRefNum: Point to query (Point number from LandXML)
    :param LandXML_Obj: LadnXML data object
    :return:
    '''
    #Find all connections to PntRefNum - has one connection iof its a dead end
    Observations = Connections.AllConnections(PntRefNum, LandXML_Obj)
    if len(Observations.__dict__.keys()) == 1:
        return True
    return False


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
        if len(ConnectionList.__dict__.keys()) > len(Observations.__dict__.keys()):
            Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations

    def FindLastConnectionBearing(self):
        '''
        Finds the bearing of last connection in the traverse
        :return:
        '''
        StartRefNum = traverse.refPnts[-2]
        EndRefNum = traverse.refPnts[-1]
        #get line bearing of lasat connection
        for key in traverse.Lines.__dict__.keys():
            Line = traverse.Lines.__getatttribute(key)
            if Line.StartRef == StartRefNum and Line.EndRef == EndRefNum:
                return float(Line.bearing), EndRefNum

    def ConnectionsWithinBearing(self, LastBearing, Connections, PntRefNum):
        '''
        Finds the connections in Connections object that are within 45 degrees
            of LastBearing
        :param LastBearing: Bearing of last connection in traverese
        :param Connections: Set of Connections from LandXML to query
        :param PntRefNum: Starting point reference of all connections to be queried
        :return: ConnectionList (List of connections that pass query)
        '''

        #Create a list to store connections to remove - only when 1 or more connections pass
            #bearing query
        ConnectionList = []
        #Loop through connections and check if their bearings are within 45 degrees
        for key in Connections.__dict__.keys():
            connection = Connections.__getattribute__(key)
            #Get connections bearing - normalised to same orientation as lat traverse connection
                #that is setupiD (Last connection) = TargetID (queried connection)
            if connection.get("setupID").replace(self.Traverse_Props.tag, "") == PntRefNum:
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


    
    