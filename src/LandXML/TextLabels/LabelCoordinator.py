'''
Coordinates the creation of label instances to Cadastral Plan
writes labels to the drawing canvas
'''

from LandXML.TextLabels import ParcelLabel, EasementLabel, RoadLabel
from PyQt5 import QtCore

def main(LandXML_Obj, gui):
    '''
    Coordinates drawing and creation of label instances
    :param LandXML_Obj:
    :param gui:
    :return:
    '''

    LabelWriterObj = LabelWriter(LandXML_Obj, gui)
    LabelWriterObj.GetLabels()
    LabelWriterObj.DrawLabels()

class LabelWriter:
    def __init__(self, LandXML_Obj, gui):
        self.LandXML_Obj = LandXML_Obj
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan
        
    def GetLabels(self):
        '''
        Coordinates writing labels
        :return: 
        '''
        
        #Add Parcel Labels to
        ParcelLabel.LotParcelLabel(self.CadastralPlan,
                                   self.LandXML_Obj.Parcels.getchildren(),
                                   self.LandXML_Obj)

        if len(self.LandXML_Obj.RoadParcels) > 0:
            RoadLabel.RoadParcelLabel(self.CadastralPlan, self.LandXML_Obj.RoadParcels,
                                      self.LandXML_Obj)

        if len(self.LandXML_Obj.EasementParcels) > 0:
            EasementLabel.EasementParcelLabel(self.CadastralPlan, 
                                              self.LandXML_Obj.EasementParcels,
                                              self.LandXML_Obj)
        
    def DrawLabels(self):
        '''
        determines what type of parcel it is
        :param parcel: 
        :return: 
        '''

        for key in self.CadastralPlan.Labels.__dict__.keys():
            Label = self.CadastralPlan.Labels.__getattribute__(key)
            rotation = Label.Orientation
            if rotation != 0:
                rotation = self.LabelRotation(rotation)
            LabelDisplay = self.gui.view.Text(Label.Easting, Label.NorthingScreen, rotation,
                                           Label.Label)
            NewEastPos = Label.Easting*1000 - LabelDisplay.boundingRect().width()/2
            NewNorthPos = Label.NorthingScreen*1000 - LabelDisplay.boundingRect().height()/2
            LabelDisplay.setPos(NewEastPos, NewNorthPos)


    def LabelRotation(self, bearing):
        '''
        Sets rotation of line props label in QT space
        :param bearing:
        :return:
        '''

        if bearing >= 180:
            rotation = bearing - 270
        else:
            rotation = bearing - 90

        return rotation