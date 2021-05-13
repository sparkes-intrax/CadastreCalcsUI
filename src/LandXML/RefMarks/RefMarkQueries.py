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
            type = monument.get("type")
            break

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
            return Point.get("oID")

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
    
    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum and \
                (monument.get("type") == "SSM" or monument.get("type") == "PM" or \
                monument.get("type") == "TS"):
            return True
    
    return False

def CheckIfMonument(LandXML_Obj, PntRefNum):
    '''
    Check if PntRefNUm is an RM
    :param LandXML_Obj:
    :param PntRefNum:
    :return: Boolean - True if RM, False otherwise
    '''

    for monument in LandXML_Obj.Monuments.getchildren():
        if monument.get("pntRef") == PntRefNum:
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
            