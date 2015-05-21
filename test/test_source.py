import pytest
import PyTango
import subprocess
import time

MAX_VOLTAGE = 60
MIN_VOLTAGE = 2
MAX_CURRENT = 80
MIN_CURRENT = 2
CORRECT_VOLTAGE = (MIN_VOLTAGE + MAX_VOLTAGE)/2
CORRECT_CURRENT = (MIN_CURRENT + MAX_CURRENT)/2
SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

@pytest.yield_fixture
def source():
    process = subprocess.Popen(['python', '../tango_ds/XRaySource/XRaySource.py', 'source'], shell=False)
    step = 0
    while step < STEP_NUMBER:
        source = PyTango.DeviceProxy('tomo/source/1')
        try:
            source.ping()
        except:
            step += 1
            time.sleep(SERVER_STARTING_TIME)
        else:
            break
    try:
        source.ping()
    except:
        process.kill()
        raise Exception('Connection with source fault')

    yield source
    process.kill()


# States testing
def test_source_init_state(source):
    assert source.State() == PyTango._PyTango.DevState.OFF


def test_source_on(source):
    source.On()
    assert source.State() == PyTango._PyTango.DevState.ON


def test_source_off(source):
    source.On()
    source.Off()
    assert source.State() == PyTango._PyTango.DevState.OFF


# Voltage and current testing
def test_source_set_correct_args(source):
    source.On()
    source.voltage = CORRECT_VOLTAGE
    source.current = CORRECT_CURRENT
    time.sleep(2)
    assert source.voltage == CORRECT_VOLTAGE and source.current == CORRECT_CURRENT


def test_source_set_min_args(source):
    source.On()
    source.voltage = MIN_VOLTAGE
    source.current = MIN_CURRENT
    time.sleep(2)
    assert source.voltage == MIN_VOLTAGE and source.current == MIN_CURRENT


def test_source_set_less_than_min_args(source):
    source.On()
    with pytest.raises(Exception):
        source.voltage = MIN_VOLTAGE - 1
    with pytest.raises(Exception):    
        source.current = MIN_CURRENT - 1
    


def test_source_set_max_args(source):
    source.On()
    source.voltage = MAX_VOLTAGE
    source.current = MAX_CURRENT
    time.sleep(2)
    assert source.voltage == MAX_VOLTAGE and source.current == MAX_CURRENT


def test_source_set_more_than_max_args(source):
    source.On()
    with pytest.raises(Exception):
        source.voltage = MAX_VOLTAGE + 1
    with pytest.raises(Exception):
        source.current = MAX_CURRENT + 1


# # Testing voltage and current change in OFF or FAULT state
# def test_source_set_args_if_off(source):
#     arg = (CORRECT_VOLTAGE, CORRECT_CURRENT)
#     with pytest.raises(Exception) as excinfo:
#         source.SetOperatingMode(arg)
#     assert excinfo

# def test_source_set_args_if_fault(source):
#     arg = (CORRECT_VOLTAGE, CORRECT_CURRENT)
#     with pytest.raises(Exception) as excinfo:
#         source.SetOperatingMode(arg)
#     assert excinfo
