'''
Coordinates the processing of landXML files
- prompts to load land XML files
- calls to create objects
    - landXML group
    - landXML traverse properties
'''

from PyQt5.QtWidgets import QFileDialog

from LandXML import LandXML_Traverse_Props, LandXML_IO
from LandXML.RefMarks import RefMark_Traverse


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
        #get connection tag in reduced observaations, assign as TraverseProps.tag
        setattr(TraverseProps, "tag", ReducedObsTag(LandXML_Obj))
        setattr(LandXML_Obj, "TraverseProps", TraverseProps)
    
    
        if LandXML_Obj.RefMarks:
            RefMark_Traverse.main(LandXML_Obj, gui)

def ReducedObsTag(LandXML_Obj):
    '''
    Determines what tag is used in the Reduced Observation connection
    :param LandXML_Obj:
    :return:
    '''

    Obs = LandXML_Obj.ReducedObs.getchildren()[0]
    #possible tags
    tags = ["IS-", "IS", "S-"]
    ID = Obs.get("setupID")
    for tag in tags:
        tagLen = len(tag)
        if ID[:(tagLen)] == tag:
            return tag



