cimport cxiapi

cdef class Detector:
    def __cinit__(self):
        cdef cxiapi.DWORD a

        e = cxiapi.xiGetNumberDevices(&a)
        print(e)
        print(a)

        cdef cxiapi.HANDLE device

        e = cxiapi.xiOpenDevice(1, &device)
        print(e)

        cdef cxiapi.XI_IMG image
        e = cxiapi.xiGetImage(device, 5000, &image)
        print(e)
