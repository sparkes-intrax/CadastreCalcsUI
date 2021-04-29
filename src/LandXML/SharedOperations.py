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
        message = "Easting Misclose: " + str(round(1000 * E_Error, 1)) + "mm\n" \
                  "Northing Misclose: " + str(round(1000 * N_Error, 1)) + "mm\n" \
                  "Total Misclose: " + str(round(1000 * close, 1)) + "mm\n"
        title = "TRAVERSE MISCLOSE"
        if close > 0.00:
            MessageBoxes.genericMessage(message, title)
        if LandXML_Obj.TraverseProps.ApplyCloseAdjustment:
            TraverseClose.TraverseAdjustment(traverse, gui.CadastralPlan,
                                         E_Error, N_Error)
    
    return gui

#def TraverseDistance