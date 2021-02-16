'''
Functions to process GUI input and view polygons on Scene
'''

import CadastreClasses as DataObjects
from GUI_Objects import Fonts
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtGui import QPen, QBrush
import MessageBoxes
import numpy as np
def ViewPolygon(gui):
    '''
    Coordinates view of polygon on scene
    :param gui:
    :return:
    '''

    PolygonData = GatherGuiData(gui)

    return PolygonData

class GatherGuiData:

    def __init__(self, gui):
        '''
        Collects Polygon data from GUI
        runs checks on data
        '''

        #####################################
        #Check inputs

        #check Point List entered
        self.InputChecks(gui)
        self.PointListCheck(gui)

        #check input data
        if gui.PolygonType.InputObj.currentText() == "PARCEL":
            self.PolygonClose(gui)
            self.AreaEntered(gui)            
        else:
            self.DescriptionEntered(gui)

        #Create ploygon object
        self.createPolygonObject(gui)

        #Colour objects
        ColouredItems = ColourObjects(gui, self.Polygon)


    def createPolygonObject(self, gui):
        '''
        Creates Polygon Object from data in gui Polygon input
        :param gui:
        :return:
        '''

        #Grab info from GUI
        PlanNumber = gui.PlanNumberInput.InputObj.text()
        LotNumber = gui.LotIdent.InputObj.text()
        AreaDp = gui.LotArea.InputObj.text()
        PolyType = gui.PolygonType.InputObj.currentText()
        Description = gui.LotDescription.InputObj.text()
        RefPntList = gui.PointList.InputObj.text().split(",")

        self.Polygon = DataObjects.Polygon(PlanNumber, LotNumber, AreaDp, None, Description,
                                           PolyType, RefPntList, None, None, None)


            
    def InputChecks(self, gui):
        '''
        Checks inputs required for all Polygon types
        :param gui: 
        :return: 
        '''
        
        #Plan Number
        PlanNumber = gui.PlanNumberInput.InputObj.text()
        if PlanNumber == "":
            PlanAlert = Dialog("Plan Number", "Enter Plan Number:")
            PlanAlert.exec_()
            PlanNumber = PlanAlert.InputText
            gui.PlanNumberInput.InputObj.setText(PlanNumber)
        
        #Lot number
        LotNumber = gui.LotIdent.InputObj.text()
        if LotNumber == "":
            LotAlert = Dialog("Lot Number", "Enter Lot Number:")
            LotAlert.exec_()
            LotNumber = LotAlert.InputText
            gui.LotIdent.InputObj.setText(LotNumber)

    def PointListCheck(self, gui):
        '''
        Checks whether the point list is the right format or exists
        if items are selected and no point list asks user whether to use selection
            and then constructs a point list from selected lines
        :param gui:
        :return:
        '''

        if gui.PointList.InputObj.text().split(",")[0] == '':
            items = gui.view.scene.selectedItems()
            if len(items) > 0:
                self.QueryUserOnSelection(items, gui)
            else:
                # raise QDialog to enter point list
                PointList = Dialog("Polygon PointList", "Enter Vertex Point List:")
                PointList.exec_()
                gui.PointList.InputObj.setText(PointList.InputText)

    def DescriptionEntered(self, gui):
        '''
        Checks if a description entered for road or Easement
        :param gui:
        :return:
        '''

        if gui.LotDescription.InputObj.text() == "":
            Description = Dialog(self.PolyType + " Description", "Enter " + self.PolyType + "Description:")
            Description.exec_()
            gui.LotDescription.InputObj.setText()

    def QueryUserOnSelection(self, items, gui):
        '''
        Raise a message box for user to use selection
        :param items:
        :return:
        '''

        #Throw message box
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setWindowTitle("Use Current Selection?")
        msg.setText("Do you want to use current selection for Polygon?\n"
                    "Were lines selected in order?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        retval = msg.exec_()

        if retval == QtWidgets.QMessageBox.Yes:
            self.RetrievePointListFromLines(items, gui)
        else:
            #raise QDialog to enter point list
            PointList = Dialog("Polygon PointList", "Enter Vertex Point List:")
            PointList.exec_()
            gui.PointList.InputObj.setText(PointList.InputText)

    def RetrievePointListFromLines(self, items, gui):
        '''
        Uses selected lines to construct point list
        :param items:
        :param gui:
        :return:
        '''

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Program Info")
        msg.setText("Using a selection to construct a vertex list for a ploygon is not implemented yet.\n"
                    "Points need to be entered manually.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        retval = msg.exec_()

        # raise QDialog to enter point list
        PointList = Dialog("Polygon PointList", "Enter Vertex Point List:")
        PointList.exec_()
        gui.PointList.InputObj.setText(PointList.InputText)

    def PolygonClose(self, gui):
        '''
        Checks if the pointlist of the polygon closes
        :return:
        '''

        RefPntList = gui.PointList.InputObj.text().split(",")
        if RefPntList[0] != RefPntList[-1]:
            RefPntList.append(RefPntList[0])

        RefPointStr = ""
        for point in RefPntList:
            RefPointStr += point+","

        RefPointStr = RefPointStr[:-1]
        gui.PointList.InputObj.setText(RefPointStr)

    def AreaEntered(self, gui):
        '''
        Check whether a parcel are was entered for a land parcel
        :return:
        '''

        if gui.LotArea.InputObj.text() == "":
            Area = Dialog("Parcel Area", "Enter Parcel Area (m2):")
            Area.exec_()
            gui.LotArea.InputObj.setText(Area.InputText)



class Dialog(QDialog):
    def __init__(self, WindowTitle, InfoText):
        super().__init__()

        self.WindowTitle = WindowTitle
        self.InfoText = InfoText
        self.setGeometry(500,500,200,100)
        self.setWindowTitle(WindowTitle)
        self.setAutoFillBackground(True)
        self.setObjectName("Dialog")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint  # hides the window controls
            | QtCore.Qt.SplashScreen  # this one hides it from the task bar!
        )
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: #5e94b8;")

        #Add Text to dialog
        self.InfoText = QtWidgets.QLabel(self)
        self.InfoText.setText(InfoText)
        self.InfoText.setStyleSheet("color: white;")
        Font = Fonts.LabelFonts()
        self.InfoText.setFont(Font)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.InfoText)
        self.setLayout(self.layout)

        #Add text input box
        self.Input = QtWidgets.QLineEdit(self)
        self.Input.setText("")
        self.Input.setStyleSheet("color: black; background-color:white")
        self.Input.setFont(Font)
        self.layout.addWidget(self.Input)
        self.setLayout(self.layout)

        self.button = QtWidgets.QPushButton(self)
        self.button.setText("OK")
        self.button.setObjectName("Button")
        Font = Fonts.ButtonFont()
        self.button.setFont(Font)
        self.button.setMaximumSize(100, 20)
        self.button.setStyleSheet(buttonStyle())
        self.button.clicked.connect(self.ClickedOk)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)



    def ClickedOk(self):

        self.InputText = self.Input.text()
        if self.InputText == "":
            Font = Fonts.LabelFonts()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle(self.WindowTitle)
            msg.setGeometry(500,600,400,100)
            msg.setWindowFlags(
                QtCore.Qt.FramelessWindowHint  # hides the window controls
                | QtCore.Qt.SplashScreen  # this one hides it from the task bar!
            )
            msg.setText(self.WindowTitle + " Still Not Set!")
            msg.setStyleSheet("color: white; background-color: #c94134; border-radius: 30px;")
            msg.setFont(Font)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            for button in msg.findChildren(QtWidgets.QPushButton):
                button.setStyleSheet("color: black; background-color: yellow; border-radius: 5px;"
                                     "border-color: silver;")
                button.setFont(Font)
                button.setMinimumWidth(100)
            #msg.setStyleSheet("QButton{background-color: #3700B3")
            retval = msg.exec_()
        else:
            self.accept()



def buttonStyle():
    style = """
    QPushButton#Button 
        {background-color: #3700B3;
        color: white;
        border-style: inset;
        border-width: 2px;
        border-radius: 5px;
        border-color: silver;}
    QPushButton#Button:hover
        {background-color : #90adf0;}
    """

    return style


class ColourObjects:

    def __init__(self, gui, Polygon):
        '''
        Analyses vertex points to colour them for display
        Retireves there coordinates in arrays and calculates the centre point for display
        :param gui:
        :param Polygon:
        '''

        #set pen and brush properties
        self.Pen = QPen(QtCore.Qt.red)
        self.Pen.setWidth(300)
        self.Brush = QBrush(QtCore.Qt.red)

        #Get Coordinates of Vertexes
        Easting, Northing, NorthingScreen = \
            self.GetCoordinatesOfVertextes(gui, Polygon)
        Polygon.VertexEastings = Easting
        Polygon.VertexNorthings = Northing
        Polygon.VertexNorthingsScreen = NorthingScreen


        if Easting is not None:
            #Set polygon centre
            Polygon.CentreEasting = np.round(np.mean(Easting), 3)
            Polygon.CentreNorthing = np.round(np.mean(Northing), 3)
            Polygon.CentreNorthingScreen = np.round(np.mean(NorthingScreen), 3)

            #Colour lines
            self.ColourLines(gui, Polygon)

    def GetCoordinatesOfVertextes(self, gui, Polygon):
        #Set arrays to store coordinates of points
        Easting = []
        Northing = []
        NorthingScreen = []

        for RefPoint in Polygon.RefPntList:
            try:
                point = gui.CadastralPlan.Points.__getattribute__(RefPoint)
                Easting.append(point.E)
                Northing.append(point.N)
                NorthingScreen.append(point.NorthingScreen)
                #get Graphics point item and colour red
                PointItem = point.GraphicsItems.Point
                PointItem.setPen(self.Pen)
                PointItem.setBrush(self.Brush)
            except AttributeError:
                MessageBoxes.PolygonRefPointError(RefPoint)
                return None, None, None


        return Easting, Northing, NorthingScreen

    def ColourLines(self, gui, Polygon):
        '''

        :param gui:
        :param Polygon:
        :return:
        '''

        #get linesegs (start and end ref points) for polygon lines
        for i, pointS in enumerate(Polygon.RefPntList):
            try:
                pointE = Polygon.RefPntList[i+1]
                line = self.FindLineItem(gui, pointS, pointE)
                if line is not None:
                    line.setPen(self.Pen)
            except IndexError:
                pass


    def FindLineItem(self, gui, pointS, pointE):
        '''
        Finds lines in Cadastral Items matching pointS, pointE
        tries Arcs and lines
        if can't find anything matching line returns None
        :return:
        '''


        #check lines
        for key in gui.CadastralPlan.Lines.__dict__.keys():
            if key == "LineNum":
                continue
            LineObj = gui.CadastralPlan.Lines.__getattribute__(key)
            #check if lineobj matches line segment of polygon
            if pointS == LineObj.StartRef and pointE == LineObj.EndRef:
                return LineObj.GraphicsItems.Line
            elif pointE == LineObj.StartRef and pointS == LineObj.EndRef:
                return LineObj.GraphicsItems.Line
        '''
        #check arcs
        for key in gui.CadastralPlan.Arcs.__dict__.keys():
            if key == "ArcNum":
                continue
            ArcObj = gui.CadastralPlan.Arcs.__getattribute__(key)
            #check if lineobj matches line segment of polygon
            if pointS == ArcObj.StartRef and pointE == ArcObj.EndRef:
                return ArcObj.GraphicsItems.Arc
        '''
        return None




