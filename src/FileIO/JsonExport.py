'''
Builds a json file to fit with the survey automatio formation
Requires:
- Plan Number
- Lot Number
- points
    {
      "Code": "",
      "Layer": "Boundary",
      "Easting": 1006.7198927332952,
      "Northing": 1032.6024210013984,
      "Elevation": "NaN"
    }
- lines
    {
      "StartPoint": 0,
      "EndPoint": 1,
      "Distance": 94.088,
      "Bearing": "30.1644",
      "ArcRadius": "NaN",
      "ArcRotation": "CCW"
    },
- Traverses
    {
      "State": "Closed",
      "Misclose": 0.00046734334520957252,
      "Adjusted": true,
      "PreAdjustMisclose": 0.00046734334520957252,
      "Lines": [
        0,
        1,
        2,
        3,
        4
      ]
    }, or for DHW etc
    {
      "State": "Closed",
      "Misclose": 0.00046734334520957252,
      "Adjusted": false,
      "PreAdjustMisclose": 0.00046734334520957252,
      "Lines": [
        1,
      ]
    },
- Buildings - empty for LandXML
- text?
- polygons (parcels, easements, roads - roads are lines)
- Parcels
        {
      "Lines": [
        14,
        51,
        42,
        50
      ],
      "PlanNumber": "DP1231811",
      "LotNumber": "75",
      "Area": 277.2,
      "LabelEasting": 995.15582106617831,
      "LabelNorthing": 1108.7436769935632
    }
- Easements - mostly empty
    {
      "Lines": [
        65,
        60,
        64,
        51
      ],
      "PlanNumber": "DP1231811",
      "Description": "(E) EASEMENT FOR REPAIRS 0.9 WIDE",
      "Identifier": "(E)",
      "LabelEasting": 997.01822793233669,
      "LabelNorthing": 1112.3653806974596
    },

- Roads one for every lot (as add road items keep track of lot numbers added
        {
      "Lines": [
        14
      ],
      "PlanNumber": "DP1231811",
      "Description": "FLEMINGTON (VARIABLE WIDTH) PARKWAY",
      "Width": "variable",
      "LabelEasting": 981.636296506681,
      "LabelNorthing": 1116.0882890281175
    }

Constraints Empty

'''

import json
from LandXML import LandXML_Objects, LandXML_Traverse_Props, Connections, LandXML_IO
from LandXML.TextLabels import ParcelCentrePoint

def main(CadastralPlan, file):
    '''
    Writes CadastralPlan data to a json
    Format matches with json import of Survey Automation
    :param CadastralPlan:
    :param file:
    :return:
    '''

    SurvDivisionObj = jsonObj(CadastralPlan, file)
    SurvDivisionObj.BuildJson()

class jsonObj:
    def __init__(self, CadastralPlan, file):
        self.CadastralPlan = CadastralPlan
        self.file = file + ".jsa"
        self.PlanNum = CadastralPlan.PlanNum
        self.DataObj = self.CreateDataObj()
        self.PointRefs = PointRef()
        self.LineRefs = LineRef()
        self.GetPlanObjects()

    def CreateDataObj(self):
        '''
        Creates dictionary to store CadastralPlan
        :return:
        '''
        DataObj = {}
        DataObj["PlanNumber"] = self.PlanNum
        DataObj["LotNumber"] = "null"

        DataObj["Points"] =[]
        DataObj["Lines"] = []
        DataObj["Traverses"] = []
        DataObj["Buildings"] = []
        DataObj["Parcels"] = []
        DataObj["Easements"] = []
        DataObj["Roads"] = []
        DataObj["Constraints"] = []

        return DataObj



    def BuildJson(self):
        '''
        Coordinates building json file
        :return:
        '''

        self.AddPoints(self.CadastralPlan.PointsRaw)
        self.AddLinesArcs(self.CadastralPlan.LinesRaw)
        self.AddTraverses(self.CadastralPlan.Traverses)
        self.AddParcels()
        self.SaveJson()

    def AddPoints(self, Points):
        '''
        Adds point objects to json
        :param Points: Points object from CadastralPlan
        :return:
        '''

        #loop through points and add to json
        i=0
        for key in Points.__dict__.keys():
            Point = Points.__getattribute__(key)
            if Point.__class__.__name__ != "Point":
                continue
            #add point refs to PointRef object
            self.PointRefs.SD_Num.append(i)
            self.PointRefs.MAD_Num.append(key)
            #Get a point dictionary
            PointDict = self.CreatePoints(Point)
            self.DataObj['Points'].append(PointDict)
            i+=1

    def AddLinesArcs(self, Lines):
        '''
        Add lines and Arcs to the line object in data object
        :param Lines:
        :return:
        '''

        # loop through lines and add to json
        i=0
        for key in Lines.__dict__.keys():
            Line = Lines.__getattribute__(key)
            if type(Line).__name__ == "int":
                continue
            #add refs to Line classes
            self.LineRefs.MAD_Num.append(key)
            self.LineRefs.SD_Num.append(i)
            #Get reference numbers for line
            StartRef, EndRef = self.FindLinePointRefs(Line)
            if StartRef is not None and EndRef is not None:
                LineDict = self.CreateLines(StartRef, EndRef, Line)
                self.DataObj["Lines"].append(LineDict)
                i+=1
            else:
                print("No Line")

    def AddTraverses(self, Traverses):
        '''
        Adds traverse object to json object
        :param Traverses:
        :return:
        '''

        # loop through traverses and add to json
        i = 0
        for key in Traverses.__dict__.keys():
            Traverse = Traverses.__getattribute__(key)
            if type(Traverse).__name__ == "int":
                continue

            #Get Line list for traverse
            LineList = self.GetTraverseLines(Traverse)
            TraverseDict = self.CreateTraverse(LineList, Traverse)
            self.DataObj["Traverses"].append(TraverseDict)
            i+=1


    def AddParcels(self):
        '''
        Loops through parcels in LANDXML_OBJ
        :return:
        '''

        # Loop through parcels in landXML file
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")
            parcelState = parcel.get("state")
            # check if a proposed parcel from subdivision
            if (parcelClass == "Lot" and parcelState == "proposed"):
                try:
                    CentroidObj = parcel.find(self.LandXML_Obj.TraverseProps.Namespace + "Center")
                    PntRefNum = CentroidObj.get("pntRef")
                    LabelEasting, LabelNorthing, NorthingScreen = self.GetPointCoordinates(PntRefNum)
                except AttributeError:
                    LabelEasting, LabelNorthing, NorthingScreen = ParcelCentrePoint.main(parcel,
                                                                                         self.CadastralPlan,
                                                                                         self.LandXML_Obj)
                LotNumber = parcel.get("name")
                Area = parcel.get("area")
                LineList = self.GetParcelLineList(parcel)
                if len(LineList) > 0:
                    LineDict = self.CreateParcel(LineList, LotNumber, Area, LabelEasting, LabelNorthing)
                    self.DataObj["Parcels"].append(LineDict)

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

    def FindLinePointRefs(self, Line):
        '''
        Finds the index number for point in json object
        :param Line:
        :return:
        '''
        PntSdStart = None
        PntSdEnd = None
        try:
            PntMadStart = Line.StartRef
            PntSdStart = self.PointRefs.SD_Num[self.PointRefs.MAD_Num.index(PntMadStart)]
            PntMadEnd = Line.EndRef
            PntSdEnd = self.PointRefs.SD_Num[self.PointRefs.MAD_Num.index(PntMadEnd)]
        except ValueError:
            pass

        return PntSdStart, PntSdEnd
            
    def GetPlanObjects(self):
        '''
        Gets the renewed lxml object from landXML file
        - required because in creating the Cadastral Plan objects all reduced obs are removed
        Creates a parcel object
        :return:
        '''

        # get LandXML props object
        TraverseProps = LandXML_Traverse_Props.TraverseProps()

        # LandXML dialog and file load
        self.LandXML_Obj = LandXML_Objects.main(self.CadastralPlan.LandXmlFile,
                                           TraverseProps)
        setattr(TraverseProps, "tag", LandXML_IO.ReducedObsTag(self.LandXML_Obj))
        setattr(self.LandXML_Obj, "TraverseProps", TraverseProps)

    def GetTraverseLines(self, Traverse):
        '''
        Gets the line references for traverse lines adds to line list
        :param Traverse:
        :return:
        '''

        LineList = []
        for key in Traverse.LinesRaw.__dict__.keys():
            Line = Traverse.LinesRaw.__getattribute__(key)
            if type(Line).__name__ == "int":
                continue

            #Get the SurvDivision Line Index number
            LineRef = self.LineRefs.SD_Num[self.LineRefs.MAD_Num.index(key)]
            LineList.append(LineRef)

        return LineList

    def GetParcelLineList(self, parcel):
        '''
        Gets the line list for a json file
        Line indexes for json file retrieved
        :param Parcel:
        :return:
        '''
        # get lines out of parcel
        lines = parcel.find(self.LandXML_Obj.TraverseProps.Namespace + "CoordGeom")
        LineList = []
        # loop through line to check vertexes
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "Start").get("pntRef")
                Observations = Connections.AllConnections(startRef, self.LandXML_Obj)
                endRef = self.LandXML_Obj.TraverseProps.tag +  \
                         line.find(self.LandXML_Obj.TraverseProps.Namespace + "End").get("pntRef")
                startRef = self.LandXML_Obj.TraverseProps.tag + startRef
                #find Observation where start and end define Observations
                for key in Observations.__dict__.keys():
                    Observation = Observations.__getattribute__(key)
                    ObRefStart = Observation.get("setupID")
                    ObRefEnd = Observation.get("targetSetupID")

                    if (ObRefStart == startRef and ObRefEnd == endRef) or \
                            (ObRefStart == endRef and ObRefEnd == startRef):
                        ObName = Observation.get("name")
                        line_i = self.LineRefs.MAD_Num.index(ObName)
                        LineList.append(self.LineRefs.SD_Num[line_i])
                        break

        return LineList





    def CreatePoints(self, Point):
        '''
        Creates a point dictionay item for
        :param Point:
        :return:
        '''

        PointDict= {}
        if Point.Code == "":
            PointDict["Code"] = ""
        else:
            PointDict["Code"] = Point.Code

        if Point.Layer == "BOUNDARY":
            PointDict["Layer"] = "Boundary"
        elif Point.Layer == "REFERENCE MARKS":
            PointDict["Layer"] = "ReferenceMarks"
        elif Point.Layer == "EASEMENT":
            PointDict["Layer"] = "Easements"
        else:
            PointDict["Layer"] = Point.Layer

        PointDict["Easting"] = Point.E
        PointDict["Northing"] = Point.N

        if Point.Elev is None:
            PointDict["Elevation"] = "NaN"
        else:
            PointDict["Elevation"] = Point.Elev


        return PointDict

    def CreateLines(self, StartRef, EndRef, Line):
        '''
        Create a dictionary item to store line object in json
        :param StartRef:
        :param EndRef:
        :param Line:
        :return:
        '''

        LineDict = {}
        LineDict["StartPoint"] = int(StartRef)
        LineDict["EndPoint"] = int(EndRef)
        LineDict["Distance"] = float(Line.Distance)
        LineDict["Bearing"] = Line.Bearing
        
        if Line.__class__.__name__ == "Arc":
            LineDict["ArcRadius"] = float(Line.Radius)
            LineDict["ArcRotation"] = Line.Rotation
        else:
            LineDict["ArcRadius"] = "NaN"
            LineDict["ArcRotation"] = "CCW"
            
        return LineDict
        
    def CreateTraverse(self, LineList, Traverse):
        '''
        Create traverse dictionary object to save in json data object
        :param LineList:
        :param Traverse:
        :return:
        '''

        TraverseDict = {}
        TraverseDict["State"] = "Closed"
        if Traverse.Close_PostAdjust is None:
            TraverseDict["Misclose"] = 0.0
        else:
            TraverseDict["Misclose"] = Traverse.Close_PostAdjust/1000
        TraverseDict["Adjusted"] = Traverse.Adjusted
        if Traverse.Close_PreAdjust is None:
            TraverseDict["PreAdjustMisclose"] = 0.0
        else:
            TraverseDict["PreAdjustMisclose"] = Traverse.Close_PreAdjust/1000

        TraverseDict["Lines"] = LineList
        return TraverseDict

    def CreateParcel(self, Lines, LotNumber, Area, LabelEasting, LabelNorthing):
        '''
        Creates a parcel dictionary to add to json data object
        :param Lines:
        :param LotNumber:
        :param Area:
        :param LabelEasting:
        :param LabelNorthing:
        :return:
        '''

        ParcelDict = {}
        ParcelDict["Lines"] = Lines
        ParcelDict["PlanNumber"] = self.CadastralPlan.PlanNum
        ParcelDict["LotNumber"] = LotNumber
        ParcelDict["Area"] = Area
        ParcelDict["LabelEasting"] = LabelEasting
        ParcelDict["LabelNorthing"] = LabelNorthing

        return ParcelDict



    def SaveJson(self):
        '''
        write json to file
        :return:
        '''
        PrettyJson = json.dumps(self.DataObj, indent=4)
        with open(self.file, 'w') as outfile:
            outfile.write(PrettyJson)
            
            
class PointRef:
    def __init__(self):
        #stores reference numbers for points in MAD and SurvDivision software
        self.MAD_Num = []
        self.SD_Num = []
        
class LineRef:
    def __init__(self):
        #stores reference numbers for points in MAD and SurvDivision software
        self.MAD_Num = []
        self.SD_Num = []