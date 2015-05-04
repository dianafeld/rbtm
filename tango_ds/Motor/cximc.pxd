cdef extern from "ximc.h":
    ctypedef int device_t
    ctypedef int result_t
    ctypedef int device_enumeration_t
    ctypedef char *pchar

    cdef int result_ok = 0
    cdef int result_error = -1
    cdef int result_not_implemented = -2
    cdef int result_value_error = -3
    cdef int result_nodevice = -4
    cdef int device_undefined = -1

    ctypedef struct status_t:
        unsigned int MoveSts  # flagset_movestate "Flags of move state".
        unsigned int MvCmdSts  # flagset_mvcmdstatus "Move command state".
        unsigned int PWRSts  # flagset_powerstate "Flags of power state of stepper motor".
        unsigned int EncSts  # flagset_encodestatus "Encoder state".
        unsigned int WindSts  # flagset_windstatus "Winding state".
        int CurPosition  # Current position.
        int uCurPosition  # Step motor shaft position in 1/256 microsteps. Used only with stepper motor.
        long EncPosition  # Current encoder position.
        int uCurSpeed  # Part of motor shaft speed in 1/256 microsteps. Used only with stepper motor.
        int Ipwr  # Engine current.
        int Upwr  # Power supply voltage.
        int Iusb  # USB current consumption.
        int Uusb  # USB voltage.
        int CurT  # Temperature in tenths of degrees C.
        unsigned int Flags  # flagset_stateflags "Status flags".
        unsigned int GPIOFlags  # flagset_gpioflags "Status flags".
        unsigned int CmdBufFreeSpace  # This field shows the amount of free cells buffer synchronization chain.

    ctypedef struct move_settings_t:
        unsigned int Speed  # Target speed(for stepper motor: steps / c, for DC: rpm). Range: 0..1000000.
        unsigned int uSpeed  # Target speed in 1/256 microsteps/s. Using with stepper motor only. Range: 0..255.
        unsigned int Accel  # Motor shaft acceleration, steps/s^2(stepper motor) or RPM/s(DC). Range: 0..65535.
        unsigned int Decel  # Motor shaft deceleration, steps/s^2(stepper motor) or RPM/s(DC). Range: 0..65535.
        unsigned int AntiplaySpeed  # Speed in antiplay mode, full steps/s(stepper motor) or RPM(DC). Range: 0..1000000.
        unsigned int uAntiplaySpeed  # Speed in antiplay mode, 1/256 microsteps/s. Used with stepper motor only. Range: 0..255.

    ctypedef struct get_position_t:
        int Position  # The position of the whole steps in the engine
        int uPosition  # Microstep position is only used with stepper motors
        long EncPosition  # Encoder position.

    device_enumeration_t enumerate_devices(int probe_flags)
    result_t free_enumerate_devices(int probe_flags)
    int get_device_count(device_enumeration_t device_enumeration)
    pchar get_device_name(device_enumeration_t device_enumeration, int device_index)

    result_t get_status(device_t id, status_t *status)

    device_t open_device(const char *name)
    result_t close_device(device_t *id)

    result_t command_zero(device_t id)
    result_t command_move(device_t id, int Position, int uPosition)
    result_t command_stop(device_t id)

    result_t get_move_settings(device_t id, move_settings_t *move_settings)
    result_t set_move_settings(device_t id, const move_settings_t *move_settings)

    result_t get_position(device_t id, get_position_t *the_get_position)





