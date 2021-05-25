'''
Writes point data to a csv file
'''

def main(CadastralPlan, file):
    '''
    Writes all points to a
    :param CadastralPlan: 
    :return: 
    '''
    
    file += ".csv"
    
    with open(file, 'w') as f:
        for key in CadastralPlan.Points.__dict__.keys():
            Point = CadastralPlan.Points.__getattribute__(key)
            if Point.__class__.__name__ != "Point" or Point.Layer != "":
                continue
                
            line = str(Point.PntNum) + ","
            line += str(Point.E) + ","
            line += str(Point.N) + ","
            if Point.Elev is not None:
                line += str(Point.Elev) + ","
            else:
                line += ","
                
            line += Point.Code + "\n"
            
            f.write(line)