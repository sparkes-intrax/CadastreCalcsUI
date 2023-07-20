'''
Workflow for Reference mark traverses
'''
import CadastreClasses as DataObjects
from LandXML import Connections, BDY_Connections, SharedOperations, PointClass, ClearTriedConnections#, LandXML_Traverses
from LandXML.RefMarks import TraverseStart, RM_TraverseCalcs
from TraverseOperations import TraverseOperations, TraverseClose
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import MessageBoxes

from DrawingObjects import LinesPoints, DrawTraverse

class RefMarkTraverses(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, LandXML_Obj, gui, parent=None):
        '''
        Coordinates workflow for the traverse of reference marks in a LandXML file
        '''
        QObject.__init__(self, parent)

        self.LandXML_Obj = LandXML_Obj
        self.gui = gui

    def process_ref_marks(self):
        '''
        Coordinates workflow for the traverse of reference marks in a LandXML file
        :param LandXML_Obj:
        :param TraverseProps:
        :param gui:
        :return:
        '''

        StartPoint = TraverseStart.TraverseStart(self.LandXML_Obj, True, None, self.gui)
        while(StartPoint.PntRefNum is None):
            #Find start of first traverse
            StartPoint.GetTravStart()

            if StartPoint.PntRefNum is None and not self.LandXML_Obj.TraverseProps.LargeLots:
                self.LandXML_Obj.TraverseProps.LargeLots = True
                StartPoint.GetTravStart()
            elif StartPoint.PntRefNum is None:
                self.LandXML_Obj.TraverseProps.ExistingLots = True
                StartPoint.GetTravStart()

        #draw point on canvas
        PointClassObj = PointClass.Points(self.LandXML_Obj, None)
        Elevation = PointClassObj.CheckElevation(StartPoint.PntRefNum)
        point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                                  StartPoint.Northing, Elevation, StartPoint.Code, "REFERENCE MARKS")
        pointObj = LinesPoints.AddPointToScene(self.gui.view, point, "REFERENCE MARKS")

        #create new traverse and add start point
        traverse = SharedOperations.initialiseTraverse(point, "REFERENCE MARKS", True)
        #setattr(gui, "traverse", traverse)

        #set traverse props for RM traverses
        setattr(self.LandXML_Obj.TraverseProps, "TraverseType", "REFERENCE MARKS")
        setattr(self.LandXML_Obj.TraverseProps, "BdyConnections", True)
        setattr(self.LandXML_Obj.TraverseProps, "MixedTraverse", False)



        traverseCounter = 1

        #set plan origin
        setattr(self.gui.CadastralPlan, "EastOrigin", StartPoint.Easting)
        setattr(self.gui.CadastralPlan, "NorthOrigin", StartPoint.Northing)
        setattr(self.gui, "CurrentCentreEasting", StartPoint.Easting)
        setattr(self.gui, "CurrentCentreNorthing", StartPoint.Northing)

        #calculate RM traverses - keeps calculating traverses until all SSMs/PMs are calcd
        while(not self.CheckRMsNotCalculated(self.LandXML_Obj.Monuments)):
            #create Branches instance and add current traverse
            self.LandXML_Obj.TraverseProps.TraverseCloseFound = False
            #complete a traverse to its close or finish
            traverseObj = RM_TraverseCalcs.Traverse(traverse, self.gui, self.LandXML_Obj, StartPoint.PntRefNum)


            #Handle branches that don't close when looking for closes (add to tried connections)
            if not traverseObj.Branches.CurrentBranch.Closed and self.LandXML_Obj.TraverseProps.TraverseClose:
                if hasattr(traverseObj.Branches.CurrentBranch, "StartObs"):
                    StartObs = traverseObj.Branches.CurrentBranch.StartObs
                    setattr(self.gui.CadastralPlan.TriedConnections, StartObs,
                            traverseObj.Branches.CurrentBranch.Lines.__getattribute__(StartObs))
            #add traverse to Cadastral Plan
            elif len(traverseObj.Branches.CurrentBranch.refPnts) > 1 and traverseObj.Branches is not None:

                #Apply close adjustment if required
                self.gui = SharedOperations.ApplyCloseAdjustment(traverseObj.Branches.CurrentBranch,
                                                                 self.LandXML_Obj,
                                                                 self.gui)
                DrawTraverse.main(self.gui, traverseObj.Branches.CurrentBranch, self.LandXML_Obj, None)

            if self.CheckRMsNotCalculated(self.LandXML_Obj.Monuments):
                break
            #after first traverse prioritise road and BDY connections
            setattr(self.LandXML_Obj.TraverseProps, "RoadConnections", True)

            # get start point for new traverse
            StartPoint = TraverseStart.TraverseStart(self.LandXML_Obj, False, traverseObj.Branches.CurrentBranch, self.gui)
            StartPoint.GetTravStart()
            # create point object and new traverse object
            try:
                traverse = SharedOperations.initialiseTraverse(StartPoint, "REFERENCE MARKS", False)
            except AttributeError:
                #no branches from last traverse check if anymore connections or tried connections
                    #to calculate
                if not self.CheckRMsNotCalculated( self.LandXML_Obj.Monuments):
                    StartPoint = TraverseStart.NextStart(self.LandXML_Obj, self.gui)
                    if StartPoint.PntRefNum is None:
                        break

                    traverse = SharedOperations.initialiseTraverse(StartPoint, "REFERENCE MARKS", False)
                else:
                    break
            '''
            if traverseCounter == 2:
                break
            traverseCounter +=1
            '''

        self.gui = ClearTriedConnections.ClearTriedConnections(self.gui)
        self.finished.emit()

    def CheckRMsNotCalculated(self, Monuments):
        '''
        Checks cadastral plan whether any RMs hav not been calculated from a traverse
        Doesn't allow dead end RMs
        :param gui: data object for GUI
        :param Monuments: MOnuments element from LandXML
        :return: Boolean (True if RMs haven't been calculated, False otherwise)
        '''

        for monument in Monuments.getchildren():
            MarkType = monument.get("type")
            monumentRefPnt = monument.get("pntRef")
            #get allconnections to monumentRefPnt
            Observations = Connections.AllConnections(monumentRefPnt, self.LandXML_Obj)
            if len(Observations.__dict__.keys()) == 1:
                continue
            if not hasattr(self.gui.CadastralPlan.Points, monumentRefPnt) and \
                (MarkType == "SSM" or MarkType == "PM") and \
                    len(Observations.__dict__.keys()) > 0:
                return False

        for point in self.LandXML_Obj.Coordinates.getchildren():
            if point.get("code") is not None and \
                    (point.get("code").startswith("SSM") or \
                     point.get("code").startswith("PM") or \
                     point.get("code").startswith("TS")):
                if not hasattr(self.gui.CadastralPlan.Points, point.get("name")):
                    return False

        return True


class Branches(object):
    pass


    

    