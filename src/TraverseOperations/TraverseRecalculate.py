'''
Recalculates a traverse using bearings and distances in the line instances
'''
import genericFunctions as funcs
from numpy import sin, cos, radians
from TraverseOperations import TraverseClose


def main(traverse, CadastralPlan):
    '''
    Coordinates recalc of
    :param traverse:
    :param gui:
    :return:
    '''
    #Recalculate close
    RecalcObs = TraverseRecalc(traverse, CadastralPlan)
    RecalcObs.CalculateTraverse()
    
    #Check traverse close
    N_Error, E_Error, close = TraverseClose.misclose(traverse, CadastralPlan)
    traverse.Close_PreAdjust = round(close * 1000, 4)
    
    return traverse, N_Error, E_Error, close
    
class TraverseRecalc:
    def __init__(self, traverse, CadastralPlan):
        self.traverse = traverse
        self.CadastralPlan = CadastralPlan

    def CalculateTraverse(self):
        '''
        Coordinates traverse calculation
        :return:
        '''

        #Get Start Coords
        self.StartEasting, self.StartNorthing, self.Start_Nscreen = self.StartCoords()

        #loop through observations calculating new coords
        for obs in self.traverse.Observations:
            ObsName = obs.get("name")
            Line = self.traverse.Lines.__getattribute__(ObsName)
            Line = self.CalcPointCoords(Line)


    def StartCoords(self):
        '''
        Retrieves the starting coordinates of the traverse
        :return:
        '''
        if self.traverse.FirstTraverse:
            Point = self.traverse.Points.__getattribute__(self.traverse.StartRefPnt)
        else:
            Point = self.CadastralPlan.Points.__getattribute__(self.traverse.StartRefPnt)

        return Point.E, Point.N, Point.NorthingScreen

    def CalcPointCoords(self, Line):
        '''
        Calcs the coordinates if the end point of the Line
        :param Line:
        :return:
        '''

        #convert bearing to decimal
        bearing = funcs.bearing2_dec(Line.Bearing)
        #Return angle for point calculate and its sign for Easting and Northing
        angle, deltaE, deltaN = funcs.bearing2angle(bearing)
        # calculate change in coordinates
        deltaE = float(Line.Distance) * sin(radians(angle)) * deltaE
        deltaN = float(Line.Distance) * cos(radians(angle)) * deltaN
        Line.deltaE = deltaE
        Line.deltaN = deltaN

        #calculate new coordinates
        E = self.StartEasting + deltaE
        N = self.StartNorthing + deltaN
        N_Screen = self.Start_Nscreen - deltaN
        
        #update point
        Point = self.traverse.Points.__getattribute__(Line.EndRef)
        Point.E = E
        Point.N = N
        Point.NorthingScreen = N_Screen
        
        self.StartEasting = E
        self.StartNorthing = N
        self.Start_Nscreen = Point.NorthingScreen
        