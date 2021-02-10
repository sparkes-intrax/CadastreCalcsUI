'''
List of checks to complete before objects are drawn
'''

class CalculatePointsChecks:
    def __init__(self, gui, traverse):
        '''
        Checks if all data is ok to calculate a point
        '''

        self.CheckReply = []

        #Check Bearing entered in GUI
        self.BearingCheck(gui)

        #Check source point exists in traverse
        self.SrcPointCheck(gui, traverse)

    def BearingCheck(self, gui):
        '''
        Checks bearing is in the right format
        :param gui:
        :return:
        '''

        #get bearing from gui
        bearing = gui.BearingToCalcPoint.InputObj.text()
        if len(bearing.split(".")) > 1:
            if len(bearing.split(".")[1]) == 4 or len(bearing.split(".")[1]) == 2:
                bearing = gui.BearingToCalcPoint.InputObj.text()
            else:
                self.CheckReply.append("Bearing Format Error: Bearing format must be d.mmss!")

        #check bearing in range
        if 360 <= float(bearing) or float(bearing) < 0 :
            self.CheckReply.append("Bearing Format Error: Bearing format must be d.mmss!")

    def SrcPointCheck(self, gui, traverse):
        '''
        Checks that the source point entered in the GUI is in the traverse object
        :param gui:
        :param traverse:
        :return:
        '''

        SrcPntNum = gui.SrcPoint.InputObj.text()
        if not hasattr(traverse.Points, SrcPntNum):
            self.CheckReply.append("Entered Source Point Number Not in Traverse!")