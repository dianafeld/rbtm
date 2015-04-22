import pytest
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

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


def test_shutter_init_state(shutter):
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE


def test_shutter_open(shutter):
    shutter.Open()
    assert shutter.State() == PyTango._PyTango.DevState.OPEN


def test_shutter_close(shutter):
    shutter.Open()
    shutter.Close()
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE
