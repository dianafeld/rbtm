from cximc cimport *

import PyTango

error_description = {result_ok: "success",
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
    cdef device_t device_id
    cdef char *device_name

    def __cinit__(self, name):
        self.device_id = device_undefined
        self.device_name = name

    def open(self):
        # cdef device_enumeration_t dev_enum
        # dev_enum = enumerate_devices(0)
        # self.device_name = get_device_name(dev_enum, 0)
        # free_enumerate_devices(dev_enum)

        self.device_id = open_device(self.device_name)
        if self.device_id == device_undefined:
            create_exception("Motor.open()", "open failed")

        cdef edges_settings_t edges_settings
        get_edges_settings(self.device_id, &edges_settings)
        edges_settings.BorderFlags = 0
        set_edges_settings(self.device_id, &edges_settings)

    def close(self):
        cdef int tmp_device_id = self.device_id
        result_code = close_device(&tmp_device_id)
        handle_error(result_code, "Motor.close()")

    def set_zero(self):
        result_code = command_zero(self.device_id)
        handle_error(result_code, "Motor.set_zero()")

    def get_position(self):
        cdef get_position_t position
        result_code = get_position(self.device_id, &position)
        handle_error(result_code, "Motor.get_position()")
        return position

    def move_to_position(self, position, uposition):
        result_code = command_move(self.device_id, position, uposition)
        handle_error(result_code, "Motor.move_to_position()")

    def get_move_settings(self):
        cdef move_settings_t move_settings
        result_code = get_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.get_move_settings()")
        return move_settings

    def set_move_settings(self, speed, accel):
        cdef move_settings_t move_settings
        get_move_settings(self.device_id, &move_settings)
        move_settings.Speed = speed
        move_settings.Accel = accel
        move_settings.Decel = accel
        result_code = set_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.set_move_settings()")

    def set_speed(self, speed):
        cdef move_settings_t move_settings
        get_move_settings(self.device_id, &move_settings)
        move_settings.Speed = speed
        result_code = set_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.set_speed()")

    def set_accel(self, accel):
        cdef move_settings_t move_settings
        get_move_settings(self.device_id, &move_settings)
        move_settings.Accel = accel
        result_code = set_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.set_accel()")

    def set_decel(self, decel):
        cdef move_settings_t move_settings
        get_move_settings(self.device_id, &move_settings)
        move_settings.Decel = decel
        result_code = set_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.set_decel()")

    def get_status(self):
        cdef status_t status
        get_status(self.device_id, &status)
        return status

    def __dealloc__(self):
        pass










