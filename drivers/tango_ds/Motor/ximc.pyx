from cximc cimport *

import time
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

    def __cinit__(self, name, number):
        self.device_id = device_undefined
        # self.device_name = name

        cdef device_enumeration_t dev_enum
        dev_enum = enumerate_devices(0, "")
        self.device_name = get_device_name(dev_enum, number)
        if self.device_name != name:
            number = 1 - number
            self.device_name = get_device_name(dev_enum, number)
        free_enumerate_devices(dev_enum)
        print(number, self.device_name)

    def open(self):
        self.device_id = open_device(self.device_name)
        if self.device_id == device_undefined:
            create_exception("Motor.open()", "open failed")

        cdef edges_settings_t edges_settings
        get_edges_settings(self.device_id, &edges_settings)
        edges_settings.BorderFlags = 0
        set_edges_settings(self.device_id, &edges_settings)

        return self

    def close(self):
        print("Close")
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
        return position.Position

    def move_to_position(self, position, uposition=0):
        result_code = command_move(self.device_id, position, uposition)
        handle_error(result_code, "Motor.move_to_position()")

    def move_by_delta(self, delta_position, udelta_position=0):
        result_code = command_movr(self.device_id, delta_position, udelta_position)
        handle_error(result_code, "Motor.move_by_delta()")

    def get_move_settings(self):
        cdef move_settings_t move_settings
        result_code = get_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.get_move_settings()")
        return move_settings

    def set_move_settings(self, speed=None, accel=None, decel=None):
        cdef move_settings_t move_settings
        get_move_settings(self.device_id, &move_settings)
        if speed is not None:
            move_settings.Speed = speed
        if accel is not None:
            move_settings.Accel = accel
        if decel is not None:
            move_settings.Decel = decel
        elif accel is not None: # may cause problems if we don't want to change decel
            move_settings.Decel = accel

        result_code = set_move_settings(self.device_id, &move_settings)
        handle_error(result_code, "Motor.set_move_settings()")

    def get_status(self):
        cdef status_t status
        get_status(self.device_id, &status)
        return status

    def wait_for_stop(self, refresh_interval_in_ms=100):
        time.sleep(0.1)
        result_code = command_wait_for_stop(self.device_id, refresh_interval_in_ms)
        handle_error(result_code, "Motor.wait_for_stop()")

    def __dealloc__(self):
        pass










