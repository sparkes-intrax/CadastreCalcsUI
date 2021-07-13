'''
Coordinates writing data to a csv and dxf file
Requests user to select the directory to write the files to
Call csv writer and dxf writer
'''

from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from FileIO import CsvWriter, DxfWriter, GIS, JsonExport

def main(CadastralPlan):
    
    #User selects output directory\
    File = None
    if hasattr(CadastralPlan, "LandXmlFile"):
        Dialog = SelectOutputDir()
        if Dialog.dir != "" and Dialog.dir is not None:
            dir = Dialog.dir
            LandXmlFile = CadastralPlan.LandXmlFile
            LandXmlFile = LandXmlFile.split("/")[-1]
            File = dir + "/" + LandXmlFile.replace(".xml", "")
    else:
        Dialog = SelectOutputFile()
        File = Dialog.file

    #check if there is data to export
    if File is not None:
        CsvWriter.main(CadastralPlan, File)
        DxfWriter.main(CadastralPlan, File)
        GIS.main(CadastralPlan, File)
        JsonExport.main(CadastralPlan, File)
        


class SelectOutputDir(QFileDialog):
    def __init__(self):
        super().__init__()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        #self.dir = dialog.getExistingDirectory()
        self.dir = dialog.getExistingDirectory()
        if not self.dir:
            self.dir = None
        self.accept()


class SelectOutputFile(QFileDialog):
    def __init__(self):
        super().__init__()
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            self.file = dialog.selectedFiles()[0]
            self.dir = dialog.directory()
        else:
            self.file = None

        self.accept()