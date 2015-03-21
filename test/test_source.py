import pytest
import os, sys
import PyTango
import subprocess

MAX_VOLTAGE = 100.0
MIN_VOLTAGE = 10.0
CORRECT_VOLTAGE = (MIN_VOLTAGE + MAX_VOLTAGE)/2

@pytest.yield_fixture
def source(request):
    #cmdRunServer = 'python ../tango-ds/XRaySource/XRaySource.py source &'
    #cmdStopServer = '''ps axf | grep source | grep -v grep | awk '{print "kill -9 " $1}' | sh'''
    #os.system(cmdRunServer)
    process = subprocess.Popen(['python', '../tango-ds/XRaySource/XRaySource.py', 'source'])
    yield PyTango.DeviceProxy('tomo/source/1')
    request.addfinalizer(process.kill)    
    #os.system(cmdStopServer)

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
"""
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
    prevVoltage = source.voltage
    source.SetOperatingMode(MIN_VOLTAGE - 0.1)
    assert source.voltage == prevVoltage

def test_source_set_max_voltage(source):
    source.On()
    source.SetOperatingMode(MAX_VOLTAGE)
    assert source.voltage == MAX_VOLTAGE

def test_source_set_more_than_max_voltage(source):
    source.On()
    prevVoltage = source.voltage
    source.SetOperatingMode(MAX_VOLTAGE + 0.1)
    assert source.voltage == prevVoltage

#Testing voltage change in OFF state
def test_source_set_voltage_if_off(source):
    source.SetOperatingMode(CORRECT_VOLTAGE)
"""
    
