import serial

def read_com_string():
	# read symbols until \r in stream

	a = ser.read()
	msg= []
	while not a =='\r':
		msg.append(a)
		a = ser.read()
	msg.append(a)
	return ''.join(msg)

def read_error():
	ser.write('ER\n')
	print 'ERROR:', read_com_string()

ser = serial.Serial('/dev/ttyUSB0')

ser.open()

# get id
ser.write('ID\n')

print 'ID:', read_com_string()

ser.write("XT\n")
print 'Tube:', read_com_string()

read_error()
# # testing warming
# ser.write("WU:4,030\n")
# # we should wait some minutes (how to chek is process finished?)

# hight votage ON
ser.write("HV:1\n")

# get current state
ser.write("SV:020000\n") # 20 keV

ser.write("VA\n")
print "VA = ", read_com_string()

ser.write("SC:010000\n") # 10 mA

ser.write("CA\n")
print "CA = ", read_com_string()


read_error()

# hight votage OFF
ser.write("HV:0\n")

ser.close()