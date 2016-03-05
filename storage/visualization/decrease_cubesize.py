#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import h5py
import numpy as np
import os
import scipy.signal

def main():

    hfd5FileInName = "largeData/hand/result_r50.hdf5"
    hdf5FileIn = h5py.File(hfd5FileInName, 'r')
    dataCube = hdf5FileIn["Results"]
    print "Original cube shape:", dataCube.shape


    M, N, K = dataCube.shape

    minValue = np.min(dataCube)
    maxValue = np.max(dataCube)

    print("Analyzing dependence of cut cube size from treshold:")


    x1 = y1 = z1 = 0
    x2 = M - 1
    y2 = N - 1
    z2 = K - 1

    boundaries = {}

    tr_range = np.arange(0, 0.5, 0.01)
    #norm_tr_range = tr_range * (maxValue - minValue) + minValue
    for tr in tr_range:
        norm_tr = tr * (maxValue - minValue) + minValue
        while (np.max(dataCube[x1,:,:]) < norm_tr):
            x1 += 1
        while (np.max(dataCube[x2,:,:]) < norm_tr):
            x2 -= 1
        while (np.max(dataCube[:,y1,:]) < norm_tr):
            y1 += 1
        while (np.max(dataCube[:,y2,:]) < norm_tr):
            y2 -= 1
        while (np.max(dataCube[:,:,z1]) < norm_tr):
            z1 += 1
        while (np.max(dataCube[:,:,z2]) < norm_tr):
            z2 -= 1
        boundaries[tr] = (x1, x2, y1, y2, z1, z2)
        print "   ", tr, " -> percentage of remain points:", float((x2-x1)*(y2-y1)*(z2-z1))/float(N*M*K)

    THRESHOLD = float(raw_input("Enter threshold to cut cube (0 to exit):"))

    while (THRESHOLD > 5):
        THRESHOLD = float(raw_input("Enter threshold to cut cube (0 to exit):"))

    if THRESHOLD == 0:
        print ("Exit")
        return

    THRESHOLD = float(int(THRESHOLD * 100))/100
    boundary = boundaries[THRESHOLD]
    x1 = boundary[0]
    x2 = boundary[1]
    y1 = boundary[2]
    y2 = boundary[3]
    z1 = boundary[4]
    z2 = boundary[5]

    print "Percentage of left points", float((x2-x1)*(y2-y1)*(z2-z1))/float(N*M*K)


    dataCube = dataCube[x1:x2, y1:y2, z1:z2]

    print "Cut cube shape:", dataCube.shape

    

    hfd5FileOutNamePrefix = hfd5FileInName[:-5]
    hfd5FileOutNameSuffix = hfd5FileInName[-5:]

    hfd5FileOutName = hfd5FileOutNamePrefix + "_t" + str(THRESHOLD) + hfd5FileOutNameSuffix

    hdf5FileOut = h5py.File(hfd5FileOutName)
    hdf5FileOut["Results"] = dataCube

    hdf5FileIn.close()
    hdf5FileOut.close()
    print("Finish, filename is: '%s', size of file: %.1f MB" 
          % (hfd5FileOutName, float(os.stat(hfd5FileOutName).st_size)/1048576.0) )



if __name__ == "__main__":
    main()
