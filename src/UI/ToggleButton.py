'''
Contains UI for toggle menu used to view calcs and traverse errors
'''
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import *
from GUI_Objects import ButtonObjects
class Toggle:#(QtWidgets.QWidget):

    def __int__(self, ui):
        #super(Toggle, self).__init__(parent)
        #UI layout element to hold the toggle
        self.ui = ui

    def create_frame(self):
        '''
        frame that contains the toggle button
        '''

        self.menu_frame = QFrame(self.ui)
        self.menu_frame.setObjectName(u"menu_toggle_frame")
        self.menu_frame.setMaximumSize(QSize(70, 16777215))
        self.menu_frame.setStyleSheet(u"background-color: rgb(27, 29, 35);")
        self.menu_frame.setFrameShape(QFrame.NoFrame)
        self.menu_frame.setFrameShadow(QFrame.Raised)

    def create_layout(self):
        self.menu_layout = QVBoxLayout(self.menu_frame)
        self.menu_layout.setSpacing(0)
        self.menu_layout.setObjectName(u"menu_toggle_layout")
        self.menu_layout.setContentsMargins(0, 0, 0, 0)

    def create_button(self):
        self.btn_toggle_menu = QPushButton(self.menu_frame)
        self.btn_toggle_menu.setObjectName(u"btn_toggle_menu")
        self.btn_toggle_menu_SizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_toggle_menu_SizePolicy.setHorizontalStretch(0)
        self.btn_toggle_menu_SizePolicy.setVerticalStretch(0)
        self.btn_toggle_menu_SizePolicy.setHeightForWidth(self.btn_toggleMenu.sizePolicy().hasHeightForWidth())
        self.btn_toggleMenu.setSizePolicy(self.btn_toggle_menu_SizePolicy)
        icon = QIcon(":/24x24/icons/24x24/cil-menu.png")
        self.btn_toggle_menu.setIcon(icon)
        self.btn_toggle_menu.setIconSize(QSize(50, 50))
        self.btn_toggle_menu.setStyleSheet(ButtonObjects.button_style())

        self.menu_layout.addWidget(self.btn_toggle_menu)
        self.ui.addWidget(self.menu_frame)

    #def create_animation(self):