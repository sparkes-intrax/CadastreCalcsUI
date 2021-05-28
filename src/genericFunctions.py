'''
Author: S Parkes
Date: 5/12/19
Version: 1.0

Generic Functions Used throughout program
'''

import numpy as np
from numpy import sin, cos, radians, arcsin

def calcLineEquation(E1, E2, N1, N2):
    '''
    calculates equation of parcel bdy line from two points
    :param E1:
    :param E2:
    :param N1:
    :param N2:
    :return: m, b
    '''

    if (E2-E1) == 0:
        b = E2 # here b is x-intercept
        m = np.inf
    elif (N2-N1) == 0:
        m = 0
        b = N2
    else:
        m = (N2-N1)/(E2-E1)
        b = N1 - m*E1

    return m, b

def calcIntersectionPoint(m1, b1, m2, b2):
    '''
    Calculate intersection coordinates between 2 lines
    :param m1:
    :param b1:
    :param m2:
    :param b2:
    :return: E, N
    '''

    if (m1-m2) == 0:
        E = 0
        N = 0
    elif m1 == np.inf:
        E = b1
        N = E*m2 + b2
    elif m2 == np.inf:
        E = b2
        N = E*m1 + b1
    else:
        E = (b2-b1)/(m1-m2)
        N = E*m1 + b1

    return E, N

def FlipBearing(bearing):
    '''
    flips bearing by 180
    :param bearing: 
    :return: 
    '''
    
    bearing += 180
    if bearing >= 360:
        bearing -= 360
        
    return round(bearing,4)

def calcBearing(startE, startN, endE, endN):
    '''
    calculates bearing of a line from 2 points
    :param startE:
    :param startN:
    :param endE:
    :param endN:
    :return:
    '''



    if endN > startN and endE > startE:
        angle = np.degrees(np.arctan((endE - startE) / (endN - startN)))
        bearing = angle
    elif endN < startN and endE > startE:
        angle = -np.degrees(np.arctan((endE - startE) / (endN - startN)))
        bearing = 180 - angle
    elif endN < startN and endE < startE:
        angle = np.degrees(np.arctan((endE - startE) / (endN - startN)))
        bearing = 180 + angle
    elif endN > startN and endE < startE:
        angle = -np.degrees(np.arctan((endE - startE) / (endN - startN)))
        bearing =360 - angle
    elif endN == startN and endE > startN:
        bearing = 90.00
    elif endN == startN and endE < startN:
        bearing = 270.00
    elif endN > startN and endE == startN:
        bearing = 0.0
    else:
        bearing = 180.0

    return bearing

def bearing2angle(bearing):
    '''
    calculates angle of line for bearing.
    Assumes Easting is always opposite

    :param startE:
    :param startN:
    :param endE:
    :param endN:
    :return:
    '''

    if bearing < 90:
        angle = bearing
        deltaE = 1
        deltaN = 1
    elif 90 < bearing < 180:
        angle = 180 - bearing
        deltaE = 1
        deltaN = -1
    elif 180 < bearing < 270:
        angle = bearing - 180
        deltaE = -1
        deltaN = -1
    elif 270 < bearing < 360:
        angle = 360 - bearing
        deltaE = -1
        deltaN = 1
    elif bearing == 0:
        deltaE = 0
        deltaN = 1
        angle = bearing
    elif bearing == 90:
        deltaE = 1
        deltaN = 0
        angle = bearing
    elif bearing == 180:
        deltaE = 0
        deltaN = -1
        angle = 0
    elif bearing == 270:
        deltaE = -1
        deltaN = 0
        angle = 90
    else:
        deltaE = 0
        deltaN = 0
        angle = bearing

    return angle, deltaE, deltaN

def Angle2Bearing(angle, deltaE, deltaN):
    '''
    Converts angle to bearing
    :param angle:
    :param deltaE:
    :param deltaN:
    :return:
    '''

    if deltaE > 0 and deltaN > 0:
        bearing = 90 - angle
    elif deltaE > 0 and deltaN < 0:
        bearing = 90 + angle
    elif deltaE < 0 and deltaN < 0:
        bearing = 270 - angle
    elif deltaE < 0 and deltaN > 0:
        bearing = 270 + angle
    elif deltaE == 0 and deltaN > 0:
        bearing = 0
    elif deltaE == 0 and deltaN < 0:
        bearing = 180
    elif deltaE > 0 and deltaN == 0:
        bearing = 90
    else:
        bearing = 270

    return bearing

def textBearing(bearing):
    '''
    dxf text bearing (bearing 90 = 0 degrees and rotating to 359.9 @ bearing 90.1 )
    '''


    if 90 > bearing > 0:
        bearing = np.abs(bearing-90)
    elif 270 < bearing < 360:
        bearing = 90 + (360-bearing)
    elif 180 < bearing <  270:
        bearing = 180 + (270-bearing)
    elif 90 < bearing < 180:
        bearing = 270 + (180 - bearing)
    elif bearing == 90:
        bearing = 0
    elif bearing  == 0:
        bearing = 90
    elif bearing == 270:
        bearing = 180
    else:
        bearing = 270

    if 270 > bearing > 90:
        bearing = bearing + 180
        if bearing > 360:
            bearing = bearing - 360

    return bearing

def bearing2slope(bearing):
    '''
    converts bearing of line to a slope
    :param bearing:
    :return:
    '''

    if bearing < 90:
        angle = 90 - bearing


    return slope

def bearing2_DMS(bearing):
    '''
    converts bearing to a string with bearing in DMS
    :param bearing:
    :return:
    '''

    #print("bearing: " + str(bearing))
    degrees = np.floor(bearing)
    #print("degrees: " +str(degrees))
    minutes = np.floor((bearing - degrees)*60)
    seconds = int(((bearing - degrees)*60 - minutes)*60)
    if minutes == 0:
        DMS = str(int(degrees)) + '.00'
    elif minutes < 10:
         DMS = str(int(degrees)) + '.0' + str(int(minutes))
    else:
        DMS = str(int(degrees)) + '.' + str(int(minutes))
        
    if seconds == 0:
        DMS += "00"
    elif seconds < 10:
        DMS += "0" + str(seconds)
    else:
        DMS += str(seconds)


    return DMS

def bearing2_dec(bearing):
    '''
    converts bearing from DMS to dec - input form is d.mmss

    :param bearing: str
    :return:
    '''

    #get degrees
    degrees = bearing.split(".")[0]
    if len(bearing.split(".")) == 1:
        minutes = "0"
        seconds = "0"
    elif len(bearing.split(".")[1]) == 2:
        minutes = bearing.split(".")[1]
        seconds = "0"
    else:
        minutes = bearing.split(".")[1][0:2]
        seconds = bearing.split(".")[1][2:]

    bearing_dec = float(degrees) + float(minutes)/60 + float(seconds)/3600

    return bearing_dec

def CalcChordLength(radius, arcLength):
    '''
    LandXML provides the arc length for an arc connection
    This functions calculated the chord length from the arc length and radius
    :param arcLength: length of arc segeent
    :return: chord length - distance
    '''
    return 2 * float(radius) * sin(float(arcLength) / (2 * float(radius)))

def CalcArcLength(radius, chord):
    return 2 * float(radius) * arcsin(float(chord)/(2 * float(radius)))

class ArcCentreCoords:

    def __init__(self, pointS, pointE, radius, rotation):
        '''
        Calculates arc centre coorindates from the chord points and the radius
        :param pointS: Start point object of choord
        :param pointE: End point object of chord
        :param rotation: rotation direction from start to end of chord (CCW or CW)
        :param radius: radius of arc
        '''

        '''
        Problems with slope = 0 ie bearing of 90 or 270 delta's = radius or zero
        slope = inf bearing 180 or 0
        -> these need to be special cases that are handled differently
        
        Still problems with start and end points -> check min-chord coordinates 
        '''
        self.ChordLength = self.CalcChordLength(pointS, pointE)
        ChordMidPoint = LineMidPoint(pointS, pointE)
        #bearing of bisector
        BisectorBearing = self.Calc_BisectorBearing(pointS, pointE)

        #distance from chord mid point to center of circle
        d = np.sqrt(float(radius)**2 - (self.ChordLength/2)**2)

        #get angle for calculations and sign of deltaE and deltaN
        angle, DeltaE, DeltaN = bearing2angle(BisectorBearing)

        #calculate deltaE and deltaN
        self.DeltaE = d * np.sin(np.radians(angle))# * DeltaE
        self.DeltaN = d * np.cos(np.radians(angle))# * DeltaN
        
        #Get Northing coordinate of centre of circle
        self.CentreNorthing = self.CentreNorthingCoord(pointS, pointE, ChordMidPoint, rotation)
        self.CentreNorthingScreen = self.CentreNorthingScreenCoord(pointS, pointE,
                                                                   ChordMidPoint, rotation)
        # Get Easting coordinate of centre of circle
        self.CentreEasting = self.CentreEastingCoord(pointS, pointE, ChordMidPoint, rotation)



    def CalcChordLength(self, pointS, pointE):
        return np.round(np.sqrt((pointS.E - pointE.E)**2 + (pointS.N - pointE.N)**2),3)

    def Calc_BisectorBearing(self, pointS, pointE):
        ChordBearing = calcBearing(pointS.E, pointS.N, pointE.E, pointE.N)
        BisectorBearing = ChordBearing + 90

        if BisectorBearing >= 360:
            BisectorBearing = BisectorBearing - 360

        return BisectorBearing

    def CentreNorthingCoord(self, pointS, pointE, ChordMidPoint, rotation):

        if (pointE.E - pointS.E) > 0 and rotation == "CW":
            Nc = ChordMidPoint.N - self.DeltaN
        elif (pointE.E - pointS.E) < 0 and rotation == "CW":
            Nc = ChordMidPoint.N + self.DeltaN
        elif (pointE.E - pointS.E) > 0 and rotation == "CCW":
            Nc = ChordMidPoint.N + self.DeltaN
        elif (pointE.E - pointS.E) < 0 and rotation == "CCW":
            Nc = ChordMidPoint.N - self.DeltaN
        else:
            Nc = ChordMidPoint.N
            
        return Nc

    def CentreNorthingScreenCoord(self, pointS, pointE, ChordMidPoint, rotation):
        '''
        flips northings chords for screen coordinates
        :param pointS:
        :param pointE:
        :param ChordMidPoint:
        :param rotation:
        :return:
        '''

        if (pointE.E - pointS.E) > 0 and rotation == "CW":
            Nc = ChordMidPoint.NorthingScreen + self.DeltaN
        elif (pointE.E - pointS.E) < 0 and rotation == "CW":
            Nc = ChordMidPoint.NorthingScreen - self.DeltaN
        elif (pointE.E - pointS.E) > 0 and rotation == "CCW":
            Nc = ChordMidPoint.NorthingScreen - self.DeltaN
        elif (pointE.E - pointS.E) < 0 and rotation == "CCW":
            Nc = ChordMidPoint.NorthingScreen + self.DeltaN
        else:
            Nc = ChordMidPoint.NorthingScreen

        return Nc

    def CentreEastingCoord(self, pointS, pointE, ChordMidPoint, rotation):

        if (pointE.N - pointS.N) > 0 and rotation == "CW":
            Ec = ChordMidPoint.E + self.DeltaE
        elif (pointE.N - pointS.N) < 0 and rotation == "CW":
            Ec = ChordMidPoint.E - self.DeltaE
        elif (pointE.N - pointS.N) > 0 and rotation == "CCW":
            Ec = ChordMidPoint.E - self.DeltaE
        elif (pointE.N - pointS.N) < 0 and rotation == "CCW":
            Ec = ChordMidPoint.E + self.DeltaE
        else:
            Ec = ChordMidPoint.E

        return Ec
    
class ArcAngles:
    
    def __init__(self, SrcPoint, EndPoint, CentreCoords, rotation):
        '''
        Calculates the start and end angles for an arc
        Used for arc objects in DXF format
        :param SrcPoint: 
        :param EndPoint: 
        '''
        self.SrcPoint = SrcPoint
        self.EndPoint = EndPoint
        self.CentreCoords = CentreCoords
        self.rotation = rotation
        
        #Calculate Angles
        self.StartAngle, self.EndAngle = self.CalcAngles()
    
    def CalcAngles(self):
        '''
        Calculates the angles for the arc
        :return: 
        '''

        # start Angle
        BaseAngle = self.Quadrant(self.SrcPoint, self.CentreCoords)
        deltaE = abs(self.SrcPoint.E - self.CentreCoords.CentreEasting)
        deltaN = abs(self.SrcPoint.N - self.CentreCoords.CentreNorthing)
        StartAngle = self.arcTan(deltaE, deltaN, BaseAngle) + BaseAngle
        #StartN = np.array(self.SrcPoint.N) - np.array(self.CentreCoords.CentreNorthing)
        #StartE = np.array(self.SrcPoint.E) - np.array(self.CentreCoords.CentreEasting)
        #StartAngle = np.degrees(np.arctan2(StartN, StartE))
        # end Angle
        BaseAngle = self.Quadrant(self.EndPoint, self.CentreCoords)
        deltaE = abs(self.EndPoint.E - self.CentreCoords.CentreEasting)
        deltaN = abs(self.EndPoint.N - self.CentreCoords.CentreNorthing)
        EndAngle = self.arcTan(deltaE, deltaN, BaseAngle) + BaseAngle
        #EndN = np.array(self.EndPoint.N) - np.array(self.CentreCoords.CentreNorthing)
        #EndE = np.array(self.EndPoint.E) - np.array(self.CentreCoords.CentreEasting)
        #EndAngle = np.degrees(np.arctan2(EndN, EndE))
        
        if self.rotation == "CW":
            return EndAngle, StartAngle
        else:
            return StartAngle, EndAngle

    def Quadrant(self, Point, Centre):

        if Point.E > Centre.CentreEasting and Point.N > Centre.CentreNorthing:
            BaseAngle = 0
        elif Point.E < Centre.CentreEasting and Point.N > Centre.CentreNorthing:
            BaseAngle = 90
        elif Point.E < Centre.CentreEasting and Point.N < Centre.CentreNorthing:
            BaseAngle = 180
        elif Point.E > Centre.CentreEasting and Point.N < Centre.CentreNorthing:
            BaseAngle = 270
        elif Point.E > Centre.CentreEasting and Point.N == Centre.CentreNorthing:
            BaseAngle = 0
        elif Point.E == Centre.CentreEasting and Point.N > Centre.CentreNorthing:
            BaseAngle = 90
        elif Point.E < Centre.CentreEasting and Point.N == Centre.CentreNorthing:
            BaseAngle = 180
        elif Point.E == Centre.CentreEasting and Point.N < Centre.CentreNorthing:
            BaseAngle = 270

        return BaseAngle

    def arcTan(self, deltaE, deltaN, baseAngle):

        if baseAngle == 0 or baseAngle == 180:
            return np.degrees(np.arctan(deltaN / deltaE))
        else:
            return np.degrees(np.arctan(deltaE / deltaN))
        


class LineMidPoint:
    def __init__(self, pointS, pointE):
        '''
        Calculates line mid point coords from start and end points
        :param pointS:
        :param pointN:
        '''

        self.E = (pointS.E + pointE.E)/2
        self.N = (pointS.N + pointE.N)/2
        self.NorthingScreen = ((pointS.NorthingScreen + pointE.NorthingScreen)/2)


if __name__ == "__main__":

    #file IO
    path = "d:\\UAVsInGreenfields\\DP1252867_MossVale\\"
    file = "DP1252867.xml"

    schema = "{http://www.landxml.org/schema/LandXML-1.2}" #annoying bit at start of element tags

    #info for json file to save property info
    DP = "DP1252867"
    TotalLots = 40
    fieldNotes ={"KerbType": "standard",
                 "TotalLots": TotalLots}
    json_ds = {DP: {"fieldNotes": fieldNotes,
                    "Parcels": {}}}
    #list of lots to be processed
    lotList = np.arange(1,(TotalLots+1),1)

    #dictonary to send arguments to xml processor
    kwargs = {"path" : path,
              "file" : file,
              "schema" : schema,
              "DP": DP,
              "lotList" : lotList,
              "json": json_ds}

    json_ds = main(**kwargs)