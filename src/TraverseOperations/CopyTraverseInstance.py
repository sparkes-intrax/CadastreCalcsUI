'''
Makes a copy of the traverse instance to avoid mirroring of 
    traverse data objects
Mainly used within LandXML calculations when testing new branches
'''

import CadastreClasses as DataObjects
from copy import copy

def TraverseCopy(traverse):
    '''
    Creates a copy of traverse in new instance
    :param traverse:
    :return:
    '''

    TraverseCopy = DataObjects.Traverse(traverse.FirstTraverse, traverse.type)
    for key in traverse.__dict__.keys():
        attr = copy(traverse.__getattribute__(key))
        setattr(TraverseCopy, key, attr)

    return TraverseCopy