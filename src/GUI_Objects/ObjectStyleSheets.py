'''
Sets ups style sheets for widgets used in GUI
'''

def QMenuBar():
    #qlineargradient(x1:1, y1:0, x2:0, y2:0,stop:0 #4caf50, stop:1 #303030);
    style = """
    QMenuBar {
        background-color: "#087f23"
    }
    QMenuBar::item {
        spacing: 10px;           
        padding: 10px 30px;
        background-color: #087f23;
        color: rgb(0,0,0);
        border-radius: 2px
    }
    QMenuBar::item:selected {    
        color: rgb(255,255,255);
        background-color: #272727;
    }
    QMenuBar::item:pressed {
        color: rgb(255,255,255);
        background: #272727;
    }

    /* +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ */  

    QMenu {
        background-color: #161616;   
        color: rgb(255,255,255);
        border: 1px solid black;
        padding: 10px 15px;
        margin: 1px;
        border-radius: 2px;
        spacing: 5px;
    }
    QMenu::item {
        background-color: transparent;
        border-radius: 2px;
        padding: 10px 15px;
        spacing: 5px;
    }
    QMenu::item:selected { 
        background-color: #272727;
        color: rgb(255,255,255);
        border-radius: 2px;
        padding: 10px 15px;
        spacing: 5px;
    }
    QMenu::item:pressed {
        background: #272727;
        border-radius: 2px;
        padding: 10px 15px;
        spacing: 5px;
    }
    """

    return style

def QToolBar():

    style = """
    QToolBar {background-color: #38453b;}

    """#303030qlineargradient(x1:0, y1:1, x2:0, y2:0,stop:0 #0f0f0f, stop:1 #005005)

    return style

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