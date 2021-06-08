'''
Load landXML file into data objects
'''
from lxml import etree
from LandXML import Connections
import MessageBoxes

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
    ns = lxml.getroot().nsmap
    #remove comments from lxml
    lxml = RemoveComments(lxml)

    # check if back capture project
    App = lxml.find("{"+ns[None]+"}"+"Application").get("name")
    if "DSMSoft" in App:
        mes = "This LandXML was generated from the Back Capture Project"
        title = "Back Capture Project"
        MessageBoxes.genericMessage(mes, title)
    #populated data classes of LandXML_Obj
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
    setattr(TraverseProps, "tag", "{"+ns[None]+"}")
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
    #remove duplicates
    RemoveDuplicatesObj = RemoveDuplicateObs(ns, TraverseProps)
    lxml = RemoveDuplicatesObj.FindDuplicates(lxml)
    # get DP number
    Survey = lxml.find(TraverseProps.Namespace + "Survey")
    SurveyHeader = Survey.find(TraverseProps.Namespace + "SurveyHeader")
    setattr(LandXML_Obj, "DP", SurveyHeader.get("name"))
    # get reduced observations
    LandXML_Obj.ReducedObs = Survey.find(TraverseProps.Namespace + "ObservationGroup")
    setattr(LandXML_Obj, "lxml", lxml)
    
    return LandXML_Obj

def RemoveComments(lxml):
    comments = lxml.xpath('//comment()')
    try:
        for comment in comments:
            parent = comment.getparent()
            parent.remove(comment)
    except AttributeError:
        pass
    return lxml

class RemoveDuplicateObs:
    def __init__(self, ns, TraverseProps):
        '''
        Checks if the ReducedObservations contain any duplicates
        :param lxml:
        :param TraverseProps:
        :param ns:
        :return:
        '''
        self.TraverseProps = TraverseProps
        self.ns = ns

    def FindDuplicates(self, lxml):


        i = 0
        RedObs = lxml.findall("//ReducedObservation", self.ns) + \
                 lxml.findall("//ReducedArcObservation", self.ns)
        while(i < len(RedObs)):
            #loop through Obs
            for Ob in RedObs:
                #SetupID for Ob
                setupID = Ob.get("setupID")
                # Reduced Observations
                tag = "//ReducedObservation"
                Query1 = tag + "[@setupID='" + setupID + "']"
                Query2 = tag + "[@targetSetupID='" + setupID + "']"
                Observations = lxml.findall(Query1, self.ns) + \
                               lxml.findall(Query2, self.ns)
                #remove Obs
                lxml, RemovedObservations = \
                    self.RemoveDuplicates(lxml, Observations, Ob)
                i+=1
                if RemovedObservations:
                    i = 0
                    break

            RedObs = lxml.findall("//ReducedObservation", self.ns) + \
                     lxml.findall("//ReducedArcObservation", self.ns)




        return lxml

    def RemoveDuplicates(self, lxml, Observations, Ob):
        '''
        Checks Observations for duplicates of Ob
        prints the difference between the Observation
        :param lxml:
        :param Observations:
        :param Ob:
        :return:
        '''
        #Set up Ob variables
        ObName = Ob.get("name")
        Ob_setupID = Ob.get("setupID")
        Ob_targetID = Ob.get("targetSetupID")

        #cycle through Observations
        RemovedObserations = False
        for Observation in Observations:
            #ignore Observations - Ob  and not line observations
            if Observation.get("name") == ObName:
                continue
            elif Ob.tag.replace("{"+self.ns[None]+"}", "") != 'ReducedObservation' and \
                    Ob.tag.replace("{" + self.ns[None] + "}", "") != 'ReducedArcObservation':
                continue

            TargetID = Connections.GetTargetID(Observation,
                                               Ob_setupID.replace("{"+self.ns[None]+"}", ""),
                                               self.TraverseProps)
            if TargetID == Ob_targetID:
                #self.PrintComparison(Ob, Observation)
                Observation.getparent().remove(Observation)
                RemovedObserations = True

        return lxml, RemovedObserations

    def PrintComparison(self, Ob1, Ob2):
        '''
        Compares the parameters in Ob1 and Ob2
        :param Ob1:
        :param Ob2:
        :return:
        '''

        # get obs parameters
        print("Observation Name: " + Ob1.get("name"))
        if Ob1.tag.replace("{" + self.ns[None] + "}", "") == 'ReducedObservation':
            ObBearing1, ObDistance1 = self.GetLineParams(Ob1)
            ObBearing2, ObDistance2 = self.GetLineParams(Ob2)
            DistDifference = (float(ObDistance1) - float(ObDistance2))*1000
            print("Distance difference(mm): " + str(DistDifference))
            print("Bearing1: " + ObBearing1 +", Bearing2: " + ObBearing2)
        elif Ob.tag.replace("{" + self.ns[None] + "}", "") == 'ReducedArcObservation':
            ObBearing1, ObDistance1, ObRadius1, ObRot1 = self.GetArcParams(Ob1)
            ObBearing2, ObDistance2, ObRadius2, ObRot2 = self.GetArcParams(Ob2)
            DistDifference = (float(ObDistance1) - float(ObDistance2))*1000
            print("Distance difference(mm): " + str(DistDifference))
            print("Bearing1: " + ObBearing1 + ", Bearing2: " + ObBearing2)
            RadiusDifference = (float(ObRadius1) -float(ObRadius2))*1000
            print("Radius Difference (mm): " + str(RadiusDifference))
            print("Rotation1: " + ObRot1 + ", Rotation 2: " + ObRot2)

        print("")


    def GetLineParams(self, Ob):
        '''
        Retrieves a line bearing and distance from Ob
        :param Ob:
        :return:
        '''
        return Ob.get("azimuth"), Ob.get("horizDistance")

    def GetArcParams(self, Ob):
        '''
        Retrieves a Arc radius, bearing and distance from Ob
        :param Ob:
        :return:
        '''
        return Ob.get("chordAzimuth"), Ob.get("length"), \
               Ob.get("radius"), Ob.get("rot")

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