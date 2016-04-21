#!/usr/bin/python
# -*- coding: UTF-8 -*-

# script for rarefying of 3d arrays

import sys
import h5py
import numpy as np
import os
import scipy.signal

def rarefaction(rarefaction_num, filt_cernel_size = 1):

    if (rarefaction_num == 1):
        print ("Rarefactrion number is 1, there is nothing to do.\nStop.")
        return

    #fileInName = "largeData/hand/result_f7.hdf5"
    fileInName = "f" + str(filt_cernel_size) + "r1.hdf5"


    fileIn = h5py.File(fileInName, 'r')
    try:
        dataCube = fileIn["Results"]
    except:
        dataCube = fileIn["Result"]

    print "Original cube shape:", dataCube.shape


    print("Rarefying dataCube...")
    dataCube = dataCube[::rarefaction_num, ::rarefaction_num, ::rarefaction_num]
    print "Rarefied cube shape:", dataCube.shape

    fileOutName = "f" + str(filt_cernel_size) + "r" + str(rarefaction_num) + ".hdf5"
    fileOut = h5py.File(fileOutName)
    fileOut["Results"] = dataCube
    fileOut["rarefaction_num"] = (rarefaction_num,)

    fileIn.close()
    fileOut.close()
    print("Finish, filename is: '%s', size of file: %.1f MB" 
          % (fileOutName, float(os.stat(fileOutName).st_size)/1048576.0) )


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "usage: rarefaction <rarefaction number>"
    else:
        rarefaction_num = int(sys.argv[1])
        rarefaction(rarefaction_num)