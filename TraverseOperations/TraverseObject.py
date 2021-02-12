'''
Sets up, adds and removes data from traverse objects
Also commits a traverse to the lxmlObj
'''

from PyQt5.QtGui import QPen, QBrush

class TraverseObject:
    def __init__(self, gui, lineWidth, Colour):
        '''
        Colours graphitems in traverse object
        :param gui: contains traverse object
        :param lineWidth:
        :param Colour:
        '''

        #lines
        if len(gui.travese.Lines.__dict__.keys()) > 0:
            self.ColourLines(gui, lineWidth, Colour)

        # Points
        if len(gui.travese.Points.__dict__.keys()) > 0:
            self.ColourLines(gui, lineWidth, Colour)

        # Arcs
        if len(gui.travese.Arcs.__dict__.keys()) > 0:
            self.ColourLines(gui, lineWidth, Colour)

    def ColourLines(self, gui, lineWidth, Colour):
        '''
        Colours lines in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''

        for key in gui.traverse.Lines.__dict__.keys():
            if key != "LineNum":
                line = gui.traverse.Lines.__getattribute__(key)
                lineItem = line.GraphicsItems.Line
                self.SetObjectPen(lineItem, Colour, lineWidth)
                gui.scene.update()

    def ColourPoints(self, gui, lineWidth, Colour):
        '''
        Colours points in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''

        for key in gui.traverse.Points.__dict__.keys():
            if key != "LineNum":
                point = gui.traverse.Lines.__getattribute__(key)
                PointItem = point.GraphicsItems.Point
                self.SetObjectPen(PointItem, Colour, lineWidth)
                self.SetObjectBrush(PointItem, Colour)
                gui.scene.update()



    def ColourArcs(self, gui, lineWidth, Colour):
        '''
        Colourts arcs in traverse object
        :param gui:
        :param lineWidth:
        :param Colour:
        :return:
        '''
        for key in self.traverse.Arcs.__dict__.keys():
            if key != "ArcNum":
                arc = self.traverse.Arcs.__getattribute__(key)
                ArcItem = arc.GraphicsItems.Arc
                self.SetLinePen(ArcItem, Colour, lineWidth)



    def SetObjectPen(self, item, colour, linewidth):
        '''
        Sets colour of item pen
        :param line:
        :return:
        '''
        # QtGui.QColor.
        Pen = QPen(colour)
        Pen.setWidth(linewidth)
        item.setPen(Pen)

    def SetObjectBrush(self, item, colour):
        '''
        Sets colour ofitem brush
        :param line:
        :return:
        '''
        # QtGui.QColor.
        Brush = QBrush(colour)
        item.setBrush(Brush)


