'''
Workflow for finding a point ot start a RefMark from
'''
from LandXML import BDY_Connections, Coordinates, Connections, RemoveCalculatedConnections
from LandXML.RefMarks import RefMarkQueries, FilterNonRMs
from TraverseOperations import TraverseOperations

class TraverseStart:
    def __init__(self, LandXML_Obj, FirstTraverse, LastTraverse, gui):
        '''
        Finds a suitable starting point for a traverse
        Adds PntRefNUm, Easting, Northing and code attributes if found
        :param LandXML_Obj:
        '''

        #If first traverse Check if control point A is connected to BDY
        self.PntRefNum = None
        self.LastTraverse = LastTraverse
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan
        self.LandXML_Obj = LandXML_Obj
        self.FirstTraverse = FirstTraverse

    def GetTravStart(self):
        '''
        Gets the start of the traverse
        :return:
        '''
        if self.FirstTraverse:
            #self.CheckSurveyOrigin()

            #if survey origin doesn't have a bdy connection find any RM with
            #           BDY connection
            #if self.PntRefNum is None:
            self.BdyConnectionStart()
        else: #
            self.NextTraverses()

    def CheckSurveyOrigin(self):
        '''
        Checks survey origin if it is connected to a BDY
        if not skips and return PntRefNum
        :param LandXML_obj:
        :return:
        '''
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)

        #Loop through coordinate points and finds the survey origin
        for point in self.LandXML_Obj.Coordinates.getchildren():
            if point.get("desc") == "A" and point.get("pntSurv") == "control":
                Observations = Connections.AllConnections(point.get("name"), self.LandXML_Obj)
                setattr(ConnectionChecker, "PntRefNum", point.get("name"))
                if ConnectionChecker.FindBdyConnection(Observations):
                    self.PntRefNum = point.get("name")
                    self.Code = "RM" + RefMarkQueries.FindMarkType(self.LandXML_Obj, self.PntRefNum) + "-" + \
                                point.get("oID")
                    self.Easting, Northing = Coordinates.getPointCoords(self.PntRefNum, self.LandXML_Obj)
                    self.Northing = Northing
                    self.NorthingScreen = Northing
                    self.Layer = "REFERENCE MARKS"
                    break
    
    def BdyConnectionStart(self):
        '''
        find a reference mark with a boundary connection
        
        :param LandXML_Obj: 
        :return: 
        '''
        # create instance of Boundary checker
        ConnectionChecker = BDY_Connections.CheckBdyConnection(self.PntRefNum, self.LandXML_Obj)

        #Loop through monuments checking for first SSM/PM with a parcel connection
        for monument in self.LandXML_Obj.Monuments.getchildren():
            MarkType = monument.get("type")
            originSurvey = monument.get("originSurvey")
            if originSurvey is not None and originSurvey != self.gui.CadastralPlan.PlanNum:
                continue
            if MarkType == "SSM" or MarkType == "PM":                
                Observations = Connections.AllConnections(monument.get("pntRef"), self.LandXML_Obj)
                setattr(ConnectionChecker, "PntRefNum", monument.get("pntRef"))
                if ConnectionChecker.FindBdyConnection(Observations):
                    self.PntRefNum = monument.get("pntRef")
                    self.Code = "RM" + MarkType + "-" + RefMarkQueries.GetMarkNumber(self.LandXML_Obj, self.PntRefNum)
                    self.Easting, Northing = Coordinates.getPointCoords(self.PntRefNum, self.LandXML_Obj)
                    self.Northing = Northing
                    self.NorthingScreen = Northing
                    self.Layer = "REFERENCE MARKS"
                    break

        if self.PntRefNum is None:
            for point in self.LandXML_Obj.Coordinates.getchildren():
                oID = point.get("oID")
                if oID is None:
                    continue
                Observations = Connections.AllConnections(point.get("name"), self.LandXML_Obj)
                setattr(ConnectionChecker, "PntRefNum", monument.get("pntRef"))
                markType = RefMarkQueries.FindMarkType(self.LandXML_Obj, point.get("name"))
                if ConnectionChecker.FindBdyConnection(Observations):
                    self.PntRefNum = point.get("name")
                    self.Code = "RM" + MarkType + "-" + oID
                    self.Easting, Northing = Coordinates.getPointCoords(self.PntRefNum, self.LandXML_Obj)
                    self.Northing = Northing
                    self.NorthingScreen = Northing
                    self.Layer = "REFERENCE MARKS"
                    break


    def NextTraverses(self):
        '''
        Finds next traverse to start
        Starts from first branch in last traverse
        If no branches or all brnaches have been calculated or tried
            Use tried connections and set traverse props self.TraverseClose to False
        :return:
        '''

        #get first branch of last traverse - handled with Index Error
                    #for no branhces
        #loop through branches until branch can be found that a 
        # traverse can be started from:
                # Connections to point have not been calculated
                # At leat 1 connection to point is an RM
        try:
            for BranchRefNum in self.LastTraverse.PrimaryBranches:
                self.PntRefNum = BranchRefNum
                traverse = TraverseOperations.NewTraverse("REFERENCE MARKS", self.PntRefNum, 
                                                          False, "DummyPoint")
                Observations = Connections.CheckStartingPoint(self.PntRefNum, self.LandXML_Obj, self.CadastralPlan,
                                                  traverse, self.gui)
                if len(Observations.__dict__.keys()) > 0:
                    point = self.CadastralPlan.Points.__getattribute__(self.PntRefNum)
                    self.Code = point.Code
                    self.Easting = point.E
                    self.Northing = point.N
                    self.NorthingScreen = point.NorthingScreen
                    self.Layer = point.Layer
                    break
            

        except IndexError:
            pass

                        
class NextStart:
    def __init__(self, LandXML_Obj, gui):
        '''
        Finds a suitable starting point for a traverse from a vertex already calculatyed
        Adds PntRefNUm, Easting, Northing and code attributes if found
        :param LandXML_Obj:
        '''

        #If first traverse Check if control point A is connected to BDY
        self.PntRefNum = None
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan
        self.LandXML_Obj = LandXML_Obj
        self.FindConnection()

        if self.PntRefNum is not None:
            #set point preperties
            point = self.CadastralPlan.Points.__getattribute__(self.PntRefNum)
            self.SetPointProps(point)
        else:
            #check tried connections and set TraverseProps to not look for closes
            self.CheckTriedConnections()
            self.LandXML_Obj.TraverseProps.TraverseClose = False
            if self.PntRefNum is not None:
                point = self.CadastralPlan.Points.__getattribute__(self.PntRefNum)
                self.SetPointProps(point)

    def FindConnection(self):
        '''
        Finds a uncalculated connection from an already calculated vertex
        '''

        #loops through calculated points
        for key in self.CadastralPlan.Points.__dict__.keys():
            point = self.CadastralPlan.Points.__getattribute__(key)
            if not point.__class__.__name__ == "Point":
                continue
            PntRefNum = point.PntNum
            traverse = TraverseOperations.NewTraverse("REFERENCE MARKS", PntRefNum,
                                                      False, "DummyPoint")
            setattr(traverse.Points, PntRefNum, point)
            Observations = Connections.CheckStartingPoint(PntRefNum, self.LandXML_Obj, self.CadastralPlan,
                                              traverse, self.gui)
            if len(Observations.__dict__.keys()) > 0:
                self.PntRefNum = PntRefNum
                break

    def CheckObs(self, Observations, PntRefNum):
        '''
        Checks if the end point of connections have been calculated
        Checks if connection in Tried Connections
        Keeps already calculated points
        :param Observations:
        :return:
        '''

        #loops through observations
        for key in Observations.__dict__.keys():
            Obs = Observations.__getattribute__(key)
            TargetID = Connections.GetTargetID(Obs, PntRefNum, self.LandXML_Obj.TraverseProps)
            if not hasattr(self.CadastralPlan.Points, TargetID):
                return True

        return False

    def SetPointProps(self, point):
        '''
        Sets properties for self.PntRefNUm from the CadastralPlan
        :param point:
        :return:
        '''

        self.Code = point.Code
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Layer = point.Layer

    def CheckTriedConnections(self):
        '''
        Checks if any of tried Connections exist
        Sets
        '''

        #check if any connections exist in Tried Connections
        if len(self.CadastralPlan.TriedConnections.__dict__.keys()) > 1:
            for key in self.CadastralPlan.TriedConnections.__dict__.keys():
                if key == "LineNum":
                    continue
                Line = self.CadastralPlan.TriedConnections.__getattribute__(key)
                self.PntRefNum = Line.StartRef
                break


                    

