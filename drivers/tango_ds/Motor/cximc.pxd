from libc.stdint cimport uint32_t

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

    cdef int BORDER_IS_ENCODER = 0x01    # Borders are fixed by predetermined encoder values, if set; borders position on limit switches, if not set. \endenglish \russian Если флаг установлен, границы определяются предустановленными точками на шкале позиции. Если флаг сброшен, границы определяются концевыми выключателями. \endrussian */
    cdef int BORDER_STOP_LEFT = 0x02    # Motor should stop on left border. \endenglish \russian Если флаг установлен, мотор останавливается при достижении левой границы. \endrussian */
    cdef int BORDER_STOP_RIGHT = 0x04   # Motor should stop on right border. \endenglish \russian Если флаг установлен, мотор останавливается при достижении правой границы. \endrussian */
    cdef int BORDERS_SWAP_MISSET_DETECTION = 0x08

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

    ctypedef struct edges_settings_t:
        unsigned int BorderFlags # flagset_borderflags "Border flags". \endenglish \russian \ref flagset_borderflags "Флаги границ". \endrussian */
        unsigned int EnderFlags  # flagset_enderflags "Limit switches flags". \endenglish \russian \ref flagset_enderflags "Флаги концевых выключателей". \endrussian */
        int LeftBorder   # Left border position, used if BORDER_IS_ENCODER flag is set. Range: -2147483647..2147483647. \endenglish \russian Позиция левой границы, используется если установлен флаг BORDER_IS_ENCODER. Диапазон: -2147483647..2147483647. \endrussian */
        int uLeftBorder # Left border position in 1/256 microsteps(used with stepper motor only). Range: -255..255. \endenglish \russian Позиция левой границы в 1/256 микрошагах( используется только с шаговым двигателем). Диапазон: -255..255. \endrussian */
        int RightBorder  # Right border position, used if BORDER_IS_ENCODER flag is set. Range: -2147483647..2147483647. \endenglish \russian Позиция правой границы, используется если установлен флаг BORDER_IS_ENCODER. Диапазон: -2147483647..2147483647. \endrussian */
        int uRightBorder # Right border position in 1/256 microsteps. Range: -255..255(used with stepper motor only). \endenglish \russian Позиция правой границы в 1/256 микрошагах( используется только с шаговым двигателем). Диапазон: -255..255. \endrussian */

    device_enumeration_t enumerate_devices(int probe_flags, const char *hints)
    result_t free_enumerate_devices(int probe_flags)
    int get_device_count(device_enumeration_t device_enumeration)
    pchar get_device_name(device_enumeration_t device_enumeration, int device_index)

    result_t get_status(device_t id, status_t *status)

    device_t open_device(const char *name)
    result_t close_device(device_t *id)

    result_t command_zero(device_t id)
    result_t command_move(device_t id, int Position, int uPosition)
    result_t command_movr(device_t id, int DeltaPosition, int uDeltaPosition)
    result_t command_stop(device_t id)

    result_t get_move_settings(device_t id, move_settings_t *move_settings)
    result_t set_move_settings(device_t id, const move_settings_t *move_settings)

    result_t get_edges_settings(device_t id, edges_settings_t* edges_settings)
    result_t set_edges_settings(device_t id, const edges_settings_t* edges_settings)

    result_t get_position(device_t id, get_position_t *the_get_position)

    result_t command_wait_for_stop(device_t id, uint32_t refresh_interval_ms)
