'''
Set routines to work with coordinates in LandXML files
'''

def getPointCoords(PntRefNum, LandXML_Obj):
    '''
    retrieves the coords for pntRef from coordinates attribute in lxmlObj
    :param pntRef: (string) point name to search for coordinates
    :param lxmlObj: landXML Object
    :return:
    '''

    #loop through points to get coords of pntRef
    for point in LandXML_Obj.Coordinates:
        Point_Name = point.get("name")
        if Point_Name == PntRefNum:
            #check for leading space in coordinate string
            if point.text.split(' ')[0] == "":
                East = float(point.text.split(' ')[2])
                North = float(point.text.split(' ')[1])
            else:
                East = float(point.text.split(' ')[1])
                North = float(point.text.split(' ')[0])

            break

    return East, North