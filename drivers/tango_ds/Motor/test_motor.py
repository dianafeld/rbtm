from ximc import Motor
from pprint import pprint

motor = Motor("COM5")
motor.open()
motor.set_zero()
status = motor.get_status()
pprint(status)
position = motor.get_position()
pprint(position)
move_settings = motor.get_move_settings()
pprint(move_settings)
motor.move_to_position(1000, 0)
motor.set_move_settings(1000, 1000)
move_settings = motor.get_move_settings()
pprint(move_settings)

motor.close()
