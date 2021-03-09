'''
Methods and workflow to calculate new points from a connection selected from the LandXMl
Adds linework (calcs for arcs)
Adds traverse side to current traverse and gui
'''
import genericFunctions as funcs
class TraverseSide:

    def __init__(self, PntRefNum, traverse, Connection, gui):
        '''
        Initialise class attributes
        :param PntRefNum: RefNum for start of traverse side
        :param traverse: traverse data object
        :param Connection: Connection to be added
        :param gui:
        '''
        self.PntRefNum = PntRefNum
        self.traverse = traverse
        self.Connection = Connection
        self.gui = gui

    def CalcPointCoordsWorkflow(self):
        '''
        Calculates the coordinates of the point at the end of the connection
        :return:
        '''
        self.ConnectionBearing()
        self.ConnectionDistance()
        self.CalcPointChords()


    def ConnectionBearing(self):
        '''
        return connection bearing from landXML element
        Accounts for chord attributes of Arcs
        :return: bearing
        '''
        try:
            self.bearing = self.Connection.get("azimuth")
        except AttributeError:
            self.bearing = self.Connection.get("chordAzimuth")

    def ConnectionDistance(self):
        '''
        return connection distance from landXML element
        Accounts for chord attributes of Arcs
        :return: distance
        '''
        try:
            self.distance = self.Connection.get("horizDistance")
        except AttributeError:
            arcLength = self.Connection.get("length")
            self.radius = self.Connection.get("radius")
            self.rotation = self.Connection.get("rot")
            self.distance = self.CalcChordLength(arcLength)

    def CalcChordLength(self, arcLength):
        '''
        LandXML provides the arc length for an arc connection
        This functions calculated the chord length from the arc length and radius
        :param arcLength: length of arc segeent
        :return: chord length - distance
        '''
        distance = 2 * self.radius * np.sin(arcLength / (2 * self.radius))
        return distance

    def CalcPointCoords(self):
        '''
        Calculates the coordinates of the new point
        creates attributes for their E and N
        '''
        #convert bearing to decimal
        bearing = funcs.bearing2_dec(self.bearing)

        #calc Easting, northing
    def AddPoint2Traverse(self):

    def AddPoint2GUI(self):

    def AddLine2Traverse(self):
    def AddLine2GUI(self):
    def ArcCalcs(self):
    def AddArc2GUI(self):
    def AddLineBearingDistance2GUI(self):