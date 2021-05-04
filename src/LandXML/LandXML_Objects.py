'''
Load landXML file into data objects
'''
from lxml import etree

def main(file, TraverseProps):
    '''
    opens landXML file and puts elements in relevant dataobjects of the landXML class
    :param file:
    :return:
    '''
    #Create data object to pass around program
    LandXML_Obj = FileObj()

    #open landXML file
    lxml = etree.parse(file)

    ##populated data classes of LandXML_Obj
    LandXML_Obj = PopulateLandXML_Object(lxml, LandXML_Obj, TraverseProps)
    
    return LandXML_Obj

def PopulateLandXML_Object(lxml, LandXML_Obj, TraverseProps):
    '''
    Adds landXML elements to LandXML_Obj
    :param lxml:
    :param LandXML_Obj:
    :return:
    '''
    ns = lxml.getroot().nsmap
    LandXML_Obj.Monuments = lxml.find(TraverseProps.Namespace + "Monuments")
    LandXML_Obj.Coordinates = lxml.find(TraverseProps.Namespace + "CgPoints")
    LandXML_Obj.Parcels = lxml.find(TraverseProps.Namespace + "Parcels")
    #get Road and Easement Parcels
    setattr(LandXML_Obj, "RoadParcels", lxml.findall("//Parcel[@class='Road']", ns))

    #Easement Parcels
    Eas = lxml.findall("//Parcel[@class='Easement']", ns)
    DesArea = lxml.findall("//Parcel[@class='Designated Area']", ns)
    RestrictLand = lxml.findall("//Parcel[@class='Restriction On Use Of Land']", ns)
    setattr(LandXML_Obj, "EasementParcels", (Eas+DesArea+RestrictLand))
    # get DP number
    Survey = lxml.find(TraverseProps.Namespace + "Survey")
    SurveyHeader = Survey.find(TraverseProps.Namespace + "SurveyHeader")
    setattr(LandXML_Obj, "DP", SurveyHeader.get("name"))
    # get reduced observations
    LandXML_Obj.ReducedObs = Survey.find(TraverseProps.Namespace + "ObservationGroup")
    setattr(LandXML_Obj, "lxml", lxml)
    
    return LandXML_Obj


class FileObj(object):

    def __init__(self):
        '''
        Set up File object and attributes
        '''
        self.Coordinates = CoordinatesObj()
        self.Monuments = MonumentsObj()
        self.ReducedObs = ReducedObsObj()
        self.Parcels = ParcelObj()

class CoordinatesObj(object):
    pass

class MonumentsObj(object):
    pass

class ReducedObsObj(object):
    pass

class ParcelObj(object):
    pass