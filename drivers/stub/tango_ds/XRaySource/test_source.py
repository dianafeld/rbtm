from driver_source import Source
import time

s = Source("COM8")

s.on_high_voltage()
time.sleep(2)
print(s.is_on_high_volatge())

av = s.get_actual_voltage()
print(av)
nv = s.get_nominal_voltage()
print(nv)
ac = s.get_actual_current()
print(ac)
nc = s.get_nominal_current()
print(nc)

time.sleep(2)
s.set_voltage(40)
av = s.get_actual_voltage()
print(av)
nv = s.get_nominal_voltage()
print(nv)

time.sleep(2)
s.set_current(20)
ac = s.get_actual_current()
print(ac)
nc = s.get_nominal_current()
print(nc)

time.sleep(2)
s.off_high_voltage()
print(s.is_on_high_volatge())

#print(s.get_error())
#print(s.get_id())