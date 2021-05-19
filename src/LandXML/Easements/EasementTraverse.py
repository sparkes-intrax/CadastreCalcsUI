'''
Calculates an easement traverse starting from the first connection,
determined in FindEasementStart until it closes (when all connections are calc'd)
'''
from LandXML import TraverseSideCalcs, SharedOperations, PointClass, Connections, \
    ConnectionMopper
from DrawingObjects import DrawTraverse, LinesPoints
import MessageBoxes


class Traverse:
    def __init__(self, LandXML_Obj, gui, EasementParcel):
        self.LandXML_Obj = LandXML_Obj
        self.gui = gui
        self.CadastralPlan = gui.CadastralPlan
        self.EasementParcel = EasementParcel

    def CalculateTraverse(self, EasementLines, StartObs, PntRefNum):
        '''
        Calculates a traverse for the Easement parcel
        :param EasementLines:
        :param StartObs:
        :return:
        '''


        #Create Traverse instance
        self.CreateTraverseObj(PntRefNum)

        #calc first observation
        point = TraverseSideCalcs.TraverseSide(PntRefNum, self.traverse,
                                               StartObs, self.gui, self.LandXML_Obj)

        PntRefNum = point.TargPntRefNum

        # If only one new connection found for easement just draw line
        if len(EasementLines) == 0:
            self.DrawObservation(StartObs, point)
        else:

            PntRefNum = self.CalculateLines(EasementLines, PntRefNum)

            #check close
            if not hasattr(self.CadastralPlan.Points, PntRefNum.split("_")[0]):
                self.EasementNotClosed()
            else:
                # apply adjustment if < 5mm or alert
                self.gui = SharedOperations.ApplyCloseAdjustment(self.traverse,
                                                                 self.LandXML_Obj,
                                                                 self.gui)
                #draw and commit traverse.
                DrawTraverse.main(self.gui, self.traverse, self.LandXML_Obj)



    def CreateTraverseObj(self, PntRefNum):
        '''
        Creates a traverse object to store Easement traverse
        :return:
        '''

        #start point
        PointObj = PointClass.Points(self.LandXML_Obj, self.CadastralPlan.Points)
        PointObj.StartPointObj(PntRefNum)
        #traverse object
        self.traverse = SharedOperations.initialiseTraverse(PointObj, "EASEMENT", False)

    def CalculateLines(self, EasementLines, PntRefNum):
        '''
        Iteratively finds the next easement line and calculates them until
        traverse is close
        :param EasementLines:
        :return:
        '''

        while (len(EasementLines) > 0):

            #check which line comes next
            for Obs in EasementLines:
                #check if line is the next line to calculate
                if self.checkLine(Obs, PntRefNum):
                    #Add line to Traverse
                    point = TraverseSideCalcs.TraverseSide(PntRefNum, self.traverse,
                                                           Obs, self.gui, self.LandXML_Obj)

                    PntRefNum = point.TargPntRefNum
                    #remove observatio from ReducedObservations
                    Obs.getparent().remove(Obs)
                    break

            EasementLines.remove(Obs)

        return PntRefNum


    def checkLine(self, Obs, PntRefNum):
        '''
        Checks whether line contains PntRefNum
        :param line:
        :param PntRefNum:
        :return:
        '''

        startRef = Obs.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        endRef = Obs.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        if PntRefNum == startRef or PntRefNum == endRef:
            return True

        return False


    def EasementNotClosed(self):
        '''
        Throws an error message when not close is found for traverse
        :return:
        '''

        message = "No close found for Easement " + self.EasementParcel.get("name")
        title = "Easement Does not Close"
        # print("Traverse #: " + str(gui.CadastralPlan.Traverses.TraverseCounter))
        # print("Misclose: " + str(round(1000 * close, 1)) + "mm")
        # print("")

        MessageBoxes.genericMessage(message, title)

    def DrawObservation(self, Obs, point):
        '''
        Draws line in UI when only one connection in Easement
        '''

        #get point objects of observation
        startRef = Obs.get("setupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        SrcPoint = self.CadastralPlan.Points.__getattribute__(startRef)
        endRef = Obs.get("targetSetupID").replace(self.LandXML_Obj.TraverseProps.tag, "")
        EndPoint = self.CadastralPlan.Points.__getattribute__(endRef)

        #Line proprs
        self.SetLinePointGuiProps()

        #Draw line
        self.GraphLine = self.gui.view.Line(SrcPoint.E*1000, SrcPoint.NorthingScreen*1000,
                                            EndPoint.E*1000, EndPoint.NorthingScreen*1000,
                                            self.LinePen)

        # add QGraphicsLine to line.GraphicsItems
        setattr(point.line.GraphicsItems, "Line", self.GraphLine)
        point.line.BoundingRect = self.GraphLine.boundingRect()

        #add line to Cadastral Plan
        setattr(self.CadastralPlan.Lines, Obs.get("name"), point.line)

    def SetLinePointGuiProps(self):
        '''
        Sets properties of line and points to be drawn on the drawing canvas
        '''

        #get line props
        LineProps = LinesPoints.LinePointProperties()

        self.LinePen, self.LineLayer, \
        self.LineColour = LineProps.SetLineProperties("EASEMENT",
                                                      "EASEMENT")




