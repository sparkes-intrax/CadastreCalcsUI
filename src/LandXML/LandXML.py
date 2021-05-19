'''
Coordinates the processing of landXML files
- prompts to load land XML files
- calls to create objects
    - landXML group
    - landXML traverse properties
'''

from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore

from LandXML import LandXML_Traverse_Props, LandXML_IO, ConnectionMopper
from LandXML.RefMarks import RefMark_Traverse
from LandXML.Cadastre import CadastreTraverse
from LandXML.Easements import EasementCalcs

import CadastreClasses as DataObjects


def LandXML(gui):
    '''
    main function coordinating landXML processing and calculations
    :param gui: gui data object from main UI
    :return:
    '''
    ##set transform params
    #start = gui.view.mapToScene(0,0)

    #get LandXML props object
    TraverseProps = LandXML_Traverse_Props.TraverseProps()
    
    #LandXML dialog and file load
    LandXML_Obj = LandXML_IO.main(TraverseProps)

    if LandXML_Obj is not None:
        #if RMs exists and are part of a traverse
        if LandXML_Obj.RefMarks:
            RefMark_Traverse.main(LandXML_Obj, gui)
            gui = ClearTriedConnections(gui)
            CadastreTraverse.CadastreTraverses(gui, LandXML_Obj)
        else:
            CadastreTraverse.CadastreTraverses(gui, LandXML_Obj)
            print("NO RMs")
            
        ConnectionMop = ConnectionMopper.main(gui, LandXML_Obj)

        #Check for easements
        if len(LandXML_Obj.EasementParcels) > 0:
            #Calculate Easements
            EaseTravObj = EasementCalcs.main(LandXML_Obj, gui)

        #Reset screen coords
        #setSceneCoords(gui)




def setSceneCoords(gui):
    sumE = 0
    sumN = 0
    for i, key in enumerate(gui.CadastralPlan.Points.__dict__.keys()):
        point = gui.CadastralPlan.Points.__getattribute__(key)
        if point.__class__.__name__ != "Point":
            continue

        sumE += point.E
        sumN += point.N
        ''' 
        if point.E < Emin:
            Emin = point.E

        if point.E > Emax:
            Emax = point.E

        if point.N < Nmin:
            Nmin = point.N

        if point.N > Nmax:
            Nmax = point.N
        '''
    midE = sumE/i
    midN = sumN/i
    Point = QtCore.QPointF(midE,midN)
    viewCoords = gui.view.mapFromScene(Point)
    gui.view.centerOn(viewCoords)
    print(viewCoords)


def ClearTriedConnections(gui):
    '''
    Remove Tried Connections from gui.CadatralPlan
    :param gui:
    :return:
    '''

    gui.CadastralPlan.TriedConnections = DataObjects.Lines()
    return gui



