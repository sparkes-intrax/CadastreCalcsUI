'''
Gets labels for Easements
One label of its identifier is display at centre coord
'''

import CadastreClasses as DataObjects
from numpy import mean


class EasementParcelLabel:
    def __init__(self, CadastralPlan, Parcels, LandXML_Obj):

        self.CadastralPlan = CadastralPlan
        self.Parcels = Parcels
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps

        self.GetParcelLabels()

    def GetParcelLabels(self):
        '''
        Loops through parcels in LandXML parcels and finds the proposed lots
        :return:
        '''
        # Loop through parcels in landXML file
        ##Loop through Easements to calculate
        for Parcel in self.LandXML_Obj.EasementParcels:
            try:
                CentroidObj = Parcel.find(self.TraverseProps.Namespace + "Center")
                PntRefNum = CentroidObj.get("pntRef")
                LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(PntRefNum)
                self.LabelInstance(LabelEasting, LabelNorthing, NorthingScreen, Parcel)
            except AttributeError:
                LabelEasting, LabelNorthing, NorthingScreen = self.LabelCoordinatesFromVertexes(Parcel)
                if LabelEasting is not None:
                    self.LabelInstance(LabelEasting, LabelNorthing, NorthingScreen, Parcel)



    def GetPointCoordinates(self, PntRefNum):
        '''
        Retrives the coordnates for the lot centroid
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

    def LabelCoordinatesFromVertexes(self, Parcel):
        '''
        Uses parcel vertexes and their coordinates to calculate centre of easemnt
        :param Parcel:
        :return:
        '''

        lines = Parcel.find(self.LandXML_Obj.TraverseProps.Namespace + "CoordGeom")
        # loop through line to check vertexes
        E = []
        N = []
        N_Screen = []
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "Start").get("pntRef")
                if hasattr(self.CadastralPlan.Points, startRef):
                    Easting, Northing, Screen = self.GetPointCoordinates(startRef)
                    E.append(Easting)
                    N.append(Northing)
                    N_Screen.append(Screen)

        if len(E) > 0:
            return mean(E), mean(N), mean(N_Screen)
        else:
            return None, None, None

    def LabelInstance(self, LabelEasting, LabelNorthing, NorthingScreen, parcel):
        '''
        Creates a label instance and adds it to CadastralPlan
        :param LabelEasting:
        :param LabelNorthing:
        :param parcel:
        :return:
        '''

        # create string for label
        try:
            TextStr = parcel.get("desc").split(" ")[0]
            if TextStr.__contains__("(") and TextStr.__contains__(")"):

                # create label object and add to CadastralPlan
                LabelObj = DataObjects.LabelObj(TextStr, LabelEasting, LabelNorthing,
                                                NorthingScreen, 0, "Easement")

                LabelName = parcel.get("name")
                setattr(self.CadastralPlan.Labels, LabelName, LabelObj)
        except AttributeError:
            pass