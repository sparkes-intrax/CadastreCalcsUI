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
        self.Lines = Lines()
        #self.Arcs = Arcs()
        self.Polygons = Polygons()
        self.Labels = Labels()
        self.Traverses = Traverses()

#set up geometry classes
class Points(object):
    '''
    parent class to store point objects
    '''
    pass

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
    def __init__(self, StartRef, EndRef, Layer, radius, centreEast, centreNorth,
                 rotation, distance, bearing, deltaE, deltaN, Colour):
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
        self.CentreEast = centreEast
        self.CentreNorth = centreNorth
        self.Rotation = rotation
        self.Distance = distance
        self.Bearing = bearing
        self.BoundingRect = None
        self.GraphicsItems = TraverseGraphItem()
        self.Colour = Colour
        self.deltaE = deltaE  # these are adjusted during traverse adjustment and used to calc line distances
        self.deltaN = deltaN

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
    def __init__(self, textStr, easting, northing, orientation):
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
        self.Orientation = orientation


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
        #self.Arcs = Arcs()
        self.RemovedLines = Lines()
        self.type = type
        self.refPnts = []
        self.StartRefPnt = None
        self.EndRefPnt = None
        self.SetupPoint = None
        self.FirstTraverse = FirstTraverse
        self.NumPoints = None
        self.Distance = None
        self.Close_PreAdjust = None
        self.Close_PostAdjust = None
        self.Branches = None



