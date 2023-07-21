'''
clears any connections thbat were added to the tried list
'''
import CadastreClasses as DataObjects

def ClearTriedConnections(gui):
    '''
    Remove Tried Connections from gui.CadatralPlan
    :param gui:
    :return:
    '''

    gui.CadastralPlan.TriedConnections = DataObjects.Lines()
    return gui