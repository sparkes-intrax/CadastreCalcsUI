'''
Methods for Points
'''

import genericFunctions as funcs
import CadastreClasses as DataObjects
from LandXML.RefMarks import RefMarkQueries
from LandXML import BDY_Connections
from numpy import sin, cos, radians

class Points:
    def __init__(self, LandXML_Obj, Points):
        self.LandXML_Obj = LandXML_Obj
        self.Points = Points
        
    def CalcPoints(self, bearingDMS, distance, 
                   PntRefNum, TargetID, Observation):
        '''
        Calculates the coordinates of the new point
        creates attributes for their E and N
        '''
        
        self.PntRefNum = PntRefNum
        #get point Code
        Code = RefMarkQueries.GetPointCode(self.LandXML_Obj, TargetID)
        if Code == "RMDH&W":
            Code = "RMDHW"
            
        #Check Elevation
        if RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, TargetID):
            self.Elevation = self.CheckElevation(TargetID)
        else:
            self.Elevation = None
            
        #convert bearing to decimal
        bearing = funcs.bearing2_dec(bearingDMS)
        #Return angle for point calculate and its sign for Easting and Northing
        angle, deltaE, deltaN = funcs.bearing2angle(bearing)
        # calculate change in coordinates
        try:
            self.deltaE = float(distance) * sin(radians(angle)) * deltaE
            self.deltaN = float(distance) * cos(radians(angle)) * deltaN
        except:
            pass
        #get source point object from traverse object
        SrcPoint = self.Points.__getattribute__(self.PntRefNum)
        #calculate new coordinates
        self.E = float(SrcPoint.E) + self.deltaE
        self.N = float(SrcPoint.N) + self.deltaN
        self.N_Screen = float(SrcPoint.NorthingScreen) - self.deltaN
        Layer = self.EndPointType(TargetID, Observation)

        # create new point object
        point = DataObjects.Point(TargetID, self.E, self.N, self.N_Screen,
                                  self.Elevation, Code, Layer)
        
        return point

    def EndPointType(self, TargetID, Observation):
        '''
        Determines the type of point
        :return:
        '''

        desc = Observation.get("desc")
        if self.CheckIfBoundary(TargetID):
            return "BOUNDARY"
        elif RefMarkQueries.CheckIfMonument(self.LandXML_Obj, TargetID.split("_")[0]):
            return "REFERENCE MARKS"
        elif desc == "Connection" or desc == "Road Extent" or desc == "IrregularLine" or \
                desc == "Road":
            return "BOUNDARY"
        else:
            return "EASEMENT"

    def CheckIfBoundary(self, TargetID):
        '''
        checks if end point is a boundary - for layer determination
        :return:
        '''

        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)
        # Loop through parcels in landXML file
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")

            if parcelClass != "Easement" or parcelClass != "Restriction On Use Of Land" or \
                    parcelClass != "Designated Area":
                if ConnectionChecker.CheckParcelLines(parcel, TargetID.split("_")[0],
                                                      self.LandXML_Obj.TraverseProps):
                    return True

        return False
    

    def StartPointObj(self, PntRefNum):
        point = self.Points.__getattribute__(PntRefNum)
        self.PntRefNum = PntRefNum
        self.Code = point.Code
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Layer = point.Layer

    def CheckElevation(self, PntRefNum):
        '''
        Checks if a vertical observation coorepsonds to Target
        :return:
        '''

        ObsID = self.LandXML_Obj.TraverseProps.tag + PntRefNum
        ns = self.LandXML_Obj.lxml.getroot().nsmap

        # Reduced Observations
        tag = "//RedVerticalObservation"
        Query = tag + "[@setupID='" + ObsID + "']"
        Observations = self.LandXML_Obj.lxml.findall(Query, ns)

        if len(Observations) > 0:
            Elevation = Observations[0].get("height")
            try:
                if Elevation is None:
                    return None
                else:
                    return float(Elevation)
            except IndexError:
                return None
        else:
            return None