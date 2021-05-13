'''
Coordinates the processing of landXML files
- prompts to load land XML files
- calls to create objects
    - landXML group
    - landXML traverse properties
'''

from PyQt5.QtWidgets import QFileDialog

from LandXML import LandXML_Traverse_Props, LandXML_IO, ConnectionMopper
from LandXML.RefMarks import RefMark_Traverse
from LandXML.Cadastre import CadastreTraverse

import CadastreClasses as DataObjects


def LandXML(gui):
    '''
    main function coordinating landXML processing and calculations
    :param gui: gui data object from main UI
    :return:
    '''

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
            
        ConnectionMop = ConnectionMopper.main(gui.CadastralPlan, LandXML_Obj)

def ClearTriedConnections(gui):
    '''
    Remove Tried Connections from gui.CadatralPlan
    :param gui:
    :return:
    '''

    gui.CadastralPlan.TriedConnections = DataObjects.Lines()
    return gui



