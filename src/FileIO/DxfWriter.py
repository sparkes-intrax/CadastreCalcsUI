'''
Writes lines and text to file
'''

import ezdxf

def main(CadastralPlan, file):
    '''
    Coordinates writing of cadastral data to dxf
    :param CadastralPlan: 
    :param file: 
    :return: 
    '''

    file += ".dxf"
    #Create writer object
    WriterObj = Writer(CadastralPlan, file)
    WriterObj.CadastreToDxf()

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
        EndPoint = self.CadastralPlan.Points.__getattribute__(EndRef)

        #get line layer
        Layer = Line.__getattribute__("Layer")
        
        #write line
        self.modSpace.add_line((SrcPoint.E, SrcPoint.N),
                               (EndPoint.E, EndPoint.N),
                               dxfattribs={'layer': Layer})
        
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
        
    def saveDxf(self):
        self.dxf.saveas(self.file)
        
        
            