#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import h5py
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import os

def main():

    COLORMAP = cm.hsv
    GROUP_COUNT = 8

    hfd5FileName = "largeData/hand/result_r50.hdf5"
    outputFileName = "on_server/R50_" + str(GROUP_COUNT) + "G.json"


    hdf5File = h5py.File(hfd5FileName, 'r')
    dataCube = hdf5File["Results"]

    #rarefaction = int(hdf5File["rarefaction_num"][0])
    rarefaction = 50
    print "Cube shape:", dataCube.shape, "  rarefaction number: ", rarefaction


    N, M, K = dataCube.shape

    minValue = np.min(dataCube)
    maxValue = np.max(dataCube)
    if maxValue == minValue:
        print "All values are the same - look for better data!\nStop."
        return

    norm = mpl.colors.Normalize(vmin=minValue, vmax=maxValue)
    m = cm.ScalarMappable(norm=norm, cmap=COLORMAP)

    range_of_values = maxValue - minValue


    thresholds = [minValue + float(i) / float(GROUP_COUNT) * range_of_values for i in xrange(0, GROUP_COUNT + 1)]

    #print dict(zip(range(0, GROUP_COUNT + 1), thresholds))

    RGBA_str = "\"RGBA\" : [\n"

    f = open(outputFileName, 'w')
    f.seek(0)
    f.truncate()
    f.write('{\n\"group_count\" : %d,\n' % GROUP_COUNT)
    f.write('\"NMK\" : [%d, %d, %d],\n\"points\" : [\n' % (N, M, K))

    print ("Splitting to %d groups..." % GROUP_COUNT)
    for group in xrange(1, GROUP_COUNT + 1):
        if group % 8 == 0:
            print ("   %d groups are done" % group)

        threshold_A, threshold_B = thresholds[group - 1], thresholds[group]
        Ix, Iy, Iz = np.where( (threshold_A <= dataCube)  & (dataCube < threshold_B) )


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
        else:
            f.write(str(XYZ.tolist()).replace(" ", "") + "\n" )
            RGBA_str += str(rgba.tolist()) + "\n"

    f.write("],\n")
    RGBA_str += "],\n"
    f.write(RGBA_str)
    f.write('\"rarefaction\" : %d\n}' % rarefaction)
    f.close()
    hdf5File.close()

    print("Finish writing, filename is: '%s', size of file: %.1f MB"
          % (outputFileName, float(os.stat(outputFileName).st_size)/1048576.0) )



if __name__ == "__main__":
    main()
