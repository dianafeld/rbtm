from serial import *
import io
from string import *

class DriverSource:
    #functions for users
    #ser = None
    def open_port(self):
        #ser = Serial('/dev/ttyUSB0', timeout=1)
        self.ser = serial_for_url('loop://', timeout=1)    
        #ser.open()

    def close_port(self):
        self.ser.close()

    def on_high_voltage(self):
        self.ser.write("HV:1\n")

    def off_high_voltage(self):
        self.ser.write("HV:0\n")

    def get_id(self):
        self.ser.write("ID\n")
        return self.get_data_string()

    def get_error(self):
        self.ser.write("ER\n")
        return self.get_data_string()

    def start_warming_up(self, interval, test_voltage):
        if len(str(interval)) != 1:
            raise Exception("Incorrect unwork interval")
        if len(str(test_voltage)) > 3:
            raise Exception("Imcorrect test voltage")
        data = "WU:" + str(interval) + str(test_voltage).zfill(3)
        self.ser.write(data)

    def get_real_voltage(self):
        self.ser.write("VA\n")
        line = self.get_data_string()
        return self.get_number(line)/1000

    def get_voltage(self):
        self.ser.write("VN\n")
        line = self.get_data_string()
        return self.get_number(line)/1000

    def get_current(self):
        self.ser.write("CN\n")
        line = self.get_data_string()
        return self.get_number(line)/1000

    def set_voltage(self, voltage):
        data = "SV:" + str(voltage*1000).zfill(6)
        self.ser.write(data)

    def set_current(self, current):
        data = "SC:" + str(current*1000).zfill(6)
        self.ser.write(data)

    #auxiliary functions
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
