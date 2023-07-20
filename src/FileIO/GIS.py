'''
Creates a geojson file containing a polygon for each lot
and the centre point for each lot
- polygon and point features

'''

import json, requests
from geojson import Point, Polygon, Feature, FeatureCollection, dump
from pyproj import Proj, transform#, compat, _compat
from LandXML.TextLabels import ParcelCentrePoint


def main(CadastralPlan, file):
    '''
    Interacts with GisFiles instance to write to geojson file
    :param CadastralPlan:
    :return:
    '''

    GisFilesObj = GisFiles(CadastralPlan, file)
    GisFilesObj.CreateGeoJsonElement()

class GisFiles:

    def __init__(self, CadastralPlan, file):
        '''
        Writes parcels and their coordinates
        :param CadastralPlan:
        :return:
        '''
        self.CadastralPlan = CadastralPlan
        self.Parcels = CadastralPlan.Parcels
        self.file = file + ".geojson"
        self.Features = [] #list to store parcel features

    def CreateGeoJsonElement(self):
        '''
        Loop through parcels
        Convert calculated coordinates to lat/lon
        :return:
        '''
        #Load geojson for writing
        #with open(self.file) as f:
        #    data = json.load(f)
        #self.Features = data["features"]

        for parcel in self.Parcels:
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")
            if (parcelClass == "Lot" and parcelState == "proposed"):
                self.CreateFeature(parcel)

        #Write Geometry Collection
        collection  = FeatureCollection(self.Features)
        
        with open(self.file, "w") as f:
            dump(collection, f)

    def CreateFeature(self, parcel):
        '''
        Creates a feature element for each
        :return:
        '''

        # get lines out of parcel
        lines = parcel.find(self.CadastralPlan.PlanAdmin.Namespace + "CoordGeom")
        #List to store coordinate of polygon
        Coords = []
        # loop through line to check vertexes
        if lines != None:
            #write polygon
            for line in lines.getchildren():
                startRef = line.find(self.CadastralPlan.PlanAdmin.Namespace + "Start").get("pntRef")
                try:
                    Coords.append(self.GetPlanCoords(startRef))
                except AttributeError:
                    pass

            Coords.append(Coords[0])
            PolygonObj = Polygon([Coords])
            #Get lot properties
            Properties = {"Lot": parcel.get("name")}
            self.Features.append(Feature(geometry=PolygonObj, properties=Properties))

            #Write centre Point
            Coords = self.GetLxmlCoords(parcel)
            PointObj = Point(Coords)
            Properties = self.GetLotProperties(parcel)
            self.Features.append(Feature(geometry=PointObj, properties=Properties))

    def GetPlanCoords(self, PntRefNum):
        # get PointObj for PntRefNUm and retrieve coordinates
        PointObj = self.CadastralPlan.Points.__getattribute__(PntRefNum)
        Easting = PointObj.E
        Northing = PointObj.N

        Coord = self.convertCoords(Easting, Northing)

        return Coord

    def GetLxmlCoords(self,parcel):
        '''
        Get point coordinates from LandXML
        Coordinates converted to lat/lon and stored as a tuple
        :param Point:
        :return:
        '''
        try: #for common cas where LandXML has a center ref
            CentrePointRef = parcel.find(self.CadastralPlan.PlanAdmin.Namespace + "Center").get("pntRef")
            Query = "//CgPoint[@name='" + CentrePointRef + "']"
            # get CgPoint
            Point = self.CadastralPlan.lxml.findall(Query, self.CadastralPlan.lxml.getroot().nsmap)[0]
            Easting = float(Point.text.split(" ")[1])
            Northing = float(Point.text.split(" ")[0])
        except AttributeError: # when the no center point ref for parcels
            Easting, Northing, NorthingScreen = ParcelCentrePoint.main(parcel, self.CadastralPlan,
                                                                       self.CadastralPlan.LandXML_Obj)
            
        Coord = self.convertCoords(Easting, Northing)

        return Coord



    def convertCoords(self, Easting, Northing):
        '''
        Converts East/North from CRSin to CRS
        :param East:
        :param North:
        :param CRSin:
        :return:
        '''

        inProj = Proj('epsg:28356')
        outProj = Proj('epsg:4326')
        Lon, Lat = transform(inProj, outProj, Easting, Northing, always_xy=True)

        return (Lon, Lat)

    def GetLotProperties(self, parcel):
        '''
        Creates a json styled property list for parcel
        :param parcel:
        :return:
        '''
        try:
            properties = {"Lot" : parcel.get("name"),
                          "Area" : parcel.get("area") + "m2",
                          "Plan" : self.CadastralPlan.PlanAdmin.DP,
                          "LGA" : self.CadastralPlan.PlanAdmin.__getattribute__("Local Government Area"),
                          "Registration Date" : self.CadastralPlan.PlanAdmin.__getattribute__("Registration Date")}
        except AttributeError:
            properties = {"Lot": parcel.get("name"),
                          "Area": parcel.get("area") + "m2",
                          "Plan": self.CadastralPlan.PlanAdmin.DP,
                          "LGA": self.CadastralPlan.PlanAdmin.__getattribute__("Local Government Area")}
        return properties