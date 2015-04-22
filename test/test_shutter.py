import pytest
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

TIME = 10

@pytest.yield_fixture
def shutter():
    process = subprocess.Popen(['python', '../tango_ds/XRayShutter/XRayShutter.py', 'shutter'], shell=False)

    step = 0
    while step < STEP_NUMBER:
        shutter = PyTango.DeviceProxy('tomo/shutter/1')
        try:
            shutter.ping()
        except:
            step += 1
            time.sleep(SERVER_STARTING_TIME)
        else:
            break

    try:
        shutter.ping()
    except:
        process.kill()
        raise Exception('Connection with shutter fault')

    yield shutter
    process.kill()

# States testing
def test_shutter_init_state(shutter):
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE


def test_shutter_open(shutter):
    shutter.Open(0)
    assert shutter.State() == PyTango._PyTango.DevState.OPEN


def test_shutter_close(shutter):
    shutter.Open(0)
    shutter.Close(0)
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE

#Time testing
def test_shutter_open_time(shutter):
    shutter.Open(TIME)
    time.sleep(TIME)
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE

def test_shutter_close_time(shutter):
    shutter.Open(0)
    shutter.Close(TIME)
    time.sleep(TIME)
    assert shutter.State() == PyTango._PyTango.DevState.OPEN
