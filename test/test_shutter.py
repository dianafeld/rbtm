import pytest
import os, sys
import PyTango
import subprocess

@pytest.yield_fixture
def shutter(request):
    #cmdRunServer = 'python ../tango-ds/XRayShutter/XRayShutter.py shutter &'
    #cmdStopServer = '''ps axf | grep shutter | grep -v grep | awk '{print "kill -9 " $1}' | sh'''
    #os.system(cmdRunServer)
    process = subprocess.Popen(['python', './tango-ds/XRayShutter/XRayShutter.py', 'shutter'])
    yield PyTango.DeviceProxy('tomo/shutter/1')
    request.addfinalizer(process.kill) 
    #os.system(cmdStopServer)

def test_shutter_init_state(shutter):
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE

def test_shutter_open(shutter):
    shutter.Open()
    assert shutter.State() == PyTango._PyTango.DevState.OPEN

def test_shutter_close(shutter):
    shutter.Open()
    shutter.Close()
    assert shutter.State() == PyTango._PyTango.DevState.CLOSE
