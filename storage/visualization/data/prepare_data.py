#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
from filtration import filtration
from rarefaction import rarefaction
from prepare_points import prepare_points

def prepare_data(hdf5_filename, dirname, max_filt_num, filt_plane_dir=""):

	os.chdir("prepared_data")

	if filt_plane_dir in ('x', 'y', 'z'):
		dirname += "_" + filt_plane_dir

	if not os.path.isdir(dirname):
		os.mkdir(dirname)
	os.chdir(dirname)
	if not os.path.isfile(hdf5_filename):
		os.rename("../../" + hdf5_filename, hdf5_filename)

	if os.path.islink("f1r1.hdf5"):
		os.remove("f1r1.hdf5")
	os.symlink(hdf5_filename, "f1r1.hdf5")


	if not os.path.isdir("cut"):
		os.mkdir("cut")

	#for FCS in xrange(3, 7, 2):

	for filt_num in xrange(1, max_filt_num, 2):

		if not os.path.isfile("f%dr1.hdf5" % filt_num):
			print "\nCREATING f%dr1.hdf5 ..." % filt_num
			filtration(filt_num, filt_plane_dir)

		for rar_num in xrange(1, 8):
			if not os.path.isfile("f%dr%d.hdf5" % (filt_num, rar_num) ):
				print "\nCREATING f%dr%d.hdf5 ..." % (filt_num, rar_num)
				rarefaction(rar_num, filt_num)

			if (rar_num > 4) and   (  not os.path.isfile("F%dR%d.json" % (filt_num, rar_num) )   ):
				print "\nCREATING F%dR%d.json ..." % (filt_num, rar_num)
				prepare_points(filt_num, rar_num)







if __name__ == "__main__":

	#MAX_FILT_NUM = 7

	if len(sys.argv) < 4:
		print "usage: prepare_data <hdf5 filename> <name of directory> <max filtration num> [direction of filtration plane]"
	else:
		hdf5_filename = str(sys.argv[1])
		dirname = str(sys.argv[2])
		MAX_FILT_NUM = int(sys.argv[3])

		filt_plane_dir = ""
		if len(sys.argv) > 4:
			filt_plane_dir = str(sys.argv[4])

		prepare_data( hdf5_filename, dirname, MAX_FILT_NUM, filt_plane_dir  )