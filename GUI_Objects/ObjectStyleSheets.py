'''
Sets ups style sheets for widgets used in GUI
'''

def QMenuBar():

    style = """
    QMenuBar {
        background-color: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                                          stop:0 #171F24, stop:1 darkgray);
    }
    QMenuBar::item {
        spacing: 3px;           
        padding: 2px 10px;
        background-color: #03DAC5;
        color: rgb(255,255,255);
    }
    QMenuBar::item:selected {    
        background-color: #3700B3;
    }
    QMenuBar::item:pressed {
        background: #0c0c63;
    }

    /* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */  

    QMenu {
        background-color: #efedf2;   
        color: rgb(0,0,0);
        border: 1px solid black;
        margin: 2px;
        border-radius: 5px;
    }
    QMenu::item {
        background-color: transparent;
    }
    QMenu::item:selected { 
        background-color: blue;
        color: rgb(255,255,255);
    }
    QMenu::item:pressed {
        background: #0c0c63;
    }
    """

    return style

def QToolBar():

    style = """
    QToolBar {background-color: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                                          stop:0 #171F24, stop:1 darkgray);}

    """

    return style