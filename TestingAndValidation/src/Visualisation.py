'''
Visualisation tools for accuracy analysis
'''
import ezdxf
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

class MapView:

    def __init__(self, AccuracyObj, File, DP, path):
        '''
        Creates a map view of data
        Draws linework for boundaries and connections
        :param AccuracyObj:
        :param MagnetData:
        :param File:
        :param DP:
        :param path:
        :return:
        '''
        self.AccuracyObj = AccuracyObj
        self.File = File

        #create figure
        fig, ax = self.SetupFigure()
        plt.title("DP"+DP, color='#3ba245')
        #draw lines
        ax = self.GetLineObjects(ax)
        #draw accuracy data
        self.AddAccuracyPoints(ax)

        #save plot
        PlotFile = path + "DP" + DP + "_MapView.jpg"
        plt.savefig(PlotFile, dpi=720)
        plt.close()




    def SetupFigure(self):
        #set up figure
        fig = plt.figure()
        fig.patch.set_facecolor('#292929')
        ax = fig.add_subplot()
        ax.set_facecolor("#1f1f1f")
        ax.xaxis.label.set_color('#3ba245')
        ax.yaxis.label.set_color('#3ba245')
        ax.tick_params(axis='both', colors="#3ba245")
        for spine in ax.spines.values():
            spine.set_edgecolor('#3ba245')

        return fig, ax

    def GetLineObjects(self, ax):
        '''
        Using ezdxf retrieves dxf line objects
        :param File:
        :return:
        '''

        #get dxf file instance and model space
        doc = ezdxf.readfile(self.File)
        msp = doc.modelspace()

        #get lines
        lines = msp.query('LINE')

        #plot lines
        for line in lines:
            layer = line.dxf.layer
            startE = line.dxf.start[0]
            startN = line.dxf.start[1]
            endE = line.dxf.end[0]
            endN = line.dxf.end[1]
            if layer == 'REFERENCE MARKS':
                ax.plot([startE, endE], [startN, endN], color="white", lw=0.5)
            elif layer == "BOUNDARY":
                ax.plot([startE, endE], [startN, endN], color="cyan", lw=0.5)
            elif layer == "EASEMENT":
                ax.plot([startE, endE], [startN, endN], color="white", linestyle="dashed", lw=0.5)

        return ax

    def AddAccuracyPoints(self, ax):
        '''
        Adds accuracy points as a scatter plot
        :return:
        '''
        #split into error ranges
        #<3mm
        indexes = np.where(np.array(self.AccuracyObj.Distances)<=3)[0]
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if i in indexes]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if i in indexes]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if i in indexes]
        plt.scatter(Easting, Northing, c="green", label="<3mm")
        # <5mm
        indexes = np.logical_and(3 < np.array(self.AccuracyObj.Distances),
                  np.array(self.AccuracyObj.Distances)<= 5)
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if indexes[i]]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if indexes[i]]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if indexes[i]]
        plt.scatter(Easting, Northing, c="blue", label="<5mm")
        # <10mm
        indexes = np.logical_and(5 < np.array(self.AccuracyObj.Distances),
                                 np.array(self.AccuracyObj.Distances) <= 10)
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if indexes[i]]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if indexes[i]]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if indexes[i]]
        plt.scatter(Easting, Northing, c="yellow", label="<10mm")
        # <15mm
        indexes = np.logical_and(10 < np.array(self.AccuracyObj.Distances),
                                 np.array(self.AccuracyObj.Distances) <= 15)
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if indexes[i]]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if indexes[i]]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if indexes[i]]
        plt.scatter(Easting, Northing, c="orange", label="<15mm")
        # <20mm
        indexes = np.logical_and(15 < np.array(self.AccuracyObj.Distances),
                                 np.array(self.AccuracyObj.Distances) <= 20)
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if indexes[i]]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if indexes[i]]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if indexes[i]]
        plt.scatter(Easting, Northing, c="red", label="<20mm")
        # >20mm
        indexes = np.where(np.array(self.AccuracyObj.Distances) > 20)[0]
        Easting = [E for i, E in enumerate(self.AccuracyObj.Easting) if i in indexes]
        Northing = [N for i, N in enumerate(self.AccuracyObj.Northing) if i in indexes]
        Distances = [D for i, D in enumerate(self.AccuracyObj.Distances) if i in indexes]
        plt.scatter(Easting, Northing, c="purple", label=">20mm")
        plt.legend(loc='upper right', bbox_to_anchor=[1.1,1.15])
        return ax

def Histogram(AccuracyObj, path, DP):
    '''
    Plots a histogram for accuracy analysis for DP
    :param AccuracyObj:
    :return:
    '''

    fig = plt.figure()
    fig.patch.set_facecolor('#292929')
    if DP == "All":
        plt.title("All Data", color='#3ba245')
    else:
        plt.title("DP" + DP, color='#3ba245')
    ax = fig.add_subplot()
    ax.set_facecolor("#1f1f1f")
    ax.xaxis.label.set_color('#3ba245')
    ax.yaxis.label.set_color('#3ba245')
    ax.tick_params(axis='both', colors="#3ba245")
    for spine in ax.spines.values():
        spine.set_edgecolor('#3ba245')
    plt.hist(AccuracyObj.Distances, color='#3ba245', ec='#292929')
    plt.xlabel("Accuracy (mm)")
    file = path + "DP" + DP + "_Hist.jpg"
    plt.savefig(file, dpi=720)
    plt.close()