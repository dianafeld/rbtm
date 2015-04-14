from serial import *
import io

#functions for users
def open_port():
    #ser = Serial('/dev/ttyUSB0', timeout=1)
    ser = serial_for_url('loop://', timeout=1)    
    #ser.open()
    return ser

def close_port(ser):
    ser.close()

def on_high_voltage(ser):
    ser.write("HV:1\n")

def off_high_voltage(ser):
    ser.write("HV:0\n")

def get_id(ser):
    ser.write("ID\n")
    return get_data_string(ser)

def get_error(ser):
    ser.write("ER\n")
    return get_data_string(ser)

def start_warming_up(ser, interval, test_voltage):
    if len(str(interval)) != 1:
        raise Exception("Incorrect unwork interval")
    if len(str(test_voltage)) > 3:
        raise Exception("Imcorrect test voltage")
    data = "WU:" + str(interval) + form_number(test_voltage, 3)
    ser.write(data)

def get_real_voltage(ser):
    ser.write("VA\n")
    line = get_data_string(ser)
    return get_number(line)/1000

def get_voltage(ser):
    ser.write("VN\n")
    line = get_data_string(ser)
    return get_number(line)/1000

def get_current(ser):
    ser.write("CN\n")
    line = get_data_string(ser)
    return get_number(line)/1000

def set_voltage(ser, voltage):
    data = "SV:" + form_number(voltage*1000, 6)
    ser.write(data)

def set_current(ser, current):
    data = "SC:" + form_number(current*1000, 6)
    ser.write(data)

#auxiliary functions
def get_data_string(ser):
    cur_byte = ser.read()
    line = cur_byte
    while cur_byte != '\n':
        cur_byte = ser.read()     
        line = line + cur_byte
    return line

def get_number(line):
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

def form_number(arg, length):
    data = ""
    line = str(arg)
    i = 0
    while i < length - len(line):
        data = data + "0"
        i = i + 1

    data = data + line + "\n"
    return data
