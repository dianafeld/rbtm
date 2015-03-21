import pytest
import os, sys
import PyTango

@pytest.yield_fixture
def source():
    cmdRunServer = 'python ..tango_ds/XRaySource/XRaySource.py source &'
    cmdStopServer = 'killall source'
    os.system(cmdRunServer)
    yield PyTango.DeviceProxy('tomo/source/1')
    os.system(cmdStopServer)

def test_shutter_init_state(source):
    assert source.State() == PyTango._PyTango.DevState.OFF
