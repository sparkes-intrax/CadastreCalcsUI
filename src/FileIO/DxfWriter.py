'''
Writes lines and text to file
'''

import ezdxf
from ezdxf.tools.text import MTextEditor
from ezdxf.enums import TextEntityAlignment

def main(CadastralPlan, file):
    '''
    Coordinates writing of cadastral data to dxf
    :param CadastralPlan: 
    :param file: 
    :return: 
    '''

    PlanFile = file + ".dxf"
    #Create writer object
    WriterObj = Writer(CadastralPlan, PlanFile)
    WriterObj.CadastreToDxf()

    #write traverses
    TravFile = file + "_Traverses.dxf"
    TravWriteObj = TraverseWriter(CadastralPlan, TravFile)
    TravWriteObj.CoordinateTravWrite()

class Writer:
    def __init__(self, CadastralPlan, file):
        '''        
        :param CadastralPlan: 
        :param file: 
        '''
        
        self.CadastralPlan = CadastralPlan
        self.file = file
        
    def CadastreToDxf(self):
        '''
        Coordinates methods to write dxf
        :return: 
        '''

        #CREATE DXF MODELSPACE ATTRIBUTES
        self.CreateDxfObj()
        #Set up file layer
        self.Layers()

        #Add lines and arcs
        if len(self.CadastralPlan.Lines.__dict__.keys()) > 1:
            self.AddLinework()

        # Add text
        if len(self.CadastralPlan.Labels.__dict__.keys()) > 0:
            self.AddText()
            
        #save dxf
        self.saveDxf()
        
        
    def CreateDxfObj(self):
    
        #Create dxf to write to
        self.dxf = ezdxf.new('AC1018')
        self.modSpace = self.dxf.modelspace()

        
    def Layers(self):
        '''
        Creates layers in file
        :return: 
        '''

        self.dxf.layers.new(name='REFERENCE MARKS', dxfattribs={'color': 7})
        self.dxf.layers.new(name='BOUNDARY', dxfattribs={'color': 4})
        self.dxf.layers.new(name='EASEMENT', dxfattribs={'linetype': 'DASHED', 'color': 88})
        self.dxf.layers.new(name='TEXT')

    def AddLinework(self):
        '''
        Adds lines to dxf
        :return:
        '''

        for key in self.CadastralPlan.Lines.__dict__.keys():
            Line = self.CadastralPlan.Lines.__getattribute__(key)
            if Line.__class__.__name__ == "Line":
                self.WriteLine(Line)
            elif Line.__class__.__name__ == "Arc":
                self.WriteArc(Line)

    def WriteLine(self, Line):
        '''
        write Line to dxf
        :param Line:
        :return:
        '''

        #Get ref num for start and end of line
        StartRef = Line.__getattribute__("StartRef")
        EndRef = Line.__getattribute__("EndRef")

        #Get points
        SrcPoint = self.CadastralPlan.Points.__getattribute__(StartRef)
        try:
            EndPoint = self.CadastralPlan.Points.__getattribute__(EndRef)
        except AttributeError:
            EndPoint = self.CadastralPlan.Points.__getattribute__(EndRef.split("_")[0])

        #get line layer
        Layer = Line.__getattribute__("Layer")
        
        #write line
        try:
            self.modSpace.add_line((SrcPoint.E, SrcPoint.N),
                               (EndPoint.E, EndPoint.N),
                               dxfattribs={'layer': Layer})
        except AttributeError:
            pass
        
    def WriteArc(self, Arc):
        '''
        Writes arc to dxf
        :param Arc: 
        :return: 
        '''
        
        #Get centre coords 
        CentreCoords = Arc.__getattribute__("CentreCoords")
        #get Angles
        Angles = Arc.__getattribute__("ArcAngles")
        
        ArcRadius = Arc.__getattribute__("Radius")
        
        Layer = Arc.__getattribute__("Layer")
        
        #write arc
        self.modSpace.add_arc((CentreCoords.CentreEasting, CentreCoords.CentreNorthing),
                              ArcRadius, Angles.StartAngle, Angles.EndAngle,
                              dxfattribs={'layer': Layer})

    def AddText(self):
        '''
        Cycle through text labels and write them to model
        :return:
        '''

        for key in self.CadastralPlan.Labels.__dict__.keys():
            Label = self.CadastralPlan.Labels.__getattribute__(key)
            if Label.ParcelType == "Parcel" or Label.ParcelType == "Easement":
                self.WriteMultiText(Label)
            else:
                self.WriteText(Label)



    def WriteMultiText(self, text):
        '''
        Writes text to file
        :param text:
        :return:
        '''

        ATTRIBS = {
            "char_height": 0.7,
            "style": 'RomanT'
        }

        #editor = MTextEditor("")
        #editor.aci(1).append(text.Label)
        mtext = self.modSpace.add_mtext(text.Label, ATTRIBS)
        #mtext.text = "{\\C1;red " + text.Label + "}"
        mtext.set_location((text.Easting, text.Northing))
        #mtext.set_color('red')
        #mtext.set_font('\Fromant__.ttf')
        mtext.dxf.attachment_point = 5
        #mtext.dxf.char_height = 0.7

    def WriteText(self, text):
        ATTRIBS = {
            "char_height": 1.4,
            "style": "OpenSans"
        }
        
        #set label rotation
        rotation = text.Orientation
        #rotation = rotation - 90
        #if rotation < 0:
        #    rotation += 360
        #if rotation >= 180:
        #    rotation -= 180

        self.modSpace.add_text(text.Label,
                          dxfattribs={
                              'style': 'RomanT',
                              'height': 0.7,
                              'rotation': rotation,
                              'layer': 'TEXT'}
                          ).set_placement((text.Easting, text.Northing),
                                          align=TextEntityAlignment.MIDDLE_CENTER)


        
    def saveDxf(self):
        self.dxf.saveas(self.file)

class TraverseWriter:
    def __init__(self, CadastralPlan, file):
        self.CadastralPlan = CadastralPlan
        self.file = file

    def CoordinateTravWrite(self):
        '''
        Coordinate the writing of traverses to dxf
        :return:
        '''
        self.WriterObj = Writer(self.CadastralPlan, self.file)
        #initiate dxf object
        self.initDxfObj()
        self.Layers()
        #write the traverses - color defined by close
        self.WriteTraverses()
        #save dxf
        self.WriterObj.saveDxf()


    def initDxfObj(self):
        #initiate object to write dxf
        self.WriterObj.CreateDxfObj()
        self.dxf = self.WriterObj.dxf
        self.modSpace = self.WriterObj.modSpace


    def Layers(self):
        '''
        Creates layers in file
        :return:
        '''

        self.dxf.layers.new(name='TravClose_5mm', dxfattribs={'color': 3})
        self.dxf.layers.new(name='TravClose_10mm', dxfattribs={'color': 5})
        self.dxf.layers.new(name='TravClose_15mm', dxfattribs={'color': 20})
        self.dxf.layers.new(name='TravClose_20mm', dxfattribs={'color': 1})
        self.dxf.layers.new(name='TravClose_Greater20mm', dxfattribs={'color': 6})

    def WriteTraverses(self):
        '''
        Sequentially writes traverses to file
        Colour coding them by misclose
        Written as polylines
        :return:
        '''

        for key in self.CadastralPlan.Traverses.__dict__.keys():
            traverse = self.CadastralPlan.Traverses.__getattribute__(key)
            if traverse.__class__.__name__ != "Traverse":
                continue

            #Create tuple list with line coords
            TravLineCoords = self.GetLineCoords(traverse)
            #Get misclose
            misclose = traverse.Close_PreAdjust
            self.WriteToDxf(TravLineCoords, misclose)


    def GetLineCoords(self, traverse):
        '''
        Cycles through lines in traverse and get there start and end coords
        :return:
        '''

        LineCoords = []
        for i, Obs in enumerate(traverse.Observations):
            #Get line
            ObsName = Obs.get("name")
            Line = traverse.Lines.__getattribute__(ObsName)
            #Get Start Point and its coords
            StartRef = Line.StartRef
            Point = self.CadastralPlan.Points.__getattribute__(StartRef)
            Coords = (Point.E, Point.N)
            LineCoords.append(Coords)

            #Add end ref if last side of traverse

            if i == (len(traverse.Observations)-1):
                EndRef = Line.EndRef
                Point = self.CadastralPlan.Points.__getattribute__(EndRef)
                Coords = (Point.E, Point.N)
                LineCoords.append(Coords)

        return LineCoords

    def WriteToDxf(self, LineCoords, Misclose):
        '''
        Writes the traverse to a polyline
        :param LineCoords:
        :param Misclose:
        :return:
        '''

        try:
            if Misclose < 5:
                self.modSpace.add_lwpolyline(LineCoords, dxfattribs={'layer': 'TravClose_5mm'})
            elif Misclose < 10:
                self.modSpace.add_lwpolyline(LineCoords, dxfattribs={'layer': 'TravClose_10mm'})
            elif Misclose < 15:
                self.modSpace.add_lwpolyline(LineCoords, dxfattribs={'layer': 'TravClose_15mm'})
            elif Misclose < 20:
                self.modSpace.add_lwpolyline(LineCoords, dxfattribs={'layer': 'TravClose_20mm'})
            else:
                self.modSpace.add_lwpolyline(LineCoords, dxfattribs={'layer': 'TravClose_Greater20mm'})
        except TypeError:
            pass




        
        
            