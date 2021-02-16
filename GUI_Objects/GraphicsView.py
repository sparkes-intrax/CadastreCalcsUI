'''
Subclasses the Graphics View and Scene for the GUI
'''

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QWheelEvent, QMouseEvent
from TraverseOperations import TraverseOperations
from MouseEvents import OnMouseClickShowLineParams, OnMouseClickJoinPoints

import sys


class GuiDrawing(QGraphicsView):
    def __init__(self, gui):
        QGraphicsView.__init__(self)

        self.gui = gui
        self.CurrentPoint = None
        self.MouseLine = None
        self.ShowSelectedParams = False
        #set the scene props and initiate
        self.scene = QGraphicsScene()
        Color = QtGui.QColor("#1d1d1f")#141a1f
        self.scene.setBackgroundBrush(Color)
        self.setScene(self.scene)

        #set graphics view properties
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.scale(0.002, 0.002)
        self.setGeometry(100, 150, 1000, 830)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.zoom = 0.002


    def mousePressEvent(self, event):

        if self.ShowSelectedParams:
            item = self.itemAt(event.pos())
            if isinstance(item, QtWidgets.QGraphicsLineItem) or \
                    isinstance(item, QtWidgets.QGraphicsPathItem):
                if item is not None:
                    #change line colour
                    rect = item.boundingRect()
                    Pen = QtGui.QPen(QtCore.Qt.red)
                    Pen.setWidth(300)
                    item.setPen(Pen)
                    Dialog = OnMouseClickShowLineParams.FindLineObject(self.gui, rect)

                    Pen = QtGui.QPen(Dialog.Colour)
                    Pen.setWidth(150)
                    item.setPen(Pen)
        elif self.JoinPoints:
            pos = self.mapToScene(event.pos())
            self.ClickedPointObj = OnMouseClickJoinPoints.FindPointObj(self.gui, pos)
            if self.ClickedPointObj.NearestPoint is not None and self.CurrentPoint is None:
                self.CurrentPoint = self.ClickedPointObj.NearestPoint.__getattribute__("PntNum")
                self.StartLinePointObj = self.__getattribute__("ClickedPointObj")
            elif self.ClickedPointObj.NearestPoint is not None:
                self.EndLinePointObj = self.ClickedPointObj.__getattribute__("NearestPoint")
                OnMouseClickJoinPoints.DrawNewLine(self.StartLinePointObj.__getattribute__("NearestPoint"),
                                                             self.EndLinePointObj, self.gui)
                #cleanup
                self.CurrentPoint = None
                self.scene.removeItem(self.MouseLine.mouseLine)

        super(GuiDrawing, self).mousePressEvent(event)

    #MOuse move event
    def mouseMoveEvent(self, event):
        if self.CurrentPoint is not None:
            '''
            draw line from CLicked Point to current position
            '''
            if self.MouseLine is not None:
                self.scene.removeItem(self.MouseLine.mouseLine)
            pos = self.mapToScene(event.pos())
            self.MouseLine = OnMouseClickJoinPoints.DrawMouseMove(self.StartLinePointObj,
                                                                  pos, self.gui)
        super(GuiDrawing, self).mouseMoveEvent(event)


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

        if self.zoom > 0:
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
        self.JoinPoints = False
        self.InsertPoints = False

    def mouseDragFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.ShowSelectedParams = False
        self.JoinPoints = False
        self.InsertPoints = False

    def mouseSelectFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.ShowSelectedParams = False
        self.JoinPoints = False
        self.InsertPoints = False

    def mouseMeasureFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.ShowSelectedParams = True
        self.JoinPoints = False
        self.InsertPoints = False

    def mouseJoinPointsFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.ShowSelectedParams = False
        self.JoinPoints = True
        self.InsertPoints = False

    def mouseInsertPointsFunction(self):
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.ShowSelectedParams = False
        self.JoinPoints = False
        self.InsertPoints = True

