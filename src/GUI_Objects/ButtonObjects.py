'''
Adds a button object to selected widget
'''

from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from DrawingObjects import LinesPoints

class Add_QButton:

    def __init__(self, widget, ButtonLabel, ObjName, Font, Slot, Button_w, Button_h,
                 ButtonRow, ButtonCol, Button_Rows, Button_Cols, ButtonColour, ButtonTextColour,
                 ButtonHoverColour):
        '''
        Creates a button and adds it to the widget
        :param widget: Widget (groupBox) where button will be added
        :param ButtonLabel: Label on button
        :param ObjName: Name button object is given
        :param Font: Font of button text
        :param Slot: function called on click
        :param Button_w: width of button
        :param Button_h: hieght of button
        :param ButtonRow: row of widget where button is placed
        :param ButtonCol: column of widget where button is placed
        :param Button_Rows: how many rows the button takes up on the widget
        :param Button_Cols: how many columns the button takes up on the widget
        :param ButtonColour: Colour of button
        :param ButtonTextColour: Colour of text label on button
        :param ButtonHoverColour: Colour button turns when mouse hovers over button
        '''

        #create button object
        self.button = QPushButton(widget.groupBox)
        #set button properties
        self.button.setText(ButtonLabel)
        self.button.setObjectName(ObjName)
        self.button.setMinimumSize(Button_w, Button_h)
        self.button.setAutoDefault(True)
        self.button.clicked.connect(Slot)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setXOffset(1)
        shadow.setYOffset(1)
        shadow.setColor(QColor("#black"))
        self.button.setGraphicsEffect(shadow)

        style = ("QPushButton#%s {background-color: %s;"
                 "color: %s;"
                 "border-style: inset;"
                 "border-width: 0.2px;"
                 "border-radius: 3px;"
                 "border-color: black;}"
                 "QPushButton#%s:hover"
                 "{background-color : %s;};" % (ObjName, ButtonColour, ButtonTextColour, ObjName, ButtonHoverColour)
                 )
        self.button.setStyleSheet(style)
        self.button.setFont(Font)
        widget.Layout.addWidget(self.button, ButtonRow, ButtonCol, Button_Rows, Button_Cols)
