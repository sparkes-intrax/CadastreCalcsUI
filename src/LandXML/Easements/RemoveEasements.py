'''
Methods to remove Easement observations from a set of Observations

Some lines in Easement parcels in a landxml are common with a Lot Parcel
- these are not removed
'''

from LandXML import BDY_Connections, Connections

class RemoveEasementObservations:
    def __init__(self, Observations, PntRefNum, LandXML_Obj):
        self.Observations = Observations
        self.PntRefNum = PntRefNum
        self.LandXML_Obj = LandXML_Obj

    def SearchObservations(self):
        '''
        CHecks each Observation in Observations whether a unique Easement line
        :return:
        '''

        RemoveObs = []
        for key in self.Observations.__dict__.keys():
            Observation = self.Observations.__getattribute__(key)
            # Get target ID for Observation
            TargetID = Connections.GetTargetID(Observation, self.PntRefNum,
                                               self.LandXML_Obj.TraverseProps)
            #check if the Observation is part of a lot parcel
            if self.CheckLotParcel(TargetID):
                continue

            if self.SearchEasementParcels(TargetID):
                RemoveObs.append(key)
                continue

            if self.RoadAndEasement(TargetID, Observation):
                RemoveObs.append(key)
                
        if len(RemoveObs) > 0:
            self.Observations = Connections.RemoveSelectedConnections(self.Observations, RemoveObs)
            
        return self.Observations

    def CheckLotParcel(self, TargetID):
        '''
        Checks whether the Observation is a Lot parcel boundary
        :param TargetID:
        :return:
        '''

        ObservationChecker = BDY_Connections.CheckBdyConnection(TargetID, self.LandXML_Obj)
        if (ObservationChecker.BdyConnection(TargetID) and \
                ObservationChecker.BdyConnection(self.PntRefNum)):
            return True

        return False

    def SearchEasementParcels(self, TargetID):
        '''
        Searches parcels in LandXML for Easements
        :param TargetID:
        :return:
        '''

        for parcel in self.LandXML_Obj.EasementParcels:
            '''
            parcelClass = parcel.get("class")

            if parcelClass == "Easement" or \
                    parcelClass == "Restriction On Use Of Land" or \
                    parcelClass == "Designated Area":
            '''
            if self.CheckParcelLines(parcel, TargetID) and \
                        self.CheckParcelLines(parcel, self.PntRefNum):
                return True
                
        return False

    def CheckParcelLines(self, Parcel, TargetID):
        '''
        Searches parcel linework and see if TargetID is part of Parcel
        :param Parcel: Parcel being queried
        :param TargetID: end of Observation being queried
        :return: 
        '''
        
        # get lines out of parcel
        lines = Parcel.find(self.LandXML_Obj.TraverseProps.Namespace + "CoordGeom")
        # loop through line to check vertexes
        if lines != None:
            for line in lines.getchildren():
                startRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "Start").get("pntRef")
                endRef = line.find(self.LandXML_Obj.TraverseProps.Namespace + "End").get("pntRef")
                # check if startRef or endRef are TargetID
                if startRef == TargetID or endRef == TargetID:
                    return True

        return False

    def RoadAndEasement(self, TargetID, Observation):
        '''
        LandXML Argh?????
        Very occassionally a road to easement vertex will make up
            the road parcel
        This method checks if the observation is a road parcel and if one of the
        vertexes is an easement
        :param TargetID:
        :return:
        '''

        # loop through parcels to find road parcels
        Road = False
        for parcel in self.LandXML_Obj.Parcels.getchildren():
            parcelClass = parcel.get("class")

            if parcelClass == "Road":
                if self.CheckParcelLines(parcel, TargetID) and \
                        self.CheckParcelLines(parcel, self.PntRefNum):
                    Road = True
                    break
                
        #check if one vertex is from easements    
        if Road:
            for parcel in self.LandXML_Obj.Parcels.getchildren():
                parcelClass = parcel.get("class")

                if parcelClass == "Easement" or \
                        parcelClass == "Restriction On Use Of Land" or \
                        parcelClass == "Designated Area":
                    if (self.CheckParcelLines(parcel, TargetID) or \
                            self.CheckParcelLines(parcel, self.PntRefNum)) and \
                            Observation.get("desc") != "Connection":
                        return True
                    
        return False