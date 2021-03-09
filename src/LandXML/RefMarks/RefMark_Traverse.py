'''
Workflow for Reference mark traverses
'''
import CadastreClasses as DataObjects
from LandXML import Connections, BDY_Connections, LandXML_Traverses
from LandXML.RefMarks import TraverseStart
from TraverseOperations import TraverseOperations

from DrawingObjects import LinesPoints

def main(LandXML_Obj, gui):
    '''
    Coordinates workflow for the traverse of reference marks in a LandXML file
    :param LandXML_Obj:
    :param TraverseProps:
    :param gui:
    :return:
    '''
    
    #Find start of first traverse
    StartPoint = TraverseStart.TraverseStart(LandXML_Obj, True)
    # create point object
    point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                              StartPoint.Northing, None, StartPoint.Code, "REFERENCE MARKS")
    
    #create new traverse and add start point
    traverse = TraverseOperations.NewTraverse("REFERENCE MARKS", StartPoint.PntRefNum, True, point)

    #set traverse props for RM traverses
    setattr(LandXML_Obj.TraverseProps, "TraverseType", "REFERENCE MARKS")
    setattr(LandXML_Obj.TraverseProps, "BdyConnections", True)

    #draw point on canvas
    pointObj = LinesPoints.AddPointToScene(gui.view, point, "REFERENCE MARKS")
    gui.view.scene.update()
    
    #calculate first traverse
    traverseObj = LandXML_Traverses.Traverse(traverse, gui, LandXML_Obj, StartPoint.PntRefNum)
    #set traverseProps to prioritise BDY connections
    setattr(LandXML_Obj.TraverseProps, "BdyConnections", True)

    #calculate RM traverses - keeps calculating traverses until all SSMs/PMs are calcd
    while(not CheckRMsNotCalculated(gui, LandXML_Obj.Monuments)):
        #complete a traqverse to its close or finish
        traverseObj = LandXML_Traverses.Traverse(traverse, gui, LandXML_Obj, StartPoint)
        # get start point for new traverse
        StartPoint = TraverseStart.TraverseStart(LandXML_Obj, False)

    
def CheckRMsNotCalculated(gui, Monuments):
    '''
    Checks cadastral plan whether any RMs hav not been calculated from a traverse
    :param gui: data object for GUI
    :param Monuments: MOnuments element from LandXML
    :return: Boolean (True if RMs haven't been calculated, False otherwise)
    '''
    
    for monument in Monuments.getchildren():
        monumentRefPnt = monument.get("pntRef")
        if hasattr(gui.CadastralPlanObj.Points, monumentRefPnt):
            return False

    return True


    

    