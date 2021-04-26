'''
Coordinates the Cadastre Traverse
Sets properties in TraverseProperties
Selects starting point for traverses
Calculates traverse paths testing different branches
Determines whether a close can be found that meets a set of criteria

'''

def main(gui, LandXML_Obj):
    '''

    :param gui:
    :param LandXML_Obj:
    :return:
    '''

    #1) Find first traverse start
    #2) Whats the condition for continuing to look for traverses
    MoreBdyTraverses = True
    while(MoreBdyTraverses):
        
