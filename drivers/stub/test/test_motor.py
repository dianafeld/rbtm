import pytest
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

MIN_ANGLE_POSITION = 0
MAX_ANGLE_POSITION = 3600
CORRECT_ANGLE_POSITION = (MIN_ANGLE_POSITION + MAX_ANGLE_POSITION) // 2
ANGLE_PRECISION = 2  # allowed discrepancy 0.2 deg

MIN_VERTICAL_POSITION = 0
MAX_VERTICAL_POSITION = 500
CORRECT_VERTICAL_POSITION = (MIN_VERTICAL_POSITION + MAX_VERTICAL_POSITION) // 2

MIN_HORIZONTAL_POSITION = 0
MAX_HORIZONTAL_POSITION = 500
CORRECT_HORIZONTAL_POSITION = (MIN_HORIZONTAL_POSITION + MAX_HORIZONTAL_POSITION) // 2

@pytest.yield_fixture
def motor():
    process = subprocess.Popen(['python', '../tango_ds/Motor/Motor.py', 'motor'], shell=False)
    step = 0
    while step < STEP_NUMBER:
        motor = PyTango.DeviceProxy('tomo/motor/1')
        try:
            motor.ping()
        except:
            step += 1
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


# States testing
def test_motor_init_state(motor):
    assert motor.State() == PyTango._PyTango.DevState.ON


def test_motor_off(motor):
    motor.Off()
    assert motor.State() == PyTango._PyTango.DevState.OFF


def test_motor_on(motor):
    motor.Off()
    motor.On()
    assert motor.State() == PyTango._PyTango.DevState.ON


# Testing position changes in OFF state
def test_motor_set_angle_position_if_off(motor):
    motor.Off()    
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.angle_position = CORRECT_ANGLE_POSITION


def test_motor_set_vertical_position_if_off(motor):
    motor.Off()
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.vertical_position = CORRECT_VERTICAL_POSITION


def test_motor_set_horizontal_position_if_off(motor):
    motor.Off()
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.horizontal_position = CORRECT_HORIZONTAL_POSITION


# Position testing
def test_set_correct_angle_position(motor):
    motor.angle_position = CORRECT_ANGLE_POSITION
    assert abs(motor.angle_position - CORRECT_ANGLE_POSITION) <= ANGLE_PRECISION


def test_set_correct_vertical_position(motor):
    motor.vertical_position = CORRECT_VERTICAL_POSITION
    assert motor.vertical_position == CORRECT_VERTICAL_POSITION


def test_set_correct_horizontal_position(motor):
    motor.horizontal_position = CORRECT_HORIZONTAL_POSITION
    assert motor.horizontal_position == CORRECT_HORIZONTAL_POSITION


def test_set_min_angle_position(motor):
    motor.angle_position = MIN_ANGLE_POSITION
    assert 0 <= (motor.angle_position - MIN_ANGLE_POSITION) <= ANGLE_PRECISION  # angle_position should always be greater then MIN_ANGLE POSITION ?


def test_set_min_vertical_position(motor):
    motor.vertical_position = MIN_VERTICAL_POSITION
    assert motor.vertical_position == MIN_VERTICAL_POSITION


def test_set_min_horizontal_position(motor):
    motor.horizontal_position = MIN_HORIZONTAL_POSITION
    assert motor.horizontal_position == MIN_HORIZONTAL_POSITION


def test_set_max_angle_position(motor):
    motor.angle_position = MAX_ANGLE_POSITION
    assert 0 <= (MAX_ANGLE_POSITION - motor.angle_position) <= ANGLE_PRECISION  # angle_position should always be lesser then MAX_ANGLE POSITION ?


def test_set_max_vertical_position(motor):
    motor.vertical_position = MAX_VERTICAL_POSITION
    assert motor.vertical_position == MAX_VERTICAL_POSITION


def test_set_max_horizontal_position(motor):
    motor.horizontal_position = MAX_HORIZONTAL_POSITION
    assert motor.horizontal_position == MAX_HORIZONTAL_POSITION


def test_set_less_than_min_angle_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.angle_position = MIN_ANGLE_POSITION - 1


def test_set_less_than_min_vertical_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.vertical_position = MIN_VERTICAL_POSITION - 1


def test_set_less_than_min_horizontal_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.horizontal_position = MIN_HORIZONTAL_POSITION - 1


def test_set_more_than_max_angle_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.angle_position = MAX_ANGLE_POSITION + 1


def test_set_more_than_max_vertical_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.vertical_position = MAX_VERTICAL_POSITION + 1


def test_set_more_than_max_horizontal_position(motor):
    with pytest.raises(PyTango.DevFailed) as excinfo:
        motor.horizontal_position = MAX_HORIZONTAL_POSITION + 1
