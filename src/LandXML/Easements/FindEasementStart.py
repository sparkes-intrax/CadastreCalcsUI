'''
Class to calculate the start of a traverse for an Easement parcel
'''

class EasementStart:
    def __init__(self, CadastralPlan, LandXML_Obj):
        self.CadastralPlan = CadastralPlan
        self.LandXML_Obj = LandXML_Obj

    def GetStartObservation(self, Easement):
        '''
        Finds the observation to start the traverse on
        :param Easement:
        :return:
        '''
        #get lines out of parcel
        lines = Easement.find(self.LandXML_Obj.TraverseProps.Namespace+"CoordGeom")
        #loop through lines to check it hasn't already been calc'd
        ObsToCalc = self.CollectObsForCalc(Easement, lines)
        if len(ObsToCalc) == 0:
            return None, None, None
        #Find start obs
        StartObs, StartPntRef = self.GetStart(ObsToCalc)
        return StartObs, StartPntRef, ObsToCalc


    def CollectObsForCalc(self, Easement, lines):
        '''
        Determines which lines of Easement need to be calc'd
        :param Easement:
        :return:
        '''
        ObsToCalc = []
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "Start").get("pntRef")
                endRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "End").get("pntRef")
                Obs = self.CheckObservationCalculated(startRef, endRef)
                if Obs is not None:
                    ObsToCalc.append(Obs)

        return ObsToCalc

    def CheckObservationCalculated(self, StartRef, EndRef):
        '''
        Checks if observation defined by StartRef/EndRef not already calculated
        :param StartRef:
        :param EndRef:
        :return:
        '''

        #loop through remaining observations to check if match easement line
        for obs in self.LandXML_Obj.ReducedObs:
            setupID = obs.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            targetID = obs.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            if (StartRef == setupID and EndRef == targetID) or \
                    (EndRef == setupID and StartRef == targetID):
                return obs

    def GetStart(self, ObsToCalc):
        '''
        Finds an observation within easement observations (ObsToCalc) to start the Easement
        traverse
        An observation where one point has already been calc'd (in CadastralPlan) is
        selected
        :param ObsToCalc: Observations in Easement parcel that need to be calc'd
        :return:
        '''

        for Obs in ObsToCalc:
            setupID = Obs.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            targetID = Obs.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
            #check if setupID and TargetID has been calc'd
            StartCalculcated = self.CheckPoint(setupID)
            EndCalculated = self.CheckPoint(targetID)
            
            if StartCalculcated or EndCalculated:
                if StartCalculcated:
                    StartPntRef = setupID
                else:
                    StartPntRef = targetID
                return Obs, StartPntRef
        
        return None, None

    def CheckPoint(self, PntRefNum):
        '''
        Checks if {ntRefNum has been calc'd
        :param PntRefNum:
        :return: Bool
        '''
        if hasattr(self.CadastralPlan.Points, PntRefNum):
            return True
        else:
            return False






