import h5py
import numpy

f = h5py.File('1.h5', 'r+')
for key_folder in f.keys():
    print("folder " + key_folder + ':')
    data = f[key_folder]
    for key_file in data.keys():
        avr = numpy.average(data[key_file][:])
        print("average of file " + key_file + " =")
        print(avr)
        data[key_file].attrs['average'] = avr
        print("attr")
        print(data[key_file].attrs['average'])
f.close()