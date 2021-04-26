'''
Creates a new traverse object for gui object
Checks the selected source point exists
'''

import CadastreClasses as DataObjects

class CreateTraverse:



    def NewTraverseObject(self, gui):
        '''
        Creates the new traverse object
        :param gui:
        :return:
        '''

        layer = gui.PointLayer.InputObj.currentText()
        traverse = DataObjects.Traverse(False, layer)

        #Get Traverse start point from CadastralPlan
        srcPointNum = gui.SrcPoint.InputObj.text()
        point = gui.CadastralPlan.Points.__getattribute__(srcPointNum)

        #add point object to traverse object
        setattr(traverse.Points, srcPointNum, point)

        #add SrcPoint RefNum to RefPntList and set startRef
        traverse.refPnts.append(srcPointNum)
        traverse.StartRefPnt = srcPointNum

        return traverse

    def CheckSourcePoint(self, gui):
        '''
        Checks source point exists in CadastralPlan.Points
        :param gui:
        :return:
        '''

        srcPointNum = gui.SrcPoint.InputObj.text()
        if hasattr(gui.CadastralPlan.Points, srcPointNum):
            return True
        else:
            return False



