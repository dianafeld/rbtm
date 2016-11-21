#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import h5py
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import os



def prepare_points(filtration_cernel_size, rarefaction, lower_bound = 0, upper_bound = 100, dirname = ""):

    COLORMAP = cm.hsv
    GROUP_COUNT = 100
    # dividing to 100, not 128 groups as earlier, because it is easier to name some files
    # which contain not all groups, but interval, for example "F7R7_L45U57.json"
    # which means from 45th to 57th groups. Also better display in percents this way.


    if upper_bound <= lower_bound:
        print "Upper bound must be more than lower bound!\nStop."
        return

    try:
        os.chdir(dirname)
    except: pass

    if (lower_bound == 0) and (upper_bound == 100):
        outputFileName = "F%dR%d.json" % (filtration_cernel_size, rarefaction)
    else:
        outputFileName = "cut/F%dR%d_L%dU%d.json" % (filtration_cernel_size, rarefaction, lower_bound, upper_bound)
        

    hfd5FileName = "f%dr%d.hdf5" % (filtration_cernel_size, rarefaction)
    hdf5File = h5py.File(hfd5FileName, 'r')
    try:
        dataCube = hdf5File["Results"]
    except:
        dataCube = hdf5File["Result"]


    print "Cube shape:", dataCube.shape, "  filtration cernel size: ", filtration_cernel_size, "  rarefaction number: ",rarefaction
    print "lower bound: %d%%      upper bound: %d%%" % (lower_bound, upper_bound)


    N, M, K = dataCube.shape

    minValue = np.min(dataCube)
    maxValue = np.max(dataCube)
    if maxValue == minValue:
        print "All values are the same - look for better data!\nStop."
        return

    range_of_values = maxValue - minValue


    maxValue = minValue + (upper_bound * range_of_values)/100
    minValue = minValue + (lower_bound * range_of_values)/100
    range_of_values = maxValue - minValue


    norm = mpl.colors.Normalize(vmin=minValue, vmax=maxValue)
    m = cm.ScalarMappable(norm=norm, cmap=COLORMAP)


    thresholds = [minValue + float(i) / float(GROUP_COUNT) * range_of_values for i in xrange(0, GROUP_COUNT + 1)]

    #print dict(zip(range(0, GROUP_COUNT + 1), thresholds))

    RGBA_str = "\"RGBA\" : [\n"

    point_cnt = 0
    COUNT_str = "\"COUNT\" : [\n0,"

    f = open(outputFileName, 'w')
    f.seek(0)
    f.truncate()
    f.write('{\n\"group_count\" : %d,\n' % GROUP_COUNT)
    f.write('\"NMK\" : [%d, %d, %d],\n\"points\" : [\n' % (N, M, K))

    print ("Splitting to %d groups..." % GROUP_COUNT)
    for group in xrange(1, GROUP_COUNT + 1):
        if group % 20 == 0:
            print ("   %d groups are done" % group)

        threshold_A, threshold_B = thresholds[group - 1], thresholds[group]
        Ix, Iy, Iz = np.where( (threshold_A <= dataCube)  & (dataCube < threshold_B) )

        point_cnt += Ix.shape[0]

        rgba = np.array(m.to_rgba(threshold_A))
        rgba[3] = float(group)/float(GROUP_COUNT)
        #rgba = (rgba * 256).astype(int)


        X = (Ix - N / 2) * rarefaction
        Y = (Iy - M / 2) * rarefaction
        Z = (Iz - K / 2) * rarefaction
        XYZ = np.concatenate(((X,), (Y,), (Z,)))
        XYZ = np.reshape(a=XYZ, newshape=(-1), order='F')
        if (group != GROUP_COUNT):
            f.write(str(XYZ.tolist()).replace(" ", "") + ",\n" )
            RGBA_str += str(rgba.tolist()) + ",\n"
            COUNT_str += str(point_cnt) + ","
        else:
            f.write(str(XYZ.tolist()).replace(" ", "") + "\n" )
            RGBA_str += str(rgba.tolist()) + "\n"
            COUNT_str += str(point_cnt) + "\n"

    RGBA_str += "],\n"
    COUNT_str += "],\n"

    f.write("],\n")
    f.write(RGBA_str)
    f.write(COUNT_str)
    f.write('\"rarefaction\" : %d\n}' % rarefaction)
    f.close()
    hdf5File.close()

    print("Finish writing, filename is: '%s', size of file: %.1f MB"
          % (outputFileName, float(os.stat(outputFileName).st_size)/1048576.0) )
    return dirname + outputFileName



if __name__ == "__main__":


    if len(sys.argv) < 3:
        print "usage: <filtration cernel size> <rarefaction num> [lower bound] [upper bound]"
    else:

        filtration_cernel_size = int(sys.argv[1])
        rarefaction = int(sys.argv[2])

        # LOWER_BOUND and UPPER_BOUND are in PERCENTS!
        LOWER_BOUND = 0
        UPPER_BOUND = 100


        if len(sys.argv) > 3:
            LOWER_BOUND = int(float(sys.argv[3]))  # int(float(...))-because it doesn't work for int('4.0000')
            LOWER_BOUND = min(max(LOWER_BOUND, 0), 100)

            if len(sys.argv) > 4:
                UPPER_BOUND = int(float(sys.argv[4]))
                UPPER_BOUND = min(max(UPPER_BOUND, 0), 100)

        prepare_points(filtration_cernel_size, rarefaction, LOWER_BOUND, UPPER_BOUND)