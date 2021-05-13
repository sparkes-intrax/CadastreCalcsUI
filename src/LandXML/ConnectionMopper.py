'''
Mops up the remaining connections that were not calculated by traverse
Draws lines between existing points
Does not calculate Easements - these are filtered
Checks if both ends of the Observation to be drawn are calc'd otherwise observation is not drawn
'''

import genericFunctions as funcs
from LandXML.RefMarks import RefMarkQueries
from LandXML import PointClass

def main(CadastralPlan, LandXML_Obj):
    '''
    Coordinates calculation of remaining connections
    Should be all single connections
    Either draws the connection (if connects to already calculated points)
        - trigger error when too different to calc'd point
    :param CadastralPlan: contains the calculated Cadastral data
    :param LandXML_Obj: contains observations to mop up
    :return Cadastral Plan
    '''

    #Create Connection Mopper Object
    ConnectionMop = ObservationMop(CadastralPlan, LandXML_Obj)

    for obs in LandXML_Obj.ReducedObs:
        ConnectionMop.ObservationCalculator(obs)

class ObservationMop:

    def __init__(self, CadastralPlan, LandXML_Obj):

        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj

    def ObservationCalculator(self, Observation):
        '''
        Coordinates the seach for observation not drawn on the UI
        or added to the Cadastral Plan
        These will be the only connections remaining in LandXML_Obj.ReducedObs
        :return:
        '''
        #Set whether observation is arc or line
        if Observation.tag.replace(self.LandXML_Obj.TraverseProps.Namespace,"") == \
                'ReducedObservation':
            self.Arc = False
        else:
            self.Arc = True

        #Get start and end point of Observation
        self.StartRef, self.EndRef, Flip = self.FindEndPoint(Observation)
        if self.StartRef is not None:
            self.distance = self.GetDistance(Observation)
            self.bearing = self.GetBearing(Observation, Flip)
            #calculate point
            self.PointCalculation(Observation)

        print("Done")

    def FindEndPoint(self, Observation):
        '''
        Determines what the start end point of the observation is
        If both end and start of Observation are already calculated - just takes setupID
        If RM with no end not calc'd - sets already calc'd point as startpoint
        :return:
        '''
        try:
            SetupID = Observation.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            TargetID = Observation.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        except AttributeError:
            return None, None, None

        if hasattr(self.CadastralPlan.Points, SetupID) and \
            hasattr(self.CadastralPlan.Points, TargetID):
            #Observation between 2 already calc'd points
            return SetupID, TargetID, False
        elif hasattr(self.CadastralPlan.Points, SetupID):
            #CadastralPlan only contains the setupid point
            return SetupID, TargetID, False
        elif hasattr(self.CadastralPlan.Points, TargetID):
            #Contains
            return TargetID, SetupID, True
        else:
            return None, None, None



    def GetDistance(self, Observation):
        '''
        Gets distance for obs
        If arc true, calculates chord distance. LandXML gives the arc
        :return:
        '''
        if not self.Arc:
            return Observation.get("horizDistance")
        else:
            ArcLength = Observation.get("length")
            Radius = Observation.get("radius")
            return funcs.CalcChordLength(Radius, ArcLength)

    def GetBearing(self, Observation, Flip):
        '''
        Gets bearing of obs, rotates if targetID is start of connection
        :param Observation:
        :return:
        '''
        #retrieve bearing of observation
        if self.Arc:
            bearing = Observation.get("chordAzimuth")
        else:
            bearing = Observation.get("azimuth")

        #Flip bearing if required
        if Flip:
            bearing = str(funcs.FlipBearing(float(bearing)))
            if len(bearing.split(".")[1]) == 1 or \
                    len(bearing.split(".")[1]) == 3:
                bearing += "0"

        return bearing

    def PointCalculation(self, Observation):
        '''
        Calculates the end point of the connection
        :return: 
        '''

        PointObj = PointClass.Points(self.LandXML_Obj, self.CadastralPlan.Points)
        self.point = PointObj.CalcPoints(self.bearing, self.distance,
                                         self.StartRef, self.EndRef,
                                         Observation)



    
    def CheckClose(self):
        '''
        For when calculation is between 2 points already calc'd
        Throw message when >5mm. Colour and show
        :return: 
        '''
        
    def DrawLine(self):
        '''
        Draws the Observation in gui and adds it to the Cadastral Plan
        :return:
        '''