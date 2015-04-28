from cximc cimport *

import PyTango

error_description = {	result_ok: "success",
						result_error: "generic error",
						result_not_implemented: "function is not implemented",
						result_value_error: "value writing error",
						result_nodevice: "device is lost" 
						}

def get_description(error_code):
	return error_description[error_code]


cdef void create_exception(func_name, description) except *:
	reason = "Motor_LibraryError"
	origin = func_name

	# DEBUG OUTPUT
	print(reason, description, origin)
	# END DEBUG OUTPUT
	
	PyTango.Except.throw_exception(reason, description, origin)

def handle_error(error_code, origin):
	if error_code != result_ok:
		create_exception(origin, get_description(error_code))
	
cdef class Motor:
	cdef device_t motor_id
	cdef char* device_name

	def __cinit__(self, name):
		self.motor_id = device_undefined
		self.device_name = name

	def open(self):
		self.motor_id = open_device(self.device_name)
		if self.motor_id == device_undefined:
			create_exception("Motor.open()", "open failed")			

	def close(self):
		result_code = close_device(&self.motor_id)
		handle_error("Motor.close()", result_code)

	def set_zero(self):
		result_code = command_zero(self.motor_id)
		handle_error("Motor.set_zero()", result_code)

	def move_to_position(self, position, uposition):
		result_code = command_move(self.motor_id, position, uposition)
		handle_error("Motor.move_to_position()", result_code)









