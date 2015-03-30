import pytest
import os, sys
import PyTango
import subprocess
import time

MAX_VOLTAGE = 100.0
MIN_VOLTAGE = 10.0
MAX_CURRENT = 100.0
MIN_CURRENT = 0.0
CORRECT_VOLTAGE = (MIN_VOLTAGE + MAX_VOLTAGE)/2
CORRECT_CURRENT = (MIN_CURRENT + MAX_CURRENT)/2
SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

@pytest.yield_fixture
def source():
    process = subprocess.Popen(['python', '../tango_ds/XRaySource/XRaySource.py', 'source'], shell = False)
    step = 0    
    while (step < STEP_NUMBER):         
        source = PyTango.DeviceProxy('tomo/source/1')
        try:
            source.ping()
        except:
            step = step + 1
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

#States testing
def test_source_init_state(source):
    assert source.State() == PyTango._PyTango.DevState.OFF

def test_source_on(source):
    source.On()
    assert source.State() == PyTango._PyTango.DevState.ON

def test_source_off(source):
    source.On()
    source.Off()
    assert source.State() == PyTango._PyTango.DevState.OFF

#Voltage testing
def test_source_set_correct_voltage(source):
    source.On()
    arg = (CORRECT_VOLTAGE, CORRECT_CURRENT)
    source.SetOperatingMode(arg)
    assert source.voltage == CORRECT_VOLTAGE and source.current == CORRECT_CURRENT

def test_source_set_min_voltage(source):
    source.On()
    arg = (MIN_VOLTAGE, MIN_CURRENT)
    source.SetOperatingMode(arg)
    assert source.voltage == MIN_VOLTAGE and source.current == MIN_CURRENT

def test_source_set_less_than_min_voltage(source):
    source.On()
    arg = (MIN_VOLTAGE - 0.1, MIN_CURRENT - 0.1)
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(arg)
    assert excinfo

def test_source_set_max_voltage(source):
    source.On()
    arg = (MAX_VOLTAGE, MAX_CURRENT)
    source.SetOperatingMode(arg)
    assert source.voltage == MAX_VOLTAGE and source.current == MAX_CURRENT

def test_source_set_more_than_max_voltage(source):
    source.On()
    arg = (MAX_VOLTAGE + 0.1, MAX_CURRENT + 0.1)
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(arg)
    assert excinfo

#Testing voltage change in OFF state
def test_source_set_voltage_if_off(source):
    arg = (CORRECT_VOLTAGE, CORRECT_CURRENT)
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(arg)
    assert excinfo
