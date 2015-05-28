import pytest
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

MIN_EXPOSURE = 1
MAX_EXPOSURE = 160000
CORRECT_EXPOSURE = (MIN_EXPOSURE + MAX_EXPOSURE) // 2
# EXPOSURE_PRECISION = 2  # allowed discrepancy 0.2 ms

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


def test_detector_min_exposure(detector):
    detector.exposure = MIN_EXPOSURE
    assert detector.exposure == MIN_EXPOSURE


def test_detector_max_exposure(detector):
    detector.exposure = MAX_EXPOSURE
    assert detector.exposure == MAX_EXPOSURE


def test_detector_correct_exposure(detector):
    detector.exposure = CORRECT_EXPOSURE
    assert detector.exposure == CORRECT_EXPOSURE


def test_detector_set_lesser_than_min_exposure(detector):
    with pytest.raises(PyTango.DevFailed):
        detector.exposure = MIN_EXPOSURE - 1


def test_detector_set_greater_than_max_exposure(detector):
    with pytest.raises(PyTango.DevFailed):
        detector.exposure = MAX_EXPOSURE + 1
