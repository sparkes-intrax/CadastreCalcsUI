'''
Workflow to prompt user to select landXML file and loads its objects
'''

from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from GUI_Objects import Fonts, ObjectStyleSheets, GroupBoxes, InputObjects, ButtonObjects
from LandXML import LandXML_Objects, Connections
import MessageBoxes
from LandXML import BDY_Connections


def main(TraverseProps, gui):
    '''
    Calls the QDialog to select landXML
    Loads landXML and creates data objects
    :return: 
    '''

    #THrow dialog asking if close should be applied.
    Message = "Apply transit adjustment to all closed traverses automatically?"
    Title = "LandXML Traverse Close Adjustments"
    if MessageBoxes.genericMessageYesNo(Message, Title) == QMessageBox.Yes:
        setattr(TraverseProps, "ApplyCloseAdjustment", True)
    else:
        setattr(TraverseProps, "ApplyCloseAdjustment", False)
    #Get LandXML file from QFileDialog
    Dialog = SelectLandXMLFile()
    LandXMLFile = Dialog.file
    setattr(gui.CadastralPlan, "LandXmlFile", LandXMLFile)

    if LandXMLFile is not None:
        setattr(gui.CadastralPlan, "LandXML_Dir", Dialog.dir.path())
        #Get LandXML objects from file
        LandXML_Obj = LandXML_Objects.main(LandXMLFile, TraverseProps)
        setattr(LandXML_Obj, "TriedConnections", TriedConnections())
        setattr(TraverseProps, "tag", ReducedObsTag(LandXML_Obj))
        setattr(LandXML_Obj, "TraverseProps", TraverseProps)
        setattr(gui.CadastralPlan, "PlanNum", LandXML_Obj.PlanAdmin.DP)

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
            self.dir = dialog.directory()
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

    #Check if file has monuments
    try:
        monument = LandXML_Obj.Monuments.getchildren()[0]
    except AttributeError:
        msg = "No Monuments in the selected LandXML file: " + LandXMLFile
        MessageBoxes.genericMessage(msg, "No Monuments in LandXML")
        return False


    for monument in LandXML_Obj.Monuments.getchildren():
        markType = monument.get("type")
        if markType == "SSM" or markType == "PM":
            pntRef = ''.join(filter(str.isdigit, monument.get("pntRef")))
            Observations = Connections.AllConnections(pntRef, LandXML_Obj)
            if len(Observations.__dict__.keys()) > 1:
                # create instance of Boundary checker
                ConnectionChecker = BDY_Connections.CheckBdyConnection(pntRef, LandXML_Obj)
                if ConnectionChecker.FindBdyConnection(Observations):
                    return True

    LandXML_Obj.TraverseProps.LargeLots = True
    for monument in LandXML_Obj.Monuments.getchildren():
        markType = monument.get("type")
        if markType == "SSM" or markType == "PM":
            pntRef = ''.join(filter(str.isdigit, monument.get("pntRef")))
            Observations = Connections.AllConnections(pntRef, LandXML_Obj)
            if len(Observations.__dict__.keys()) > 1:
                # create instance of Boundary checker
                ConnectionChecker = BDY_Connections.CheckBdyConnection(pntRef, LandXML_Obj)
                if ConnectionChecker.FindBdyConnection(Observations):
                    return True

    
    msg = "No SSMs or PMs in the selected LandXML file: " + LandXMLFile 
    MessageBoxes.genericMessage(msg, "No Reference Marks in LandXML")
    return False

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
        