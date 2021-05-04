'''
Event handler for undo - ctrl-z keyPressEvent
Event handler for redo - ctrl-shift-z

Has functions for adding graphics items to a list items.
Functions add items to an undo list
As operations are undone they are added to the redo list

'''

class UndoList:

    def __init__(self, gui):
        self.GraphicsItems = []
        self.gui = gui

    def AddToList(self, GraphicsItem):
        '''
        Adds the Graphics Item to the GraphicsItems list
        Added to the front of the list
        :param GraphicsItem:
        :return:
        '''

        self.GraphicsItems.insert(0, GraphicsItem)

    def UndoGraphicsItem(self, GraphicsItem, RedoList):
        '''
        Removes the Graphics Item from the graphicsview
        Removes GraphicsItem from the GraphicsItems list
        Adds GraphicsItem to RedoList
        Class routine to remove ite from traverse
        :param GraphicsItem:
        :param RedoList:
        :return:
        '''

        #remove from scene
        self.gui.view.scene.removeItem(GraphicsItem)

        #remove item from GraphicsItems list
        self.GraphicsItems.pop(0)

        #add item to redo list
        RedoList.GraphicsItems.insert(0, GraphicsItem)

    def RedoGraphicsItem(self, GraphicsItem, RedoList):
        # add to scene
        self.gui.view.scene.addItem(GraphicsItem)
        #remove from redo list and add to undo list
        RedoList.GraphicsItems.pop(0)
        self.GraphicsItems.insert(0, GraphicsItem)


class RedoList:

    def __init__(self):
        self.GraphicsItems = []

