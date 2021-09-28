'''
Creates label instances in CadastralPlan
'''

import CadastreClasses as DataObjects
from LandXML.TextLabels import ParcelCentrePoint

class LotParcelLabel:
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
        #Loop through parcels in landXML file
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")
            #check if a proposed parcel from subdivision
            if (parcelClass == "Lot" and parcelState == "proposed"):
                try:
                    CentroidObj = parcel.find(self.TraverseProps.Namespace+"Center")
                    PntRefNum = CentroidObj.get("pntRef")
                    LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(PntRefNum)
                    self.LabelInstance(LabelEasting, LabelNorthing, NorthingScreen, parcel)
                except AttributeError:
                    LabelEasting, LabelNorthing, NorthingScreen = ParcelCentrePoint.main(parcel,
                                                                                self.CadastralPlan,
                                                                                self.LandXML_Obj)
                self.LabelInstance(LabelEasting, LabelNorthing, NorthingScreen, parcel)
                
    def GetPointCoordinates(self, PntRefNum):
        '''
        Retrives the coordnates for the lot centroid
        :param PntRefNum: 
        :return: 
        '''
        
        #set up point query
        ns = self.LandXML_Obj.lxml.getroot().nsmap
        Query = "//CgPoint[@name='" + PntRefNum + "']"
        #get CgPoint
        Point = self.LandXML_Obj.lxml.findall(Query, ns)[0]
        #Retrieve coordinates
        Easting = float(Point.text.split(" ")[1])
        Northing = float(Point.text.split(" ")[0])

        #Calculate screen coordinates for drawing canvas
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
        
        #Lot area
        Area = float(parcel.get("area"))
        Area = round(Area,1)
        Area = str(Area)
        
        #create string for label
        TextStr = "Lot " + parcel.get("name") + "\n"
        TextStr += Area + " m2\n"
        if self.LandXML_Obj.PlanAdmin.DP[0:2] == "DP":
            TextStr += self.LandXML_Obj.PlanAdmin.DP
        else:
            TextStr += "DP" + self.LandXML_Obj.PlanAdmin.DP
        
        #create label object and add to CadastralPlan
        LabelObj = DataObjects.LabelObj(TextStr, LabelEasting, LabelNorthing,
                                        NorthingScreen, 0, "Parcel")
        
        LabelName = "Lot" + parcel.get("name")
        setattr(self.CadastralPlan.Labels, LabelName, LabelObj)
        
