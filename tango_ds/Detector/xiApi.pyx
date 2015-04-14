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

        e = cxiapi.xiSetParamInt(device, cxiapi.XI_PRM_IMAGE_DATA_FORMAT, cxiapi.XI_MONO8)
        print(e)

        cdef cxiapi.XI_IMG image
        e = cxiapi.xiGetImage(device, 5000, &image)
        print(e)

        e = cxiapi.xiCloseDevice(device)
        print(e)