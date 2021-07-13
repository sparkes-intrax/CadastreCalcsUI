'''
List of Applications used to create LandXML:
DSMSoft v-2.0 (Back Capture Project)
Landxml for Autocad v-1.13.7
LandMarK v-LMK V18.01[rj]
LandMarK v-LMK V20.01[tj]
Stringer ePlan v-Stringer ePlan V20.10 Build Number 34
Stringer ePlan V21.00 Build Number 4
GeoSurvey v-8.05
12d Model v-14.0C2f

'''

class AppLibrary:
    def __init__(self):
        self.DSMSoft_v2 = "DSMSoft_2.0"

class app:
    def __init__(self, AppName, Version):
        self.AppName = AppName
        self.version = Version
