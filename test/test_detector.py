import pytest
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

@pytest.yield_fixture
def detector():
    process = subprocess.Popen(['python', '../tango_ds/Detector/Detector.py', 'detector'], shell=False)
    step = 0
    while step < STEP_NUMBER:
        detector = PyTango.DeviceProxy('tomo/detector/1')
        try:
            detector.ping()
        except:
            step += 1
            time.sleep(SERVER_STARTING_TIME)
        else:
            break
    
    try:
        detector.ping()
    except:
        process.kill()
        raise Exception('Connection with detector fault')

    yield detector
    process.kill()


# States testing
def test_detector_init_state(detector):
    assert detector.State() == PyTango._PyTango.DevState.OFF


def test_detector_off(detector):
    detector.On()
    detector.Off()
    assert detector.State() == PyTango._PyTango.DevState.OFF


def test_detector_on(detector):
    detector.On()
    assert detector.State() == PyTango._PyTango.DevState.ON
