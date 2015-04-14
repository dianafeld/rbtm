#from libc.stdint cimport uint32_t, int64_t


cdef extern from "m3api/xiApi.h":

    ctypedef int XI_RETURN

    ctypedef void*HANDLE
    ctypedef HANDLE*PHANDLE
    ctypedef int DWORD
    ctypedef DWORD*PDWORD
    ctypedef void*LPVOID

    cdef char*XI_PRM_IMAGE_DATA_FORMAT = "imgdataformat"

    ctypedef enum XI_IMG_FORMAT:
        XI_MONO8,  # 8 bits per pixel
        XI_MONO16,  # 16 bits per pixel
        XI_RGB24,  # RGB data format
        XI_RGB32,  # RGBA data format
        XI_RGB_PLANAR,  # RGB planar data format
        XI_RAW8,  # 8 bits per pixel raw data from sensor
        XI_RAW16,  # 16 bits per pixel raw data from sensor
        XI_FRM_TRANSPORT_DATA  # Data from transport layer (e.g. packed). Format see XI_PRM_TRANSPORT_PIXEL_FORMAT

    ctypedef struct XI_IMG:
        DWORD         size  # Size of current structure on application side. When xiGetImage is called and size>=SIZE_XI_IMG_V2 then GPI_level, tsSec and tsUSec are filled.
        LPVOID        bp  # pointer to data. If NULL, xiApi allocates new buffer.
        DWORD         bp_size  # Filled buffer size. When buffer policy is set to XI_BP_SAFE, xiGetImage will fill this field with current size of image data received.
        XI_IMG_FORMAT frm  # format of incoming data.
        DWORD         width  # width of incoming image.
        DWORD         height  # height of incoming image.
        DWORD         nframe  # frame number(reset by exposure, gain, downsampling change).
        DWORD         tsSec  # TimeStamp in seconds
        DWORD         tsUSec  # TimeStamp in microseconds
        DWORD         GPI_level  # Input level
        DWORD         black_level  # Black level of image (ONLY for MONO and RAW formats)
        DWORD         padding_x  # Number of extra bytes provided at the end of each line to facilitate image alignment in buffers.
        DWORD         AbsoluteOffsetX  # Horizontal offset of origin of sensor and buffer image first pixel.
        DWORD         AbsoluteOffsetY  # Vertical offset of origin of sensor and buffer image first pixel.

    ctypedef XI_IMG*LPXI_IMG

    ctypedef enum XI_OPEN_BY:
        XI_OPEN_BY_INST_PATH,  # Open camera by its hardware path
        XI_OPEN_BY_SN,  # Open camera by its serial number
        XI_OPEN_BY_USER_ID  # open camera by its custom user ID

    ctypedef enum XI_PRM_TYPE:
        xiTypeInteger,  # integer parameter type
        xiTypeFloat,  # float parameter type
        xiTypeString  # string parameter type


    XI_RETURN xiGetNumberDevices(PDWORD pNumberDevices)

    XI_RETURN xiGetDeviceInfo(DWORD DevId, const char*prm, void*val, DWORD *size, XI_PRM_TYPE *type)

    XI_RETURN xiOpenDevice(DWORD DevId, PHANDLE hDevice)

    XI_RETURN xiOpenDeviceBy(XI_OPEN_BY sel, const char*prm, PHANDLE hDevice);

    XI_RETURN xiCloseDevice(HANDLE hDevice)

    XI_RETURN xiStartAcquisition(HANDLE hDevice)

    XI_RETURN xiStopAcquisition(HANDLE hDevice)

    XI_RETURN xiGetImage(HANDLE hDevice, DWORD timeout, LPXI_IMG img)

    XI_RETURN xiSetParam(HANDLE hDevice, const char*prm, void*val, DWORD size, XI_PRM_TYPE type);

    XI_RETURN xiGetParam(HANDLE hDevice, const char*prm, void*val, DWORD *size, XI_PRM_TYPE *type);

    # -----------------------------------------------------------------------------------
    # Set device parameter
    XI_RETURN xiSetParamInt(HANDLE hDevice, const char*prm, const int val);
    XI_RETURN xiSetParamFloat(HANDLE hDevice, const char*prm, const float val);
    XI_RETURN xiSetParamString(HANDLE hDevice, const char*prm, void*val, DWORD size);
    # -----------------------------------------------------------------------------------
    # Get device parameter
    XI_RETURN xiGetParamInt(HANDLE hDevice, const char*prm, int*val);
    XI_RETURN xiGetParamFloat(HANDLE hDevice, const char*prm, float*val);
    XI_RETURN xiGetParamString(HANDLE hDevice, const char*prm, void*val, DWORD size);
    # -----------------------------------------------------------------------------------
    # Get device info
    XI_RETURN xiGetDeviceInfoInt(DWORD DevId, const char*prm, int*value);
    XI_RETURN xiGetDeviceInfoString(DWORD DevId, const char*prm, char*value, DWORD value_size);
    # -----------------------------------------------------------------------------------






