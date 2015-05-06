import serial
import sys
import PyTango


class Source:

    def __init__(self, tty_name):
        self.tty_name = tty_name

    # functions for users
    # ser = None
    def open_port(self):
        try:
            # ser = Serial('/dev/ttyUSB0', timeout=1)
            self.ser = serial.serial_for_url('loop://', timeout=1)
        except serial.SerialException:
            python_exception = PyTango.Except.to_dev_failed(*sys.exc_info())
            PyTango.Except.re_throw_exception(python_exception,
                                              "XRaySource_ConnectionFailed",
                                              "Can't open a port",
                                              "Source.open_port()")

    def close_port(self):
        self.ser.close()

    def on_high_voltage(self):
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("HV:1\n")

        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.on_high_voltage()")

    def off_high_voltage(self):
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("HV:0\n")

        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.off_high_voltage()")

    def get_id(self):
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("ID\n")

        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.get_id()")
        return self.get_data_string()

    def get_error(self):
        self.ser.write("SR\n")
        line = self.get_data_string()
        if self.get_number(line) != 0:
            self.ser.write("ER\n")
            error_line = self.get_data_string()
            length = len(error_line)
            return error_line[2:length-2]
        else:
            return ""

    def start_warming_up(self, interval, test_voltage):
        if len(str(interval)) != 1:
            PyTango.Except.throw_exception("XRaySource_IllegalArgument",
                                           "Incorrect unwork interval",
                                           "Source.start_warming_up()")
        if len(str(test_voltage)) > 3:
            PyTango.Except.throw_exception("XRaySource_IllegalArgument",
                                           "Incorrect test voltage",
                                           "Source.start_warming_up()")
        data = "WU:" + str(interval) + str(test_voltage).zfill(3)
        self.ser.write(data)
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.start_warming_up()")

    def get_real_voltage(self):
        self.ser.write("VA\n")
        line = self.get_data_string()
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.get_real_voltage()")
        return self.get_number(line)/1000

    def get_voltage(self):
        self.ser.write("VN\n")
        line = self.get_data_string()
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.get_voltage()")
        return self.get_number(line)/1000

    def get_current(self):
        self.ser.write("CN\n")
        line = self.get_data_string()
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.get_current()")
        return self.get_number(line)/1000

    def set_voltage(self, voltage):
        data = "SV:" + str(voltage*1000).zfill(6)
        self.ser.write(data)
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.set_voltage()")

    def set_current(self, current):
        data = "SC:" + str(current*1000).zfill(6)
        self.ser.write(data)
        error_line = self.get_error()
        if error_line != "":
            PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
                                           error_line,
                                           "Source.set_current()")

    # auxiliary functions

    def get_data_string(self):
        cur_byte = self.ser.read()
        line = cur_byte
        while cur_byte != '\n':
            cur_byte = self.ser.read()     
            line = line + cur_byte
        return line

    def get_number(self, line):
        number_line = ""
        i = 0
        while i < len(line):
            if line[i].isdigit():
                number_line = number_line + line[i]
            i = i + 1
        if len(number_line) == 0:
            return 0
        else:
            return int(number_line)
