import numpy as np
import h5py

f = h5py.File('2.h5', 'r')
for key in f.keys():
    print(key + ':')
    data = f[key]
    avr = 0
    for key1 in data.keys():
        print(key1)
        avr += np.average(data[key1][:])
    print(avr/4)
f.close()