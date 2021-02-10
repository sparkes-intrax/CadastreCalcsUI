'''
Functions creating QFont Objects
'''

from PyQt5.QtGui import QFont

def MajorGroupBox():
    '''
    Sets font for a major group box
    :return: QFont object
    '''

    font = QFont("Segoe UI", 12, QFont.Bold)

    return font

def MinorGroupBox():
    '''
    Sets font for a major group box
    :return: QFont object
    '''

    font = QFont("Segoe UI", 10, QFont.Bold)

    return font

def LabelFonts():
    font = QFont("Segoe UI Black", 10, )

    return font

def ButtonFont():
    font = QFont("Segoe UI Black", 10, QFont.Bold)
    return font

def comboBoxFont():
    font = QFont("Segoe UI Black", 10, )
    return font