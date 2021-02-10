'''
Sets up group boxes for the GUI
'''

from PyQt5.QtWidgets import QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout

class GUI_GroupBox:

    def __init__(self, QRectObj, Title, Name, Font, Layout, widget, TextColour, BackgroundColour):
        '''
        Sets up a group box and its layout
        :param QRectObj: QREct object defining the size and location of the GroupBox
        :param Title: Title text used for GroupBox
        :param Name: Name of Object
        :param Font: QFont object
        :param Layout: layout type for groupbox
        :param widget: widget item for GUI
        '''

        self.groupBox = QGroupBox(widget)
        if QRectObj is not None:
            self.groupBox.setGeometry(QRectObj)
        self.groupBox.setTitle(Title)
        self.groupBox.setObjectName("GroupBox_" + Name)
        self.groupBox.setFont(Font)
        self.groupBox.setStyleSheet("QGroupBox#GroupBox_%s {color: %s;"
                                    "background-color:%s;}" % (Name, TextColour, BackgroundColour))


        if Layout == "Grid":
            self.Layout = QGridLayout(self.groupBox)
            self.Layout.setObjectName("Layout_" + Name)
        elif Layout == "Vertical":
            self.Layout = QVBoxLayout(self.groupBox)
            self.Layout.setObjectName("Layout_" + Name)
        else:
            self.Layout = QHBoxLayout(self.groupBox)
            self.Layout.setObjectName("Layout_" + Name)
            
