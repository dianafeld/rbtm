import pytest
import os, sys
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

MIN_ANGLE_POSITION = 0
MAX_ANGLE_POSITION = 360
CORRECT_ANGLE_POSITION = (MIN_ANGLE_POSITION + MAX_ANGLE_POSITION)/2

MIN_VERTICAL_POSITION = 0
MAX_VERTICAL_POSITION = 500
CORRECT_VERTICAL_POSITION = (MIN_VERTICAL_POSITION + MAX_VERTICAL_POSITION)/2

MIN_HORIZONTAL_POSITION = 0
MAX_HORIZONTAL_POSITION = 500
CORRECT_HORIZONTAL_POSITION = (MIN_HORIZONTAL_POSITION + MAX_HORIZONTAL_POSITION)/2

@pytest.yield_fixture
def motor():
    process = subprocess.Popen(['python', '../tango-ds/Motor/Motor.py', 'motor'], shell = False)
    step = 0    
    while (step < STEP_NUMBER):         
        motor = PyTango.DeviceProxy('tomo/motor/1')
        try:
            motor.ping()
        except:
            step = step + 1
            time.sleep(SERVER_STARTING_TIME)
        else:
            break
    
    try:
        motor.ping()
    except:
        process.kill()
        raise Exception('Connection with motor fault')

    yield motor
    process.kill()

#States testing
def test_motor_init_state(motor):
    assert motor.State() == PyTango._PyTango.DevState.ON

def test_motor_off(motor):
    motor.Off()
    assert motor.State() == PyTango._PyTango.DevState.OFF

def test_motor_on(motor):
    motor.Off()
    motor.On()
    assert motor.State() == PyTango._PyTango.DevState.ON

#Testing position changes ib OFF state
def test_motor_set_angle_position_if_off(motor):
    with pytest.raises(Exception) as excinfo:
        motor.angle_position = CORRECT_ANGLE_POSITION
    assert excinfo

def test_motor_set_vertical_position_if_off(motor):
    with pytest.raises(Exception) as excinfo:
        motor.vertical_position = CORRECT_VERTICAL_POSITION
    assert excinfo

def test_motor_set_horizontal_position_if_off(motor):
    with pytest.raises(Exception) as excinfo:
        motor.horizontal_position = CORRECT_HORIZONTAL_POSITION
    assert excinfo
