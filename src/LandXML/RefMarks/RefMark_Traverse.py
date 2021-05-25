'''
Workflow for Reference mark traverses
'''
import CadastreClasses as DataObjects
from LandXML import Connections, BDY_Connections, SharedOperations#, LandXML_Traverses
from LandXML.RefMarks import TraverseStart, RM_TraverseCalcs
from TraverseOperations import TraverseOperations, TraverseClose

import MessageBoxes

from DrawingObjects import LinesPoints, DrawTraverse

def main(LandXML_Obj, gui):
    '''
    Coordinates workflow for the traverse of reference marks in a LandXML file
    :param LandXML_Obj:
    :param TraverseProps:
    :param gui:
    :return:
    '''
    
    StartPoint = TraverseStart.TraverseStart(LandXML_Obj, True, None, gui)
    while(StartPoint.PntRefNum is None):
        #Find start of first traverse
        StartPoint.GetTravStart()

        if StartPoint.PntRefNum is None and not LandXML_Obj.TraverseProps.LargeLots:
            LandXML_Obj.TraverseProps.LargeLots = True
        elif StartPoint.PntRefNum is None:
            LandXML_Obj.TraverseProps.ExistingLots = True
    #create new traverse and add start point
    traverse = SharedOperations.initialiseTraverse(StartPoint, "REFERENCE MARKS", True)
    #setattr(gui, "traverse", traverse)

    #set traverse props for RM traverses
    setattr(LandXML_Obj.TraverseProps, "TraverseType", "REFERENCE MARKS")
    setattr(LandXML_Obj.TraverseProps, "BdyConnections", True)
    setattr(LandXML_Obj.TraverseProps, "MixedTraverse", False)

    #draw point on canvas
    point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                              StartPoint.Northing, None, StartPoint.Code, "REFERENCE MARKS")
    pointObj = LinesPoints.AddPointToScene(gui.view, point, "REFERENCE MARKS")

    traverseCounter = 1

    #calculate RM traverses - keeps calculating traverses until all SSMs/PMs are calcd
    while(not CheckRMsNotCalculated(gui, LandXML_Obj.Monuments, LandXML_Obj)):
        #create Branches instance and add current traverse
        LandXML_Obj.TraverseProps.TraverseCloseFound = False
        #complete a traverse to its close or finish
        traverseObj = RM_TraverseCalcs.Traverse(traverse, gui, LandXML_Obj, StartPoint.PntRefNum)


        #Handle branches that don't close when looking for closes (add to tried connections)
        if not traverseObj.Branches.CurrentBranch.Closed and LandXML_Obj.TraverseProps.TraverseClose:
            StartObs = traverseObj.Branches.CurrentBranch.StartObs
            setattr(gui.CadastralPlan.TriedConnections, StartObs,
                    traverseObj.Branches.CurrentBranch.Lines.__getattribute__(StartObs))
        #add traverse to Cadastral Plan
        elif len(traverseObj.Branches.CurrentBranch.refPnts) > 1 and traverseObj.Branches is not None:

            #Apply close adjustment if required
            gui = SharedOperations.ApplyCloseAdjustment(traverseObj.Branches.CurrentBranch,
                                                             LandXML_Obj,
                                                             gui)
            DrawTraverse.main(gui, traverseObj.Branches.CurrentBranch, LandXML_Obj, None)
        
        if CheckRMsNotCalculated(gui, LandXML_Obj.Monuments, LandXML_Obj):
            break
        #after first traverse prioritise road and BDY connections
        setattr(LandXML_Obj.TraverseProps, "RoadConnections", True)

        # get start point for new traverse
        StartPoint = TraverseStart.TraverseStart(LandXML_Obj, False, traverseObj.Branches.CurrentBranch, gui)
        StartPoint.GetTravStart()
        # create point object and new traverse object
        try:
            traverse = SharedOperations.initialiseTraverse(StartPoint, "REFERENCE MARKS", False)
        except AttributeError:
            #no branches from last traverse check if anymore connections or tried connections
                #to calculate
            if not CheckRMsNotCalculated(gui, LandXML_Obj.Monuments, LandXML_Obj):
                StartPoint = TraverseStart.NextStart(LandXML_Obj, gui)
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





    
def CheckRMsNotCalculated(gui, Monuments, LandXML_Obj):
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
        Observations = Connections.AllConnections(monumentRefPnt, LandXML_Obj)
        if len(Observations.__dict__.keys()) == 1:
            continue
        if not hasattr(gui.CadastralPlan.Points, monumentRefPnt) and \
            (MarkType == "SSM" or MarkType == "PM"):
            return False

    return True


class Branches(object):
    pass


    

    