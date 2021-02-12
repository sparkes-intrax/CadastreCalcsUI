'''
Subclasses the Graphics View and Scene for the GUI
'''

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QWheelEvent, QMouseEvent

import sys


class GuiDrawing(QGraphicsView):
    def __init__(self):
        QGraphicsView.__init__(self)

        #set the scene props and initiate
        self.scene = QGraphicsScene()
        Color = QtGui.QColor("#1d1d1f")#141a1f
        self.scene.setBackgroundBrush(Color)
        self.setScene(self.scene)

        #set graphics view properties
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.scale(0.002, 0.002)
        self.setGeometry(50, 150, 1050, 830)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom = 0.002

    #############################################
    #Event handlers
    def wheelEvent(self, event: QWheelEvent):
        """
        Zoom in or out of the view.
        """
        #Set event properties
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)
        #current scene event location
        StartPos = self.mapToScene(event.pos())

        #set zoom props
        delta = event.angleDelta().y()/5e5
        self.zoom += delta
        #view_pos = event.pos()
        #self.centerOn(view_pos)
        if self.zoom > 0.03:
            self.zoom = 0.03

        elif self.zoom < 0.000001:
            self.zoom = 0.000001

        self.scale(self.zoom, self.zoom)
        #self.centerOn(view_pos)
        self.updateView()
        print("zoom=" + str(self.zoom))
        #New scene positions
        EndPos = self.mapToScene(event.pos())

        #move scene back
        delta = EndPos - StartPos
        self.translate(delta.x(), delta.y())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    '''
    def mousePressEvent(self, event: QMouseEvent):

        items = self.scene.selectedItems()
        self.items()
        try:
            item = self.itemAt(event.pos())
            #print(item.type())

            items = self.scene.itemAt(item, self.viewportTransform())
            print(items.y())
        except Exception:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
    '''
    def updateView(self):

        #print(self.zoom)
        try:
            self.setTransform(QtGui.QTransform().scale(self.zoom, self.zoom))
        except Exception as e:
            print(e)

    #Scene objects
    def Point(self, E, N, size, Pen, Brush):
        '''
        Adds point to scene
        :return:
        '''
        PointObj = self.scene.addEllipse((E - size/2), (N - size/2), size, size, Pen, Brush)
        PointObj.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        return PointObj

    def Line(self, SrcEasting, SrcNorthing, E, N, LinePen):
        '''
        Adds Line to scene
        :return:
        '''

        GraphLine = self.scene.addLine(SrcEasting, SrcNorthing, E, N, LinePen)
        GraphLine.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        return GraphLine

    def Text(self, Easting, Northing, rotation, text):
        '''
        Adds Text at set location with rotation
        :param Easting:
        :param Northing:
        :param rotation:
        :return:
        '''

        TextLabel = self.scene.addText(text)
        width = TextLabel.boundingRect().width()
        height = TextLabel.boundingRect().height()
        TextLabel.setPos((int(Easting * 1000)),
                               (int(Northing * 1000)))
        TextLabel.setRotation(rotation)
        TextLabel.setDefaultTextColor(QtCore.Qt.white)
        TextLabel.setFont(QtGui.QFont("Segoe UI", 1000, ))
        TextLabel.setTextWidth(TextLabel.boundingRect().width())
        TextLabel.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        TextLabel.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        return TextLabel

    #mouse modes
    def mousePointFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.ShowSelectedParams = False

    def mouseDragFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ShowSelectedParams = False

    def mouseSelectFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.ShowSelectedParams = False

    def ShowLineParams(self):
        self.ShowSelectedParams = True