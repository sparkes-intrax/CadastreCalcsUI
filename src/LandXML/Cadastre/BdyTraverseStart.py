'''
Determines starting points for traverses
'''

from LandXML.Cadastre import BdyQueries

def main(gui, LandXML_Obj):
    '''
    Coordinates workflow to determine starting point for traverse
    :return:
    '''
    
    
    
class TraverseStart:
    def __init__(self, gui, LandXML_Obj):
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj
        self.TraverseProps = LandXML_Obj.TraverseProps
        self.QueryType = "RoadParcel" #determines whats queried when looking at connections
        
    def NoRefMarks(self):
        '''
        Finds starting point for a plan with no RMs and for the
            first traverse
        :return:
        '''

    def RefMarks(self):
        '''
        Coordinates finding a starting point when plan has RMs
        Runs a series of Query type. These are run sequentially and only when
            the previous query type did not return a start point.
        :return: PntRefNum - reference number of the traverse start
        '''

        #Test RoadParcel Query
        PntRefNum = self.CalculatedRM()
        if PntRefNum is None:
            self.QueryType = "Road"
        else:
            return PntRefNum

        #Test Road Query
        PntRefNum = self.CalculatedRM()
        if PntRefNum is None:
            self.QueryType = "KnownPointRoadParcel"
        else:
            return PntRefNum

        # Test if already calculated points have road frontage
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is None:
            self.QueryType = "RmAndBdy"
        else:
            return PntRefNum

        # Test if already calculated points have road frontage
        PntRefNum = self.CalculatedPoint()
        if PntRefNum is None:
            self.QueryType = "KnownPointAndBdy"
        else:
            return PntRefNum

    def CalculatedRM(self):
        '''
        Finds Calculated RMs and queries their connections to Boundaries
        :return:
        '''

        for monument in self.LandXML_Obj.Monuments.getchildren():
            MonumentType = monument.get("type")
            PntRefNum = monument.get("pntRef")
            #check monument is an RM
            if MonumentType == "SSM" or MonumentType == "PM" or \
                     MonumentType == "TS":
                #check if RM has been calculated in RM traverse
                if hasattr(self.gui.CadastralPlan.Points, PntRefNum):
                    #Query the boundaries connected to RM
                    if self.QueryRMsObservations(PntRefNum):
                        return PntRefNum


        return False

    def QueryRMsObservations(self, PntRefNum):
        '''
        Gets connections to RM defined by PntRefNum and checks whether
        :param PntRefNum:
        :return:
        '''

        if self.QueryType == "RoadParcel": #road frontage and parcel
            
