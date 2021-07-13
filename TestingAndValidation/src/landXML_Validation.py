'''
Coordinates processing of LandXML validation data
'''

import DataLoaders, Analysis

def main(path):
    '''
    Coordinates workflow
    :return:
    '''
    #Get filenames
    Files =FileNames(path)

    #retrieve translation data
    transData = DataLoaders.TranslationData(Files.TransDataFile)

    #Analysis
    Analysis.main(path, transData)

class FileNames:
    def __init__(self, path):
        self.TransDataFile = path +  "TranslationData.csv"

if __name__ == "__main__":

    #path to data
    path = "d:\\UAVsInGreenfields\\Code\\MAD\\TestingAndValidation\\"
    main(path)