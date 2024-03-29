'''
Main module to open form to calculate cadastre manually from pdf plan

Enables digitial traverse and checking closes
- adds numbers to points
- determine parcels from numbers added in form
- saves points and parcels to 2 separate csvs
'''

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsTextItem, \
    QFrame, QSizePolicy
import sys
from PyQt5.QtGui import QBrush, QPen, QWheelEvent, QMouseEvent
from PyQt5.QtCore import Qt, QThreadPool, QThread, QSize
import genericFunctions as funcs
import numpy as np
import CadastreClasses as dataObjects
from FileIO import Writer
from TraverseOperations import TraverseClose, CreateTraverseObject
import drawObjects

from GUI_Objects import GroupBoxes, Fonts, InputObjects, ButtonObjects, \
    ObjectStyleSheets, GraphicsView, ColourScheme, MAD_Frames, MAD_Layouts
from DrawingObjects import LinesPoints, DrawingChecks
from TraverseOperations import TraverseOperations, TraverseObject
from Polygons import ViewPolygon
import MessageBoxes
from LandXML import LandXML
from LandXML.RefMarks import RefMark_Traverse
from LandXML.Cadastre import CadastreTraverse
#import psutil

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # set up window icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("IntraxMadIcon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon.addPixmap(QtGui.QPixmap("IntraxMadIcon.ico"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("IntraxMadIcon.ico"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self.setWindowIcon(icon)
        self.setAutoFillBackground(True)

        #window properties
        self.title = "Manual & Digital Calcs"
        self.top = 30
        self.left = 30
        self.width = 1500
        self.height = 990

        self.CadastralPlan = self.initialiseDataObjects()
        self.ShowSelectedParams = False

        #Add menu bar to QMainWindow
        #self.AddMenuBar()

        #add main layout
        self.widget_layout = MAD_Layouts.MAD_Layout(self, "widget_layout")
        self.widget_layout.horizontal()
        #add main frame
        self.main_frame = MAD_Frames.MAD_Frame(widget=self,
                                               name="MAD_main_frame",
                                               frame_shape=QFrame.NoFrame,
                                               frame_shadow=QFrame.Raised,
                                               min_size=QSize(1500,990))
        self.main_frame.create_frame()
        self.main_frame.frame_size_policy(x_size_policy=QSizePolicy.Expanding,
                                             y_size_policy=QSizePolicy.Expanding,
                                             heightForWidth=True)
        self.main_layout = MAD_Layouts.MAD_Layout(self, "main_layout")
        self.main_layout.horizontal()
        #Add toggleButton



        # Add groupBoxes
        self.AddGroupBoxes()
        self.AddToolBar()
        #Add Inputs
        self.GUI_Inputs_Buttons()


        self.InitWindow()

    def initialiseDataObjects(self):
        '''
        sets up the CadastralPlan parent class
        :return:
        '''
        self.Colours = ColourScheme.Colours()
        #a list of codes to always start a new traverse
        #RMs that are dead ends - RMDHW etc
        self.CodeList = ["RMDHW", "RMGIP", "RMCB", "RMPLUG", "RMNAIL",
                         "ROCK"]
        return dataObjects.CadastralPlan()


    def InitWindow(self):




        self.view = GraphicsView.GuiDrawing(self)

        self.drawing_frame_layout.layout.addWidget(self.view)
        self.main_layout.layout.addWidget(self.drawing_frame.frame)
        self.main_layout.layout.addWidget((self.data_entry_frame.frame))
        self.widget_layout.layout.addWidget(self.main_frame.frame)

        #self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.setStyleSheet("background-color: %s;" % self.Colours.backgroundUI)
        self.show()

        self.threadpool = QThreadPool()
        #self.worker = MessageBoxes.Worker()

    def AddMenuBar(self):
        '''
        Adds a menu bar to GUI
        '''
        #export dxf/csv action
        ExportDxfCsv = QtWidgets.QAction("Export to DXF and CSV", self)
        ExportDxfCsv.triggered.connect(self.CallWriter)
        #get style sheet
        Font = Fonts.MenuBarFont()
        style = ObjectStyleSheets.QMenuBar()
        self.bar = self.menuBar()
        self.bar.setStyleSheet(style)
        fileMenu = QtWidgets.QMenu("&File", self)
        fileMenu.setStyleSheet(style)
        fileMenu.addAction(ExportDxfCsv)
        self.bar.addMenu(fileMenu)
        #fileMenu.addAction("Export to LandXML")
        #fileMenu.addAction("Export to DXF and CSV")
        ViewMenu = QtWidgets.QMenu("&View", self)
        ViewMenu.setStyleSheet(style)

        self.bar.addMenu(ViewMenu)
        self.bar.setFont(Font)
        Font = Fonts.MenuItemFont()
        fileMenu.setFont(Font)
        ViewMenu.setFont(Font)


        DataTableMenu = ViewMenu.addMenu("View Data Table")
        DataTableMenu.addAction("Current Traverse")
        DataTableMenu.addAction("All Data")
        DataTableMenu.setStyleSheet(style)
        DataTableMenu.setFont(Font)

    def AddToolBar(self):
        '''
        Adds to toolbar to GUI
        '''
        style =ObjectStyleSheets.QToolBar()
        ToolBar = self.addToolBar("MouseAction")
        ToolBar.setOrientation(QtCore.Qt.Vertical)
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

        ToolBar.setIconSize(QtCore.QSize(20, 20))
        self.drawing_frame_layout.layout.addWidget(ToolBar)
        #self.addToolBar(Qt.LeftToolBarArea, ToolBar)

    def AddGroupBoxes(self):
        '''
        adds groupboxes to the GUI window
        :return:
        '''

        #Drawing GroupBox
        Font = Fonts.MajorGroupBox()
        rect = QtCore.QRect(10, 48, 1100, 894)

        self.drawing_frame = MAD_Frames.MAD_Frame(widget=self.main_frame.frame,
                                                  name='drawing_frame',
                                                  min_size=QSize(1000,800),
                                                  max_size=QSize(16777215, 900))
        self.drawing_frame.create_frame()
        self.drawing_frame.frame = SizePolicyObj(QSizePolicy.Expanding, QSizePolicy.Expanding, self.drawing_frame.frame)
        #self.drawing_frame.frame_size_policy(x_size_policy=QSizePolicy.Expanding,
                                             #y_size_policy=QSizePolicy.Expanding,
                                             #heightForWidth=True)
        self.drawing_frame_layout = MAD_Layouts.MAD_Layout(widget=self.drawing_frame.frame,
                                                           name="drawing_frame_layout")
        self.drawing_frame_layout.horizontal()
            #(rect, "", "Drawing", Font,
            #                                           "Grid", self, self.Colours.backgroundUI,
            #                                            self.Colours.backgroundUI)
        #Points main groupbox
        self.data_entry_frame = MAD_Frames.MAD_Frame(widget=self.main_frame.frame,
                                                     name="data_entry_frame",
                                                     frame_shape=QFrame.NoFrame,
                                                     frame_shadow=QFrame.Raised
                                                     )
        self.data_entry_frame.create_frame()

        self.data_entry_layout = MAD_Layouts.MAD_Layout(widget=self.data_entry_frame.frame,
                                                        name="data_entry_layout")
        self.data_entry_layout.vertical()

        rect = QtCore.QRect(1120, 40, 350, 670)
        self.data_entry_points_frame = MAD_Frames.MAD_Frame(widget=self.data_entry_frame.frame,
                                                     name="data_entry_frame_points",
                                                     frame_shape=QFrame.NoFrame,
                                                     frame_shadow=QFrame.Raised,
                                                        max_size=QSize(350,670), min_size=QSize(350,670)
                                                     )
        self.data_entry_points_frame.create_frame()

        self.data_entry_points_layout = MAD_Layouts.MAD_Layout(widget=self.data_entry_points_frame.frame,
                                                        name="data_entry_layout")
        self.data_entry_points_layout.vertical()

        self.groupBox_Points = GroupBoxes.GUI_GroupBox(rect, "Points", "Points", Font,
                                                       "Grid", self.data_entry_points_frame.frame, self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)

        self.data_entry_points_layout.layout.addWidget(self.groupBox_Points.groupBox)
        #Enter Point GroupBox
        Font = Fonts.MinorGroupBox()
        self.groupBox_EnterPoint = GroupBoxes.GUI_GroupBox(None, "Add Point by Coordinates",
                                                           "EnterPoints", Font,
                                                           "Grid", self.groupBox_Points.groupBox,
                                                           self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)
        self.groupBox_EnterPoint.groupBox.setMaximumSize(330, 160)
        self.groupBox_EnterPoint.groupBox.setMinimumSize(330, 160)
        self.data_entry_points_layout.layout.addWidget(self.groupBox_EnterPoint.groupBox)
        #self.groupBox_Points.Layout.addWidget(self.groupBox_EnterPoint.groupBox, 2, 0, 1, 1)

        #Calculate Points GroupBox
        self.groupBox_CalcPoint = GroupBoxes.GUI_GroupBox(None, "Calculate Points",
                                                           "CalcPoints", Font,
                                                           "Grid", self.groupBox_Points.groupBox,
                                                           self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)
        self.groupBox_CalcPoint.groupBox.setMaximumSize(330, 160)
        self.groupBox_CalcPoint.groupBox.setMinimumSize(330, 160)
        self.groupBox_Points.Layout.addWidget(self.groupBox_CalcPoint.groupBox, 3, 0, 1, 1)

        #Point Info
        self.groupBox_PointInfo = GroupBoxes.GUI_GroupBox(None, "Point Information",
                                                          "PointInfo", Font,
                                                          "Grid", self.groupBox_Points.groupBox,
                                                          self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)
        self.groupBox_PointInfo.groupBox.setMaximumSize(330, 100)
        self.groupBox_PointInfo.groupBox.setMinimumSize(330, 100)
        self.groupBox_Points.Layout.addWidget(self.groupBox_PointInfo.groupBox, 4, 0, 1, 1)

        # Arc Params
        self.groupBox_ArcParams = GroupBoxes.GUI_GroupBox(None, "Arc Parameters",
                                                          "ArcParams", Font,
                                                          "Grid", self.groupBox_Points.groupBox,
                                                          self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)
        self.groupBox_ArcParams.groupBox.setMaximumSize(330, 100)
        self.groupBox_ArcParams.groupBox.setMinimumSize(330, 100)
        self.groupBox_Points.Layout.addWidget(self.groupBox_ArcParams.groupBox, 5, 0, 1, 1)
        '''
        #Polygon Input
        rect = QtCore.QRect(1120, 730, 350, 250)
        Font = Fonts.MajorGroupBox()

        self.groupBox_PolyInput = GroupBoxes.GUI_GroupBox(rect, "Polygons", "Polygons",
                                                          Font, "Grid", self,
                                                          self.Colours.GroupBoxLabelColour,
                                                       self.Colours.backgroundUI)
        #Traverse GroupBox
        rect = QtCore.QRect(10, 885, 1100, 95)

        #self.groupBox_Traverses = GroupBoxes.GUI_GroupBox(rect, "Traverse Functions",
        #                                                  "Traverses", Font, "Grid",
        #                                                  self,  self.Colours.GroupBoxLabelColour,
        #                                               self.Colours.backgroundUI)
        '''
    def GUI_Inputs_Buttons(self):
        '''
        Adds INput items and Buttons
        :return:
        '''

        #Point Number for point entered or calculated
        Font = Fonts.LabelFonts()
        self.LandXML_Button = ButtonObjects.Add_QButton(self.groupBox_Points, "LandXML",
                                                          "LandXML", Fonts.ButtonFont(),
                                                          self.ProcessLandXML, 190, 30,
                                                          0, 0, 1, 0, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

        self.PointNumber = InputObjects.InputObjects(self.groupBox_Points,
                                                     "Point Number", "PointNum", Font,
                                                     self.Colours.LabelColour, self.Colours.backgroundUI,
                                                     "QSpinBox", None, None, "white",
                                                     self.Colours.TextBackgroundColour, 90, 20, 1, 0, 1)
        self.PointNumber.InputObj.setMaximum(10000)

        #Enter Points group box
        self.EnterPointGroupBox_Objects()
        #Calc Points Group Boc
        self.CalcPointGroupBox_Objects()
        #Point Info groupBox
        self.PointInfoGroupBox_Objects()
        #Arc Params GroupBox
        self.ArcParamsGroupBox_Objects()
        #Polygon GroupBox
        #self.PolygonGroupBox_Objects()
        #Traverse Ops GroupBox
        #self.TraverseOpsGroupBox_Objects()

    def EnterPointGroupBox_Objects(self):
        '''
        Adds object to the groupBox_EnterPoint object
        '''

        #Easting Label and Input
        Font = Fonts.LabelFonts()
        self.EastingCoord = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                      "Easting", "Easting", Font,
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QLineEdit", None, None, "white",
                                                      self.Colours.TextBackgroundColour, 100, 20, 1, 0, 2)

        # Northing Label and Input
        self.NorthingCoord = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                      "Northing", "Northing", Font,
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QLineEdit", None, None, "white",
                                                      self.Colours.TextBackgroundColour, 100, 20, 2, 0, 2)

        # Elevation Label and Input
        self.PointElevation = InputObjects.InputObjects(self.groupBox_EnterPoint,
                                                       "Elevation", "Elevation", Font,
                                                       self.Colours.LabelColour, self.Colours.backgroundUI,
                                                       "QLineEdit", None, None, "white",
                                                       self.Colours.TextBackgroundColour, 100, 20, 3, 0, 2)

        #Enter Point button
        Font = Fonts.ButtonFont()
        self.EnterPointButton = ButtonObjects.Add_QButton(self.groupBox_EnterPoint, "Enter Point",
                                                          "EnterPointButton", Font,
                                                          self.EnterPoint, 190, 30,
                                                          5, 0, 2, 3, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

    def CalcPointGroupBox_Objects(self):
        '''
        Adds object to the groupBox_CalcPoints object
        '''

        #Source Point for point calculation Label and Input
        Font = Fonts.LabelFonts()
        self.SrcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                      "Source Point Number", "SrcPoint", Font,
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QSpinBox", None, None, "white",
                                                      self.Colours.TextBackgroundColour, 100, 20, 2, 0, 2)
        self.SrcPoint.InputObj.setMaximum(10000)
        # Bearing Label and Input
        self.BearingToCalcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                      "Bearing (d.mmss)", "Bearing", Font,
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QLineEdit", None, None, "white",
                                                      self.Colours.TextBackgroundColour, 100, 20, 3, 0, 2)

        self.BearingToCalcPoint.InputObj.returnPressed.connect(self.CalcPointChecks)


        # Elevation Label and Input
        self.DistanceToCalcPoint = InputObjects.InputObjects(self.groupBox_CalcPoint,
                                                       "Distance", "Distance", Font,
                                                       self.Colours.LabelColour, self.Colours.backgroundUI,
                                                       "QLineEdit", None, None, "white",
                                                       self.Colours.TextBackgroundColour, 100, 20, 4, 0, 2)
        self.DistanceToCalcPoint.InputObj.returnPressed.connect(self.CalcPointChecks)

        #Enter Point button
        Font = Fonts.ButtonFont()
        self.CalcPointButton = ButtonObjects.Add_QButton(self.groupBox_CalcPoint, "Calculate Point",
                                                          "CalcPointButton", Font,
                                                          self.CalcPointChecks, 190, 30,
                                                          5, 0, 2, 3, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)


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
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QLineEdit", ComboBoxItems, Font, "white",
                                                      self.Colours.TextBackgroundColour, 150, 20, 1, 0, 2)

        # Point Layer
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["REFERENCE MARKS", "BOUNDARY", "EASEMENT"]
        self.PointLayer = InputObjects.InputObjects(self.groupBox_PointInfo,
                                                      "Point Layer", "Layer", Font,
                                                      self.Colours.LabelColour, self.Colours.backgroundUI,
                                                      "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                      self.Colours.TextBackgroundColour, 150, 20, 2, 0, 2)

    def ArcParamsGroupBox_Objects(self):
        '''
        Adds input widgets to the Arc Params group box
        '''

        #Radius
        Font = Fonts.LabelFonts()
        self.RadiusInput = InputObjects.InputObjects(self.groupBox_ArcParams,
                                                     "Arc Radius", "Radius", Font,
                                                     self.Colours.LabelColour, self.Colours.backgroundUI,
                                                     "QLineEdit", None, None, "white",
                                                     self.Colours.TextBackgroundColour, 100, 20, 1, 0, 2)

        # Rotation direction
        # Point Layer
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["CCW", "CW"]
        self.ArcRotationDirection = InputObjects.InputObjects(self.groupBox_ArcParams,
                                                    "Arc Rotation", "Rotation", Font,
                                                    self.Colours.LabelColour, self.Colours.backgroundUI,
                                                    "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                    self.Colours.TextBackgroundColour, 100, 20, 2, 0, 2)

    def PolygonGroupBox_Objects(self):
        '''
        Adds widgets objects to Polygons group box
        '''

        # PlanNumber
        Font = Fonts.LabelFonts()
        self.PlanNumberInput = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                         "Plan Number", "PlanNum", Font,
                                                         self.Colours.LabelColour, self.Colours.backgroundUI,
                                                         "QLineEdit", None, None, "white",
                                                         self.Colours.TextBackgroundColour, 100, 20, 1, 0, 2)

        # Lot identifier
        self.LotIdent = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                         "Lot Number", "LotNum", Font,
                                                         self.Colours.LabelColour, self.Colours.backgroundUI,
                                                         "QLineEdit", None, None, "white",
                                                         self.Colours.TextBackgroundColour, 100, 20, 2, 0, 2)

        # Area
        self.LotArea = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Lot Area (m2)", "Area", Font,
                                                  self.Colours.LabelColour, self.Colours.backgroundUI,
                                                  "QLineEdit", None, None, "white",
                                                  self.Colours.TextBackgroundColour, 100, 20, 3, 0, 2)
        #Polygon Type comboBox
        ComboBoxFont = Fonts.comboBoxFont()
        ComboBoxItems = ["PARCEL", "EASEMENT", "ROAD"]
        self.PolygonType = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                              "Type", "Rotation", Font,
                                                              self.Colours.LabelColour, self.Colours.backgroundUI,
                                                              "QComboBox", ComboBoxItems, ComboBoxFont, "white",
                                                              self.Colours.TextBackgroundColour, 100, 20, 4, 0, 2)
        # Description
        self.LotDescription = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Lot Description", "Description", Font,
                                                  self.Colours.LabelColour, self.Colours.backgroundUI,
                                                  "QLineEdit", None, None, "white",
                                                  self.Colours.TextBackgroundColour, 230, 20, 5, 0, 1)

        # Point List
        self.PointList = InputObjects.InputObjects(self.groupBox_PolyInput,
                                                  "Point List", "PointList", Font,
                                                  self.Colours.LabelColour, self.Colours.backgroundUI,
                                                  "QLineEdit", None, None, "white",
                                                  self.Colours.TextBackgroundColour, 230, 20, 6, 0, 1)
        self.PointList.Label.setToolTip("List of comma separated vertexes\n making up the polyon")
        self.PointList.InputObj.setToolTip("List of comma separated vertexes\n making up the polyon\n-> Point Numbers")
        self.PointList.InputObj.returnPressed.connect(self.ViewPolygon)

        # VIew Polygon button
        Font = Fonts.ButtonFont()
        self.ViewPolyButton = ButtonObjects.Add_QButton(self.groupBox_PolyInput, "View",
                                                         "ViewPolyButton", Font,
                                                         self.ViewPolygon, 100, 30,
                                                         7, 0, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)


        # Commit Polygon button
        self.CommitPolyButton = ButtonObjects.Add_QButton(self.groupBox_PolyInput, "Commit",
                                                        "ViewPolyButton", Font,
                                                        self.CommitPolygon, 100, 30,
                                                        7, 2, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

    def TraverseOpsGroupBox_Objects(self):
        '''
        Sets up buttons in the Traverse Functions GroupBox
        '''

        # Close Traverse Button
        Font = Fonts.ButtonFont()
        self.NewTraverseButton = ButtonObjects.Add_QButton(self.groupBox_Traverses, "New / Reset Traverse",
                                                        "NewTravButton", Font,
                                                        self.NewTraverse, 100, 50,
                                                        1, 0, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

        #CLose Traverse Button
        self.TravCloseButton = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Close Traverse",
                                                        "CloseTravButton", Font,
                                                        self.TraverseClose, 100, 50,
                                                        1, 1, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

        # Commit Traverse Button
        self.CommitTraverse = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Commit Traverse",
                                                        "CommitTravButton", Font,
                                                        self.CommitCurrentTraverse, 100, 50,
                                                        1, 2, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

        # Show Traverse Button
        self.ShowTraverse = ButtonObjects.Add_QButton(self.groupBox_Traverses, "Show Traverses",
                                                        "ShowTravButton", Font,
                                                        TraverseOperations.CommitTraverse, 100, 50,
                                                        1, 3, 1, 1, self.Colours.buttonColour,
                                                          self.Colours.buttonTextColor,
                                                          self.Colours.buttonHoverColour)

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
            if itemType == QtWidgets.QGraphicsLineItem or itemType == QtWidgets.QGraphicsPathItem:
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
            if hasattr(object.__getattribute__(key).GraphicsItems, "LineLabel"):
                self.view.scene.removeItem(object.__getattribute__(key).GraphicsItems.LineLabel)
            object.__delattr__(key)

        return object

    ##################################################################
    #mouse toolbar functions
    def mousePointFunction(self):
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.dragAction.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.pointer.setChecked(True)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
        self.view.mousePointFunction()
        #self.view.ShowSelectedParams = False

    def mouseDragFunction(self):
        self.BoxSelectionAction.setChecked(False)
        self.InsertPointsAction.setChecked(False)
        self.JoinPointsAction.setChecked(False)
        self.pointer.setChecked(False)
        self.MeasureAction.setChecked(False)
        self.dragAction.setChecked(True)
        self.ParrallelLineAction.setChecked(False)
        self.TrimLineAction.setChecked(False)
        self.IntersectionPointAction.setChecked(False)
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
                if returnValue.Role == "Close && Adjust":
                    self.ApplyTraverseAdjust = True
                    #set traverse close point ref
                    setattr(self.traverse, "EndRefPnt", CloseCheck.ClosePointRefNum)
                    self.CloseTraverse(CloseCheck)
                elif returnValue.Role == "Close && NO Adjust":
                    self.ApplyTraverseAdjust = False
                    # Redraw Traverse with adjusted points
                    TraverseOperations.RedrawTraverse(self)
                    self.view.scene.removeItem(self.CloseIndicatorPoint)

                    # Commit Traverse
                    self.CommitCurrentTraverse()
                else:
                    self.ApplyTraverseAdjust = False
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

    def ProcessLandXML(self):
        self.load_landXML()
        # self.view.scene.clear()
        self.view = GraphicsView.GuiDrawing(self)
        self.groupBox_Drawing.Layout.addWidget(self.view, 1, 1, 1, 1)

        #check if landXML contains data
        if self.LandXML_Obj is None:
            return None
        #process ref marks
        if self.LandXML_Obj.LandXML_Obj.RefMarks:
            self.ref_mark_traverses()


        # self.LandXML = LandXML.LandXML(self)
    def load_landXML(self):
        self.LandXML_Obj = LandXML.LandXML(gui=self)
        self.LandXML_Obj.load_landXML()

    def ref_mark_traverses(self):
        self.thread = QThread()
        self.process_worker = RefMark_Traverse.RefMarkTraverses(gui=self,
                                                                LandXML_Obj=self.LandXML_Obj.LandXML_Obj)
        self.thread_setup(method=self.process_worker.process_ref_marks,
                          finish_method=self.cadastre_traverses, progress_complete_meth=self.debug_ref_marks_processed,
                          progress_report_meth=None, set_progress_meth=None)
        # disable landXML button
        self.LandXML_Button.button.setEnabled(False)


    def cadastre_traverses(self):
        self.thread = QThread()
        self.process_worker = CadastreTraverse.CadastreTraverses(gui=self,
                                                                LandXML_Obj=self.LandXML_Obj.LandXML_Obj)
        self.thread_setup(method=self.process_worker.calculate_traverses,
                          finish_method=self.cadastre_traverses, progress_complete_meth=self.debug_cadastre_processed,
                          progress_report_meth=None, set_progress_meth=None)
        self.thread.finished.connect(lambda: self.LandXML_Button.button.setEnabled(True))

    def debug_ref_marks_processed(self):
        print("RMs CALCULATED")

    def debug_cadastre_processed(self):
        print("CADASTRE CALCULATED")


    def thread_setup(self, method, finish_method, progress_complete_meth,
                     progress_report_meth,
                     set_progress_meth):
        '''
        genereic method for running threads and calling reporting methods
        :param method:
        :param finish_method:
        :param progress_complete_meth:
        :param progress_report_meth:
        :param set_progress_meth:
        :return:
        '''

        self.process_worker.moveToThread(self.thread)
        self.thread.started.connect(method)
        self.process_worker.finished.connect(self.thread.quit)
        self.process_worker.finished.connect(self.process_worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        if progress_report_meth is not None:
            self.process_worker.progress.connect(progress_report_meth)
        if set_progress_meth is not None:
            self.process_worker.progress.connect(set_progress_meth)

        # Start Thread
        self.thread.start()

        # Final resets
        # self.ui.pBut_processSurvey.setEnabled(False)
        # self.thread.finished.connect(lambda: self.ui.pBut_processSurvey.setEnabled(True))

        if finish_method is not None:
            self.thread.finished.connect(finish_method)
        else:
            self.thread.finished.connect(progress_complete_meth)

    def CallWriter(self):
        Writer.main(self.CadastralPlan)

def SizePolicyObj(PolicyX, PolicyY, object):

    SizePolicy = QSizePolicy(PolicyX, PolicyY)
    SizePolicy.setHorizontalStretch(0)
    SizePolicy.setVerticalStretch(0)

    SizePolicy.setHeightForWidth(object.sizePolicy().hasHeightForWidth())

    object.setSizePolicy(SizePolicy)

    return object
        

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
    #process = psutil.Process()

    # Print all loaded DLLs.
    #for i in process.memory_maps():
    #    print(i.path)
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()
    sys.exit( app.exec_() )

