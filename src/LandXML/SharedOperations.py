'''
Set of common functions used by all traverse type calculated from LandXMl

'''
import CadastreClasses as DataObjects
from TraverseOperations import TraverseOperations, TraverseClose
import MessageBoxes

def initialiseTraverse(StartPoint, Layer, FirstTraverse):
    '''
    Creates a traverse object for starting a new traverse from startPoint
    :param StartPoint: 
    :param Layer: 
    :param FirstTraverse: whether first traverse in calcs - bool
    :return: 
    '''

    point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                              StartPoint.NorthingScreen, None, StartPoint.Code, StartPoint.Layer)
    traverse = TraverseOperations.NewTraverse(Layer, StartPoint.PntRefNum, FirstTraverse, point)

    return traverse


def ApplyCloseAdjustment(traverse, LandXML_Obj, gui):
    '''
    Checks if a close adjustment is required and automatically applies
    '''

    if LandXML_Obj.TraverseProps.TraverseClose:
        N_Error, E_Error, close = TraverseClose.misclose(traverse, gui.CadastralPlan)
        close_error = (close/traverse.Distance) * 1e6
        message = "Easting Misclose: " + str(round(1000 * E_Error, 1)) + "mm\n" \
                  "Northing Misclose: " + str(round(1000 * N_Error, 1)) + "mm\n" \
                  "Total Misclose: " + str(round(1000 * close, 1)) + "mm\n" \
                    "Close Error: " + str(round(close_error,0)) + " ppm\n"
        title = "TRAVERSE MISCLOSE"
        #print("Traverse #: " + str(gui.CadastralPlan.Traverses.TraverseCounter))
        #print("Misclose: " + str(round(1000 * close, 1)) + "mm")
        #print("")

        if close_error > 100:
            MessageBoxes.genericMessage(message, title)
        if LandXML_Obj.TraverseProps.ApplyCloseAdjustment and close_error < 500:
            TraverseClose.TraverseAdjustment(traverse, gui.CadastralPlan,
                                         E_Error, N_Error)
    
    return gui

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
        if line.__class__.__name__ != "Line":
            continue

        distance += line.__getattribute__("Distance")
        deltaE += abs(line.__getattribute__("deltaE"))
        deltaN += abs(line.__getattribute__("deltaN"))

    #add distance attribute to traverse
    traverse.Distance = distance
    setattr(traverse, "deltaE", deltaE)
    setattr(traverse, "deltaN", deltaN)

    return traverse