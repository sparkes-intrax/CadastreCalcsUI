'''
Window Instance created when large errors found
'''

from PyQt5.QtWidgets import QDialog, QDesktopWidget, QPushButton, QLabel, QLineEdit
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from GUI_Objects import ColourScheme, InputObjects, ButtonObjects
from GUI_Objects import Fonts, GroupBoxes, ObjectStyleSheets
from TraverseOperations import TraverseRecalculate
import MessageBoxes
import genericFunctions as funcs
from LandXML import LandXML_Objects
from lxml import etree


class TraverseErrorWin(QDialog):
    def __init__(self, gui, traverse, LandXML_Obj):
        super().__init__()
        self.gui = gui
        self.traverse = traverse
        self.LandXML_Obj = LandXML_Obj
        self.AdjustCurrentTrav = False

        #Set up window
        self.WindowTitle = "Traverse Error"
        self.windowGeometry()
        self.setWindowTitle(self.WindowTitle)
        self.setAutoFillBackground(True)
        self.setObjectName("Dialog")
        self.Colours = ColourScheme.Colours()
        self.setStyleSheet("background-color: %s;" % self.Colours.backgroundUI)
        Font = Fonts.MajorGroupBox()
        rect = QtCore.QRect(5, 5,390, (self.winHeight-10))
        self.GB_Main = GroupBoxes.GUI_GroupBox(rect, "", "Drawing", Font,
                                               "Grid", self, self.Colours.backgroundUI,
                                                        self.Colours.backgroundUI)

        #Add traverse close specs
        self.CloseSpecs()
        self.SideBearingDistances()
        self.buttonObj()
        self.Changed = False
    '''
        self.InfoText = QLabel(self)
        self.InfoText.setText(self.textStr)
        self.InfoText.setStyleSheet("color: white;")

        self.InfoText.setFont(Font)
        self.GB_main.Layout.addWidget(self.InfoText)
        self.setWindowTitle("Traverse Error")
        self.Colours = ColourScheme.Colours()
        self.setStyleSheet("background-color: %s;" % self.Colours.backgroundUI)
        self.setAutoFillBackground(True)
        self.setObjectName("Dialog")
        # set window size
        self.windowGeometry()
        self.buttonObj()

        self.show()
    '''
    def windowGeometry(self):
        '''
        Sets window size based on number of lines in traverse
        :return:
        '''
        #ag = QDesktopWidget().availableGeometry()
        left = self.gui.width
        numLines = len(self.traverse.Lines.__dict__.keys())
        self.winHeight = 150 + numLines * 30
        if self.winHeight > self.gui.frameGeometry().height():
            self.winHeight = self.gui.frameGeometry().height() - 50

        self.setGeometry(left, 30, 400, self.winHeight)

    def CloseSpecs(self):
        '''
        writes close speces to window
        :return:
        '''
        Font = QFont("Segoe UI", 10,)
        LabelColour  = "white"
        self.TravDistLabel = QLabel(self)
        txtStr = "Distance(m): " + str(round(self.traverse.Distance,2))
        self.TravDistLabel.setText(txtStr)
        self.TravDistLabel.setFont(Font)
        self.TravDistLabel.setStyleSheet("color: %s;" % LabelColour)
        self.TravDistLabel.setObjectName("TravDistLabel")
        self.TravDistLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.TravDistLabel, 1, 0, 1, 1)

        self.TravCloseLabel = QLabel(self)
        misclose = str(round(float(self.traverse.Close_PreAdjust),1))
        txtStr = "Misclose (mm): " + misclose
        self.TravCloseLabel.setText(txtStr)
        self.TravCloseLabel.setFont(Font)
        self.TravCloseLabel.setStyleSheet("color: %s;" % LabelColour)
        self.TravCloseLabel.setObjectName("TravDistLabel")
        self.TravCloseLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.TravCloseLabel, 2, 0, 1, 1)

        self.TravCloseBearingLabel = QLabel(self)
        txtStr = "Misclose Bearing: " + self.traverse.CloseBearing
        self.TravCloseBearingLabel.setText(txtStr)
        self.TravCloseBearingLabel.setFont(Font)
        self.TravCloseBearingLabel.setStyleSheet("color: %s;" % LabelColour)
        self.TravCloseBearingLabel.setObjectName("TravDistLabel")
        self.TravCloseBearingLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.TravCloseBearingLabel, 3, 0, 1, 1)
        
        Font =Fonts.comboBoxFont()
        self.ObsNameLabel = QLabel(self)
        self.ObsNameLabel.setText("Obs Name")
        self.ObsNameLabel.setFont(Font)
        self.ObsNameLabel.setStyleSheet("color: %s;" % LabelColour)
        self.ObsNameLabel.setObjectName("TravDistLabel")
        self.ObsNameLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.ObsNameLabel, 4, 0, 1, 1)
        
        self.BearingLabel = QLabel(self)
        self.BearingLabel.setText("Bearing")
        self.BearingLabel.setFont(Font)
        self.BearingLabel.setStyleSheet("color: %s;" % LabelColour)
        self.BearingLabel.setObjectName("TravDistLabel")
        self.BearingLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.BearingLabel, 4, 1, 1, 1)
        self.DistanceLabel = QLabel(self)
        self.DistanceLabel.setText("Distance")
        self.DistanceLabel.setFont(Font)
        self.DistanceLabel.setStyleSheet("color: %s;" % LabelColour)
        self.DistanceLabel.setObjectName("TravDistLabel")
        self.DistanceLabel.setMaximumHeight(15)
        self.GB_Main.Layout.addWidget(self.DistanceLabel, 4, 2, 1, 1)

    def SideBearingDistances(self):
        '''
        Adds bearing and distances to dialog

        :return:
        '''
        Font = Fonts.LabelFonts()
        LabelColour = "white"

        self.SideLabels = []
        self.BearingEdits = []
        self.DistanceEdits = []
        for i, key in enumerate(self.traverse.Lines.__dict__.keys()):
            if key == "LineNum":
                continue
            Line = self.traverse.Lines.__getattribute__(key)
            row = i + 4
            setattr(self, "ObsForm_"+key, SideObjects(self.GB_Main, Line, row, key))
            setattr(self, "Obs_"+key, Originals(Line, key))
            #row = 1+i
            #label =
        self.row = row

    def buttonObj(self):

        Font = Fonts.ButtonFont()
        self.ButtonOk = ButtonObjects.Add_QButton(self.GB_Main, "OK",
                                                          "OkButton", Font,
                                                          self.ClickedOk, 50, 20,
                                                          (self.row+1), 0, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

        self.Recalc = ButtonObjects.Add_QButton(self.GB_Main, "Recalculate",
                                                       "Recalc", Font,
                                                       self.Recaculate, 50, 20,
                                                       (self.row + 1), 1, 1, 1, self.Colours.buttonColour,
                                                       self.Colours.buttonTextColor,
                                                       self.Colours.buttonHoverColour)

        self.Adjust = ButtonObjects.Add_QButton(self.GB_Main, "Adjust",
                                                "Adjust", Font,
                                                self.AdjustTrav, 50, 20,
                                                (self.row + 1), 2, 1, 1, self.Colours.buttonColour,
                                                self.Colours.buttonTextColor,
                                                self.Colours.buttonHoverColour)


    def ClickedOk(self):
        self.accept()
        
    def AdjustTrav(self):
        self.AdjustCurrentTrav = True
        self.accept()


    def Recaculate(self):
        '''
        Checks if there are any changes been made:
        - updates landXML
        - triggers recalc of traverse object
        :return:
        '''

        keyChanged = self.CheckForChanges()
        #Update LandXML
        if self.Changed:
            #self.UpdateLandXML(keyChanged)
            self.UpdateLineParams(keyChanged)
            self.traverse, self.N_Error, self.E_Error, self.close = \
                TraverseRecalculate.main(self.traverse, self.gui.CadastralPlan)
            setattr(self.traverse, "CloseBearing",
                    funcs.BearingFromDeltas(self.E_Error, self.N_Error))

            #Update close in window
            misclose = str(round(float(self.traverse.Close_PreAdjust), 1))
            txtStr = "Misclose (mm): " + misclose
            self.TravCloseLabel.setText(txtStr)

            txtStr = "Misclose Bearing: " + self.traverse.CloseBearing
            self.TravCloseBearingLabel.setText(txtStr)


        #self.accept()

    def CheckForChanges(self):
        '''
        Checks if changes made
        :return:
        '''

        keyChanged = []
        for i, key in enumerate(self.traverse.Lines.__dict__.keys()):
            if key == "LineNum":
                continue

            FormObj = self.__getattribute__("ObsForm_"+key)
            OrigObj = self.__getattribute__("Obs_"+key)

            if FormObj.BearingEdit.text() != OrigObj.Bearing:
                keyChanged.append(key)
                self.Changed = True

            if FormObj.DistanceEdit.text() != str(OrigObj.Distance):
                self.Changed = True
                if keyChanged not in keyChanged:
                    keyChanged.append(key)

        return keyChanged

    def UpdateLandXML(self, keyChanged):
        '''
        updates landXML file
        :param keyChanged:
        :return:
        '''

        lxml = etree.parse(self.gui.CadastralPlan.LandXmlFile)
        lxml = LandXML_Objects.RemoveComments(lxml)
        ns = lxml.getroot().nsmap
        for key in keyChanged:
            ObsForm = self.__getattribute__("ObsForm_"+key)
            # Reduced Observations
            tag = "//ReducedObservation"
            Query = tag + "[@name='" + key + "']"
            Observations = lxml.findall(Query, ns)
            if len(Observations) == 1:
                # get Observation
                Obs = Observations[0]
                Obs.attrib['horizDistance'] = ObsForm.DistanceEdit.text()
                bearing = self.BearingFlippedQuery(key, Obs, ObsForm.BearingEdit.text())
                Obs.attrib['azimuth'] = bearing
            else:
                # Reduced ArcObservations
                tag = "//ReducedArcObservation"
                Query = tag + "[@name='" + key + "']"
                Observations = lxml.findall(Query, ns)
                if len(Observations) == 1:
                    Obs = Observations[0]
                    radius = Obs.get("radius")
                    bearing = self.BearingFlippedQuery(key, Obs, ObsForm.BearingEdit.text())
                    Obs.attrib["chordAzimuth"] = bearing
                    ArcLength = round(funcs.CalcArcLength(radius, ObsForm.DistanceEdit.text()),3)
                    Obs.attrib["length"] = str(ArcLength)
                    #msg = "Modifying Arcs is not supported in this version.\n" \
                    #      "Further investigation is required"
                    #MessageBoxes.genericMessage(msg, "Arc Not Supported")

        with open(self.gui.CadastralPlan.LandXmlFile, 'wb') as f:
            lxml.write(f)
            
    def UpdateLineParams(self, keyChanged):
        '''
        Updates the changed parameters in the line
        :param keyChanged: 
        :return: 
        '''
        for key in keyChanged:
            Line = self.traverse.Lines.__getattribute__(key)
            ObsForm = self.__getattribute__("ObsForm_" + key)
            Line.Distance = float(ObsForm.DistanceEdit.text())
            Line.Bearing = ObsForm.BearingEdit.text()

    def BearingFlippedQuery(self, key, Obs, bearing):
        '''
        Checks if bearing was flipped before writing back to landXML
        :return:
        '''
        #get traverse line start ref
        line = self.traverse.Lines.__getattribute__(key)
        StartRef = line.StartRef

        #get observation start ref
        SetupID = Obs.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")

        if SetupID != StartRef:
            bearing = str(funcs.FlipBearing(float(bearing)))
            if len(bearing.split(".")[1]) == 1 or len(bearing.split(".")[1]) == 3:
                bearing += "0"



        return bearing




class SideObjects:
    def __init__(self, GB, Line, row, name):
        self.Label = QLabel(GB.groupBox)
        self.Label.setText(name)
        Font = QFont("Segoe UI", 10, )
        LabelColour = "white"
        self.Label.setObjectName("Label_" + name)
        self.Label.setStyleSheet("color: %s;" % LabelColour)
        GB.Layout.addWidget(self.Label, row, 0, 1, 1)
        
        self.BearingEdit = QLineEdit(GB.groupBox)
        self.BearingEdit.setText(Line.__getattribute__("Bearing"))
        self.BearingEdit.setStyleSheet("color: %s;" % LabelColour)
        GB.Layout.addWidget(self.BearingEdit, row, 1, 1, 1)

        self.DistanceEdit = QLineEdit(GB.groupBox)
        self.DistanceEdit.setText(str(round(Line.__getattribute__("Distance"),4)))
        self.DistanceEdit.setStyleSheet("color: %s;" % LabelColour)
        GB.Layout.addWidget(self.DistanceEdit, row, 2, 1, 1)

class Originals:
    def __init__(self, Line, key):
        '''
        creates an instance of original data from LandXML file
        :param Line:
        :param key:
        '''

        self.ObsName = key
        self.Bearing = Line.Bearing
        self.Distance = Line.Distance



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = TraverseErrorWin()
    mainWin.show()
    sys.exit( app.exec_() )