'''
Set of classes to store cadstral information
- Points
- Lines
- Arcs
- Polygons - Including lot, easement ad road info
- Text
'''

class CadastralPlan:

    def __init__(self):
        '''
        Parent Class that owns all cadastral data

        '''

        self.Points = Points()
        self.PointsRaw = Points()
        self.Lines = Lines()
        self.LinesRaw = Lines()
        #self.Arcs = Arcs()
        self.Polygons = Polygons()
        self.Labels = Labels()
        self.Traverses = Traverses()
        self.TriedConnections = Lines()

#set up geometry classes
class Points:
    '''
    parent class to store point objects
    '''
    def __init__(self):
        #If all connections to a point have been calc'd - they are removed from list
        self.PointList = []

class Point:
    def __init__(self, PntNum, Easting, Northing, NorthingScreen, Elevation, Code, Layer):
        '''
        point object to store coordinates, layer etc
        spatial data used by lines and arcs etc
        :param NorthingScreen: Is the Northing coordinates for the scene object. Northing coordinates are
                                flipped in the the display
        '''
        self.PntNum = PntNum
        self.E = float(Easting)
        self.N = float(Northing)
        self.NorthingScreen = float(NorthingScreen)
        self.Elev = Elevation
        self.Code = Code
        self.Layer = Layer
        self.BoundingRect = None
        self.GraphicsItems = TraverseGraphItem()

class Lines:

    '''
    parent class to store line objects
    '''
    def __init__(self):
        self.LineNum = 0

class Line():
    def __init__(self, StartRef, EndRef, Layer, distance, deltaE, deltaN, bearing, Colour):
        '''
        Line object to store refpoints for start and end of line - and layer of line
        - refpoints reference Points
        :param StartRef:
        :param EndRef:
        :param Layer:
        '''

        self.type = "Line"
        self.StartRef = StartRef
        self.EndRef = EndRef
        self.Layer = Layer
        self.Distance = distance
        self.deltaE = deltaE #these are adjusted during traverse adjustment and used to calc line distances
        self.deltaN = deltaN
        self.Bearing = bearing
        self.BoundingRect = None
        self.Colour = Colour
        self.GraphicsItems = TraverseGraphItem()


class Arcs:
    '''
    parent class to store arc objects
    '''

    def __init__(self):
        self.ArcNum = 0

class Arc():
    def __init__(self, StartRef, EndRef, Layer, radius, centreCoords,
                 rotation, distance, bearing, deltaE, deltaN, Colour,
                 ArcAngles):
        '''
        Line object to store refpoints for start and end of line - and layer of line
        - refpoints reference Points
        :param StartRef:
        :param EndRef:
        :param Layer:
        '''

        self.type = "Arc"
        self.StartRef = StartRef
        self.EndRef = EndRef
        self.Layer = Layer
        self.Radius = radius
        self.CentreCoords = centreCoords
        self.Rotation = rotation
        self.Distance = distance
        self.Bearing = bearing
        self.BoundingRect = None
        self.GraphicsItems = TraverseGraphItem()
        self.Colour = Colour
        self.deltaE = deltaE  # these are adjusted during traverse adjustment and used to calc line distances
        self.deltaN = deltaN
        self.ArcAngles = ArcAngles

class Polygons(object):
    '''
    Parent class to store polygon objects
    '''
    pass

class Polygon():
    def __init__(self, PlanNumber, LotNum, AreaDP, AreaCalc,
                 description, PolyType, refPntList, CentreEasting, CentreNorthing,
                 CentreNorthingScreen):
        '''
        Stores polygon entities and relevant info
        - are saved as polylines in dxf
        :param description:
        :param area:
        :param layer:
        :param refPntList: list of reference numbers defining polygon
        '''

        self.PlanNumber = PlanNumber
        self.LotNum = LotNum
        self.AreaDp = AreaDP
        self.AreaCalc = AreaCalc
        self.Description = description
        self.PolyType = PolyType
        self.RefPntList = refPntList
        self.CentreEasting = CentreEasting
        self.CentreNorthing = CentreNorthing
        self.CentreNorthingScreen = CentreNorthingScreen
        self.VertexEastings = None
        self.VertexNorthings = None
        self.VertexNorthingsScreen = None

class Labels(object):
    '''
    parent class for labels
    '''
    pass

class LabelObj():
    def __init__(self, textStr, easting, northing, NorthingScreen, 
                 orientation, ParcelType):
        '''
        stores text entities, their location and orientation
        :param textStr:
        :param easting:
        :param northing:
        :param orientation:
        '''

        self.Label = textStr
        self.Easting = easting
        self.Northing = northing
        self.NorthingScreen = NorthingScreen
        self.Orientation = orientation
        self.ParcelType = ParcelType


#Traverse objects - adds different traverse instances
class Traverses(object):

    def __init__(self):
        '''
        Set up File object and attributes
        '''

        self.TraverseCounter = 1

class TraverseGraphItem(object):
    pass

class Traverse():
    def __init__(self, FirstTraverse, type):
        '''
        Empty Traverse Object
        '''

        self.Points = Points()
        self.Lines = Lines()
        self.PointsRaw = Points()
        self.LinesRaw = Lines()
        #self.Arcs = Arcs()
        self.TriedConnections = Lines()
        self.type = type
        self.refPnts = []
        self.refPntsRaw = []
        self.StartRefPnt = None
        self.EndRefPnt = None
        self.FirstTraverse = FirstTraverse
        self.NumPoints = None
        self.Distance = 0
        self.Close_PreAdjust = None
        self.Close_PostAdjust = None
        self.PrimaryBranches = [] #branches in traverse of traverse type
        self.SecondaryBranches = [] #branches of other type (ie BDYs in RM traverse
        self.NonRmBranches = [] #only relevant for RM traverse
        self.Observations = []
        self.Closed = False
        self.Adjusted = False
        self.LineNum = 1
        self.MixedTraverse = False



