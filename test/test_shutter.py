import pytest
import os, sys
import PyTango
import subprocess
import time

SERVER_STARTING_TIME = 1

@pytest.yield_fixture
def shutter():
    process = subprocess.Popen(['python', '../tango-ds/XRayShutter/XRayShutter.py', 'shutter'], shell = False)
    time.sleep(SERVER_STARTING_TIME)
    yield PyTango.DeviceProxy('tomo/shutter/1')
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
