'''
Set of common functions used by all traverse type calculated from LandXMl

'''
import CadastreClasses as DataObjects
from TraverseOperations import TraverseOperations, TraverseClose
from GUI_Objects import GraphicsView
import MessageBoxes
from LandXML import TraverseErrorWindow
from DrawingObjects import DrawTraverse
from PyQt5.QtCore import Qt
import genericFunctions as funcs


def initialiseTraverse(StartPoint, Layer, FirstTraverse):
    '''
    Creates a traverse object for starting a new traverse from startPoint
    :param StartPoint: 
    :param Layer: 
    :param FirstTraverse: whether first traverse in calcs - bool
    :return: 
    '''
    if not hasattr(StartPoint, "Elev"):
        point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                              StartPoint.NorthingScreen, None, StartPoint.Code, StartPoint.Layer)
        traverse = TraverseOperations.NewTraverse(Layer, StartPoint.PntRefNum, FirstTraverse, point)
    else:
        traverse = TraverseOperations.NewTraverse(Layer, StartPoint.PntNum, FirstTraverse, StartPoint)

    return traverse


def ApplyCloseAdjustment(traverse, LandXML_Obj, gui):
    '''
    Checks if a close adjustment is required and automatically applies
    '''
    traverse = CalculateTraverseDistances(traverse)
    if LandXML_Obj.TraverseProps.TraverseClose:
        N_Error, E_Error, close = TraverseClose.misclose(traverse, gui.CadastralPlan)
        if E_Error != 0 or N_Error !=0:
            setattr(traverse, "CloseBearing", funcs.BearingFromDeltas(E_Error, N_Error))
        traverse.Close_PreAdjust = round(close*1000,4)
        if traverse.Distance != 0:
            close_error = (close/traverse.Distance) * 1e6
        else:
            close_error = 0
        message = "Traverse Type: " + traverse.type + "\n"\
                    "Easting Misclose: " + str(round(1000 * E_Error, 1)) + "mm\n" \
                    "Northing Misclose: " + str(round(1000 * N_Error, 1)) + "mm\n" \
                    "Total Misclose: " + str(round(1000 * close, 1)) + "mm\n" \
                    "Close Error: " + str(round(close_error,0)) + " ppm\n"
        title = "TRAVERSE MISCLOSE"
        #print("Traverse #: " + str(gui.CadastralPlan.Traverses.TraverseCounter))
        #print("Misclose: " + str(round(1000 * close, 1)) + "mm")
        #print("")

        if close_error >1e10 and traverse.type != "EASEMENT":
            MessageBoxes.genericMessage(message, title)
            traverse.Adjusted = False
        elif close > 5 and traverse.type == "EASEMENT":
            MessageBoxes.genericMessage(message, title)
            traverse.Adjusted = False
            
        if (close*1000 > 30 or close_error > LandXML_Obj.TraverseProps.CloseTolerance) and \
                traverse.type == "REFERENCE MARKS" and \
                not traverse.MixedTraverse:

            Dialog = CloseErrorWindow(gui, traverse, LandXML_Obj)
            if not Dialog.Changed:
                if Dialog.AdjustCurrentTrav:
                    traverse = TraverseAdjustment(traverse, gui.CadastralPlan, E_Error, N_Error)
                    traverse.Adjusted = True
            else:
                traverse = TraverseAdjustment(traverse, gui.CadastralPlan,
                                              Dialog.E_Error, Dialog.N_Error)
                traverse.Adjusted = True
            return gui
        elif traverse.type == "BOUNDARY" and \
            close_error > LandXML_Obj.TraverseProps.CloseTolerance and \
            close*1000 > 10:
            Dialog = CloseErrorWindow(gui, traverse, LandXML_Obj.TraverseProps.CloseTolerance)
            if not Dialog.Changed:
                if Dialog.AdjustCurrentTrav:
                    traverse = TraverseAdjustment(traverse, gui.CadastralPlan, E_Error, N_Error)
                    traverse.Adjusted = True

            else:
                traverse = TraverseAdjustment(traverse, gui.CadastralPlan,
                                              Dialog.E_Error, Dialog.N_Error)
                traverse.Adjusted = True
            return gui
        elif close_error > LandXML_Obj.TraverseProps.CloseTolerance and close*1000 >= 10:
            Dialog = CloseErrorWindow(gui, traverse, LandXML_Obj.TraverseProps.CloseTolerance)
            if not Dialog.Changed:
                if Dialog.AdjustCurrentTrav:
                    traverse = TraverseAdjustment(traverse, gui.CadastralPlan, E_Error, N_Error)
                    traverse.Adjusted = True
                return gui
            else:
                traverse = TraverseAdjustment(traverse, gui.CadastralPlan,
                                              Dialog.E_Error, Dialog.N_Error)
                traverse.Adjusted = True
            return gui
                

        if LandXML_Obj.TraverseProps.ApplyCloseAdjustment and close_error < LandXML_Obj.TraverseProps.CloseTolerance:
            traverse = TraverseAdjustment(traverse, gui.CadastralPlan, E_Error, N_Error)
            traverse.Adjusted = True
        elif close_error < 1:
            traverse = CleanUpTraverseEnd(traverse)

    
    return gui

def CloseErrorWindow(gui, traverse, LandXML_Obj):
    '''
    Calls traverse close and traverse component window
    :param gui:
    :param traverse:
    :param LandXML_Obj:
    :return:
    '''

    GraphicsView.UpdateView(gui, traverse)
    DrawCurrentTraverse(gui, traverse)
    Dialog = TraverseErrorWindow.TraverseErrorWin(gui, traverse, LandXML_Obj)
    Dialog.exec_()
    if Dialog.Changed:
        N_Error = Dialog.N_Error
        E_Error = Dialog.E_Error
        traverse = CalculateTraverseDistances(traverse)
        close = Dialog.close
        close_error = (close / traverse.Distance) * 1e6

    RemoveDrawnTraverse(gui, traverse)

    return Dialog

def TraverseAdjustment(traverse, CadastralPlan, E_Error, N_Error):
    TraverseClose.TraverseAdjustment(traverse, CadastralPlan,
                                     E_Error, N_Error)
    traverse = CleanUpTraverseEnd(traverse)
    
    return traverse

def DrawCurrentTraverse(gui, traverse):
    DrawObj = DrawTraverse.DrawTraverse(gui, traverse, Qt.red)
    DrawObj.DrawLines()

def RemoveDrawnTraverse(gui, traverse):

    for key in traverse.Lines.__dict__.keys():
        if key == "LineNum":
            continue
        Line = traverse.Lines.__getattribute__(key)
        gui.view.scene.removeItem(Line.GraphicsItems.Line)
        try:
            gui.view.scene.removeItem(Line.GraphicsItems.LineLabel)
        except AttributeError:
            pass


def CleanUpTraverseEnd(traverse):
    '''
    After an adjustment. Cleans up traverse end.
    Sets end of last connection to traverse end (ie not PntNum_1)
    :param traverse:
    :return:
    '''

    if len(traverse.EndRefPnt.split("_")) > 1:
        #Get last connection of traverse
        ObsName = traverse.Observations[-1].get("name")
        traverse.refPnts.remove(traverse.EndRefPnt)
        #get corresponding line
        line = traverse.Lines.__getattribute__(ObsName)
        #Change its end reference point
        line.EndRef = traverse.EndRefPnt.split("_")[0]
        #delete duplicate end point
        delattr(traverse.Points, traverse.EndRefPnt)
        #Change end point ref of traverse
        traverse.EndRefPnt = traverse.EndRefPnt.split("_")[0]

    return traverse

class TraverseStartPoint:
    def __init__(self, PntRefNum, CadastralPlan):

        point = CadastralPlan.Points.__getattribute__(PntRefNum)
        self.PntRefNum = PntRefNum
        self.Easting = point.E
        self.Northing = point.N
        self.NorthingScreen = point.NorthingScreen
        self.Layer = point.Layer
        self.Code = point.Code

class DummyStartPoint:
    def __init__(self, PntRefNum):
        self.PntRefNum = PntRefNum
        self.Easting = 1000
        self.Northing = 1000
        self.NorthingScreen = 1000
        self.Layer = "REFERENCE MARKS"
        self.Code = ""

def CalculateTraverseDistances(traverse):
    '''
    Calculates the overall distances for traverse
    Calculates deltaE and delta N for traverse
    :param traverse:
    :return:
    '''
    distance = 0
    deltaE = 0
    deltaN = 0

    #loop through lines to calculate distances
    for key in traverse.Lines.__dict__.keys():
        line = traverse.Lines.__getattribute__(key)
        if key == "LineNum":
            continue

        distance += float(line.__getattribute__("Distance"))
        deltaE += abs(line.__getattribute__("deltaE"))
        deltaN += abs(line.__getattribute__("deltaN"))

    #add distance attribute to traverse
    traverse.Distance = distance
    setattr(traverse, "deltaE", deltaE)
    setattr(traverse, "deltaN", deltaN)

    return traverse

