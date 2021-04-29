'''
Determines starting points for traverses
'''

from LandXML.Cadastre import BdyQueries
from LandXML.RefMarks import RefMarkQueries
from LandXML import BDY_Connections, Coordinates

class TraverseStartPoint:
    def __init__(self, gui, LandXML_Obj, FirstTraverse):
        '''
        Coordinates workflow to determine starting point for traverse
        :return:
        '''
    
        TraverseStartObj = TraverseStart(gui, LandXML_Obj)
        if LandXML_Obj.RefMarks or (LandXML_Obj.RefMarks and not FirstTraverse):
            PntRefNum = TraverseStartObj.RefMarks()
        else:
            PntRefNum = TraverseStartObj.NoRefMarks()
        
        try:
            self.SetStartPointProps(gui, PntRefNum, LandXML_Obj)
        except TypeError:
            pass
            
    def SetStartPointProps(self, gui, PntRefNum, LandXML_Obj):
        '''
        Set class attribute for start point (PntRefNum
        :param gui: 
        :param PntRefNum: 
        :return: 
        '''
        if LandXML_Obj.RefMarks:
            point = gui.CadastralPlan.Points.__getattribute__(PntRefNum)
            self.PntRefNum = PntRefNum
            self.Easting = point.E
            self.Northing = point.N
            self.NorthingScreen = point.NorthingScreen
            self.Layer = point.Layer
            self.Code = point.Code
        else:
            self.PntRefNum = PntRefNum
            self.Code = ""
            self.Easting, self.Northing = Coordinates.getPointCoords(self.PntRefNum,
                                                                     LandXML_Obj)
            self.NorthingScreen = self.Northing
            self.Layer = "BOUNDARY"
    
    
class TraverseStart:
    def __init__(self, gui, LandXML_Obj):
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.QueryType = "RoadParcel" #determines whats queried when looking at connections
        
    def NoRefMarks(self):
        '''
        Finds starting point for a plan with no RMs and for the
            first traverse
        :return:
        '''

        # loop through observations
        for ob in self.LandXML_Obj.ReducedObs.getchildren():
            # check if observation contains PntRefNum is connection
            attrib = ob.attrib
            if "targetSetupID" in attrib.keys():
                SetupID = ob.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
                TargetID = ob.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
                #check if a boundary connection of subdivision parcel
                ObservationChecker = BDY_Connections.CheckBdyConnection(SetupID, self.LandXML_Obj)
                if (ObservationChecker.BdyConnection(SetupID) and
                        ObservationChecker.BdyConnection(TargetID)):
                    return SetupID

        return None

    def RefMarks(self):
        '''
        Coordinates finding a starting point when plan has RMs
        Runs a series of Query type. These are run sequentially and only when
            the previous query type did not return a start point.
        :return: PntRefNum - reference number of the traverse start
        '''

        #Test RoadParcel Query
        PntRefNum = False
        if not self.LandXML_Obj.BdyStartChecks.RmToRoadFrontage:
            PntRefNum = self.CalculatedRM()
        if PntRefNum is False:
            self.LandXML_Obj.BdyStartChecks.RmToRoadFrontage = True
            self.QueryType = "ConnectionRoadParcel"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        # Test connection observation connected to road frontage
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is False:
            self.QueryType = "RoadExtent"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum

        #Test Road Query - known point and parcel observation with as
            #road frontage
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is False:
            self.QueryType = "Road"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        # For old plans looks for a road extent observation
        PntRefNum = self.CalculatedRM()
        if PntRefNum is False:
            self.QueryType = "KnownPointRoadParcel"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum
        # Test Road Query - known point and
        # road frontage - part of a subdivision parcel
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is False:
            self.QueryType = "KnownPointRoad"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum

        # Test if already calculated points have road frontage
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is False:
            self.QueryType = "RmAndBdy"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum

        # Test if already calculated points have road frontage
        PntRefNum = self.CalculatedRM()
        if PntRefNum is False:
            self.QueryType = "KnownPointAndBdy"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        PntRefNum = self.CalculatedPoint()
        self.TraverseProps.RmBdyTraverseStart = False
        return PntRefNum

    def CalculatedRM(self):
        '''
        Finds Calculated RMs and queries their connections to Boundaries
        :return:
        '''

        for monument in self.LandXML_Obj.Monuments.getchildren():
            MonumentType = monument.get("type")
            PntRefNum = monument.get("pntRef")
            #check monument is an RM
            if MonumentType == "SSM" or MonumentType == "PM" or \
                     MonumentType == "TS":
                #check if RM has been calculated in RM traverse
                if hasattr(self.gui.CadastralPlan.Points, PntRefNum):
                    #Query the boundaries connected to RM
                    if BdyQueries.main(self.LandXML_Obj, PntRefNum,
                                       self.gui, self.QueryType, True):
                        return PntRefNum


        return False

    def CalculatedPoint(self):
        '''
        Checks calculated points (not RMs) for a traverse start
        :return:
        '''

        for key in self.gui.CadastralPlan.Points.__dict__.keys():
            point = self.gui.CadastralPlan.Points.__getattribute__(key)
            #check point is not RM
            if not RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, point.PntNum.split("_")[0]):
                if self.QueryType == "ConnectionRoadParcel" or self.QueryType == "RoadExtent":
                    QueryResult = BdyQueries.main(self.LandXML_Obj, point.PntNum,
                                       self.gui, self.QueryType, True)
                else:
                    QueryResult = BdyQueries.main(self.LandXML_Obj, point.PntNum,
                                                  self.gui, self.QueryType, False)

                if QueryResult:
                    return point.PntNum

        return False


            
