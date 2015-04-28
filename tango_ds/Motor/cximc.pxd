cdef extern from "ximc.h":
	cdef int result_ok = 0
	cdef int result_error = -1
	cdef int result_not_implemented = -2
	cdef int result_value_error = -3
	cdef int result_nodevice = -4
	cdef int device_undefined = -1
	
	ctypedef int device_t
	ctypedef int result_t
	ctypedef int device_enumeration_t
	ctypedef char* pchar

	device_t open_device(const char* name)
	result_t close_device(device_t* id)
	result_t command_zero(device_t id)
	result_t command_move(device_t id, int Position, int uPosition)
	result_t command_stop(device_t id)
	device_enumeration_t enumerate_devices(int probe_flags)
	int get_device_count(device_enumeration_t device_enumeration)
	pchar get_device_name(device_enumeration_t device_enumeration, int device_index)



