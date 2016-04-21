#!/usr/bin/python
# -*- coding: UTF-8 -*-

# script for doing median filtration of 3d arrays

import sys
import h5py
import numpy as np
import os
import scipy.signal

def filtration(cernel_size, plane_dir = ""):

    if (cernel_size == 1):
        print ("Filtration cernel size is 1, there is nothing to do.\nStop.")
        return

    out_dir_name = ""

    print ("Median filtration kernel size is %d") % (cernel_size)

    fileIn = h5py.File("f1r1.hdf5", 'r')
    try:
        dataCube = fileIn["Results"]
    except:
        dataCube = fileIn["Result"]

    if plane_dir == "x":
        print("Doing square filtration, direction is X...")
        filtered_datacube = scipy.signal.medfilt(dataCube, (1, cernel_size, cernel_size)).astype(np.float32)
    elif plane_dir == "y":
        print("Doing square filtration, direction is Y...")
        filtered_datacube = scipy.signal.medfilt(dataCube, (cernel_size, 1, cernel_size)).astype(np.float32)
    elif plane_dir == "z":
        print("Doing square filtration, direction is Z...")
        filtered_datacube = scipy.signal.medfilt(dataCube, (cernel_size, cernel_size, 1)).astype(np.float32)
    else:
        plane_dir = ""
        print("Doing cubic filtration...")
        filtered_datacube = scipy.signal.medfilt(dataCube, cernel_size).astype(np.float32)
    fileIn.close()
    print "filtered_datacube1.shape: ", filtered_datacube.shape
    dataCube = filtered_datacube

    """
    hfd5FileInName1 = "largeData/hand/result11.hdf5"
    hfd5FileInName2 = "largeData/hand/result22.hdf5"
    hfd5FileInName3 = "largeData/hand/result33.hdf5"


    hfd5FileIn1 = h5py.File(hfd5FileInName1, 'r')
    dataCube1 = hfd5FileIn1["Results"]
    filtered_datacube1 = scipy.signal.medfilt(dataCube1, cernel_size).astype(np.float32)
    hfd5FileIn1.close()
    print "filtered_datacube1.shape: ", filtered_datacube1.shape

    hfd5FileIn2 = h5py.File(hfd5FileInName2, 'r')
    dataCube2 = hfd5FileIn2["Results"]
    filtered_datacube2 = scipy.signal.medfilt(dataCube2, cernel_size).astype(np.float32)
    hfd5FileIn2.close()
    print "filtered_datacube2.shape: ", filtered_datacube2.shape

    hfd5FileIn3 = h5py.File(hfd5FileInName3, 'r')
    dataCube3 = hfd5FileIn3["Results"]
    filtered_datacube3 = scipy.signal.medfilt(dataCube3, cernel_size).astype(np.float32)
    hfd5FileIn3.close()
    print "filtered_datacube3.shape: ", filtered_datacube3.shape

    dataCube = np.concatenate((filtered_datacube1[:-10], filtered_datacube2[10:-10], filtered_datacube3[10:]))
    print("Done")
    """

    fileOutName = out_dir_name + "f" + str(cernel_size) + "r1.hdf5"
    fileOut = h5py.File(fileOutName)
    fileOut["Results"] = dataCube
    fileOut["filtration_cernel_size"] = (cernel_size,)
    fileOut["filtration_plane_direction"] = (plane_dir,)
    fileOut.close()
    print("Finish, filename is: '%s', size of file: %.1f MB" 
          % (fileOutName, float(os.stat(fileOutName).st_size)/1048576.0) )


if __name__ == "__main__":


    if len(sys.argv) < 2:
        print "usage: filtration <filtration_cernel_size> [direction of plane of filtration ('x', 'y' or 'z')]"
    else:
        cernel_size = int(sys.argv[1])

        plane_dir = ""
        if len(sys.argv) > 2:
            plane_dir = str(sys.argv[2])

        filtration(cernel_size, plane_dir)
