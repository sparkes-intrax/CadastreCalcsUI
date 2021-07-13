'''
Set of methods to load files required to analyse LandXML validation data
'''

class TranslationData:
    def __init__(self, file):
        '''
        Loads Translation data to move manual calcs to MAD calcs
        :param file:
        '''

        with open(file, 'r') as f:

            for line in f.readlines():
                if line.split(",")[0] == "DP":
                    continue

                setattr(self, line.split(",")[0], DpObj(line))



class DpObj:
    def __init__(self, line):

        self.DeltaE = float(line.split(",")[3])
        self.DeltaN = float(line.split(",")[-1])
        pass


class CalcData:

    def __init__(self, file, source):
        '''
        Loads data and puts coordinate data in lists
        :param file:
        '''

        self.file = file
        self.source = source

        #lists to store coordinate data
        self.Easting = []
        self.Northing = []

    def LoadData(self, deltaE, deltaN):
        #open file and extract data
        with open(self.file, 'r') as f:
            for line in f.readlines():
                self.AddData(line, deltaE, deltaN)

    def AddData(self, line, deltaE, deltaN):
        '''
        Adds data in line to list
        :param line:
        :param deltaE:
        :param deltaN:
        :return:
        '''

        self.deltaE = deltaE
        self.deltaN = deltaN
        Easting = float(line.split(",")[1])
        Northing = float(line.split(",")[2])

        #if magnet apply translation
        if self.source == "Magnet":
            Easting += deltaE
            Northing += deltaN

        self.Easting.append(Easting)
        self.Northing.append(Northing)
