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

class LandXML():
    def __init__(self, gui):
        '''
        main function coordinating landXML processing and calculations
        :param gui: gui data object from main UI
        :return:
        '''
        self.gui = gui
        self.TraverseProps = None
        self.LandXML_Obj = None

    def load_landXML(self):

        #get LandXML props object
        self.TraverseProps = LandXML_Traverse_Props.TraverseProps()

        #LandXML dialog and file load
        self.LandXML_Obj = LandXML_IO.main(self.TraverseProps, self.gui)

        if self.LandXML_Obj is not None:
            #get connection tag in reduced observaations, assign as TraverseProps.tag
            setattr(self.TraverseProps, "tag", self.ReducedObsTag())
            setattr(self.LandXML_Obj, "TraverseProps", self.TraverseProps)


            #if LandXML_Obj.RefMarks:
            #    RefMark_Traverse.main(LandXML_Obj, gui)



    def ReducedObsTag(self):
        '''
        Determines what tag is used in the Reduced Observation connection
        :return:
        '''

        Obs = self.LandXML_Obj.ReducedObs.getchildren()[0]
        #possible tags
        tags = ["IS-", "IS", "S-"]
        ID = Obs.get("setupID")
        for tag in tags:
            tagLen = len(tag)
            if ID[:(tagLen)] == tag:
                return tag



