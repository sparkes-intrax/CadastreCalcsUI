'''
Functions to throw message boxes from form
'''

from PyQt5 import QtWidgets, QtCore
from GUI_Objects import Fonts

def EnterPointAlert():
    # Warn user that entering point starts a new traverse
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle("Enter Point Warning!")
    msg.setInformativeText("Enter Point will start a new traverse.\n"
                           "Are you sure you want to start a new traverse?\n\n"
                           "Click Ok to continue with Enter Point")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    msg = messgaeBoxFormat(msg)

    retval = msg.exec_()

    return retval

def CommitTraverseBeforeReset():
    # Warn user that entering point starts a new traverse
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Question)
    msg.setWindowTitle("Commit Current Traverse?")
    msg.setInformativeText("Do you want to commit current traverse?\n\n"
                           "If you select 'NO' the current traverse will be deleted!\n")
    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msg = messgaeBoxFormat(msg)

    retval = msg.exec_()

    return retval

def TraverseCloseInfo(close):
    # Create a message box saying what close is and
    # asking whether a transit adjustment should be applied
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("Misclose for the current Traverse: " + str(round(close * 1000, 1)) + "mm")
    msg.setInformativeText("\n\nDo you want to apply a transit adjustment to force traverse to close?")
    msg.setWindowTitle("Traverse Close Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()

    return returnValue

def TraverseSuccesfulAdjustment():
    # Create a message box saying close forced on traverse
    # asking whether a transit adjustment should be applied
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("Traverse was closed!")
    msg.setInformativeText("\nTraverse will be commited to the CadastralPlan.")
    msg.setWindowTitle("Traverse Adjusted")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()

def TraverseUnSuccesfulAdjustment(close):
    # Create a message box saying that traverse couldn't be closed
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("Traverse Could Not be Closed.\n"
                "After adjustment close was: " + str(round(close * 1000, 1)) + "mm")
    msg.setWindowTitle("Traverse Close Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()

def CloseDetectedMessage(CloseCheck):
    '''
    Triggers an message box telling user that a close was detected
    and what the close error is, and whether the user wants to close the traverse
    :param CloseCheck: object with close info
    :return:
    '''

    msgStr = "Close Point Number: " + CloseCheck.ClosePointRefNum +"\n"
    msgStr += "Close Error: " + str(round(CloseCheck.CloseError*1000, 1)) + " mm\n\n"
    msgStr += "Close Traverse on this Point?"
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("A Traverse Close was detected for the calculated point:\n\n")
    msg.setInformativeText(msgStr)
    msg.setWindowTitle("Traverse Close Detected")
    msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()

    return returnValue

def PolygonRefPointError(RefPoint):

    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setWindowTitle("Reference Point Error")
    msg.setText("Point Number " + str(RefPoint) + " does not exist!\n\n"
                                                  "Only Enter Point Numbers from Committed Traverses.")
    msg.setGeometry(500, 600, 400, 100)
    msg = messgaeBoxFormat(msg)
    # msg.setStyleSheet("QButton{background-color: #3700B3")
    retval = msg.exec_()


def NoTraverseExistsCalcPoint():
    Font = Fonts.LabelFonts()
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText("A point can not be calculated from a non-existent point!")
    msg.setInformativeText("Either calculate a point from a point that exists, or\n"
                           "enter a point to start the traverse from")
    msg.setWindowTitle("No Traverse Exists")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)

    returnValue = msg.exec()

def CalcPointChecksError(error):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText("Input Data Error For Point Calculation:")
    msg.setInformativeText(error)
    msg.setWindowTitle("Calculate Point Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()
    if returnValue == QtWidgets.QMessageBox.Ok:
        msg.close()

def NoTraverseError():
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText("No Traverse Exists!")
    msg.setWindowTitle("No Traverse Error")
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()
    if returnValue == QtWidgets.QMessageBox.Ok:
        msg.close()

def genericMessage(mes, title):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(mes)
    #msg.setInformativeText(error)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg = messgaeBoxFormat(msg)
    returnValue = msg.exec()
    if returnValue == QtWidgets.QMessageBox.Ok:
        msg.close()


def messgaeBoxFormat(msg):
    Font = Fonts.LabelFonts()
    msg.setWindowFlags(
        QtCore.Qt.FramelessWindowHint  # hides the window controls
        | QtCore.Qt.SplashScreen  # this one hides it from the task bar!
    )
    msg.setStyleSheet("color: white; background-color: #c94134; border-radius: 30px;")
    msg.setFont(Font)
    for button in msg.findChildren(QtWidgets.QPushButton):
        button.setStyleSheet("color: black; background-color: yellow; border-radius: 5px;"
                             "border-color: silver;")
        button.setFont(Font)
        button.setMinimumWidth(100)

    return msg
