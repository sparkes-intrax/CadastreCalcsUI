'''
Determines starting points for traverses
'''

from LandXML.Cadastre import BdyQueries, ConnectionObservations
from LandXML.RefMarks import RefMarkQueries
from LandXML import BDY_Connections, Coordinates

from timer import Timer

class TraverseStartPoint:
    def __init__(self, gui, LandXML_Obj, FirstTraverse):
        '''
        Coordinates workflow to determine starting point for traverse
        :return:
        '''
    
        TraverseStartObj = TraverseStart(gui, LandXML_Obj)
        if LandXML_Obj.RefMarks or (not LandXML_Obj.RefMarks and not FirstTraverse):
            PntRefNum = TraverseStartObj.RefMarks()
        else:
            #tObj = Timer()
            #tObj.start()
            PntRefNum = TraverseStartObj.NoRefMarks()
            #tObj.stop("No RMs, First Traverse")
        
        if not PntRefNum:
            PntRefNum = False
        else:
            self.SetStartPointProps(gui, PntRefNum, LandXML_Obj, FirstTraverse)

            
    def SetStartPointProps(self, gui, PntRefNum, LandXML_Obj, FirstTraverse):
        '''
        Set class attribute for start point (PntRefNum
        :param gui: 
        :param PntRefNum: 
        :return: 
        '''
        if LandXML_Obj.RefMarks or (not LandXML_Obj.RefMarks and not FirstTraverse):
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
            #tObj = Timer()
            #tObj.start()
            PntRefNum = self.CalculatedRM()
            #tObj.stop("Road Parcel RM search")
        if PntRefNum is False:
            self.LandXML_Obj.BdyStartChecks.RmToRoadFrontage = True
            self.QueryType = "ConnectionRoadParcel"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        # Test connection observation connected to road frontage
        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.ConnectionPoints("Connection")
        #tObj.stop("Road Parcel Connection search", 1)
        if PntRefNum is False:
            self.QueryType = "RoadExtent"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum

        #Test Road Query - known point and parcel observation with as
            #road frontage
        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.CalculatedRM()
        #tObj.stop("Road Extent Connection - old plans")
        if PntRefNum is False:
            self.QueryType = "Road"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        # For old plans looks for a road extent observation
        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.CalculatedRM()
        #tObj.stop("Road parcel - not a lot - RM search")
        if PntRefNum is False:
            self.QueryType = "KnownPointRoadParcel"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum
        # Test Road Query - known point and
        # road frontage - part of a subdivision parcel
        #tObj = Timer()
        #tObj.start()
        #PntRefNum = self.CalculatedPoint()
        PntRefNum = self.ConnectionPoints("Road")

        #tObj.stop("Calculated Point road parcel connection",1)
        '''
        if PntRefNum is False:
            self.QueryType = "KnownPointRoad"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum
        
        # Test if already calculated points have road frontage
        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.CalculatedPoint()
        '''
        #tObj.stop("Calculated Point onto any road parcel - not a Lot")
        if PntRefNum is False:
            self.QueryType = "RmAndBdy"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return PntRefNum

        # Test if already calculated points have road frontage
        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.CalculatedRM()
        '''
        #tObj.stop("RM connection to Boundary")
        if PntRefNum is False:
            self.QueryType = "KnownPointAndBdy"
        else:
            self.TraverseProps.RmBdyTraverseStart = True
            return PntRefNum

        #tObj = Timer()
        #tObj.start()
        PntRefNum = self.CalculatedPoint()
        #tObj.stop("Calculated Point connection to a boundary vertex")
        
        '''
        if PntRefNum is False:
            self.QueryType = "Any"
        else:
            self.TraverseProps.RmBdyTraverseStart = False
            return  PntRefNum
        
        #PntRefNum = self.CalculatedPoint()
        PntRefNum = self.ConnectionPoints("Any")
        self.TraverseProps.RmBdyTraverseStart = False
            
        return PntRefNum

    def CalculatedRM(self):
        '''
        Finds Calculated RMs and queries their connections to Boundaries
        :return:
        '''

        try:
            monument = self.LandXML_Obj.Monuments.getchildren()[0]
        except AttributeError:
            return False

        RemovePntList = []
        for monument in self.LandXML_Obj.Monuments.getchildren():
            MonumentType = monument.get("type")
            PntRefNum = monument.get("pntRef")
            if PntRefNum not in self.gui.CadastralPlan.Points.PointList:
                continue
            #check monument is an RM
            if MonumentType == "SSM" or MonumentType == "PM" or \
                     MonumentType == "TS":
                #check if RM has been calculated in RM traverse
                if hasattr(self.gui.CadastralPlan.Points, PntRefNum):
                    #Query the boundaries connected to RM
                    QueryResult = BdyQueries.main(self.LandXML_Obj, PntRefNum,
                                       self.gui, self.QueryType, True)

                    #print(QueryResult.__class__.__name__)
                    if QueryResult.__class__.__name__ == "str":
                        RemovePntList.append(PntRefNum)
                    elif QueryResult:
                        if len(RemovePntList) > 0:
                            self.RemovePointsWithNoConnections(RemovePntList)
                        return PntRefNum

        if len(RemovePntList) > 0:
            self.RemovePointsWithNoConnections(RemovePntList)

        return False
    
    def ConnectionPoints(self, Query):
        '''
        Checks connections specified as road Extent or Connection
        :return: 
        '''
        #get connections
        Observations = ConnectionObservations.main(self.gui.CadastralPlan, self.LandXML_Obj,
                                                   Query)


        if Query == "Connection":
            PntRefNum = BdyQueries.TestTargetObservations(Observations, self.LandXML_Obj, self.gui,
                                                      self.QueryType, None, True)

        else:
            QueryObj = BdyQueries.RunQuery(Observations, self.LandXML_Obj, self.QueryType,
                                           False, self.gui.CadastralPlan, True)
            ObsFound = QueryObj.CoordinateQuery()
            if ObsFound:
                PntRefNum = QueryObj.PntRefNum
            else:
                PntRefNum = False



        return PntRefNum

        
        

    def CalculatedPoint(self):
        '''
        Checks calculated points (not RMs) for a traverse start
        :return:
        '''
        
        RemovePntList = []
        for point in self.gui.CadastralPlan.Points.PointList:
            #check point is not RM
            #f point == "66":
            #    print("Stop")
            if not RefMarkQueries.CheckIfRefMark(self.LandXML_Obj, point.split("_")[0]):
                if self.QueryType == "ConnectionRoadParcel" or self.QueryType == "RoadExtent":
                    QueryResult = BdyQueries.main(self.LandXML_Obj, point,
                                       self.gui, self.QueryType, True)
                else:
                    QueryResult = BdyQueries.main(self.LandXML_Obj, point,
                                                  self.gui, self.QueryType, False)

                if QueryResult.__class__.__name__ == "str":
                    RemovePntList.append(point)
                elif QueryResult:
                    #remove points with no connections
                    if len(RemovePntList) > 0:
                        self.RemovePointsWithNoConnections(RemovePntList)
                    return point

        if len(RemovePntList) > 0:
            self.RemovePointsWithNoConnections(RemovePntList)

        return False

    def RemovePointsWithNoConnections(self, RemovePntList):
        
        for Pnt in list(set(RemovePntList)):
            self.gui.CadastralPlan.Points.PointList.remove(Pnt)
            
