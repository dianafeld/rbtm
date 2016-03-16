#!/usr/bin/python
# -*- coding: UTF-8 -*-

# script for rarefying and doing median filtration of 3d arrays

import sys
import h5py
import numpy as np
import os
import scipy.signal

def main():

    hfd5FileInName = "largeData/hand/result.hdf5"

    if len(sys.argv) < 2:
        print("usage: rarefaction.py  RAREFACTION_NUM(int) [FILTRATION_KERNEL_SIZE(int)]\nIf you don't want to rarefy, set RAREFACTION_NUM as 1\nIf you don't want to filter, set FILTRATION_KERNEL_SIZE as 1 (default value is 3)")
        return

    RAREFACTION = int(sys.argv[1])

    KERNEL_SIZE = 3
    if len(sys.argv) > 2:
        KERNEL_SIZE = int(sys.argv[2])

    print ("Rarefaction number is %d, median filtration kernel size is %d") % (RAREFACTION, KERNEL_SIZE)
    if (RAREFACTION == 1 and KERNEL_SIZE == 1):
        print ("Both of parameters are 1, there is nothing to do")
        return

    hdf5FileIn = h5py.File(hfd5FileInName, 'r')
    dataCube = hdf5FileIn["Results"]
    print "Original cube shape:", dataCube.shape


    hfd5FileOutNamePrefix = hfd5FileInName[:-5]
    hfd5FileOutNameSuffix = hfd5FileInName[-5:]

    hfd5FileOutName = hfd5FileOutNamePrefix + "_"

    if RAREFACTION > 1:
        print("Rarefying dataCube...")
        dataCube = dataCube[::RAREFACTION, ::RAREFACTION, ::RAREFACTION]
        print "Rarefied cube shape:", dataCube.shape
        hfd5FileOutName += "r" + str(RAREFACTION)

    if KERNEL_SIZE > 1:
        print("Filtering dataCube...")
        dataCube[:200] = scipy.signal.medfilt(dataCube[:200], KERNEL_SIZE).astype(np.float32)
        dataCube[200:400] = scipy.signal.medfilt(dataCube[200:400], KERNEL_SIZE).astype(np.float32)
        dataCube[400:] = scipy.signal.medfilt(dataCube[400:], KERNEL_SIZE).astype(np.float32)
        print("Done")
        hfd5FileOutName += "f" + str(KERNEL_SIZE)

    hfd5FileOutName += hfd5FileOutNameSuffix
    hdf5FileOut = h5py.File(hfd5FileOutName)
    hdf5FileOut["Results"] = dataCube
    hdf5FileOut["rarefaction_num"] = (RAREFACTION,)
    hdf5FileOut["filtration_cernel_size"] = (KERNEL_SIZE,)

    hdf5FileIn.close()
    hdf5FileOut.close()
    print("Finish, filename is: '%s', size of file: %.1f MB" 
          % (hfd5FileOutName, float(os.stat(hfd5FileOutName).st_size)/1048576.0) )


if __name__ == "__main__":
    main()
