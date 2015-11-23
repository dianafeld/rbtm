import sys
sys.path.insert(0, 'lib')
from ximc import Motor
from pprint import pprint
import time

motor = Motor("xi-com:///dev/ximc/0000037A")
hor_motor = Motor("xi-com:///dev/ximc/00000271")
hor_motor.open()
motor.open()
motor.set_zero()
status = motor.get_status()
pprint(status)
position = motor.get_position()
pprint(position)
move_settings = motor.get_move_settings()
pprint(move_settings)
motor.move_to_position(1000, 100)
motor.set_move_settings(500, 500)
move_settings = motor.get_move_settings()
pprint(move_settings)

for i in range(1500):
    motor.move_to_position(i * 83)
    motor.wait_for_stop()
    hor_motor.get_position()
    position = motor.get_position()
    pprint(position)


motor.close()
