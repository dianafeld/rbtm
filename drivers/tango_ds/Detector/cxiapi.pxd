#from libc.stdint cimport uint32_t, int64_t


cdef extern from "m3api/xiApi.h":

    ctypedef int XI_RETURN

    ctypedef void *HANDLE
    ctypedef HANDLE *PHANDLE
    ctypedef int DWORD
    ctypedef DWORD *PDWORD
    ctypedef void *LPVOID

    cdef char *XI_PRM_IMAGE_DATA_FORMAT = "imgdataformat" # Output data format. XI_IMG_FORMAT
    cdef char *XI_PRM_EXPOSURE = "exposure" # Exposure time in microseconds
    cdef char *XI_PRM_COOLING = "cooling" # Start camera cooling. XI_SWITCH
    cdef char *XI_PRM_BUFFER_POLICY = "buffer_policy"# Data move policy XI_BP

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

    ctypedef XI_IMG *LPXI_IMG

    ctypedef enum XI_OPEN_BY:
        XI_OPEN_BY_INST_PATH,  # Open camera by its hardware path
        XI_OPEN_BY_SN,  # Open camera by its serial number
        XI_OPEN_BY_USER_ID  # open camera by its custom user ID

    ctypedef enum XI_PRM_TYPE:
        xiTypeInteger,  # integer parameter type
        xiTypeFloat,  # float parameter type
        xiTypeString  # string parameter type

    ctypedef enum XI_SWITCH:
        XI_OFF # Turn parameter off
        XI_ON # Turn parameter on


    ctypedef enum XI_BP:
        XI_BP_UNSAFE #User gets pointer to internally allocated circle buffer and data may be overwritten by device.
        XI_BP_SAFE  # Data from device will be copied to user allocated buffer or xiApi allocated memory.





    # Error codes xiApi
    ctypedef enum XI_RET:
        XI_OK                             = 0, # Function call succeeded
        XI_INVALID_HANDLE                 = 1, # Invalid handle
        XI_READREG                        = 2, # Register read error
        XI_WRITEREG                       = 3, # Register write error
        XI_FREE_RESOURCES                 = 4, # Freeing resiurces error
        XI_FREE_CHANNEL                   = 5, # Freeing channel error
        XI_FREE_BANDWIDTH                 = 6, # Freeing bandwith error
        XI_READBLK                        = 7, # Read block error
        XI_WRITEBLK                       = 8, # Write block error
        XI_NO_IMAGE                       = 9, # No image
        XI_TIMEOUT                        =10, # Timeout
        XI_INVALID_ARG                    =11, # Invalid arguments supplied
        XI_NOT_SUPPORTED                  =12, # Not supported
        XI_ISOCH_ATTACH_BUFFERS           =13, # Attach buffers error
        XI_GET_OVERLAPPED_RESULT          =14, # Overlapped result
        XI_MEMORY_ALLOCATION              =15, # Memory allocation error
        XI_DLLCONTEXTISNULL               =16, # DLL context is NULL
        XI_DLLCONTEXTISNONZERO            =17, # DLL context is non zero
        XI_DLLCONTEXTEXIST                =18, # DLL context exists
        XI_TOOMANYDEVICES                 =19, # Too many devices connected
        XI_ERRORCAMCONTEXT                =20, # Camera context error
        XI_UNKNOWN_HARDWARE               =21, # Unknown hardware
        XI_INVALID_TM_FILE                =22, # Invalid TM file
        XI_INVALID_TM_TAG                 =23, # Invalid TM tag
        XI_INCOMPLETE_TM                  =24, # Incomplete TM
        XI_BUS_RESET_FAILED               =25, # Bus reset error
        XI_NOT_IMPLEMENTED                =26, # Not implemented
        XI_SHADING_TOOBRIGHT              =27, # Shading too bright
        XI_SHADING_TOODARK                =28, # Shading too dark
        XI_TOO_LOW_GAIN                   =29, # Gain is too low
        XI_INVALID_BPL                    =30, # Invalid bad pixel list
        XI_BPL_REALLOC                    =31, # Bad pixel list realloc error
        XI_INVALID_PIXEL_LIST             =32, # Invalid pixel list
        XI_INVALID_FFS                    =33, # Invalid Flash File System
        XI_INVALID_PROFILE                =34, # Invalid profile
        XI_INVALID_CALIBRATION            =35, # Invalid calibration
        XI_INVALID_BUFFER                 =36, # Invalid buffer
        XI_INVALID_DATA                   =38, # Invalid data
        XI_TGBUSY                         =39, # Timing generator is busy
        XI_IO_WRONG                       =40, # Wrong operation open/write/read/close
        XI_ACQUISITION_ALREADY_UP         =41, # Acquisition already started
        XI_OLD_DRIVER_VERSION             =42, # Old version of device driver installed to the system.
        XI_GET_LAST_ERROR                 =43, # To get error code please call GetLastError function.
        XI_CANT_PROCESS                   =44, # Data can't be processed
        XI_ACQUISITION_STOPED             =45, # Acquisition has been stopped. It should be started before GetImage.
        XI_ACQUISITION_STOPED_WERR        =46, # Acquisition has been stoped with error.
        XI_INVALID_INPUT_ICC_PROFILE      =47, # Input ICC profile missed or corrupted
        XI_INVALID_OUTPUT_ICC_PROFILE     =48, # Output ICC profile missed or corrupted
        XI_DEVICE_NOT_READY               =49, # Device not ready to operate
        XI_SHADING_TOOCONTRAST            =50, # Shading too contrast
        XI_ALREADY_INITIALIZED            =51, # Module already initialized
        XI_NOT_ENOUGH_PRIVILEGES          =52, # Application doesn't enough privileges(one or more app
        XI_NOT_COMPATIBLE_DRIVER          =53, # Installed driver not compatible with current software
        XI_TM_INVALID_RESOURCE            =54, # TM file was not loaded successfully from resources
        XI_DEVICE_HAS_BEEN_RESETED        =55, # Device has been reseted, abnormal initial state
        XI_NO_DEVICES_FOUND               =56, # No Devices Found
        XI_RESOURCE_OR_FUNCTION_LOCKED    =57, # Resource(device) or function locked by mutex
        XI_BUFFER_SIZE_TOO_SMALL          =58, # Buffer provided by user is too small
        XI_COULDNT_INIT_PROCESSOR         =59, # Couldn't initialize processor.
        XI_NOT_INITIALIZED                =60, # The object/module/procedure/process being referred to has not been started.
        XI_UNKNOWN_PARAM                  =100, # Unknown parameter
        XI_WRONG_PARAM_VALUE              =101, # Wrong parameter value
        XI_WRONG_PARAM_TYPE               =103, # Wrong parameter type
        XI_WRONG_PARAM_SIZE               =104, # Wrong parameter size
        XI_BUFFER_TOO_SMALL               =105, # Input buffer too small
        XI_NOT_SUPPORTED_PARAM            =106, # Parameter info not supported
        XI_NOT_SUPPORTED_PARAM_INFO       =107, # Parameter info not supported
        XI_NOT_SUPPORTED_DATA_FORMAT      =108, # Data format not supported
        XI_READ_ONLY_PARAM                =109, # Read only parameter
        XI_BANDWIDTH_NOT_SUPPORTED        =111, # This camera does not support currently available bandwidth
        XI_INVALID_FFS_FILE_NAME          =112, # FFS file selector is invalid or NULL
        XI_FFS_FILE_NOT_FOUND             =113, # FFS file not found
        XI_PROC_OTHER_ERROR               =201, # Processing error - other
        XI_PROC_PROCESSING_ERROR          =202, # Error while image processing.
        XI_PROC_INPUT_FORMAT_UNSUPPORTED  =203, # Input format is not supported for processing.
        XI_PROC_OUTPUT_FORMAT_UNSUPPORTED =204, # Output format is not supported for processing.


    XI_RETURN xiGetNumberDevices(PDWORD pNumberDevices)

    XI_RETURN xiGetDeviceInfo(DWORD DevId, const char *prm, void *val, DWORD *size, XI_PRM_TYPE *type)

    XI_RETURN xiOpenDevice(DWORD DevId, PHANDLE hDevice)

    XI_RETURN xiOpenDeviceBy(XI_OPEN_BY sel, const char *prm, PHANDLE hDevice);

    XI_RETURN xiCloseDevice(HANDLE hDevice)

    XI_RETURN xiStartAcquisition(HANDLE hDevice)

    XI_RETURN xiStopAcquisition(HANDLE hDevice)

    XI_RETURN xiGetImage(HANDLE hDevice, DWORD timeout, LPXI_IMG img)

    XI_RETURN xiSetParam(HANDLE hDevice, const char *prm, void *val, DWORD size, XI_PRM_TYPE type);

    XI_RETURN xiGetParam(HANDLE hDevice, const char *prm, void *val, DWORD *size, XI_PRM_TYPE *type);

    # -----------------------------------------------------------------------------------
    # Set device parameter
    XI_RETURN xiSetParamInt(HANDLE hDevice, const char *prm, const int val);
    XI_RETURN xiSetParamFloat(HANDLE hDevice, const char *prm, const float val);
    XI_RETURN xiSetParamString(HANDLE hDevice, const char *prm, void *val, DWORD size);
    # -----------------------------------------------------------------------------------
    # Get device parameter
    XI_RETURN xiGetParamInt(HANDLE hDevice, const char *prm, int *val);
    XI_RETURN xiGetParamFloat(HANDLE hDevice, const char *prm, float *val);
    XI_RETURN xiGetParamString(HANDLE hDevice, const char *prm, void *val, DWORD size);
    # -----------------------------------------------------------------------------------
    # Get device info
    XI_RETURN xiGetDeviceInfoInt(DWORD DevId, const char *prm, int *value);
    XI_RETURN xiGetDeviceInfoString(DWORD DevId, const char *prm, char *value, DWORD value_size);
    # -----------------------------------------------------------------------------------






