'''
Gets road labels and position and aligns them
'''

import CadastreClasses as DataObjects
import genericFunctions as funcs
import numpy as np
from lxml import etree
from LandXML import BDY_Connections



class RoadParcelLabel:
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
        for parcel in self.Parcels:
            #if not self.ProposedParcelConnection(parcel):
            #    continue
            CentroidObj = parcel.find(self.TraverseProps.Namespace + "Center")
            try:
                PntRefNum = CentroidObj.get("pntRef")
                LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(PntRefNum)
            except AttributeError:
                LabelEasting, LabelNorthing, NorthingScreen = self.FindRoadLabelCoordinate(parcel)

            Bearing = self.CalculateRoadLabelRotation(parcel)
            self.LabelInstance(LabelEasting, LabelNorthing, NorthingScreen, parcel, Bearing)

    def ProposedParcelConnection(self, parcel):
        '''
        Checks if road is frontage to at least one parcel from proposed subdivision
        :param parcel:
        :return:
        '''

        lines = parcel.find(self.TraverseProps.Namespace + "CoordGeom")
        for line in lines.getchildren():

            startRef = line.find(self.TraverseProps.Namespace + "Start").get("pntRef")
            endRef = line.find(self.TraverseProps.Namespace + "End").get("pntRef")

            for LotParcel in self.LandXML_Obj.Parcels.getchildren():
                parcelClass = LotParcel.get("class")
                parcelState = LotParcel.get("state")
                if (parcelClass == "Lot" and parcelState == "proposed"):
                    BdyObj = BDY_Connections.CheckBdyConnection(startRef, self.LandXML_Obj)
                    if BdyObj.CheckParcelLines(LotParcel, startRef, self.LandXML_Obj.TraverseProps) and \
                        BdyObj.CheckParcelLines(LotParcel, endRef, self.LandXML_Obj.TraverseProps):
                        return True



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

    def FindRoadLabelCoordinate(self, parcel):
        '''
        When no road parcel centroid available
        :param parcel:
        :return:
        '''

        lines = parcel.find(self.TraverseProps.Namespace + "CoordGeom")
        for line in lines.getchildren():

            startRef = line.find(self.TraverseProps.Namespace + "Start").get("pntRef")
            LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(startRef)
            break

        return LabelEasting, LabelNorthing, NorthingScreen

    def CalculateRoadLabelRotation(self, parcel):
        '''
        Calculates the rotation of the road label
        Uses max and min easting and northing to assign rotation
        :param parcel:
        :return:
        '''

        lines = parcel.find(self.TraverseProps.Namespace + "CoordGeom")
        maxDist = 0
        LabelBearing = None
        for line in lines.getchildren():

            startRef = line.find(self.TraverseProps.Namespace + "Start").get("pntRef")
            endRef = line.find(self.TraverseProps.Namespace + "End").get("pntRef")
            distance, bearing = self.FindConnection(startRef, endRef)
            if distance is not None and distance > maxDist:
                LabelBearing = bearing
                maxDist = distance

        return LabelBearing

    def FindConnection(self, StartRef, EndRef):
        '''
        Funds connection matching startRef to endRef
        returns connections bearing and distance
        :param StartRef:
        :param EndRef:
        :return:
        '''
        lxml = etree.parse(self.CadastralPlan.LandXmlFile)
        #get connections containing STart and EnddRef
        StartID = self.TraverseProps.tag + StartRef
        EndID = self.TraverseProps.tag + EndRef
        ns = lxml.getroot().nsmap

        #Reduced Observations
        tag = "//ReducedObservation"
        Query1 = tag + "[@setupID='" + StartID + "']"
        Query2 = tag + "[@targetSetupID='" + StartID + "']"
        Query3 = tag + "[@setupID='" + EndID + "']"
        Query4 = tag + "[@targetSetupID='" + EndID + "']"
        Observations = lxml.findall(Query1, ns) + lxml.findall(Query2, ns) + \
                       lxml.findall(Query3, ns) + \
                       lxml.findall(Query4, ns)

        #Check if any match end Ref to start ref
        for Obs in Observations:
            SetupID = Obs.get("setupID").replace(self.TraverseProps.tag, "")
            TargetID = Obs.get("targetSetupID").replace(self.TraverseProps.tag, "")
            if (SetupID == StartRef and TargetID == EndRef) or \
                    (SetupID == EndRef and TargetID == StartRef):
                return float(Obs.get("horizDistance")), funcs.bearing2_dec(Obs.get("azimuth"))

        return None, None
        
    def GetRotation(self, deltaE, deltaN):
        '''
        Calculates rotation for display and dxf
        :param deltaE: 
        :param deltaN: 
        :return: 
        '''
        
        angle = np.degrees(np.arctan(abs(deltaN)/abs(deltaE)))
        bearing = funcs.Angle2Bearing(angle, deltaE, deltaN)
        return bearing

    def LabelInstance(self, LabelEasting, LabelNorthing, NorthingScreen, parcel, Bearing):
        '''
        Creates a label instance and adds it to CadastralPlan
        :param LabelEasting:
        :param LabelNorthing:
        :param parcel:
        :return:
        '''

        # create string for label
        TextStr = parcel.get("desc")

        # create label object and add to CadastralPlan
        if Bearing is None:
            LabelObj = DataObjects.LabelObj(TextStr, LabelEasting, LabelNorthing,
                                        NorthingScreen, 0, "Road")
        else:
            LabelObj = DataObjects.LabelObj(TextStr, LabelEasting, LabelNorthing,
                                            NorthingScreen, Bearing, "Road")

        LabelName = parcel.get("name")
        setattr(self.CadastralPlan.Labels, LabelName, LabelObj)