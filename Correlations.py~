import numpy as np
import visualize as vs


def getCorrelation(X,Y):
    
        cor = np.zeros((2,len(X)))

        cor[0] = X[:]
        cor[1] = Y[:]
        c = np.corrcoef(cor)
        l = "Korrelationskoeffizient = " + str(c[0][1])
        vs.plot_Data(X,Y,l)
        return c[0][1]