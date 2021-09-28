'''
Extracts mark type from the Monuments class based on the PntRefNum
'''

def FindMarkType(LandXML_Obj, PntRefNum):
    '''
    finds RM type in monuments
    :param lxmlObj:
    :param refPnt:
    :return:
    '''

    type = None
    for monument in LandXML_Obj.Monuments.getchildren():
        monumentRefPnt = monument.get("pntRef")
        if PntRefNum == monumentRefPnt:
            return monument.get("type")


    for point in LandXML_Obj.Coordinates.getchildren():
        if point.get("name") == PntRefNum and point.get("code") is not None:
            if point.get("code").startswith("SSM"):
                return "SSM"
            elif point.get("code").startswith("PM"):
                return "PM"
            elif point.get("code").startswith("TS"):
                return "TS"

    return type

def GetMarkNumber(LandXML_Obj, PntRefNum):
    '''
    find RM in Coordinates and 
    :param LandXML_Obj: 
    :param PntRefNum: 
    :return: 
    '''

    for Point in LandXML_Obj.Coordinates.getchildren():
        if PntRefNum == Point.get("name"):
            ID_Num = Point.get("oID")
            if ID_Num is None:
                break
            else:
                return ID_Num

    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum:
            return monument.get("desc")

def GetMarkNumberMonuments(LandXML_Obj, PntRefNum):
    '''
    When Cg Points doesn't contain RM number it sometimes can be found in
        Monuments class. Inconsistency of LRS's LandXML
    :param LandXML_Obj:
    :param PntRefNum:
    :return:
    '''
    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum:
            return monument.get("desc")
    
    return None

def CheckIfRefMark(LandXML_Obj, PntRefNum):
    '''
    Check if PntRefNUm is an RM
    :param LandXML_Obj:
    :param PntRefNum:
    :return: Boolean - True if RM, False otherwise
    '''
    try:
        monument = LandXML_Obj.Monuments.getchildren()[0]
    except AttributeError:
        return False

    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum and \
                (monument.get("type") == "SSM" or monument.get("type") == "PM"):# or \
                #monument.get("type") == "TS"):
            return True
        
    for point in LandXML_Obj.Coordinates.getchildren():
        if point.get("name") == PntRefNum:
            if point.get("code") is not None and \
                    (point.get("code").startswith("SSM") or \
                     point.get("code").startswith("PM")):  # or \
                # point.get("code").startswith("TS")):
                return True
    
    return False

def CheckIfMonument(LandXML_Obj, PntRefNum):
    '''
    Check if PntRefNUm is an RM
    :param LandXML_Obj:
    :param PntRefNum:
    :return: Boolean - True if RM, False otherwise
    '''

    if LandXML_Obj.Monuments is not None:
        for monument in LandXML_Obj.Monuments.getchildren():
            if monument.get("pntRef") == PntRefNum:
                return True

    for point in LandXML_Obj.Coordinates.getchildren():
        if point.get("name") == PntRefNum:
            if point.get("code") is not None and \
                    (point.get("code").startswith("SSM") or \
                     point.get("code").startswith("PM")):# or \
                     #point.get("code").startswith("TS")):
                return True
        
    return False

def CheckIfConnectionMark(LandXML_Obj, PntRefNum):
    '''
    Checks if pntrefNum is a refmark found on boundary corner
    - Peg, Nail, Post, Not Marked, GIN, Approved Mark, DH
    :param LandXML_Obj:
    :param PntRefNum:
    :return: Bool
    '''
    AcceptedMonumentList = ["CB", "GIP", "DH&W"]
    try:
        monument = LandXML_Obj.Monuments.getchildren()[0]
    except AttributeError:
        return False

    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum and \
                monument.get("type") in AcceptedMonumentList:
            return True

    return False

def GetPointCode(LandXML_Obj, TargetID):
    '''
    Gets the point code of the point to be calculated
    Only retrieves codes for RMs
    '''
    try:
        monument = LandXML_Obj.Monuments.getchildren()[0]
    except AttributeError:
        Code = ""
        return Code

    # Get RM type - None if not RM
    MarkType = FindMarkType(LandXML_Obj, TargetID)
    if MarkType is not None:
        Code = "RM"+MarkType

        #Check if SSM or PM
        if CheckIfRefMark(LandXML_Obj, TargetID):
            try:
                Code += "-" + GetMarkNumber(LandXML_Obj, TargetID)
            except TypeError:
                if GetMarkNumberMonuments(LandXML_Obj, TargetID) is not None:
                    Code += "-" + GetMarkNumberMonuments(LandXML_Obj, TargetID)
    else:
        Code = ""

    return Code
            