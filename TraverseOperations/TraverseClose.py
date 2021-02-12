'''
Functions to calculate and process misclose of a traverse
 - coorindated from main
 - misclose() calculates misclose
 - adjust() adjust coordinates of traverse to reduce misclose

'''

import numpy as np
import CadastreClasses as DataObjects
import genericFunctions as funcs
#from LXML_Modules import lxmlLoader
#import copy


def CalcClose(travSeries, PlanObj):
    '''
    Coordinates misclose calculations and processing
    updates travSeries
    adds travSeries to allTraverses
    adds traveSeries to points
    :param travSeries: object with traverse series info and points
    :param TargetID: close ref pnt
    :param lxmlObj:
    :param allTraverses: object storing all traverses
    :return: points
    '''

    #Add data to traverse series
    #calculate traverse misclose
    N_Error, E_Error, close = misclose(travSeries, PlanObj)

    return N_Error, E_Error, close



def misclose(travSeries, PlanObj):
    '''
    Calculates misclose of traverse
    - find ref pnt in either travSeries or points -> precedence to points as
        these are already corrected
    :param travSeries:
    :param TargetID:
    :param points:
    :param East:
    :param North:
    :return:
    '''

    # set end of traverse Coords - endPoint is the last point of the traverse, it's compared to
            # the close point (either first point of traverse (travSeries
    endPoint = travSeries.Points.__getattribute__(travSeries.refPnts[-1])
    EastEnd = endPoint.E
    NorthEnd = endPoint.N
    if travSeries.FirstTraverse and travSeries.type == "REFERENCE MARKS":
        closePoint = travSeries.Points.__getattribute__(travSeries.StartRefPnt)

    else:
        #closePointRefNum = findNearestPoint(PlanObj, EastEnd, NorthEnd)
        closePoint = PlanObj.Points.__getattribute__(travSeries.EndRefPnt)

    EastClose = float(closePoint.E)
    NorthClose = float(closePoint.N)

    misclose = np.sqrt((EastEnd - EastClose)**2 + (NorthEnd - NorthClose)**2)

    return (NorthEnd - NorthClose), (EastEnd - EastClose), misclose

def findNearestPoint(PlanObj, East, North):
    '''
    Finds the nearest point in PlanObj to the last point in the travSeries
    :param East and North: Coordinates of end of travSeries
    :param PlanObj:
    :return:
    '''

    #set lists to store distance from point and its refNum
    dist = []
    refPnt = []

    for key in PlanObj.Points.__dict__.keys():
        point = PlanObj.Points.__getattribute__(key)
        #add data to lists
        refPnt.append(key)
        distance = np.sqrt((East - point.E)**2 + (North - point.N)**2)
        dist.append(distance)

    #get index of minimum
    i = np.argmin(np.array(distance))
    refNumMin = refPnt[i]

    return refNumMin

class TraverseAdjustment:
    def __init__(self, Traverse, PlanObj, E_Error, N_Error):
        '''
        Methods to adjust a traverse to force closure using a transit method
        :param Traverse:
        :param PlanObj:
        :param E_Error:
        :param N_Error:
        '''

        #Calculate Traverse length
        self.TraverseDistance = self.TraverseLength(Traverse)

        #Adjust traverse
        Traverse = self.AdjustTraverse(Traverse, E_Error, N_Error)

        #calculate New Traverse close
        N_Error, E_Error, close = misclose(Traverse, PlanObj)
        Traverse.Close_PostAdjust = round(close, 1)
        Traverse.Distance = self.TraverseDistance

        self.Traverse = Traverse

    def TraverseLength(self, Traverse):
        '''
        From side lengths calculates the traverse length
        :param Traverse:
        :return:
        '''

        TotalTraverseDistance = 0
        for key in Traverse.Lines.__dict__.keys():
            if key != "LineNum":
                line = Traverse.Lines.__getattribute__(key)
                TotalTraverseDistance += float(line.Distance)

        return TotalTraverseDistance

    def AdjustTraverse(self, Traverse, E_Error, N_Error):
        '''
        Sequential Adjust Traverse sides to force closure -> transit method
        :param Traverse:
        :param E_Error:
        :param N_Error:
        :return:
        '''

        for key in Traverse.Lines.__dict__.keys():
            if key == "LineNum":
                continue

            #retrieve line and point object for traverse line segment
            line = Traverse.Lines.__getattribute__(key)
            deltaE = line.__getattribute__("deltaE")
            deltaN = line.__getattribute__("deltaN")
            pointS = Traverse.Points.__getattribute__(line.StartRef)
            pointE = Traverse.Points.__getattribute__(line.EndRef)

            #calculate error to be added to cumulative error for this traverse line
            LineEastingCorrection, LineNorthingCorrection = \
                self.LineSegmentCorrection(float(line.Distance), N_Error, E_Error)

            #calculate new side length correction to traverse side
            deltaE = self.ApplyCorrection(LineEastingCorrection, deltaE)
            deltaN = self.ApplyCorrection(LineNorthingCorrection, deltaN)

            #Calculate adjusted point coords
            Easting = pointS.E + deltaE
            Northing = pointS.N + deltaN
            NorthingScreen = pointS.NorthingScreen - deltaN

            Traverse = self.UpdateTraverseProperties(Traverse, Easting, Northing, NorthingScreen,
                                                     deltaE, deltaN, pointS, pointE, line)

        return Traverse

    def LineSegmentCorrection(self, distance, N_Error, E_Error):
        '''
        Calculates the error for the queried traverse side
        :param distance:
        :param N_Error:
        :param E_Error:
        :return:
        '''

        LineNorthingCorrection = (distance/self.TraverseDistance) * N_Error
        LineEastingCorrection = (distance / self.TraverseDistance) * E_Error
        return LineEastingCorrection, LineNorthingCorrection

    def ApplyCorrection(self, Error, SideLength):
        '''
        Calculates cumulative error
        Note: this is the error that is applied to end coordinates of a traverse line
        :param SideLength: Length of traverse side - either deltaE or deltaN
        '''

        if Error >= 0:
            CorrectedSide = SideLength - Error
        elif Error < 0:
            CorrectedSide = SideLength - Error

        return CorrectedSide

    def UpdateTraverseProperties(self, Traverse, Easting, Northing, NorthingScreen,
                                 deltaE, deltaN, pointS, pointE, line):
        '''
        After adjustment updates the traverse properties - point and line data.
        Point Coordinates, line length and bearing

        :return:
        '''

        #Update point coords
        setattr(pointE, "E", Easting)
        setattr(pointE, "N", Northing)
        setattr(pointE, "NorthingScreen", NorthingScreen)

        #update line properties
        lineDistance  = np.sqrt((deltaE)**2 + (deltaN)**2)
        setattr(line, "Distance", lineDistance)

        #line bearing
        lineBearing = funcs.calcBearing(pointS.E, pointS.N, pointE.E, pointE.N)
        setattr(line, "Bearing", lineBearing)

        return Traverse
'''
def adjust(travSeries, PlanObj, E_Error, N_Error):
    
    Adjusts coordinates of traverse using transit method
    :return:
    

    CloseObject = TraverseCloseObj()
    # set Correction lists
    PntKey = []
    E_sides = []
    N_sides = []

    # test cumulative error - should = E_error or N_error
    E_cumError = 0
    N_cumError = 0

    #total length of traverse
    TotalTraverseDistance = 0
    for key in travSeries.Lines.__dict__.keys():
        if key != "LineNum":
            line = travSeries.Lines.__getattribute__(key)
            TotalTraverseDistance += float(line.Distance)
    Close
    #adjust traverse
    for key in travSeries.Lines.__dict__.keys():
        if key == "LineNum":
            continue
        line = travSeries.Lines.__getattribute__(key)

        pointS = travSeries.Points.__getattribute__(line.StartRef)
        pointE = travSeries.Points.__getattribute__(line.EndRef)

        #get traverse side distance and change in Eastings/Northings
        deltaE = float(pointE.E) - float(pointS.E)
        deltaN = float(pointE.N) - float(pointS.N)

        #calculate N correctio for trav side
        N_corr = (float(line.Distance)/TotalTraverseDistance)*N_Error
        N_cumError += N_corr
        N_side = calcCorrection(deltaN, N_cumError, N_corr)
        # calculate E correction for trav side
        E_corr = (float(line.Distance)/TotalTraverseDistance)*E_Error
        E_cumError += E_corr
        E_side = calcCorrection(deltaE, E_cumError, E_corr)
        #sideDist = np.sqrt(E_side**2 + N_side**2)
        #PntKey.append(key)
        #E_sides.append(E_side)
        #N_sides.append(N_side)
        pointE.E = pointS.E + E_side
        pointE.N = pointS.N + N_side

    print("calc'd corrections sum N: " + str(np.round(N_cumError*1000,1))+"mm")
    print("N miscloses: " + str(np.round(N_Error*1000,1))+"mm")
    print("calc'd corrections sum E: " + str(np.round(E_cumError*1000,1))+"mm")
    print("E miscloses: " + str(np.round(E_Error*1000,1))+"mm")

    # apply correction
    #travSeries = UpdateCorrectedTraverse(travSeries, PntKey, E_sides, N_sides)

    
    travSeries.Easting = [travSeries.Easting[0]]
    travSeries.Northing = [travSeries.Northing[0]]
    for i, East in enumerate(E_side):
        if i < (len(E_side)-1):
            travSeries.Easting.append(travSeries.Easting[i] + E_side[i+1])
            travSeries.Northing.append(travSeries.Northing[i] + N_side[i + 1])
    

    #calculate new misclose - should be zero
    endPntRef = travSeries.refPnts[-1]
    TraverseEndPoint = travSeries.Points.__getattribute__(endPntRef)
    if travSeries.FirstTraverse:
        TraverseClosePoint = travSeries.Points.__getattribute__(travSeries.StartRefPnt)
    else:
        closePointRefNum = findNearestPoint(PlanObj, TraverseEndPoint.E, TraverseEndPoint.N)
        TraverseClosePoint = PlanObj.Points.__getattribute__(closePointRefNum)

    travSeries.traverseClose_PostAdjustment = np.sqrt((TraverseClosePoint.E - TraverseEndPoint.E)**2 +
                       (TraverseClosePoint.N - TraverseEndPoint.N)**2)
    travSeries.traverseClose_PostAdjustment = np.round(travSeries.traverseClose_PostAdjustment*1000,1)
    print("Post Adjustment Misclose: " + str(travSeries.traverseClose_PostAdjustment) + "mm")
    print("____________________________________________________________________________")
    print("")

    return travSeries

def calcCorrection(SideLength, CumulativeError, SideError):
    
    Calculates the new traverse side base don sign of correction and SideLength
    :param delta:
    :param Correction:
    :return:
    

    if SideError >= 0:
        CorrectedSide = SideLength - CumulativeError
    elif SideError < 0:
        CorrectedSide = SideLength + CumulativeError

    return CorrectedSide

def UpdateCorrectedTraverse(travSeries, PntKey, E_sides, N_sides):
    
    Corrects traverse
    :param travSeries:
    :param PntKey:
    :param E_sides:
    :param N_sides:
    :return:
    

    i=0
    for key in travSeries.Lines.__dict__.keys():
        if key == "LineNum":
            continue
        line = travSeries.Lines.__getattribute__(key)

        pointS = travSeries.Points.__getattribute__(line.StartRef)
        pointE = travSeries.Points.__getattribute__(line.EndRef)

        pointE.E = pointS.E + E_sides[i]
        pointE.N = pointS.N + N_sides[i]
        i+=1

    return travSeries
'''







