'''
Coordinates the Cadastre Traverse
Sets properties in TraverseProperties
Selects starting point for traverses
Calculates traverse paths testing different branches
Determines whether a close can be found that meets a set of criteria

'''
from LandXML.Cadastre import BdyTraverseStart
from LandXML import Connections, SharedOperations
from LandXML.Cadastre import BdyTraverseCalcs

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

        #1) Find first traverse start
        setattr(self.LandXML_Obj, "BdyStartChecks", BdyTraverseStartCheckList())
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
            traverseObj = BdyTraverseCalcs.TraverseCalcs(self.gui, self.LandXML_Obj,
                                                         StartPoint.PntRefNum)
            traversePath = traverseObj.FindPath(traverse)

            #add traverse to CadastralPlan
            try:
                if len(traversePath.refPnts) > 2:
                    DrawTraverse.main(self.gui, traversePath)
                    self.gui = SharedOperations.ApplyCloseAdjustment(traverse,
                                                                     self.LandXML_Obj,
                                                                     self.gui)
                elif len(traversePath.refPnts) == 2:
                    DrawTraverse.SingelConnection(self.gui, traversePath)
                    
            except AttributeError as err:
                print("AttributeError: {0}".format(err))

            #Get next start
            StartPoint = BdyTraverseStart.TraverseStartPoint(self.gui, self.LandXML_Obj, False)
            traverse, StartPoint = self.StartPointQuery(StartPoint)
            if traverse is None:
                print("Found all boundary traverse Paths")
                break


    def StartPointQuery(self, StartPoint):
        '''
        tests whether start point is null and adjust settings to retry
        :param StartPoint:
        :return:
        '''

        try:
            print(StartPoint.PntRefNum)
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


class BdyTraverseStartCheckList:
    def __init__(self):
        '''
        Set of switches to tell if a certain start type has been fully discovered
        for example potential RM starts have been discovered so don't look again
        '''
        #more to be added
        self.RmToRoadFrontage = False
        