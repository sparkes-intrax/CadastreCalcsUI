'''
Main module to open form to calculate cadastre manually from pdf plan

Enables digitial traverse and checking closes
- adds numbers to points
- determine parcels from numbers added in form
- saves points and parcels to 2 separate csvs
'''

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsTextItem
import sys
from PyQt5.QtGui import QBrush, QPen, QWheelEvent, QMouseEvent
from PyQt5.QtCore import Qt, QThreadPool
import genericFunctions as funcs
import numpy as np
import CadastreClasses as dataObjects
from TraverseOperations import TraverseClose, CreateTraverseObject
import drawObjects

from GUI_Objects import GroupBoxes, Fonts, InputObjects, ButtonObjects, ObjectStyleSheets, GraphicsView
from DrawingObjects import LinesPoints, DrawingChecks
from TraverseOperations import TraverseOperations, TraverseObject
from Polygons import ViewPolygon
import MessageBoxes


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        #window properties
        self.title = "Cadastre Calcs"
        self.top = 30
        self.left = 30
        self.width = 1500
        self.height = 990

        self.CadastralPlan = self.initialiseDataObjects()
        self.ShowSelectedParams = False

        #Add menu bar to QMainWindow
        self.AddMenuBar()

        #Add Toolbar
        self.AddToolBar()

        # Add groupBoxes
        self.AddGroupBoxes()
        #Add Inputs
        self.GUI_Inputs_Buttons()


        self.InitWindow()

    def initialiseDataObjects(self):
        '''
        sets up the CadastralPlan parent class
        :return:
        '''
        #a list of codes to always start a new traverse
        #RMs that are dead ends - RMDHW etc
        self.CodeList = ["RMDHW", "RMGIP", "RMCB", "RMPLUG", "RMNAIL",
                         "ROCK"]
        return dataObjects.CadastralPlan()


    def InitWindow(self):

        self.view = GraphicsView.GuiDrawing(self)
        self.groupBox_Drawing.Layout.addWidget(self.view)


        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setStyleSheet("background-color: %s;" % "#171F24")
        self.show()

        self.threadpool = QThreadPool()
        #self.worker = MessageBoxes.Worker()

    def AddMenuBar(self):
        '''
        Adds a menu bar to GUI
        '''
        #get style sheet
        style = ObjectStyleSheets.QMenuBar()
        self.bar = self.menuBar()
        self.bar.setStyleSheet(style)
        fileMenu = QtWidgets.QMenu("&File", self)
        fileMenu.setStyleSheet(style)
        self.bar.addMenu(fileMenu)
        fileMenu.addAction("Export to LandXML")
        fileMenu.addAction("Export CSV with RM Levels")
        ViewMenu = QtWidgets.QMenu("&View", self)
        ViewMenu.setStyleSheet(style)
        self.bar.addMenu(ViewMenu)

        DataTableMenu = ViewMenu.addMenu("View Data Table")
        DataTableMenu.addAction("Current Traverse")
        DataTableMenu.addAction("All Data")

    def AddToolBar(self):
        '''
        Adds to toolbar to GUI
        '''
        style =ObjectStyleSheets.QToolBar()
        ToolBar = self.addToolBar("MouseAction")
        self.pointer = QtWidgets.QAction(self)
        self.pointer.setText("Pointer")
        self.pointer.setIcon(QtGui.QIcon("PointerIcon.ico"))
        self.pointer.triggered.connect(self.mousePointFunction)
        self.pointer.setCheckable(True)
        self.pointer.setChecked(True)
        PointTip = "Select Items"
        self.pointer.setStatusTip(PointTip)
        self.pointer.setToolTip(PointTip)
        ToolBar.addAction(self.pointer)

        self.dragAction = QtWidgets.QAction(self)
        self.dragAction.setText("&Drag")
        self.dragAction.setIcon(QtGui.QIcon("PanIcon.ico"))
        self.dragAction.triggered.connect(self.mouseDragFunction)
        self.dragAction.setCheckable(True)
        dragTip = "Pan"
        self.dragAction.setStatusTip(dragTip)
        self.dragAction.setToolTip(dragTip)
        ToolBar.addAction(self.dragAction)

        self.BoxSelectionAction = QtWidgets.QAction(self)
        self.BoxSelectionAction.setText("Select By Area")
        self.BoxSelectionAction.setIcon(QtGui.QIcon("RectangleSelection.ico"))
        self.BoxSelectionAction.triggered.connect(self.mouseSelectFunction)
        self.BoxSelectionAction.setCheckable(True)
        Tip = "Select By Area"
        self.BoxSelectionAction.setStatusTip(Tip)
        self.BoxSelectionAction.setToolTip(Tip)
        ToolBar.addAction(self.BoxSelectionAction)

        self.MeasureAction = QtWidgets.QAction(self)
        self.MeasureAction.setText("Measure Selection")
        self.MeasureAction.setIcon(QtGui.QIcon("MeasureIcon.ico"))
        self.MeasureAction.triggered.connect(self.mouseMeasureFunction)
        self.MeasureAction.setCheckable(True)
        Tip = "Measure & Inquire Items"
        self.MeasureAction.setStatusTip(Tip)
        self.MeasureAction.setToolTip(Tip)
        ToolBar.addAction(self.MeasureAction)

        self.JoinPointsAction = QtWidgets.QAction(self)
        self.JoinPointsAction.setText("Join points")
        self.JoinPointsAction.setIcon(QtGui.QIcon("JoinPointsIcon.ico"))
        Tip = "Create Line between points"
        self.JoinPointsAction.setStatusTip(Tip)
        self.JoinPointsAction.setToolTip(Tip)
        self.JoinPointsAction.setCheckable(True)
        self.JoinPointsAction.triggered.connect(self.mouseJoinPointsFunction)
        ToolBar.addAction(self.JoinPointsAction)
        ToolBar.setStyleSheet(style)

        self.InsertPointsAction = QtWidgets.QAction(self)
        self.InsertPointsAction.setText("Insert points")
        self.InsertPointsAction.setIcon(QtGui.QIcon("InsertPointsIcon.ico"))
        Tip = "Inserts a traverse side at selected point"
        self.InsertPointsAction.setStatusTip(Tip)
        self.InsertPointsAction.setToolTip(Tip)
        self.InsertPointsAction.setCheckable(True)
        self.InsertPointsAction.triggered.connect(self.mouseInsertPointsFunction)
        ToolBar.addAction(self.InsertPointsAction)
        ToolBar.setStyleSheet(style)
        
        self.ParrallelLineAction = QtWidgets.QAction(self)
        self.ParrallelLineAction.setText("Parrallel")
        self.ParrallelLineAction.setIcon(QtGui.QIcon("ParrallelLineIcon.ico"))
        Tip = "Creates A Parrallel Line to selected line"
        self.ParrallelLineAction.setStatusTip(Tip)
        self.ParrallelLineAction.setToolTip(Tip)
        self.ParrallelLineAction.setCheckable(True)
        self.ParrallelLineAction.triggered.connect(self.mouseParrallelLineFunction)
        ToolBar.addAction(self.ParrallelLineAction)
        ToolBar.setStyleSheet(style)

        self.TrimLineAction = QtWidgets.QAction(self)
        self.TrimLineAction.setText("Trims")
        self.TrimLineAction.setIcon(QtGui.QIcon("TrimIcon.ico"))
        Tip = "Trims Line"
        self.TrimLineAction.setStatusTip(Tip)
        self.TrimLineAction.setToolTip(Tip)
        self.TrimLineAction.setCheckable(True)
        self.TrimLineAction.triggered.connect(self.mouseTrimLineFunction)
        ToolBar.addAction(self.TrimLineAction)
        ToolBar.setStyleSheet(style)

        self.IntersectionPointAction = QtWidgets.QAction(self)
        self.IntersectionPointAction.setText("Intersection point")
        self.IntersectionPointAction.setIcon(QtGui.QIcon("IntersectionPointIcon.ico"))
        Tip = "Calcs intersection point between 2 selected lines"
        self.IntersectionPointAction.setStatusTip(Tip)
        self.IntersectionPointAction.setToolTip(Tip)
        self.IntersectionPointAction.setCheckable(True)
        self.IntersectionPointAction.triggered.connect(self.mouseIntersectionPointFunction)
        ToolBar.addAction(self.IntersectionPointAction)
        ToolBar.setStyleSheet(style)

        ToolBar.setIconSize(QtCore.QSize(50, 50))
        self.addToolBar(Qt.LeftToolBarArea, ToolBar)

    def AddGroupBoxes(self):
        '''
        adds groupboxes to the GUI window
        :return:
        '''

        #Drawing GroupBox
        Font = Fonts.MajorGroupBox()
        rect = QtCore.QRect(70, 150, 1030, 830)
        self.groupBox_Drawing = GroupBoxes.GUI_GroupBox(rect, "", "Drawing", Font,
                                                       "Grid", self, "#171F24", "#171F24")
        #Points main groupbox
        rect = QtCore.QRect(1120, 30, 350, 700)
        self.groupBox_Points = GroupBoxes.GUI_GroupBox(rect, "Points", "Points", Font,
                                                       "Grid", self, "white", "#171F24")

        #Enter Point GroupBox
        Font = Fonts.MinorGroupBox()
        self.groupBox_EnterPoint = GroupBoxes.GUI_GroupBox(None, "Add Point by Coordinates",
                                                           "EnterPoints", Font,
                                                           "Grid", self.groupBox_Points.groupBox,
                                                           "white", "#171F24")
        self.groupBox_EnterPoint.groupBox.setMaximumSize(310, 180)
        self.groupBox_EnterPoint.groupBox.setMinimumSize(310, 180)
        self.groupBox_Points.Layout.addWidget(self.groupBox_EnterPoint.groupBox, 2, 0, 1, 1)

        #Calculate Points GroupBox
        self.groupBox_CalcPoint = GroupBoxes.GUI_GroupBox(None, "Calculate Points",
                                                           "CalcPoints", Font,
                                                           "Grid", self.groupBox_Points.groupBox,
                                                           "white", "#171F24")
        self.groupBox_CalcPoint.groupBox.setMaximumSize(310, 180)
        self.groupBox_CalcPoint.groupBox.setMinimumSize(310, 180)
        self.groupBox_Points.Layout.addWidget(self.groupBox_CalcPoint.groupBox, 3, 0, 1, 1)

        #Point Info
        self.groupBox_PointInfo = GroupBoxes.GUI_GroupBox(None, "Point Information",
                                                          "PointInfo", Font,
                                                          "Grid", self.groupBox_Points.groupBox,
                                                          "white", "#171F24")
        self.groupBox_PointInfo.groupBox.setMaximumSize(310, 100)
        self.groupBox_PointInfo.groupBox.setMinimumSize(310, 100)
        self.groupBox_Points.Layout.addWidget(self.groupBox_PointInfo.groupBox, 4, 0, 1, 1)

        # Arc Params
        self.groupBox_ArcParams = GroupBoxes.GUI_GroupBox(None, "Arc Parameters",
                                                          "ArcParams", Font,
                                                          "Grid", self.groupBox_Points.groupBox,
                                                          "white", "#171F24")
        self.groupBox_ArcParams.groupBox.setMaximumSize(310, 100)
        self.groupBox_ArcParams.groupBox.setMinimumSize(310, 100)
        self.groupBox_Points.Layout.addWidget(self.groupBox_ArcParams.groupBox, 5, 0, 1, 1)

        #Polygon Input
        rect = QtCore.QRect(1120, 730, 350, 250)
        Font = Fonts.MajorGroupBox()

        self.groupBox_PolyInput = GroupBoxes.GUI_GroupBox(rect, "Polygons", "Polygons",
                                                          Font, "Grid", self,
                                                          "white", "#171F24")
        #Traverse GroupBox
        rect = QtCore.QRect(70, 30, 1030, 90)

        self.groupBox_Traverses = GroupBoxes.GUI_GroupBox(rect, "Traverse Functions",
                                                          "Traverses", Font, "Grid",
                                                          self,  "white", "#171F24")

    def GUI_Inputs_Buttons(self):
        '''
        Adds INput items and Buttons
        :return:
        '''

        #Point Number for point entered or calculated
        Font = Fonts.LabelFonts()
        self.PointNumber = InputObjects.InputObjects(self.groupBox_Points,
                                                     "Point Number", "PointNum", Font,
                                                     "#03DAC5", "#171F24",
                                                     "QSpinBox", None, None, "white",
                                                     "#3a4f5c", 90, 20, 1, 0, 1)

        #Enter Points group box
        self.EnterPointGroupBox_Objects()
        #Calc Points Group Boc
        self.CalcPointGroupBox_Objects()
        #Point Info groupBox
        self.PointInfoGroupBox_Objects()
        #Arc Params GroupBox
        self.ArcParamsGroupBox_Objects()
        #Polygon GroupBox
        self.PolygonGroupBox_Objects()
        #Traverse Ops GroupBox
        self.TraverseOpsGroupBox_Objects()

    def EnterPointGroupBox_Objects(self):
        '''
        Adds object to the groupBox_EnterPoint object
        '''

        #Easting Label and Input
        Font = Fonts.LabelFonts()
        self.EastingCoord = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                      "Easting", "Easting", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QLineEdit", None, None, "white",
                                                      "#3a4f5c", 100, 20, 1, 0, 2)

        # Northing Label and Input
        self.NorthingCoord = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                      "Northing", "Northing", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QLineEdit", None, None, "white",
                                                      "#3a4f5c", 100, 20, 2, 0, 2)

        # Elevation Label and Input
        self.PointElevation = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                       "Elevation", "Elevation", Font,
                                                       "#03DAC5", "#171F24",
                                                       "QLineEdit", None, None, "white",
                                                       "#3a4f5c", 100, 20, 3, 0, 2)

        #Enter Point button
        Font = Fonts.ButtonFont()
        self.EnterPointButton = ButtonObjects.Add_QButton(self.groupBox_EnterPoint, "Enter Point",
                                                          "EnterPointButton", Font,
                                                          self.EnterPoint, 190, 30,
                                                          5, 0, 2, 3, "#3700B3", "white", "#90adf0")

    def CalcPointGroupBox_Objects(self):
        '''
        Adds object to the groupBox_CalcPoints object
        '''

        #Source Point for point calculation Label and Input
        Font = Fonts.LabelFonts()
        self.SrcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                      "Source Point Number", "SrcPoint", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QSpinBox", None, None, "white",
                                                      "#3a4f5c", 100, 20, 2, 0, 2)

        # Bearing Label and Input
        self.BearingToCalcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                      "Bearing (d.mmss)", "Bearing", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QLineEdit", None, None, "white",
                                                      "#3a4f5c", 100, 20, 3, 0, 2)

        self.BearingToCalcPoint.InputObj.returnPressed.connect(self.CalcPointChecks)


        # Elevation Label and Input
        self.DistanceToCalcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                       "Distance", "Distance", Font,
                                                       "#03DAC5", "#171F24",
                                                       "QLineEdit", None, None, "white",
                                                       "#3a4f5c", 100, 20, 4, 0, 2)
        self.DistanceToCalcPoint.InputObj.returnPressed.connect(self.CalcPointChecks)

        #Enter Point button
        Font = Fonts.ButtonFont()
        self.CalcPointButton = ButtonObjects.Add_QButton(self.groupBox_CalcPoint, "Calculate Point",
                                                          "CalcPointButton", Font,
                                                          self.CalcPointChecks, 190, 30,
                                                          5, 0, 2, 3, "#3700B3", "white", "#90adf0")


    def PointInfoGroupBox_Objects(self):
        '''
        Adds object to the groupBox_PointInfo object
        '''

        #Point Code calculation Label and Input
        Font = Fonts.LabelFonts()
        ComboBoxItems = ["RMSSM", "RMPM", "RMDHW", "RMGIP", "RMCB", "RMPLUG", "RMNAIL",
                         "ROCK"]
        self.PointCode = InputObjects.InputObjects(self.groupBox_PointInfo,
                                                      "Point Code", "Code", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QLineEdit", ComboBoxItems, Font, "white",
                                                      "#3a4f5c", 150, 20, 1, 0, 2)

        # Point Layer
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["REFERENCE MARKS", "BOUNDARY", "EASEMENT"]
        self.PointLayer = InputObjects.InputObjects(self.groupBox_PointInfo,
                                                      "Point Layer", "Layer", Font,
                                                      "#03DAC5", "#171F24",
                                                      "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                      "#3a4f5c", 150, 20, 2, 0, 2)

    def ArcParamsGroupBox_Objects(self):
        '''
        Adds input widgets to the Arc Params group box
        '''

        #Radius
        Font = Fonts.LabelFonts()
        self.RadiusInput = InputObjects.InputObjects(self.groupBox_ArcParams,
                                                     "Arc Radius", "Radius", Font,
                                                     "#03DAC5", "#171F24",
                                                     "QLineEdit", None, None, "white",
                                                     "#3a4f5c", 100, 20, 1, 0, 2)

        # Rotation direction
        # Point Layer
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["CCW", "CW"]
        self.ArcRotationDirection = InputObjects.InputObjects(self.groupBox_ArcParams,
                                                    "Arc Rotation", "Rotation", Font,
                                                    "#03DAC5", "#171F24",
                                                    "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                    "#3a4f5c", 100, 20, 2, 0, 2)

    def PolygonGroupBox_Objects(self):
        '''
        Adds widgets objects to Polygons group box
        '''

        # PlanNumber
        Font = Fonts.LabelFonts()
        self.PlanNumberInput = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                         "Plan Number", "PlanNum", Font,
                                                         "#03DAC5", "#171F24",
                                                         "QLineEdit", None, None, "white",
                                                         "#3a4f5c", 100, 20, 1, 0, 2)

        # Lot identifier
        self.LotIdent = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                         "Lot Number", "LotNum", Font,
                                                         "#03DAC5", "#171F24",
                                                         "QLineEdit", None, None, "white",
                                                         "#3a4f5c", 100, 20, 2, 0, 2)

        # Area
        self.LotArea = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Lot Area (m2)", "Area", Font,
                                                  "#03DAC5", "#171F24",
                                                  "QLineEdit", None, None, "white",
                                                  "#3a4f5c", 100, 20, 3, 0, 2)
        #Polygon Type comboBox
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["PARCEL", "EASEMENT", "ROAD"]
        self.PolygonType = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                              "Type", "Rotation", Font,
                                                              "#03DAC5", "#171F24",
                                                              "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                              "#3a4f5c", 100, 20, 4, 0, 2)
        # Description
        self.LotDescription = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Lot Description", "Description", Font,
                                                  "#03DAC5", "#171F24",
                                                  "QLineEdit", None, None, "white",
                                                  "#3a4f5c", 230, 20, 5, 0, 1)

        # Point List
        self.PointList = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Point List", "PointList", Font,
                                                  "#03DAC5", "#171F24",
                                                  "QLineEdit", None, None, "white",
                                                  "#3a4f5c", 230, 20, 6, 0, 1)
        self.PointList.Label.setToolTip("List of comma separated vertexes\n making up the polyon")
        self.PointList.InputObj.setToolTip("List of comma separated vertexes\n making up the polyon\n-> Point Numbers")
        self.PointList.InputObj.returnPressed.connect(self.ViewPolygon)

        # VIew Polygon button
        Font = Fonts.ButtonFont()
        self.ViewPolyButton = ButtonObjects.Add_QButton(self.groupBox_PolyInput, "View",
                                                         "ViewPolyButton", Font,
                                                         self.ViewPolygon, 100, 30,
                                                         7, 0, 1, 1, "#3700B3", "white", "#90adf0")


        # Commit Polygon button
        self.CommitPolyButton = ButtonObjects.Add_QButton(self.groupBox_PolyInput, "Commit",
                                                        "ViewPolyButton", Font,
                                                        self.CommitPolygon, 100, 30,
                                                        7, 2, 1, 1, "#3700B3", "white", "#90adf0")

    def TraverseOpsGroupBox_Objects(self):
        '''
        Sets up buttons in the Traverse Functions GroupBox
        '''

        # Close Traverse Button
        Font = Fonts.ButtonFont()
        self.NewTraverseButton = ButtonObjects.Add_QButton(self.groupBox_Traverses, "New / Reset Traverse",
                                                        "NewTravButton", Font,
                                                        self.NewTraverse, 100, 50,
                                                        1, 0, 1, 1, "#3700B3", "white", "#90adf0")

        #CLose Traverse Button
        self.TravCloseButton = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Close Traverse",
                                                        "CloseTravButton", Font,
                                                        self.TraverseClose, 100, 50,
                                                        1, 1, 1, 1, "#3700B3", "white", "#90adf0")

        # Commit Traverse Button
        self.CommitTraverse = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Commit Traverse",
                                                        "CommitTravButton", Font,
                                                        self.CommitCurrentTraverse, 100, 50,
                                                        1, 2, 1, 1, "#3700B3", "white", "#90adf0")

        # Show Traverse Button
        self.ShowTraverse = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Show Traverses",
                                                        "ShowTravButton", Font,
                                                        TraverseOperations.CommitTraverse, 100, 50,
                                                        1, 3, 1, 1, "#3700B3", "white", "#90adf0")

    #################################################################################################
    #################################################################################################
    #Scene functions
        #Delete Objects
        #Zoom functions
        #MOuse Modes

    #################################################################################################
    #################################################################################################
    def keyPressEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if event.key() == Qt.Key_Delete:
            self.deleteSelectedObject()

        if modifiers == (QtCore.Qt.ControlModifier) and event.key() == Qt.Key_A:
            print("Clicked")

        if modifiers == (QtCore.Qt.ControlModifier) and event.key() == Qt.Key_Z:
            print("Clicked")

        if event.key() == Qt.Key_Escape and \
                self.view.JoinPoints and \
                self.view.CurrentPoint is not None:
            self.view.CurrentPoint = None
            self.view.scene.removeItem(self.view.MouseLine.mouseLine)


    def deleteSelectedObject(self):
        '''
        Deletes selected objects
        :return:
        '''
        for item in self.view.scene.selectedItems():
            rect = item.boundingRect()
            itemType = type(item)

            #remove items from traverse
            if itemType == QtWidgets.QGraphicsLineItem:
                try:
                    self.traverse.Lines = self.removeFromTraverse(rect, self.traverse.Lines)
                except AttributeError:
                    pass
            elif itemType == QtWidgets.QGraphicsEllipseItem:
                try:
                    self.traverse.Points = self.removeFromTraverse(rect, self.traverse.Points)
                except AttributeError:
                    pass

            #remove items from display
            self.view.scene.removeItem(item)


    def removeFromTraverse(self, rect, object):
        '''
        loop through line objects in traverse and delete
        :param rect:
        :return:
        '''

        DeleteKeys = []
        for key in object.__dict__.keys():
            if key == "LineNum" or key == "ArcNum":
                continue
            child = object.__getattribute__(key)
            if rect == child.BoundingRect:
                DeleteKeys.append(key)
                break

        if len(DeleteKeys) > 0:
            object = self.DeleteObjectKeys(object, DeleteKeys)

        return object

    def DeleteObjectKeys(self, object, DeleteKeys):

        for key in DeleteKeys:
            #delete points associated labels
            if hasattr(object.__getattribute__(key).GraphicsItems, "PointNumLabel"):
                item = object.__getattribute__(key).GraphicsItems.PointNumLabel
                self.view.scene.removeItem(item)
                index = self.traverse.refPnts.index(key)
                del self.traverse.refPnts[index]
            if hasattr(object.__getattribute__(key).GraphicsItems, "CodeLabel"):
                self.view.scene.removeItem(object.__getattribute__(key).GraphicsItems.CodeLabel)
            object.__delattr__(key)

        return object

    """
    def wheelEvent(self, event: QWheelEvent):
        
        Zoom in or out of the view.
        
        #Set event properties
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.view.setResizeAnchor(QGraphicsView.NoAnchor)
        #current scene event location
        StartPos = self.view.mapToScene(event.pos())

        #set zoom props
        delta = event.angleDelta().y()/5e5
        self.zoom += delta
        if 0.030 > self.zoom > 0.000001:

            #self.view.scale(self.zoom, self.zoom)
            view_pos = event.pos()
            self.view.scale(self.zoom, self.zoom)
            self.view.centerOn(view_pos)

            self.updateView()
            #self.view.move(scene_pos)
            print("zoom=" + str(self.zoom))

        elif self.zoom > 0.03:
            self.zoom = 0.03
            self.view.scale(self.zoom, self.zoom)
            self.updateView()
            print("zoom=" + str(self.zoom))
        elif self.zoom < 0.000001:
            self.zoom = 0.000001
            self.view.scale(self.zoom, self.zoom)
            self.updateView()
            print("zoom=" + str(self.zoom))

        #New scene positions
        EndPos = self.view.mapToScene(event.pos())

        #move scene back
        delta = EndPos - StartPos
        self.view.translate(delta.x(), delta.y())
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    
    def mousePressEvent(self, event: QMouseEvent):

        items = self.view.scene.selectedItems()
        try:
            item = self.view.itemAt(event.pos())
            #print(item.type())

            items = self.scene.itemAt(item, self.view.viewportTransform())
            print(items.y())
        except Exception:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
    
    def updateView(self):

        #print(self.zoom)
        try:
            self.view.setTransform(QtGui.QTransform().scale(self.zoom, self.zoom))
        except Exception as e:
            print(e)
    """
    def mousePointFunction(self):
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.dragAction.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.pointer.setChecked(True)
        self.view.mousePointFunction()
        #self.view.ShowSelectedParams = False

    def mouseDragFunction(self):
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.dragAction.setChecked(True)
        self.view.mouseDragFunction()
        #self.view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        #self.view.ShowSelectedParams = False

    def mouseSelectFunction(self):
        self.InsertPointsAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(True)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
        
        self.view.mouseSelectFunction()
        #self.view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        #self.view.ShowSelectedParams = False
    def mouseMeasureFunction(self):
        self.InsertPointsAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.MeasureAction.setChecked(True)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
        self.view.mouseMeasureFunction()

    def mouseJoinPointsFunction(self):
        self.InsertPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.JoinPointsAction.setChecked(True)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
        self.view.mouseJoinPointsFunction()

    def mouseInsertPointsFunction(self):
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(True)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
        self.view.mouseInsertPointsFunction()

    def mouseParrallelLineFunction(self):
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(True)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)

    def mouseTrimLineFunction(self):
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(True)
        self.IntersectionPointAction.setChecked(False)

    def mouseIntersectionPointFunction(self):
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.dragAction.setChecked(False)
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(True)

    def ShowLineParams(self):
        self.ShowSelectedParams = True

    ################################################################################################
    #Button Rest Points

    def EnterPoint(self):
        '''
        Called from Enter Point click event
        :return:
        '''
        """
        message = "Enter Point will start a new traverse.\n" \
                  "Are you sure you want to start a new traverse?\n\n" \
                  "Click Ok to continue with Enter Point"
        MessageBoxArgs = MessageBoxes.MessageBoxArgs("Enter Point Warning!",
                                                     message, "Warning", ["OK", "CANCEL"])
        worker = MessageBoxes.Worker(MessageBoxArgs)
        self.threadpool.start(worker)
        worker.signals.finished.connect(self.worker_complete)
        """
        retval = MessageBoxes.EnterPointAlert()
        #User wants to create a new traverse
        if retval == QtWidgets.QMessageBox.Ok:

            #check if there a traverse object has already been created
            if TraverseOperations.CheckTraverseExists(self):
                retval = MessageBoxes.CommitTraverseBeforeReset()
                if retval == QtWidgets.QMessageBox.Yes:
                    self.CommitCurrentTraverse()
                else:
                    TraverseOperations.RemoveCurrentTraverseFromGui(self)


            #gather point information
            PntNum = self.PointNumber.InputObj.text()
            E = self.EastingCoord.InputObj.text()
            N = self.NorthingCoord.InputObj.text()
            Elev = self.PointElevation.InputObj.text()
            Code = self.PointCode.InputObj.text()
            Layer = self.PointLayer.InputObj.currentText()

            # create point object
            point = dataObjects.Point(PntNum, E, N, N, Elev, Code, Layer)

            #create a new traverse series and add point and props
            self.traverse = TraverseOperations.NewTraverse(Layer, PntNum, True, point)


            #add point to Scene
            pointObj = LinesPoints.AddPointToScene(self.view, point, Layer)
            setattr(self.traverse.Points, PntNum, pointObj.point)

            #Update GUI point numbers
            PntNum = int(PntNum) + 1
            self.PointNumber.InputObj.setValue(PntNum)
            self.SrcPoint.InputObj.setValue(PntNum - 1)

            #update view
            #SceneRect = self.scene.sceneRect()
            #SceneRect.moveCenter(QtCore.QPointF(int(point.E*1000), int(point.NorthingScreen*1000)))
            #self.scene.setSceneRect(SceneRect)
            #self.scene.update()



    def CalcPointChecks(self):
        '''
        Calculates Points from bearing/distance and source Point
        :return:
        '''
        Code = self.PointCode.InputObj.text()
        if not hasattr(self, "traverse") or Code in self.CodeList:
            #When no traverse exists
            NewTraverse = CreateTraverseObject.CreateTraverse()
            if NewTraverse.CheckSourcePoint(self):
                self.traverse = NewTraverse.NewTraverseObject(self)
                self.CalcPointInputChecks()
            else:
                message = "On trying to create a new traverse,\n" \
                          "the Selected Source Point does not exist.\n\n" \
                          "Enter a Source Point from an already committed traverse."
                MessageBoxes.genericMessage(message, "Source Point Error")


        else:
            self.CalcPointInputChecks()



    def CalcPointInputChecks(self):
        '''
        Checks input values for point calculation
        :return:
        '''

        CalcChecks = DrawingChecks.CalculatePointsChecks(self, self.traverse)
        if len(CalcChecks.CheckReply) != 0:
            error = ""
            for err in CalcChecks.CheckReply:
                error += err + "\n"
            MessageBoxes.genericMessage(error, "Calculate Point Input Error")
        else:
            self.CalcPoint()

    def CalcPoint(self):
        '''
        Calculates Points from bearing/distance and source Point
        :return:
        '''

        #calculate point
        pointObj = LinesPoints.CalculatePoint(self, self.traverse)

        # Add point to scene
        pointSceneObj = LinesPoints.AddPointToScene(self.view, pointObj.point,
                                                    pointObj.Params.Layer)
        setattr(self.traverse.Points, pointObj.Params.PntNum, pointSceneObj.point)
        self.traverse.refPnts.append(pointObj.Params.PntNum)
        #If dead end traverse to a RM add point to CadastralPlan


        #add linework to data objects and draw on screen
        LinesPoints.LineObjects(pointObj, self)

        if pointObj.point.Code in self.CodeList:
            setattr(self.CadastralPlan.Points, pointObj.Params.PntNum, pointSceneObj.point)
        else:
            #Check if calculated point is close enough for a close
            CloseCheck = TraverseOperations.CheckTraverseClose(pointObj.point, self.traverse,
                                                               self.CadastralPlan)

            if CloseCheck.Close:
                #show close error marker with colour coding
                point = pointObj.__getattribute__("point")
                E = point.E*1000
                N = point.NorthingScreen*1000
                CloseColour = toleranceColour(CloseCheck.CloseError * 1000)
                PenColor = QtGui.QColor("silver")
                Pen = QPen(PenColor)
                Pen.setWidth(500)
                Brush = QBrush(CloseColour)
                self.CloseIndicatorPoint = QtWidgets.QGraphicsEllipseItem((E - 3000), (N - 3000), 6000, 6000)
                self.CloseIndicatorPoint.setPen(Pen)
                self.CloseIndicatorPoint.setBrush(Brush)
                self.CloseIndicatorPoint.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.CloseIndicatorPoint = self.view.Point(E, N, 6000, Pen, Brush)
                # linewidth for displayed travers
                lineWidth = 1000
                #chnage colour of traverse to indicator colour
                TraverseOperations.ColourTraverseObjects(self, lineWidth, CloseColour)
                returnValue = MessageBoxes.CloseDetectedMessage(CloseCheck)
                if returnValue == QtWidgets.QMessageBox.Yes:
                    #set traverse close point ref
                    setattr(self.traverse, "EndRefPnt", CloseCheck.ClosePointRefNum)
                    self.CloseTraverse(CloseCheck)
                else:
                    TraverseOperations.RedrawTraverse(self)
                    self.view.scene.removeItem(self.CloseIndicatorPoint)

            #update Point numbers on display
            SrcPntNum = int(pointObj.Params.PntNum)
            self.SrcPoint.InputObj.setValue(SrcPntNum)
            self.PointNumber.InputObj.setValue(SrcPntNum+1)

    def CloseTraverse(self, CloseCheck):
        '''
        Calculates the close for the current traverse
        - uses first and last point of travers
        :return:
        '''

        try:
            #N_Error, E_Error, close = TraverseClose.CalcClose(self.traverse, self.CadastralPlan)
            self.traverse.Close_PreAdjust = CloseCheck.CloseError
            Colour = toleranceColour(CloseCheck.CloseError*1000)

            returnValue = MessageBoxes.TraverseCloseInfo(CloseCheck.CloseError)
            if returnValue == QtWidgets.QMessageBox.Yes:
                TraverseClose.TraverseAdjustment(self.traverse, self.CadastralPlan,
                                                                 CloseCheck.EastError, CloseCheck.NorthError)
                #If successful adjustment throw message to tell user
                if self.traverse.Close_PostAdjust < 0.001:
                    MessageBoxes.TraverseSuccesfulAdjustment()
                    #Redraw Traverse with adjusted points
                    TraverseOperations.RedrawTraverse(self)

                    #Commit Traverse
                    self.CommitCurrentTraverse()

                else:
                    MessageBoxes.TraverseUnSuccesfulAdjustment(self.traverse.Close_PostAdjust)

            else:
                # Redraw Traverse with adjusted points
                TraverseOperations.RedrawTraverse(self)
                self.view.scene.removeItem(self.CloseIndicatorPoint)

                # Commit Traverse
                self.CommitCurrentTraverse()



        except IndexError as e:
            print(e)

            MessageBoxes.NoTraverseError()




    ################################################################################
    #Polygon
    def ViewPolygon(self):
        '''
        Called from View button in Polygon Group Box
        :return:
        '''

        Polygon = ViewPolygon.ViewPolygon(self)
        if Polygon.Polygon.CentreEasting is not None:
            self.Polygon = Polygon.Polygon
            #create polygon label and place at centre
            if self.Polygon.PolyType == "PARCEL":
                PolyLabel = "LOT " + self.Polygon.LotNum + "\n" + self.Polygon.PlanNumber +\
                    "\nArea: " + self.Polygon.AreaDp + "m2"
            else:
                PolyLabel = self.Polygon.Description
            #add polygon label
            self.PolygonLabel(PolyLabel)

            #polygon screen rect object
            width = (max(Polygon.Polygon.VertexEastings)+5) - \
                    (min(Polygon.Polygon.VertexEastings)-5)
            height = (max(Polygon.Polygon.VertexNorthingsScreen)+5) -\
                      (min(Polygon.Polygon.VertexNorthingsScreen)-5)
            rect = QtCore.QRectF(int((min(Polygon.Polygon.VertexEastings)-5)*1000),
                               int((max(Polygon.Polygon.VertexNorthingsScreen)+5)*1000),
                               int(width*1000), int(height*1000))

            #rect = self.scene.itemsBoundingRect()


            self.view.ensureVisible(rect)
            self.view.fitInView(rect, Qt.KeepAspectRatio)
            self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.view.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            #self.view.setTransform(QtGui.QTransform())

    def PolygonLabel(self, PolyLabel):
        '''
        Sets label for selected polygon
        :param PolyLabel:
        :return:
        '''


        PolyScreenLabel = self.view.scene.addText(PolyLabel)
        width = PolyScreenLabel.boundingRect().width()*100
        height = PolyScreenLabel.boundingRect().height()*100
        PolyScreenLabel.setPos((int(self.Polygon.CentreEasting * 1000) -
                                (width)/2),
                               (int(self.Polygon.CentreNorthingScreen * 1000) -
                                (height)/2))

        PolyScreenLabel.setDefaultTextColor(Qt.red)
        PolyScreenLabel.setFont(QtGui.QFont("Segoe UI", 1000, ))
        PolyScreenLabel.setTextWidth(PolyScreenLabel.boundingRect().width())
        PolyScreenLabel.setFlag(QGraphicsItem.ItemIsMovable, True)
        PolyScreenLabel.setFlag(QGraphicsItem.ItemIsSelectable, True)

        # Set text alignment
        format = QtGui.QTextBlockFormat()
        format.setAlignment(Qt.AlignCenter)
        cursor = PolyScreenLabel.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        PolyScreenLabel.setTextCursor(cursor)
        setattr(self.Polygon, "ScreenLabel", PolyScreenLabel)

    def CommitPolygon(self):
        '''
        Adds viewed polygon to Polygons object
        :return:
        '''

        setattr(self.CadastralPlan.Polygons, self.Polygon.LotNum, self.Polygon)
        #print("Polygon Commitetd")

    def bearingCheck(self, bearing):
        '''
        chececks bearing is ok to use
        checks for right number of digits after decimal point
        and that 0<=bearing<360
        :return:
        '''

        #check mmss format
        #try:
        if len(bearing.split(".")) > 1:
            if len(bearing.split(".")[1]) != 4 or len(bearing.split(".")[1]) != 2:
                self.bearingFormatError()
                return False

        #check bearing in range
        if 360 <= float(bearing) or float(bearing) < 0 :
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Bearing Format Error:")
            msg.setInformativeText("Bearing format must be d.mmss")
            msg.setWindowTitle("Bearing Error")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.close()
            returnValue = msg.exec()
            if returnValue == QtWidgets.QMessageBox.Ok:
                msg.close()
            return False
        #except IndexError:
        #    pass

        return True


    def bearingFormatError(self):
        '''

        :param self:
        :return:
        '''

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Bearing Format Error:\nBearing format must be d.mmss!")
        msg.setWindowTitle("Bearing Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.close()
        returnValue = msg.exec()
        if returnValue == QtWidgets.QMessageBox.Ok:
            msg.close()
        return False

    ##########################################################################
    #TRaverse operation buttons

    def CommitCurrentTraverse(self):
        '''
        Commits traverse to objects
        :return:
        '''

        if hasattr(self, "traverse") and len(self.traverse.Points.__dict__.keys())>0:
            try:
                self.view.scene.removeItem(self.CloseIndicatorPoint)
            except AttributeError:
                pass
            TraverseOperations.CommitTraverse(self)
            # remove traverse attribute
            delattr(self, "traverse")
        else:
            message = "No traverse to commit!"
            MessageBoxes.genericMessage(message, "Traverse Commit Error.")

        #print("")

    def NewTraverse(self):
        '''
        Creates a new Traverse and resets current
        Give option to commit current traverse
        Throws a form
        :return:
        '''

        self.traverse = dataObjects.Traverse(False, None)

    def TraverseClose(self):

        self.CloseTraverse()

    def worker_complete(self, button):
        self.ButtonEvent = button

    def JoinPoints(self):
        PointsJoin = True




def SetLinePen(line, colour, linewidth):
    '''
    Sets colour of line
    :param line:
    :return:
    '''
    #QtGui.QColor.
    Pen = QPen(colour)
    Pen.setWidth(linewidth)
    line.setPen(Pen)

    return line




def PenBrushProps(Layer):
    '''
    Sets Pen and brush properties for a specific layer
    :param Layer:
    :return:
    '''

    # set pen colour
    if Layer == "BOUNDARY":
        Pen = QPen(Qt.cyan)
        Pen.setWidth(500)
        Brush = QBrush(Qt.cyan)
    elif Layer == "REFERENCE MARKS":
        Pen = QPen(Qt.white)
        Pen.setWidth(500)
        Brush = QBrush(Qt.white)
    elif Layer == "EASEMENT":
        Pen = QPen(Qt.green)
        Pen.setWidth(500)
        Brush = QBrush(Qt.green)

    return Pen, Brush

def toleranceColour(measure):
    '''
    Set colour for an object based on measure
    :param measure: 
    :return: 
    '''

    # set measure colour
    if measure < 5:
        colour = QtGui.QColor("#0f961f")
    elif measure < 10:
        colour = QtGui.QColor("#3c67de")
    elif measure < 15:
        colour = QtGui.QColor("#EDF904")
    elif measure < 20:
        colour = QtGui.QColor("#F99605")
    else:
        colour = QtGui.QColor("#f90505")

    return colour



'''
def MainGroupBoxFont():
    font = QtGui.QFont()
    font.setFamily()

def subGroupBoxFont_1():

def subGroupBoxFont_2():

def labelFont():

def ButtonFont():
'''



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit( app.exec_() )

