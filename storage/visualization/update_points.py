#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import h5py
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm


def main():


    RAREFACTION = 1
    MIN_ALPHA = 0.5
    COLORMAP = cm.hsv

    if len (sys.argv) > 1:
        MIN_ALPHA = float(sys.argv[1])
        if len (sys.argv) > 2:
            RAREFACTION = int(sys.argv[2])
    print "MIN_ALPHA = ", MIN_ALPHA, "  RAREFACTION = ",  RAREFACTION



    hfd5FileName = "largeData/hand/result.hdf5"
    outputFileName = "largeData/hand/MA" + str(MIN_ALPHA) + "_RF" + str(RAREFACTION) + ".js"
    # !! ATTENTION, THIS FILE WILL BE TOTALLY OWERWRITTEN !!



    hdf5File = h5py.File(hfd5FileName, 'r')
    
    dataCube = hdf5File["Results"]
    print "Original cube shape:", dataCube.shape

    print("Rarefying dataCube...")
    if (RAREFACTION > 1):
        rarefiedDataCube = dataCube[::RAREFACTION, ::RAREFACTION, ::RAREFACTION]
    else:
        rarefiedDataCube = dataCube[::2,:,:]

    print "Rarefied cube shape:", rarefiedDataCube.shape
    N, M, K = rarefiedDataCube.shape


    minValue = np.min(rarefiedDataCube)
    maxValue = np.max(rarefiedDataCube)
    if maxValue == minValue:
        print "All values are the same - look for better data!\nStop."
        return

    norm = mpl.colors.Normalize(vmin=MIN_ALPHA, vmax=1)
    m = cm.ScalarMappable(norm=norm, cmap=COLORMAP)



    # this block normalizes all values
    # I divided normalization into three steps beacuse of limited memory of my laptop
    A_all = rarefiedDataCube
    # A_all = (A_all - minValue) / (maxValue - minValue)
    A_all[:,:,:200] =    (A_all[:,:,:200] - minValue) / (maxValue - minValue)
    A_all[:,:,200:400] = (A_all[:,:,200:400] - minValue) / (maxValue - minValue)
    A_all[:,:,400:] =    (A_all[:,:,400:] - minValue) / (maxValue - minValue)

    

    # leaving only vertices that have alpha more than MIN_ALPHA
    Ix, Iy, Iz = np.where(A_all > MIN_ALPHA)
    numVertices =  len(Ix)
    A = np.empty((numVertices), dtype=float)
    for i in xrange(numVertices):
        A[i] = A_all[ Ix[i], Iy[i], Iz[i] ]

    f = open(outputFileName, 'w')
    print("File opened, starting to write...")
    f.seek(0)
    f.truncate()
    f.write("var NMK = [%d, %d, %d]" % (N, M, K))


    RGBA = m.to_rgba(A)
    RGBA = RGBA * 512
    RGBA = RGBA.astype(int)


    A = A * 512
    A = A.astype(int)

    R = (RGBA[:,0]).flatten()
    G = (RGBA[:,1]).flatten()
    B = (RGBA[:,2]).flatten()

    if RAREFACTION != 1:
        X = Ix - N / 2
    else:
        X = 2 * Ix - N
        # strange multiplying by 2 when RAREFACTION==1, it's becuase of using half of 
        # array, not full (look at code above where array is rarefied)
    Y = Iy - M / 2
    Z = Iz - K / 2

    print("Writing R values...")
    f.write(";\nvar R_arr = ")
    f.write(str(R.tolist()))

    print("Writing G values...")
    f.write(";\nvar G_arr = ")
    f.write(str(G.tolist()))

    print("Writing B values...")
    f.write(";\nvar B_arr = ")
    f.write(str(B.tolist()))

    print("Writing A values...")
    f.write(";\nvar A_arr = ")
    f.write(str(A.tolist()))

    print("Writing X values...")
    f.write(";\nvar X_arr = ")
    f.write(str(X.tolist()))

    print("Writing Y values...")
    f.write(";\nvar Y_arr = ")
    f.write(str(Y.tolist()))

    print("Writing Z values...")
    f.write(";\nvar Z_arr = ")
    f.write(str(Z.tolist()))


    f.write(";\n")
    print "number of leftover vertices: %d,  %.2f%% from all" % (numVertices, float(numVertices * 100)/float(N * M * K))
    f.write("var numVertices = " + str(numVertices) + ";\n")

    f.close()
    hdf5File.close()
    print("File is closed, FINISH")

if __name__ == "__main__":
    main()
