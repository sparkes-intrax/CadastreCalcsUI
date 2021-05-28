'''
Draws arcs from small chord segments
'''

from numpy import abs, sin, cos, radians, concatenate
from PyQt5.QtGui import QPainterPath
import genericFunctions as funcs

class DrawArc:
    def __init__(self, pointS, pointE, CentreChords, Params):
        '''
        draws arc in GUI using small chords segments and moveto path op
        '''
        
        #get chords segments
        ArcSegments =ArcChordSegs(pointS, pointE, CentreChords,
                                     float(Params.Radius), Params.ArcRotation)

        self.arcPath = self.drawArcObject(ArcSegments.Eastings, ArcSegments.Northings)
        
    def drawArcObject(self, Eastings, Northings):

        arcPath = QPainterPath()
        for i, Easting in enumerate(Eastings):
            if i == 0:
                arcPath.moveTo(Easting*1000, Northings[i]*1000)
            else:
                arcPath.lineTo(Easting*1000, Northings[i]*1000)

        return arcPath
        
        

class ArcChordSegs:

    def __init__(self, pointS, pointE, CentreCoords, Radius, Rotation):
        '''
        Calculates a path to represent arc
        Stored in Arrays as coordinates
        1) Calculate pointS and pointE bearings from centrepoint
        2) Iteratively add 0.5 degree angles from pointS bearing until reach pointE
            a) CHeck added angle is within 0.5 degrees of centre to pointE bearing,
                    if it is stop iteration and add pointE to arc coordinate arrays
            b) Get angle and the deltaE and deltaN for new arc segment end point
                includes determines of deltaE and deltaN sign
            c) Add deltaN and deltaE to centre coords and add to array
        :param pointS: object
        :param pointE: object
        :param CentreCoords: object
        :param Radius:
        :param Rotation:
        :return:
        '''

        #chord Angle
        self.CentreToStartBearing = funcs.calcBearing(CentreCoords.CentreEasting,
                                                      CentreCoords.CentreNorthingScreen,
                                                      pointS.E, pointS.NorthingScreen)

        self.CentreToEndBearing = funcs.calcBearing(CentreCoords.CentreEasting,
                                                    CentreCoords.CentreNorthingScreen,
                                                    pointE.E, pointE.NorthingScreen)
        #create arrays to store arc coordinates
        Eastings = [pointS.E]
        Northings = [pointS.NorthingScreen]

        #set bearing variable for first arc segment
        ArcAngle = 0.1
        bearing = self.AddArcAngleSeg(Rotation, ArcAngle)
        while(abs(bearing - self.CentreToEndBearing) > 0.25):

            #get angle for calculation arc segment coordinates - also sign for deltaE and deltaN
            angle, deltaE, deltaN = funcs.bearing2angle(bearing)
            #calculate deltaE and deltaN from Centre of arc
            deltaE = float(Radius) * sin(radians(angle)) * deltaE
            deltaN = float(Radius) * cos(radians(angle)) * deltaN

            Eastings.append(CentreCoords.CentreEasting + deltaE)
            Northings.append(CentreCoords.CentreNorthingScreen + deltaN)

            ArcAngle += 0.5
            bearing = self.AddArcAngleSeg(Rotation, ArcAngle)

        #check if pointE is in arc path if not add it
        if pointE.E not in Eastings or pointE.NorthingScreen not in Northings:
            Eastings = concatenate([Eastings, [pointE.E]])
            Northings = concatenate([Northings, [pointE.NorthingScreen]])

        self.Eastings = Eastings
        self.Northings = Northings

    def AddArcAngleSeg(self, Rotation, ArcAngle):
        '''
        Adds ArcAngle to bearing StartBearing
        :param Rotation:
        :param ArcAngle:
        :return:
        '''

        if Rotation == "CW":
            bearing = self.CentreToStartBearing - ArcAngle
        else:
            bearing = self.CentreToStartBearing + ArcAngle

        if bearing >= 360:
            bearing = bearing - 360
        elif bearing < 0:
            bearing = bearing + 360

        return bearing

class ArcClass:

    def __init__(self, rotation):
        self.rotation = rotation

    def SetArcRotation(self, reverse):
        '''
        Reverses rotation of arc when src point is target in alndXML Observation
        :return:
        '''

        if self.rotation == "ccw" and reverse:
            return "CW"
        elif self.rotation == "cw" and reverse:
            return "CCW"
        elif self.rotation == "ccw":
            return "CCW"
        else:
            return "CW"

