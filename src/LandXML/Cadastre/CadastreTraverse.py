'''
Coordinates the Cadastre Traverse
Sets properties in TraverseProperties
Selects starting point for traverses
Calculates traverse paths testing different branches
Determines whether a close can be found that meets a set of criteria

'''
from LandXML.Cadastre import BdyTraverseStart
from LandXML import Connections, SharedOperations, ConnectionMopper
from LandXML.Cadastre import BdyTraverseCalcs
from timer import Timer

from DrawingObjects import DrawTraverse

from TraverseOperations import TraverseClose

import MessageBoxes
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class CadastreTraverses(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(str)
    def __init__(self, gui, LandXML_Obj, parent=None):
        '''

        :param gui:
        :param LandXML_Obj:
        :return:
        '''
        QObject.__init__(self, parent)
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        #self.CalculateTraverses()

    def calculate_traverses(self):
        '''
        Calculates boundary traverse paths
        :return:
        '''
        tObjAll = Timer()
        tObjAll.start()
        tObjStarts = Timer()
        tObj = Timer()
        #1) Find first traverse start
        setattr(self.LandXML_Obj, "BdyStartChecks", BdyTraverseStartCheckList())
        setattr(self.LandXML_Obj.TraverseProps, "RoadConnections", False)
        setattr(self.LandXML_Obj.TraverseProps, "MixedTraverse", False)
        setattr(self.LandXML_Obj.TraverseProps, "TraverseClose", True)
        setattr(self.LandXML_Obj.TraverseProps, "LargeLots", False)
        #2) Create traverse instance
        if self.LandXML_Obj.RefMarks:
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, False)
            if not hasattr(StartPoint, "Easting"):
                setattr(self.LandXML_Obj.TraverseProps, "LargeLots", True)
                StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, True)
            traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", False)
        else:
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, True)
            if not hasattr(StartPoint, "Easting"):
                setattr(self.LandXML_Obj.TraverseProps, "LargeLots", True)
                StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, True)
            traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", True)

        #3) Whats the condition for continuing to look for traverses
        MoreBdyTraverses = True
        
        #Set plan origin if no Points
        if len(self.gui.CadastralPlan.Points.__dict__.keys()) == 1:
            setattr(self.gui.CadastralPlan, "EastOrigin", StartPoint.Easting)
            setattr(self.gui.CadastralPlan, "NorthOrigin", StartPoint.Northing)

        #LIst of point not allowed to start again - for when trying tried connections
        TriedStartPoints = []
        while(MoreBdyTraverses):

            #Find a traverse path (to close)
            tObj.start()
            traverseObj = BdyTraverseCalcs.TraverseCalcs(self.gui, self.LandXML_Obj,
                                                         StartPoint.PntRefNum)
            traversePath = traverseObj.FindPath(traverse)

            #add traverse to CadastralPlan
            try:
                if len(traversePath.refPnts) >= 2:
                    
                    if len(traversePath.refPnts) > 2 and self.LandXML_Obj.TraverseProps.TraverseClose:
                        self.gui = SharedOperations.ApplyCloseAdjustment(traversePath,
                                                                     self.LandXML_Obj,
                                                                     self.gui)
                    if  len(traversePath.refPnts) > 2 and not self.LandXML_Obj.TraverseProps.TraverseClose:
                        traversePath = self.Add2RawPoints(traversePath)
                        
                    DrawTraverse.main(self.gui, traversePath, self.LandXML_Obj, None)

                elif len(traversePath.refPnts) == 1 and \
                    not self.LandXML_Obj.TraverseProps.TraverseClose:
                    TriedStartPoints.append(StartPoint.PntRefNum)
                    
            except AttributeError as err:
                pass
                #print("AttributeError: {0}".format(err))
            tObj.stop("Traverse Closed", 1)
            #Get next start
            tObjStarts.start()
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, False)

            traverse, StartPoint = self.StartPointQuery(StartPoint)

            if traverse is None:
                if self.LandXML_Obj.TraverseProps.TraverseClose:
                    self.LandXML_Obj.TraverseProps.TraverseClose = False

                numTriedConnections = len((self.gui.CadastralPlan.TriedConnections.__dict__.keys()))
                if numTriedConnections > 1:
                    StartPoint = GetTriedConnections(self.gui, TriedStartPoints)
                    traverse, StartPoint = self.StartPointQuery(StartPoint)
                    if traverse is None:
                        print("Found all boundary traverse Paths")
                        break
                    else:
                        tObjStarts.stop("Found Start Point: " + StartPoint.PntRefNum, 1)
                else:
                    print("Found all boundary traverse Paths")
                    #MopObj = ConnectionMopper.ObservationMop(self.gui.CadastralPlan, self.LandXML_Obj)
                    break
            else:
                if StartPoint.PntRefNum == "42":
                    print("hereh")
                tObjStarts.stop("Found Start Point: " + StartPoint.PntRefNum, 1)
            #    print("StartPoint: " + StartPoint.PntRefNum)

        tObjAll.stop("Done!", 1)


    def StartPointQuery(self, StartPoint):
        '''
        tests whether start point is null and adjust settings to retry
        :param StartPoint:
        :return:
        '''

        try:
            #print(StartPoint.PntRefNum)
            #if StartPoint.PntRefNum == "53":
            #    print("Stop")
            traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", False)
            return traverse, StartPoint
        except AttributeError:
            if not self.LandXML_Obj.TraverseProps.LargeLots:
                self.LandXML_Obj.TraverseProps.LargeLots = True
                StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, False)
                try:
                    traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", False)
                    return traverse, StartPoint
                except AttributeError:
                    return None, StartPoint
            else:
                return None, StartPoint



    def ApplyCloseAdjustment(self, traverse):
        '''
        Checks if a close adjustment is required and automatically applies
        '''

        if self.LandXML_Obj.TraverseProps.TraverseClose and \
                self.LandXML_Obj.TraverseProps.ApplyCloseAdjustment:
            N_Error, E_Error, close = TraverseClose.misclose(traverse,
                                                             self.gui.CadastralPlan)
            message = "Easting Misclose: " + str(round(1000 * E_Error, 1)) + "mm\n" \
                    "Northing Misclose: " + str(round(1000 * N_Error, 1)) + "mm\n" \
                    "Total Misclose: " + str(round(1000 * close, 1)) + "mm\n"
            title = "TRAVERSE MISCLOSE"

            MessageBoxes.genericMessage(message, title)
            TraverseClose.TraverseAdjustment(traverse, self.gui.CadastralPlan,
                                             E_Error, N_Error)

    def Add2RawPoints(self, traversePath):
        '''
        Creates LineRaw and PointRaw
        :param traversePath:
        :return:
        '''
        
        for key in traversePath.Points.__dict__.keys():
            point = traversePath.Points.__getattribute__(key)
            if point.__class__.__name__ == "Point":
                setattr(traversePath.PointsRaw, key, point)
                traversePath.refPntsRaw.append(key)

        for key in traversePath.Lines.__dict__.keys():
            line = traversePath.Lines.__getattribute__(key)
            if line.__class__.__name__ == "Line" or line.__class__.__name__ == "Arc":
                setattr(traversePath.LinesRaw, key, line)

        return traversePath

class GetTriedConnections:
    def __init__(self, gui, TriedStartPoints):
        '''
        Gets Tried connections and returns start point
        :return:
        '''

        for key in gui.CadastralPlan.TriedConnections.__dict__.keys():
            Obs = gui.CadastralPlan.TriedConnections.__getattribute__(key)
            if Obs.__class__.__name__ != "Line":
                continue

            #Get the start point
            PntRefNum = Obs.__getattribute__("StartRef")
            if PntRefNum in TriedStartPoints:
                continue
            self.GetStartPoint(PntRefNum, gui)
            break

        #remove tried connection
        delattr(gui.CadastralPlan.TriedConnections, key)



    def GetStartPoint(self, PntRefNum, gui):

        point = gui.CadastralPlan.Points.__getattribute__(PntRefNum)
        self.PntRefNum = PntRefNum
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Layer = point.Layer
        self.Code = point.Code


class BdyTraverseStartCheckList:
    def __init__(self):
        '''
        Set of switches to tell if a certain start type has been fully discovered
        for example potential RM starts have been discovered so don't look again
        '''
        #more to be added
        self.RmToRoadFrontage = False
        