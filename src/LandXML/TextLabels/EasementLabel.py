'''
Gets labels for Easements
One label of its identifier is display at centre coord
'''

import CadastreClasses as DataObjects


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
            CentroidObj = Parcel.find(self.TraverseProps.Namespace + "Center")
            PntRefNum = CentroidObj.get("pntRef")
            LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(PntRefNum)
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

            # create label object and add to CadastralPlan
            LabelObj = DataObjects.LabelObj(TextStr, LabelEasting, LabelNorthing,
                                            NorthingScreen, 0, "Easement")

            LabelName = parcel.get("name")
            setattr(self.CadastralPlan.Labels, LabelName, LabelObj)
        except AttributeError:
            pass