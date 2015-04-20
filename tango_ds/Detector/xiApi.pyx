cimport cxiapi


def handle_error(return_code):
    if return_code != cxiapi.XI_OK:
        print("Detector. Error occurred: {}".format(return_code))

cdef class Detector:

    cdef cxiapi.HANDLE handle
    TIMEOUT = 10 # in ms
    def __cinit__(self):
        cdef cxiapi.DWORD a

        e = cxiapi.xiGetNumberDevices(&a)
        handle_error(e)
        print(a)

        e = cxiapi.xiOpenDevice(1, &self.handle)
        handle_error(e)

        e = cxiapi.xiSetParamInt(self.handle, cxiapi.XI_PRM_IMAGE_DATA_FORMAT, cxiapi.XI_MONO16)
        handle_error(e)

    def set_exposure(self, exposure):
        e = cxiapi.xiSetParamInt(self.handle, cxiapi.XI_PRM_EXPOSURE, exposure * 1000)
        handle_error(e)

    def get_exposure(self):
        cdef int exposure_in_us
        e = cxiapi.xiGetParamInt(self.handle, cxiapi.XI_PRM_EXPOSURE, &exposure_in_us)
        handle_error(e)
        return round(exposure_in_us / 1000)

    def get_image(self):
        cdef cxiapi.XI_IMG image
        e = cxiapi.xiGetImage(self.handle, Detector.TIMEOUT, &image)
        handle_error(e)

        #return image.height, image.width, image.bp

    def __dealloc__(self):
        e = cxiapi.xiCloseDevice(self.handle)
        handle_error(e)
        print('Dealloc')