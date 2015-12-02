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



    hfd5FileName = "<path to reconstruction's hdf5 file>"
    outputFileName = "<folder_for_numbers_of_one_reconstruction>/MA" + str(MIN_ALPHA) + "_RF" + str(RAREFACTION) + ".js"
    # !! ATTENTION, THIS FILE WILL BE TOTALLY OWERWRITTEN !!



    hdf5File = h5py.File(hfd5FileName, 'r')
    
    dataCube = hdf5File["Results"]
    print "Original cube shape:", dataCube.shape
    Q, W, E = dataCube.shape


    # this block of code is used to set boundaries in visualization, the longest side of limiting box is 80
    maxDim = max(Q, W, E)
    spacePerPoint = 40.0 / float(maxDim) 
    maxAbsX = Q * spacePerPoint
    maxAbsY = W * spacePerPoint
    maxAbsZ = E * spacePerPoint

    print("Rarefying dataCube...")
    if (RAREFACTION > 1):
        rarefiedDataCube = dataCube[::RAREFACTION, ::RAREFACTION, ::RAREFACTION]
    else:
        rarefiedDataCube = dataCube

    print "Rarefied cube shape:", rarefiedDataCube.shape
    N, M, K = rarefiedDataCube.shape

    def convertToX(binNum):
        return (2 * binNum/float(N) - 1.0) * maxAbsX

    def convertToY(binNum):
        return (2 * binNum/float(M) - 1.0) * maxAbsY

    def convertToZ(binNum):
        return (2 * binNum/float(K) - 1.0) * maxAbsZ

    minValue = np.min(rarefiedDataCube)
    maxValue = np.max(rarefiedDataCube)

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
    f.write("var NMK = [%d, %d, %d];\nvar numbers = " % (N, M, K))


    if (maxValue != minValue):
        RGBA = m.to_rgba(A)

        X = np.reshape(convertToX(Ix), (-1, 1))
        Y = np.reshape(convertToY(Iy), (-1, 1))
        Z = np.reshape(convertToZ(Iz), (-1, 1))

        A = np.reshape(A, (-1, 1))

        number_arr = (np.concatenate((RGBA[:,:3], A, X, Y, Z), axis = 1)).flatten()
        f.write(str(number_arr.tolist()))
    else:
        f.write('[]')


    f.write(";\n")
    print "number of leftover vertices: %d,  %.2f%% from all" % (numVertices, float(numVertices * 100)/float(N * M * K))
    f.write("var numVertices = " + str(numVertices) + ";\n")
    f.write("var maxAbsX = " + str(maxAbsX) + ";\n")
    f.write("var maxAbsY = " + str(maxAbsY) + ";\n")
    f.write("var maxAbsZ = " + str(maxAbsZ) + ";\n")

    f.close()
    hdf5File.close()
    print("File is closed, FINISH")

if __name__ == "__main__":
    main()
