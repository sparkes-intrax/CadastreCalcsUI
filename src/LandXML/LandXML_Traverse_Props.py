'''
Set of properties for traversing that tells the program what to do
'''

class TraverseProps:
    def __init__(self):
        self.FirstTraverse = None # whether the traverse is the first traverse of the calculations - bool
        self.TraverseType = None # what is being traversed (Ref Marks or Boundaries)
        self.BdyConnections = True #whether traverse should look for and priorities ref marks with a
                                                #parcel bdy connection (parcel from plan being calculated) - bool
                                                #once all RMs with a boundary connection have been calc'd set to False
        self.RoadConnections = False
        self.TraverseClose = True #whether all traverse closes (for ref marks) have been found. Set to False allows
                                                                                #dead end traverses
        self.Branches = [] #list of point numbers where branches in the traverse occurred
        self.PointsSinceBdy = 0 #integer with number of traverse sides calculated since the first branch in the
                                            #traverse not connected to a BDY.
                                            # Reset to zero if a boundary connection is found.

        self.Namespace = '{http://www.landxml.org/schema/LandXML-1.2}'
        self.MixedTraverse = False
        self.TraverseCloseFound = False
        #LargeLots and ExistingLots are properties reserved for plans containing large lots (ie rural subdivisions),
            #or where the RMs joining onto existing lots
        self.LargeLots = False
        self.ExistingLots = False

