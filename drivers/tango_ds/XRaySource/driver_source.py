import serial
import PyTango


def make_exception(reason, desc, origin):
    PyTango.Except.throw_exception(reason, desc, origin)


def handle_error(error, func_name):
    if error is not None:
        error_code, error_desc = error
        make_exception("XRaySource_UnexpectedValue", error_desc, func_name)

TIMEOUT = 10
class Source(object):

    def __init__(self, tty_name):
        self.tty_name = tty_name

    def on_high_voltage(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("HV:1\n")
            error = self._get_error(serial_port)  
        handle_error(error, "Source.on_high_voltage()")
        
    def off_high_voltage(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("HV:0\n")
            error = self._get_error(serial_port)
        handle_error(error, "Source.off_high_voltage()")

    def is_on_high_volatge(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("SR:01\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.is_on_high_voltage()")
        return self.get_number(answer) & 64 != 0

    def get_nominal_voltage(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("VN\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_nominal_voltage()")
        return self.get_number(answer) / 100

    def get_actual_voltage(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("VA\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_actual_voltage()")
        return self.get_number(answer) / 100

    def get_nominal_current(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("CN\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_nominal_current()")
        return self.get_number(answer) / 100

    def get_actual_current(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("CA\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_actual_current()")
        return self.get_number(answer) / 100

    def set_voltage(self, voltage):
        command = "SV:" + str(voltage*100).zfill(6) + "\n"
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write(command)
            error = self._get_error(serial_port)
        handle_error(error, "Source.set_voltage()")

    def set_current(self, current):
        command = "SC:" + str(current*100).zfill(6) + "\n"
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write(command)
            error = self._get_error(serial_port)
        handle_error(error, "Source.set_current()")

    def get_id(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("ID\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_id()")
        return answer 

    def get_tube_name(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            serial_port.write("XT\n")
            answer = self.get_data_string(serial_port)
            error = self._get_error(serial_port)
        handle_error(error, "Source.get_tube_name()")
        return answer

    def get_error(self):
        with serial.Serial(self.tty_name, timeout=TIMEOUT) as serial_port:
            return self._get_error(serial_port)

    def _get_error(self, serial_port):
        serial_port.write("SR:12\n")
        answer = self.get_data_string(serial_port)
        error_code = int(answer[1:-1])

        if error_code != 0:
            serial_port.write("ER\n")
            error_line = self.get_data_string(serial_port)
            print(error_line)
            return (ord(error_line[0]), error_line[2:])
        else:
            return None


    # def start_warming_up(self, interval, test_voltage):
    #     if len(str(interval)) != 1:
    #         PyTango.Except.throw_exception("XRaySource_IllegalArgument",
    #                                        "Incorrect unwork interval",
    #                                        "Source.start_warming_up()")
    #     if len(str(test_voltage)) > 3:
    #         PyTango.Except.throw_exception("XRaySource_IllegalArgument",
    #                                        "Incorrect test voltage",
    #                                        "Source.start_warming_up()")
    #     data = "WU:" + str(interval) + str(test_voltage).zfill(3)
    #     self.ser.write(data)
    #     error_line = self.get_error()
    #     if error_line != "":
    #         PyTango.Except.throw_exception("XRaySource_UnexpectedValue",
    #                                        error_line,
    #                                        "Source.start_warming_up()")

    # auxiliary functions

    def get_data_string(self, serial_port):
        cur_byte = serial_port.read()
        line = cur_byte
        while cur_byte != '\r':
            cur_byte = serial_port.read()     
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
