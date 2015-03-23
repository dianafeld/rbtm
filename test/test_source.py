import pytest
import os, sys
import PyTango
import subprocess
import time

MAX_VOLTAGE = 100.0
MIN_VOLTAGE = 10.0
CORRECT_VOLTAGE = (MIN_VOLTAGE + MAX_VOLTAGE)/2
SERVER_STARTING_TIME = 0.5
STEP_NUMBER = 7

@pytest.yield_fixture
def source():
    process = subprocess.Popen(['python', '../tango-ds/XRaySource/XRaySource.py', 'source'], shell = False)
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
def test_source_init_voltage(source):
    source.On()
    assert source.voltage == MIN_VOLTAGE

def test_source_set_correct_voltage(source):
    source.On()
    source.SetOperatingMode(CORRECT_VOLTAGE)
    assert source.voltage == CORRECT_VOLTAGE

def test_source_set_min_voltage(source):
    source.On()
    source.SetOperatingMode(MIN_VOLTAGE)
    assert source.voltage == MIN_VOLTAGE

def test_source_set_less_than_min_voltage(source):
    source.On()
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(MIN_VOLTAGE - 0.1)
    assert excinfo

def test_source_set_max_voltage(source):
    source.On()
    source.SetOperatingMode(MAX_VOLTAGE)
    assert source.voltage == MAX_VOLTAGE

def test_source_set_more_than_max_voltage(source):
    source.On()
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(MAX_VOLTAGE + 0.1)
    assert excinfo

#Testing voltage change in OFF state
def test_source_set_voltage_if_off(source):
    with pytest.raises(Exception) as excinfo:
        source.SetOperatingMode(CORRECT_VOLTAGE)
    assert excinfo
