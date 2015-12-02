#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import h5py
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import os

def main():

    RAREFACTION = 1
    LEVEL1, LEVEL2 = 10, 10
    # Script will create files for each level between LEVEL1 and LEVEL2 including
    COLORMAP = cm.hsv


    # User can input RAREFACTION, LEVEL1 and LEVEL2
    if len (sys.argv) > 1:
        RAREFACTION = int(sys.argv[1])
        if len (sys.argv) > 2:
            LEVEL1 = int(sys.argv[2])
            if len (sys.argv) > 3:
                LEVEL2 = int(sys.argv[3])
            else:
                LEVEL2 = LEVEL1
    
    # Correcting values inputed by user
    RAREFACTION = max(RAREFACTION, 1)
    LEVEL1 = min (max (LEVEL1, 0), 25)
    LEVEL2 = min (max (LEVEL2, 0), 25)
    if LEVEL2 < LEVEL1:
        LEVEL1, LEVEL2 = LEVEL2, LEVEL1

    levels = range(LEVEL1, LEVEL2+1)
    print "RAREFACTION = ",  RAREFACTION, "  LEVELS = ", levels


    hfd5FileName = "largeData/hand/result.hdf5"
    outputFileNamePrefix = "largeData/hand/RF" + str(RAREFACTION)


    hdf5File = h5py.File(hfd5FileName, 'r')
    dataCube = hdf5File["Results"]
    print "Original cube shape:", dataCube.shape

    print("Rarefying dataCube...")
    if (RAREFACTION > 1):
        dataCube = dataCube[::RAREFACTION, ::RAREFACTION, ::RAREFACTION]
    else:
        dataCube = dataCube[::2,:,:]

    print "Rarefied cube shape:", dataCube.shape
    N, M, K = dataCube.shape

    minValue = np.min(dataCube)
    maxValue = np.max(dataCube)
    if maxValue == minValue:
        print "All values are the same - look for better data!\nStop."
        return

    print("Looking for thresholds...")
    list_of_percents_to_left = [  (1 - 0.5 ** level) * 100   for level in levels ]
    thresholds_list = np.percentile(dataCube, list_of_percents_to_left)
    thresholds_dict = dict( zip(levels, thresholds_list) )
    print("Done")


    for level in levels:
        print ("Creating file with level: %d" % level)
        outputFileName =  outputFileNamePrefix + "_LVL" + str(level) +  ".js"

        threshold = thresholds_dict[level]
        print("    Throwing away points with small values...")
        Ix, Iy, Iz = np.where(dataCube > threshold)

        print("    Calculating values to write...")
        numVertices =  len(Ix)
        left_values = np.empty((numVertices), dtype=float)
        for i in xrange(numVertices):
            left_values[i] = dataCube[ Ix[i], Iy[i], Iz[i] ]



        norm = mpl.colors.Normalize(vmin=threshold, vmax=maxValue)
        m = cm.ScalarMappable(norm=norm, cmap=COLORMAP)
        RGBA = m.to_rgba(left_values)
        RGBA = (RGBA * 512).astype(int)

        R, G, B = RGBA[:, 0], RGBA[:, 1], RGBA[:, 2]

        A = left_values
        del(left_values)
        A = (A - minValue) / (maxValue - minValue)
        A = (A * 512).astype(int)

        if RAREFACTION != 1:
            X = Ix - N / 2
        else:
            X = 2 * Ix - N
            # strange multiplying by 2 when rarefaction==1, it's becuase of using half of 
            # array, not full (look at code above where array is rarefied)
        Y = Iy - M / 2
        Z = Iz - K / 2


        f = open(outputFileName, 'w')
        print("    Writing to file...")
        f.seek(0)
        f.truncate()
        f.write("var NMK = [%d, %d, %d]" % (N, M, K))

        f.write(";\nvar R_arr = " + str(R.tolist()))
        f.write(";\nvar G_arr = " + str(G.tolist()))
        f.write(";\nvar B_arr = " + str(B.tolist()))
        f.write(";\nvar A_arr = " + str(A.tolist()))
        f.write(";\nvar X_arr = " + str(X.tolist()))
        f.write(";\nvar Y_arr = " + str(Y.tolist()))
        f.write(";\nvar Z_arr = " + str(Z.tolist()))

        f.write(";\nvar numVertices = " + str(numVertices) + ";\n")
        f.close()

        print("    Finish writing, filename is: '%s', size of file: %.1f kB" 
              % (outputFileName, float(os.stat(outputFileName).st_size)/1024.0) )
        print("    Number of leftover vertices: %d,  %.2f%% from all" % (numVertices, float(numVertices * 100)/float(N * M * K)))

    hdf5File.close()
    print("Finish")


if __name__ == "__main__":
    main()
