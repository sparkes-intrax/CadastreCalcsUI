'''
Methods to calculate easements in LandXML_Obj.EasementParcels by traverse
'''

from LandXML.Easements import FindEasementStart, EasementTraverse

def main(LandXML_Obj, gui):
    '''
    Calculate Easement traverse for Easement parcels
    :param LandXML_Obj:
    :param gui:
    :return:
    '''

    #EasementTraverseObject
    EasementCalcsObj = EasementCalcs(LandXML_Obj, gui)

    ##Loop through Easements to calculate
    for Easement in LandXML_Obj.EasementParcels:
        if Easement.get("state") == "adjoining":
            continue
        EasementCalcsObj.CoordinateTraverse(Easement)



class EasementCalcs:
    def __init__(self, LandXML_Obj, gui):
        self.LandXML_Obj = LandXML_Obj
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan

    def CoordinateTraverse(self, EasementParcel):
        '''
        Calculates traverse for easement parcel
        Adds traverse to CadastralPlan and draws in UI
        :param EasementParcel:
        :return:
        '''
        #if EasementParcel.get("name") == "E27":
        #    print("stop")
        EasementStartObj = FindEasementStart.EasementStart(self.CadastralPlan, self.LandXML_Obj)
        StartObs, StartPntRef, ObsToCalc = EasementStartObj.GetStartObservation(EasementParcel)
        if StartObs is not None:

            #print(EasementParcel.get("name"))
            StartObs.getparent().remove(StartObs)
            ObsToCalc.remove(StartObs)
            EasementTravOb = EasementTraverse.Traverse(self.LandXML_Obj, self.gui, EasementParcel)
            EasementTravOb.CalculateTraverse(ObsToCalc, StartObs, StartPntRef)
            #print(StartObs.get("name"))


