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


class CadastreTraverses:
    def __init__(self, gui, LandXML_Obj):
        '''

        :param gui:
        :param LandXML_Obj:
        :return:
        '''

        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.CalculateTraverses()

    def CalculateTraverses(self):
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
        #2) Create traverse instance
        if self.LandXML_Obj.RefMarks:
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, False)
            traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", False)
        else:
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, True)
            traverse = SharedOperations.initialiseTraverse(StartPoint, "BOUNDARY", True)
        #3) Whats the condition for continuing to look for traverses
        MoreBdyTraverses = True

        while(MoreBdyTraverses):

            #Find a traverse path (to close)
            tObj.start()
            traverseObj = BdyTraverseCalcs.TraverseCalcs(self.gui, self.LandXML_Obj,
                                                         StartPoint.PntRefNum)
            traversePath = traverseObj.FindPath(traverse)

            #add traverse to CadastralPlan
            try:
                if len(traversePath.refPnts) >= 2:
                    DrawTraverse.main(self.gui, traversePath, self.LandXML_Obj)
                    if len(traversePath.refPnts) > 2 and self.LandXML_Obj.TraverseProps.TraverseClose:
                        self.gui = SharedOperations.ApplyCloseAdjustment(traversePath,
                                                                     self.LandXML_Obj,
                                                                     self.gui)
                    
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
                    StartPoint = GetTriedConnections(self.gui)
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
                if StartPoint.PntRefNum == "6":
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

class GetTriedConnections:
    def __init__(self, gui):
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
        