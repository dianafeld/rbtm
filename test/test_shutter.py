import pytest
import os, sys
import PyTango

@pytest.yield_fixture
def shutter():
    cmdRunServer = 'python ../tango_ds/XRayShutter/XRayShutter.py shutter &'
    cmdStopServer = 'killall shutter'
    os.system(cmdRunServer)
    yield PyTango.DeviceProxy('tomo/shutter/1')
    os.system(cmdStopServer)

def test_shutter_init_state(shutter):
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE

def test_shutter_status(shutter):
    assert shutter.Status() == 'The device is in CLOSE state.'

def test_shutter_open(shutter):
    shutter.Open()
    assert shutter.Status() == 'The device is in OPEN state.'

def test_shutter_close(shutter):
    shutter.Open()
    shutter.Close()
    assert shutter.Status() == 'The device is in CLOSE state.'
