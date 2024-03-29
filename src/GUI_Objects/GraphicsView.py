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
        self.JoinPoints = False
        self.InsertPoints = False
        #set the scene props and initiate
        self.scene = QGraphicsScene()
        Color = QtGui.QColor(self.gui.Colours.backgroundCanvas)#141a1f
        self.scene.setBackgroundBrush(Color)
        self.setScene(self.scene)
        self._zoom = 0

        #set graphics view properties
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.scale(0.001, 0.001)
        self.setGeometry(100, 150, 1000, 830)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.zoom = 0.001


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
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom > 0:
            self.scale(factor, factor)
        else:
            self._zoom = 0
        '''
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0
        '''

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)
            self._zoom = 0
    '''
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
            #print(self.ce)
            #print("zoom=" + str(self.zoom))
            #New scene positions
            EndPos = self.mapToScene(event.pos())

            #move scene back
            delta = EndPos - StartPos
            self.translate(delta.x(), delta.y())
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
    '''
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
        TextLabel.setFont(QtGui.QFont("Segoe UI", 1500, ))
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


class UpdateView:
    def __init__(self, gui, traverse):
        '''
        Updates the view to center on center of plan
        :param gui:
        '''
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan

        #Get new centre
        if traverse is not None:
            self.NewCentreEast, self.NewCentreNorth = self.NewCentre(traverse.Points)
        else:
            self.NewCentreEast, self.NewCentreNorth = self.NewCentre(self.CadastralPlan.Points)

        self.RecentreScene()
        self.UpdateLoggedSceneCentre()

    def NewCentre(self, Points):
        '''
        Finds the new centre of the view
        :return:
        '''
        sumE = 0
        sumN = 0
        for i, key in enumerate(Points.__dict__.keys()):
            point = Points.__getattribute__(key)
            if point.__class__.__name__ != "Point":
                continue

            sumE += point.E
            sumN += point.N

        midE = sumE/i
        midN = sumN/i
        midN = self.GetNorthScreenCoords(midN)

        return midE, midN

    def GetNorthScreenCoords(self, North):
        '''
        Getes Northing of the new centre in screen coords
        :param North:
        :return:
        '''

        DistToOrigin = North - self.CadastralPlan.NorthOrigin
        NorthingScreen = self.CadastralPlan.NorthOrigin - DistToOrigin
        return NorthingScreen

    def RecentreScene(self):
        '''
        Recentres the scene on self.NewCentreEast, self.NewCentreNorth
        :return:
        '''

        #EndPos = QtCore.QPointF(self.NewCentreEast*1000, self.NewCentreNorth*1000)
        #StartPos = QtCore.QPointF(self.gui.CurrentCentreEasting*1000,
        #                          self.gui.CurrentCentreNorthing*1000)
        self.gui.view.centerOn(self.NewCentreEast*1000, self.NewCentreNorth*1000)
        #self.gui.view.fitInView()
        #self.gui.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        #self.gui.view.setResizeAnchor(QGraphicsView.NoAnchor)
        # move scene back
        #delta = EndPos - StartPos
        #self.gui.view.translate(delta.x(), delta.y())
        #self.gui.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        #self.gui.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def UpdateLoggedSceneCentre(self):
        '''
        Sets gui centre to coords of new centre
        :return:
        '''
        self.gui.CurrentCentreEasting= self.NewCentreEast
        self.gui.CurrentCentreNorthing = self.NewCentreNorth