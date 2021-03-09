'''
Workflow for finding a point ot start a RefMark from
'''
from LandXML import BDY_Connections, Coordinates, Connections
from LandXML.RefMarks import RefMarkQueries

class TraverseStart:
    def __init__(self, LandXML_Obj, FirstTraverse):
        '''
        Finds a suitable starting point for a traverse
        Adds PntRefNUm, Easting, Northing and code attributes if found
        :param LandXML_Obj:
        '''

        #If first traverse Check if control point A is connected to BDY
        self.PntRefNum = None

        if FirstTraverse:
            self.CheckSurveyOrigin(LandXML_Obj)

            #if survey origin doesn't have a bdy connection find any RM with BDY connection
            if self.PntRefNum is None:
                self.BdyConnectionStart(LandXML_Obj)

    def CheckSurveyOrigin(self, LandXML_Obj):
        '''
        Checks survey origin if it is connected to a BDY
        if not skips and return PntRefNum
        :param LandXML_obj:
        :return:
        '''
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, LandXML_Obj)

        #Loop through coordinate points and finds the survey origin
        for point in LandXML_Obj.Coordinates.getchildren():
            if point.get("desc") == "A" and point.get("pntSurv") == "control":
                Observations = Connections.AllConnections(point.get("name"), LandXML_Obj)
                setattr(ConnectionChecker, "PntRefNum", point.get("name"))
                if ConnectionChecker.FindBdyConnection(Observations):
                    self.PntRefNum = point.get("name")
                    self.Code = "RM" + RefMarkQueries.FindMarkType(LandXML_Obj, self.PntRefNum) + "-" + \
                                point.get("oID")
                    self.Easting, self.Northing = Coordinates.getPointCoords(self.PntRefNum, LandXML_Obj)
                    break
    
    def BdyConnectionStart(self, LandXML_Obj):
        '''
        find a reference mark with a boundary connection
        
        :param LandXML_Obj: 
        :return: 
        '''
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, LandXML_Obj)

        #Loop through monuments checking for first SSM/PM with a parcel connection
        for monument in LandXML_Obj.Monuments.getchildren():
            MarkType = monument.get("type")
            if MarkType == "SSM" or MarkType == "PM":                
                Observations = Connections.AllConnections(monument.get("pntRef"), LandXML_Obj)
                setattr(ConnectionChecker, "PntRefNum", monument.get("pntRef"))
                if ConnectionChecker.FindBdyConnection(Observations):
                    self.PntRefNum = monument.get("pntRef")
                    self.Code = "RM" + MarkType + "-" + RefMarkQueries.GetMarkNumber(LandXML_Obj, self.PntRefNum)
                    self.Easting, self.Northing = Coordinates.getPointCoords(self.PntRefNum, LandXML_Obj)
                    break
                        
                    
                    



