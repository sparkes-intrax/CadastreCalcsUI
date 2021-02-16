'''
Dialog created from mousePressEvent
When Point enabled - retreive Line props on click
Dialog gives option to change line properties
TODO: recalculate and redraw traverse when line props are changed in dialog
'''

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt5 import QtCore
from GUI_Objects import Fonts, GroupBoxes, ObjectStyleSheets
import MessageBoxes

class FindLineObject:
    def __init__(self, gui, rect):
        self.Distance = None
        self.type = "Traverse"
        self.Radius = None
        self.Rotation = None
        # retrieve Line props to display
        if hasattr(gui, "traverse"):
            self.LineProps(rect, gui.traverse)
        if not hasattr(gui, "traverse") or self.Distance is None:
            self.LineProps(rect, gui.CadastralPlan)
            self.type = "Cadastral"

        #Send to dialog if a traverse as allows editing
        if hasattr(gui, "traverse") and self.Distance is not None:
            Dialog = ModifyLineDialog(self.Distance, self.Bearing,
                             self.LineType, self.Radius, self.Rotation)
            Dialog.exec_()

            self.Dialog = Dialog

        else:
            TextStr = "Line Properties: " + self.Bearing + " ~ " + self.Distance + "\n"
            if self.LineType == "Arc":
                TextStr += "Arc Radius: " + self.Radius + "\nArc Rotation: " + self.Rotation

            MessageBoxes.genericMessage(TextStr, "Line Properties")


    def LineProps(self, rect, object):
        '''
        Returns the bearing and distance of the line
        :param gui: gui object
        :param line: line being queried
        :return:
        '''
        # get bounding rect of item to be queried
        # LineRect = line.boundingRect()
        # loop through lines in traverse and to find queried line - match by bounding rect
        self.LineType = "Line"
        for key in object.Lines.__dict__.keys():
            if key == "LineNum" or key == "ArcNum":
                continue
            child = object.Lines.__getattribute__(key)

            if rect == child.BoundingRect:

                Distance = abs(float(child.Distance))
                self.Distance = str(Distance)
                self.Bearing = self.BearingString(str(child.Bearing))
                self.Colour = child.Colour
                if child.type == "Arc":
                    self.LineType = "Arc"
                    self.Rotation = child.Rotation
                    self.Radius = child.Radius

                break

    def BearingString(self, bearing):

        if len(bearing.split(".")) == 1:
            bearingStr = bearing + eval(r'"\u00B0"')
        elif len(bearing.split(".")[1]) == 2:
            bearingStr = bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         bearing.split(".")[1][0:2] + "'"
        else:
            bearingStr = bearing.split(".")[0] + eval(r'"\u00B0"') + \
                         bearing.split(".")[1][0:2] + "' " + \
                         bearing.split(".")[1][2:] + "\""

        return bearingStr

class ModifyLineDialog(QDialog):
    def __init__(self, Distance, Bearing,
                             LineType, Radius, Rotation):
        super().__init__()
        self.LineType = LineType
        TextStr = "Line Properties: " + Bearing + " ~ " + Distance + "\n"
        if LineType == "Arc":
            TextStr += "Arc Radius: " + Radius + "\nArc Rotation: " + Rotation

        self.WindowTitle = "Selected Line Properties"
        self.InfoText = TextStr


        if LineType == "Arc":
            self.setGeometry(900, 100, 300, 300)
        else:
            self.setGeometry(900, 100, 300, 200)

        self.setWindowTitle(self.WindowTitle)
        self.setAutoFillBackground(True)
        self.setObjectName("Dialog")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint  # hides the window controls
            | QtCore.Qt.SplashScreen  # this one hides it from the task bar!
        )
        self.setStyleSheet("background-color: #284254;")

        # Add Text to dialog
        Font = Fonts.MajorGroupBox()
        if LineType == "Arc":
            rect = QtCore.QRect(5, 5, 290, 290)
        else:
            rect = QtCore.QRect(5, 5, 290, 190)
        self.GB_main = GroupBoxes.GUI_GroupBox(rect, "", "Drawing", Font,
                                               "Vertical", self, "#284254", "#284254")
        self.InfoText = QLabel(self)
        self.InfoText.setText(TextStr)
        self.InfoText.setStyleSheet("color: white;")

        self.InfoText.setFont(Font)
        self.GB_main.Layout.addWidget(self.InfoText)

        # Add text input box
        Font = Fonts.LabelFonts()
        self.GB_modify = GroupBoxes.GUI_GroupBox(None, "Modify Line Properties", "LineProps", Font,
                                                 "Grid", self.GB_main.groupBox, "white", "#284254;")
        self.GB_main.Layout.addWidget(self.GB_modify.groupBox)

        self.DistanceLabel = QLabel(self)
        self.DistanceLabel.setFont(Font)
        self.DistanceLabel.setStyleSheet("color: white; background-color:#284254")
        self.GB_modify.Layout.addWidget(self.DistanceLabel, 1, 0, 1, 1)
        if LineType == "Arc":
            self.DistanceLabel.setText("Arc Chord Length:")
        else:
            self.DistanceLabel.setText("Line Length:")

        self.DistanceInput = QLineEdit(self)
        self.DistanceInput.setText("")
        self.DistanceInput.setStyleSheet("color: black; background-color:white")
        self.DistanceInput.setFont(Font)
        self.GB_modify.Layout.addWidget(self.DistanceInput, 1, 1, 1, 1)

        self.BearingLabel = QLabel(self)
        self.BearingLabel.setFont(Font)
        self.BearingLabel.setStyleSheet("color: white; background-color:#284254")
        self.GB_modify.Layout.addWidget(self.BearingLabel, 2, 0, 1, 1)
        if LineType == "Arc":
            self.BearingLabel.setText("Arc Chord Bearing (d.mmss):")
        else:
            self.BearingLabel.setText("Line Bearing (d.mmss):")

        self.BearingInput = QLineEdit(self)
        self.BearingInput.setText("")
        self.BearingInput.setStyleSheet("color: black; background-color:white")
        self.BearingInput.setFont(Font)
        self.GB_modify.Layout.addWidget(self.BearingInput, 2, 1, 1, 1)

        # Arc Params
        if LineType == "Arc":
            self.RadiusLabel = QLabel(self)
            self.RadiusLabel.setFont(Font)
            self.RadiusLabel.setStyleSheet("color: white; background-color:#284254")
            self.GB_modify.Layout.addWidget(self.RadiusLabel, 3, 0, 1, 1)
            self.RadiusLabel.setText("Arc Radius:")

            self.RadiusInput = QLineEdit(self)
            self.RadiusInput.setText("")
            self.RadiusInput.setStyleSheet("color: black; background-color:white")
            self.RadiusInput.setFont(Font)
            self.GB_modify.Layout.addWidget(self.RadiusInput, 3, 1, 1, 1)

            self.RotationLabel = QLabel(self)
            self.RotationLabel.setFont(Font)
            self.RotationLabel.setStyleSheet("color: white; background-color:#284254")
            self.GB_modify.Layout.addWidget(self.RotationLabel, 4, 0, 1, 1)
            self.RotationLabel.setText("Arc Rotation (d.mmss):")

            self.RotationInput = QComboBox(self)
            self.RotationInput.addItems(["CCW", "CW"])
            self.RotationInput.setCurrentText("CCW")
            self.RotationInput.setStyleSheet("color: black; background-color:white")
            self.RotationInput.setFont(Font)
            self.GB_modify.Layout.addWidget(self.RotationInput, 4, 1, 1, 1)

        self.button = QPushButton(self)
        self.button.setText("OK")
        self.button.setObjectName("Button")
        Font = Fonts.ButtonFont()
        self.button.setFont(Font)
        self.button.setMaximumSize(100, 20)
        self.button.setStyleSheet(ObjectStyleSheets.buttonStyle())
        self.button.clicked.connect(self.ClickedOk)
        if LineType == "Arc":
            self.GB_modify.Layout.addWidget(self.button, 5, 0, 1, 1)
        else:
            self.GB_modify.Layout.addWidget(self.button, 3, 0, 1, 1)

    def ClickedOk(self):

        self.DistanceText = self.DistanceInput.text()
        self.BearingText = self.BearingInput.text()
        if self.LineType == "Arc":
            self.RadiusText = self.RadiusInput.text()
            self.RotationText = self.RotationInput.currentText()
        self.accept()


