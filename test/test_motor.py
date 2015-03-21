import pytest
import os, sys
import PyTango

@pytest.yield_fixture
def motor():
    cmdRunServer = 'python ../tango_ds/Motor/Motor.py motor &'
    cmdStopServer = 'killall motor'
    os.system(cmdRunServer)
    yield PyTango.DeviceProxy('tomo/motor/1')
    os.system(cmdStopServer)

def test_shutter_init_state(motor):
    assert motor.State() == PyTango._PyTango.DevState.CLOSE
