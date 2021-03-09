'''
Workflow to prompt user to select landXML file and loads its objects
'''

from PyQt5.QtWidgets import QDialog, QFileDialog
from GUI_Objects import Fonts, ObjectStyleSheets, GroupBoxes, InputObjects, ButtonObjects
from LandXML import LandXML_Objects
import MessageBoxes


def main(TraverseProps):
    '''
    Calls the QDialog to select landXML
    Loads landXML and creates data objects
    :return: 
    '''
    
    #Get LandXML file from QFileDialog
    Dialog = SelectLandXMLFile()
    LandXMLFile = Dialog.file

    if LandXMLFile is not None:
        #Get LandXML objects from file
        LandXML_Obj = LandXML_Objects.main(LandXMLFile, TraverseProps)
        setattr(LandXML_Obj, "TriedConnections", TriedConnections())

        # Check for Reference marks in landXML
        setattr(LandXML_Obj, "RefMarks", RefMarkCheck(LandXML_Obj, LandXMLFile))

        return LandXML_Obj

    return None

class SelectLandXMLFile(QFileDialog):
    def __init__(self):
        super().__init__()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("XML files (*.xml)")
        dialog.selectNameFilter("XML files (*.xml)")
        if dialog.exec_():
            self.file = dialog.selectedFiles()[0]
        else:
            self.file = None
            
        self.accept()
        
class TriedConnections(object):
    pass

def RefMarkCheck(LandXML_Obj, LandXMLFile):
    '''
    Checks if there are SSMs/PMs in the LandXML file
    Effects the traverse workflow
    :param LandXML_Obj:
    :return: boolean whether RMs are present or not
    '''

    for monument in LandXML_Obj.Monuments.getchildren():
        markType = monument.get("type")
        if markType == "SSM" or markType == "PM":
            return True
    
    msg = "No SSMs or PMs in the selected LandXML file: " + LandXMLFile 
    MessageBoxes.genericMessage(msg, "No Reference Marks in LandXML")
    return False
        