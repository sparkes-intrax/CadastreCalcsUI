'''
Methods to manipulate and analyse data
'''
import DataLoaders, Visualisation
import numpy as np

def main(path, transData):
    '''
    Coordinates analysis
    Create class instance to store all difference data
    1) loop through dp's in transdata
    2) Load data into data classes
        - magnet - shift
        - MAD
    3) find nearest data and calculate differences
    4) Create visualisations
        - map with boundaries and colour coded markers (colour indicates error)
        - Create histogram
    5) Overall histogram
    :param path:
    :return:
    '''

    #Create data class to store all different data
    OverallAccuracy = DataAccuracy()

    #Loop through dps in transData

    for key in transData.__dict__.keys():
        DP = transData.__getattribute__(key)

        #Get Magnet Data
        File = path + "TestDps\\DP" + key + "_Magnet.csv"
        MagnetData = DataLoaders.CalcData(File, "Magnet")
        MagnetData.LoadData(DP.__getattribute__("DeltaE"), DP.__getattribute__("DeltaN"))

        #Get MAD data
        File = path + "TestDps\\DP" + key + "_MAD.csv"
        MadData = DataLoaders.CalcData(File, "MAD")
        MadData.LoadData(0, 0)

        #Analyse Data
        Accuracy = CalcDifferences(MagnetData, MadData)
        OverallAccuracy = AddAccuracyData(Accuracy, OverallAccuracy)

        #Visualise Data
        dxfFile = path+"TestDps\\DP" + key + ".dxf"
        Visualisation.MapView(Accuracy, dxfFile, key, path)
        Visualisation.Histogram(Accuracy, path, key)

    Visualisation.Histogram(OverallAccuracy, path, "All")
    print("Num Obs: " + str(len(OverallAccuracy.Distances)))

def AddAccuracyData(Accuracy, OverallAccuracy):

    for distance in Accuracy.Distances:
        OverallAccuracy.Distances.append(distance)

    return OverallAccuracy

def CalcDifferences(MagnetData, MadData):
    '''
    Calculates
    :param MagnetData:
    :param MadData:
    :return:
    '''
    #Data class to store analysis data
    AccuracyObj = DataAccuracy()

    #loop through Magnet data and find matching points
    MagE = MagnetData.__getattribute__("Easting")
    MagN = MagnetData.__getattribute__("Northing")
    MadE = MadData.__getattribute__("Easting")
    MadN = MadData.__getattribute__("Northing")

    for i, Easting in enumerate(MagE):
        Northing = MagN[i]

        #calculate distance between Magnet point and all Mad points
        Distances = np.sqrt((Northing-np.array(MadN))**2 + (Easting-np.array(MadE))**2)
        #index with minimum distance
        n_MadMin = np.argmin(Distances)
        if Distances[n_MadMin] <0.1:
            AccuracyObj.EastingAccuracy.append(Easting - MadE[n_MadMin])
            AccuracyObj.NorthingAccuracy.append(Northing - MadN[n_MadMin])
            AccuracyObj.Distances.append(Distances[n_MadMin]*1000)
            AccuracyObj.Easting.append(Easting - MagnetData.deltaE)
            AccuracyObj.Northing.append(Northing - MagnetData.deltaN)

    return AccuracyObj

class DataAccuracy:
    def __init__(self):
        self.EastingAccuracy = []
        self.NorthingAccuracy = []
        self.Easting = []
        self.Northing = []
        self.Distances = []