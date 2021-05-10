'''
Mops up the remaining connections that were not calculated by traverse
Draws lines between existing points
Does not calculate Easements - these are filtered
Checks if both ends of the Observation to be drawn are calc'd otherwise observation is not drawn
'''

class ObservationMop:

    def __init__(self, CadastralPlan, LandXML_Obj):

        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj

    def ObservationFinder(self):
        '''
        Coordinates the seach for observation not drawn on the UI
        or added to the Cadastral Plan
        :return:
        '''