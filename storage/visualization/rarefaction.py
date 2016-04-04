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
        print("usage: rarefaction_filtration.py  <RAREFACTION_NUM(int)>\nIf you don't want to rarefy, set RAREFACTION_NUM as 1")
        return

    RAREFACTION = int(sys.argv[1])

    print ("Rarefaction number is %d") % (RAREFACTION)
    if (RAREFACTION == 1):
        print ("Rarefaction number is 1, there is nothing to do")
        return

    hdf5FileIn = h5py.File(hfd5FileInName, 'r')
    dataCube = hdf5FileIn["Results"]
    print "Original cube shape:", dataCube.shape


    hfd5FileOutNamePrefix = hfd5FileInName[:-5]
    hfd5FileOutNameSuffix = hfd5FileInName[-5:]

    hfd5FileOutName = hfd5FileOutNamePrefix

    if RAREFACTION > 1:
        print("Rarefying dataCube...")
        dataCube = dataCube[::RAREFACTION, ::RAREFACTION, ::RAREFACTION]
        print "Rarefied cube shape:", dataCube.shape
        if (hfd5FileOutNamePrefix[-1] == 't'):
            hfd5FileOutName += "_"
        hfd5FileOutName += "r" + str(RAREFACTION)

    hfd5FileOutName += hfd5FileOutNameSuffix
    hdf5FileOut = h5py.File(hfd5FileOutName)
    hdf5FileOut["Results"] = dataCube
    hdf5FileOut["rarefaction_num"] = (RAREFACTION,)

    hdf5FileIn.close()
    hdf5FileOut.close()
    print("Finish, filename is: '%s', size of file: %.1f MB" 
          % (hfd5FileOutName, float(os.stat(hfd5FileOutName).st_size)/1048576.0) )


if __name__ == "__main__":
    main()
