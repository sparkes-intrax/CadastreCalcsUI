'''
When parcels in LandXML do not include a centre point reference
 - Application name="GeoCadastre" version="5.81"
'''
import numpy as np
def main(parcel, CadastralPlan, LandXML_Obj):
    '''
    loop s through lines in parcel and gets coordinates of all vertexes
    - calculates mean coordinates fir centre point
    :param parcel:
    :return: Centre coordinates of parcel
    '''
    
    ParcelCentroidObj = ParcelCentroid(parcel, CadastralPlan, LandXML_Obj)
    CentreEasting, CentreNorthing, CentreNorthingScreen = ParcelCentroidObj.GetParcelCentroid()
    
    return CentreEasting, CentreNorthing, CentreNorthingScreen

    

class ParcelCentroid:
    def __init__(self, parcel, CadastralPlan, LandXML_Obj):
        self.parcel = parcel
        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.Easting = []
        self.Northing = []
        self.NorthingScreen = []

    def GetParcelCentroid(self):
        '''
        Loops through parcel lines to retrieve vertexes
        :return:
        '''

        self.GetVertexCoords()
        CentreEasting = np.mean(self.Easting)
        CentreNorthing = np.mean(self.Northing)
        CentreNorthingScreen = np.mean(self.NorthingScreen)

        return CentreEasting, CentreNorthing, CentreNorthingScreen

    def GetVertexCoords(self):
        # get lines out of parcel
        lines = self.parcel.find(self.TraverseProps.Namespace + "CoordGeom")
        # loop through line to check vertexes
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.TraverseProps.Namespace + "Start").get("pntRef")
                Easting, Northing, NorthingScreen = self.GetPointCoords(startRef)
                self.Easting.append(Easting)
                self.Northing.append(Northing)
                self.NorthingScreen.append(NorthingScreen)

    def GetPointCoords(self, PntRefNum):
        '''
        retrieves the coordinates for PntRefNum from landXML
        :param PntRefNum:
        :return:
        '''
        # set up point query
        ns = self.LandXML_Obj.lxml.getroot().nsmap
        Query = "//CgPoint[@name='" + PntRefNum + "']"
        # get CgPoint
        Point = self.LandXML_Obj.lxml.findall(Query, ns)[0]
        # Retrieve coordinates
        Easting = float(Point.text.split(" ")[1])
        Northing = float(Point.text.split(" ")[0])

        # Calculate screen coordinates for drawing canvas
        DistToOrigin = Northing - self.CadastralPlan.NorthOrigin
        NorthingScreen = self.CadastralPlan.NorthOrigin - DistToOrigin

        return Easting, Northing, NorthingScreen
