'''
Filters data based on Bearing and distance
When all other prioritising filters fail to select a single Observation
'''
from LandXML import Connections
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

        # Check if first connection
        if len(self.traverse.refPnts) == 1:
            return Observations

        # get bearing of last connection
        LastBearing, EndRefNum = self.FindLastConnectionBearing()
        # Find Observations within 45 degrees of LastBearing
        ConnectionList = self.ObservationsWithinBearing(LastBearing, Observations, EndRefNum)
        # if find Observations within 45 degrees, delete other bearings
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
        # get line bearing of lasat connection
        for key in self.traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            Line = self.traverse.Lines.__getattribute__(key)
            if Line.StartRef == StartRefNum and Line.EndRef == EndRefNum:
                return float(Line.Bearing), EndRefNum

    def ObservationsWithinBearing(self, LastBearing, Observations, PntRefNum):
        '''
        Finds the Observation in Observations object that are within 45 degrees
            of LastBearing
        :param LastBearing: Bearing of last connection in traverese
        :param Observations: Set of Observations from LandXML to query
        :param PntRefNum: Starting point reference of all Observations to be queried
        :return: ConnectionList (List of Observations that pass query)
        '''

        # Create a list to store Observations to remove - only when 1 or more Observations pass
        # bearing query
        ConnectionList = []
        # Loop through Observations and check if their bearings are within 45 degrees
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            # Get Observations bearing - normalised to same orientation as lat traverse connection
            # that is setupiD (Last connection) = TargetID (queried connection)

            if connection.get("setupID").replace(self.TraverseProps.tag, "") == PntRefNum:
                azimuth = float(Connections.GetObservationAzimuth(connection))
            else:
                azimuth = self.FlipBearing(float(Connections.GetObservationAzimuth(connection)))

            # test of bearing with 45 degrees
            if abs(LastBearing - azimuth) > 60:
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
        # Loop through Observations
        for key in Observations.__dict__.keys():
            connection = Observations.__getattribute__(key)
            distance = float(Connections.GetObservationDistance(connection))
            if distance < ShortestDistance:
                KeepConnection = key
                ShortestDistance = distance

        # delete all but shortest side
        for key in Observations.__dict__.keys():
            if key != KeepConnection:
                ConnectionList.append(key)
        Observations = Connections.RemoveSelectedConnections(Observations, ConnectionList)

        return Observations