'''
Methods and workflow to calculate a traverse
Universal function for all traverse types (RMs, Boundaries, Easements).
- calls relevant methods to run the different traver types
'''

from LandXML import Connections, TraverseClose, TraverseNoConnection, FindConnection

class Traverse:
    def __init__(self, traverse, gui, LandXML_Obj, PntRefNum):
        '''
        Contains methods to calculate a traverse
        :param traverse: traverse object to store all traverse attributes
        :param gui: ui data object
        :param LandXML_Obj: LandXML data object
        :param PntRefNum: The starting point for the traverse. Updates with new traverse sides
        '''

        self.traverse = traverse
        self.PntRefNum = PntRefNum
        self.gui = gui
        self.LandXML_Obj = LandXML_Obj

        # defines whether a finish to a traverse has been found
        # not neccesarily a close
        self.TraverseFinished = False        

        #loop to add sides to a traverse
        while(not self.TraverseFinished):
            #find all connections for self.PntRefNum
            Observations = Connections.AllConnections(self.PntRefNum, self.LandXML_Obj)
            #select connection
            connection = FindConnection.FindNextConnection(Observations, self.traverse,
                                                           self.PntRefNum, 
                                                           self.LandXML_Obj.TraverseProps,
                                                           self.gui.CadastralPlan, 
                                                           self.LandXML_Obj)
            
            #calculate new point and create line object - send gui and update drawing canvas
            #text etc
            point = DataObjects.Point(StartPoint.PntRefNum, StartPoint.Easting, StartPoint.Northing,
                                      StartPoint.Northing, None, StartPoint.Code, "REFERENCE MARKS")
            if connection.TraverseClose:
                self.TraverseFinished = True
                break



        