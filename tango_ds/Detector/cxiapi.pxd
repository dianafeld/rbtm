from libc.stdint cimport uint32_t, int64_t


cdef extern from "m3api/xiApi.h":
    ctypedef int XI_RETURN

    ctypedef void*HANDLE
    ctypedef HANDLE*PHANDLE
    ctypedef uint32_t DWORD
    ctypedef DWORD*PDWORD

    ctypedef struct XI_IMG:
        pass
    ctypedef XI_IMG*LPXI_IMG

    XI_RETURN xiGetNumberDevices(PDWORD pNumberDevices)

    XI_RETURN xiOpenDevice(DWORD DevId, PHANDLE hDevice)

    XI_RETURN xiCloseDevice(HANDLE hDevice)

    XI_RETURN xiStartAcquisition(HANDLE hDevice)

    XI_RETURN xiStopAcquisition(HANDLE hDevice)

    XI_RETURN xiGetImage(HANDLE hDevice, DWORD timeout, LPXI_IMG img);
