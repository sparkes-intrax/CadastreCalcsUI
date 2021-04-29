'''
Create line edits, combo boxes and spin boxes with labels to be added to main GUI
'''

from PyQt5.QtWidgets import QLabel, QLineEdit, QSpinBox, QComboBox, QCompleter

class InputObjects:

    def __init__(self, widget, LabelTxt, ObjName, Font,
                 TextColour, BackgroundColour, InputType,
                 ComboItems, ComboFont, InputTextColour, InputBackgroundColour,
                 InputObj_w, InputObj_h, ObjRow, LabelCol, InputObj_Col):

        #Label
        self.Label = QLabel(widget.groupBox)
        self.Label.setText(LabelTxt)
        self.Label.setFont(Font)
        self.Label.setStyleSheet("color: %s;" % TextColour)
        self.Label.setObjectName("Label_"+ ObjName)

        if InputType == "QLineEdit":
            self.InputObj = QLineEdit(widget.groupBox)
            self.InputObj.setFont(Font)
            if ComboItems is not None:
                completer = QCompleter(ComboItems)
                #completer.complete()
                self.InputObj.setCompleter(completer)

        elif InputType == "QSpinBox":
            self.InputObj = QSpinBox(widget.groupBox)
            self.InputObj.setValue(1)

        else:
            self.InputObj = QComboBox(widget.groupBox)
            self.InputObj.setFont(ComboFont)
            self.InputObj.addItems(ComboItems)

        #stylesheet
        style = self.InputObj_Stylesheet(InputType, ObjName, InputTextColour, InputBackgroundColour, BackgroundColour)

        #set generic properties
        self.InputObj.setObjectName(InputType + "_" + ObjName)
        self.InputObj.setStyleSheet(style)
        self.InputObj.setMinimumSize(InputObj_w, InputObj_h)
        self.InputObj.setMaximumSize(InputObj_w, InputObj_h)

        #add widgets to GUI in defined groupBox
        widget.Layout.addWidget(self.Label, ObjRow, LabelCol, 1, 1)
        widget.Layout.addWidget(self.InputObj, ObjRow, InputObj_Col, 1, 1)

    def InputObj_Stylesheet(self,  InputType, ObjName,
                                   InputTextColour, InputBackgroundColour, BackgroundColour):
        '''
        Sets style sheet based on inputObj type
        :param InputType: type of widget
        :return: style
        '''

        if InputType == "QComboBox":
            style = ("%s#%s_%s {color: %s; "
                     "background-color: %s; "
                     "border-top: 1px solid %s; "
                     "border-left: 1px solid %s; "
                     "border-right: 1px solid %s; "
                     "border-bottom: 2px solid %s; "
                     "padding: 1px 0px 1px 3px;} "
                     "%s#%s_%s QListView {color: white;}" % (InputType, InputType, ObjName,
                                   InputTextColour, BackgroundColour, BackgroundColour,
                                                             BackgroundColour, BackgroundColour,
                                                             InputBackgroundColour,
                                                             InputType, InputType, ObjName))
        else:
            style = ("%s#%s_%s {color: %s; "
                     "background-color: %s;"
                     "border-top: 1px solid %s; "
                     "border-left: 1px solid %s; "
                     "border-right: 1px solid %s; "
                     "border-bottom: 2px solid %s;}" % (InputType, InputType, ObjName,
                                                           InputTextColour, BackgroundColour, BackgroundColour,
                                                             BackgroundColour, BackgroundColour,
                                                             InputBackgroundColour))

        return style