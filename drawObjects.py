'''
Drawing objects and methods
'''

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

class Ellipse(QtWidgets.QGraphicsItem):

    def __init__(self, Pen, Brush, E, N, scene):
        '''
        Draws an ellipse with colour and fill of Pen and Brush @ E and N
        :param Pen:
        :param Brush:
        :param E:
        :param N:
        :return:
        '''
        super(Ellipse, self).__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.E = E
        self.N = N
        self.Pen = Pen
        self.Brush = Brush
        self.Ellipse = scene.addEllipse((self.E - 1000), (self.N - 1000), 2000, 2000, self.Pen, self.Brush)
        self.boundingRect = self.Ellipse.boundingRect()

    def drawEllipseMeth(self):
        painter = QtGui.QPainter(self)
        painter.drawEllipse(((self.E-1000), (self.N-1000), 2000, 2000, self.Pen, self.Brush))
        painter.end()

    def changeColour(self, Brush, Pen):
        self.Brush = Brush
        self.Pen = Pen
        self.update()

    def paint(self, painter=None, style=None, widget=None):
        painter.fillRect(self.boundingRect, self.Brush)

def drawPoint():
    pass

def drawLine():
    pass

