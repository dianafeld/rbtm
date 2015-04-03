#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        XRaySource.py
## 
## Project :     XRaySource
##
## This file is part of Tango device class.
## 
## Tango is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Tango is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with Tango.  If not, see <http://www.gnu.org/licenses/>.
## 
##
## $Author :      mariya.ryabova$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##            This file is generated by POGO
##    (Program Obviously used to Generate tango Object)
##
##        (c) - Software Engineering Group - ESRF
##############################################################################

"""It is a class for XRay sourse, which is used for setting operating mode (voltage)"""

__all__ = ["XRaySource", "XRaySourceClass", "main"]

__docformat__ = 'restructuredtext'

import PyTango
import sys
# Add additional import
#----- PROTECTED REGION ID(XRaySource.additionnal_import) ENABLED START -----#

#----- PROTECTED REGION END -----#	//	XRaySource.additionnal_import

## Device States Description
## ON : The state in which the source is active
## OFF : The state in which the source is not active
## FAULT : The state in which the source is fault
## STANDBY : 

class XRaySource (PyTango.Device_4Impl):

    #--------- Add you global variables here --------------------------
    #----- PROTECTED REGION ID(XRaySource.global_variables) ENABLED START -----#
    
    #----- PROTECTED REGION END -----#	//	XRaySource.global_variables

    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.debug_stream("In __init__()")
        XRaySource.init_device(self)
        #----- PROTECTED REGION ID(XRaySource.__init__) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.__init__
        
    def delete_device(self):
        self.debug_stream("In delete_device()")
        #----- PROTECTED REGION ID(XRaySource.delete_device) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.delete_device

    def init_device(self):
        self.debug_stream("In init_device()")
        self.get_device_properties(self.get_device_class())
        self.attr_voltage_read = 0
        self.attr_current_read = 0
        #----- PROTECTED REGION ID(XRaySource.init_device) ENABLED START -----#

        self.set_state(PyTango.DevState.OFF)

        # read actual values from source

        #----- PROTECTED REGION END -----#	//	XRaySource.init_device

    def always_executed_hook(self):
        self.debug_stream("In always_excuted_hook()")
        #----- PROTECTED REGION ID(XRaySource.always_executed_hook) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.always_executed_hook

    #-----------------------------------------------------------------------------
    #    XRaySource read/write attribute methods
    #-----------------------------------------------------------------------------
    
    def read_voltage(self, attr):
        self.debug_stream("In read_voltage()")
        #----- PROTECTED REGION ID(XRaySource.voltage_read) ENABLED START -----#

        attr.set_value(self.attr_voltage_read)

        #----- PROTECTED REGION END -----#	//	XRaySource.voltage_read
        
    def write_voltage(self, attr):
        self.debug_stream("In write_voltage()")
        data=attr.get_write_value()
        # ----- PROTECTED REGION ID(XRaySource.voltage_write) ENABLED START -----#

        self.attr_voltage_read = data

        #----- PROTECTED REGION END -----#	//	XRaySource.voltage_write
        
    def read_current(self, attr):
        self.debug_stream("In read_current()")
        # ----- PROTECTED REGION ID(XRaySource.current_read) ENABLED START -----#

        attr.set_value(self.attr_current_read)

        # ----- PROTECTED REGION END -----#	//	XRaySource.current_read
        
    def write_current(self, attr):
        self.debug_stream("In write_current()")
        data=attr.get_write_value()
        # ----- PROTECTED REGION ID(XRaySource.current_write) ENABLED START -----#

        # ----- PROTECTED REGION END -----#	//	XRaySource.current_write
        
    
    
        #----- PROTECTED REGION ID(XRaySource.initialize_dynamic_attributes) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.initialize_dynamic_attributes
            
    def read_attr_hardware(self, data):
        self.debug_stream("In read_attr_hardware()")
        #----- PROTECTED REGION ID(XRaySource.read_attr_hardware) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.read_attr_hardware


    #-----------------------------------------------------------------------------
    #    XRaySource command methods
    #-----------------------------------------------------------------------------
    
    def Off(self):
        """ Turns off the X-Ray source
        
        :param : 
        :type: PyTango.DevVoid
        :return: 
        :rtype: PyTango.DevVoid """
        self.debug_stream("In Off()")
        #----- PROTECTED REGION ID(XRaySource.Off) ENABLED START -----#

        self.set_state(PyTango.DevState.OFF)

        #----- PROTECTED REGION END -----#	//	XRaySource.Off
        
    def On(self):
        """ Turns on the X-Ray source
        
        :param : 
        :type: PyTango.DevVoid
        :return: 
        :rtype: PyTango.DevVoid """
        self.debug_stream("In On()")
        #----- PROTECTED REGION ID(XRaySource.On) ENABLED START -----#

        self.set_state(PyTango.DevState.ON)

        #----- PROTECTED REGION END -----#	//	XRaySource.On
        
    def is_On_allowed(self):
        self.debug_stream("In is_On_allowed()")
        state_ok = not(self.get_state() in [PyTango.DevState.FAULT])
        # ----- PROTECTED REGION ID(XRaySource.is_On_allowed) ENABLED START -----#

        #----- PROTECTED REGION END -----#	//	XRaySource.is_On_allowed
        return state_ok
        
    def SetOperatingMode(self, argin):
        """ Sets new voltage and current
        
        :param argin: voltage, current
        :type: PyTango.DevVarShortArray
        :return: 
        :rtype: PyTango.DevVoid """
        self.debug_stream("In SetOperatingMode()")
        #----- PROTECTED REGION ID(XRaySource.SetOperatingMode) ENABLED START -----#

        if len(argin) != 2:
            PyTango.Except.throw_exception(
                "TOMOGRAPH_invalid_arguments",
                "Invalid number of arguments: {} provided, 2 needed (voltage, current)".format(len(argin)),
                "XRaySource::SetOperatingMode")

        new_voltage = argin[0]
        new_current = argin[1]

        voltage = self.get_device_attr().get_attr_by_name("voltage")
        min_voltage_value = voltage.get_min_value()
        max_voltage_value = voltage.get_max_value()
        if min_voltage_value <= new_voltage <= max_voltage_value:
            self.attr_voltage_read = new_voltage
        else:
            PyTango.Except.throw_exception(
                "TOMOGRAPH_invalid_arguments",
                "Invalid voltage value",
                "XRaySource::SetOperatingMode")

        current = self.get_device_attr().get_attr_by_name("current")
        min_current_value = current.get_min_value()
        max_current_value = current.get_max_value()
        if min_current_value <= new_current <= max_current_value:
            self.attr_current_read = new_current
        else:
            PyTango.Except.throw_exception(
                "TOMOGRAPH_invalid_arguments",
                "Invalid current value",
                "XRaySource::SetOperatingMode")

        #----- PROTECTED REGION END -----#	//	XRaySource.SetOperatingMode
        
    def is_SetOperatingMode_allowed(self):
        self.debug_stream("In is_SetOperatingMode_allowed()")
        state_ok = not (self.get_state() in [PyTango.DevState.FAULT])
        # ----- PROTECTED REGION ID(XRaySource.is_SetOperatingMode_allowed) ENABLED START -----#

        #----- PROTECTED REGION END -----#	//	XRaySource.is_SetOperatingMode_allowed
        return state_ok
        

class XRaySourceClass(PyTango.DeviceClass):
    #--------- Add you global class variables here --------------------------
    #----- PROTECTED REGION ID(XRaySource.global_class_variables) ENABLED START -----#
    
    #----- PROTECTED REGION END -----#	//	XRaySource.global_class_variables

    def dyn_attr(self, dev_list):
        """Invoked to create dynamic attributes for the given devices.
        Default implementation calls
        :meth:`XRaySource.initialize_dynamic_attributes` for each device
    
        :param dev_list: list of devices
        :type dev_list: :class:`PyTango.DeviceImpl`"""
    
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                import traceback
                dev.warn_stream("Failed to initialize dynamic attributes")
                dev.debug_stream("Details: " + traceback.format_exc())
        #----- PROTECTED REGION ID(XRaySource.dyn_attr) ENABLED START -----#
        
        #----- PROTECTED REGION END -----#	//	XRaySource.dyn_attr

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        }


    #    Command definitions
    cmd_list = {
        'Off':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'On':
            [[PyTango.DevVoid, "none"],
            [PyTango.DevVoid, "none"]],
        'SetOperatingMode':
            [[PyTango.DevVarShortArray, "voltage, current"],
            [PyTango.DevVoid, "none"]],
        }


    #    Attribute definitions
    attr_list = {
        'voltage':
            [[PyTango.DevShort,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label': "Input Voltage",
                'unit': "0.1 kV",
                'standard unit': "10E+2",
                'max value': "600",
                'min value': "20",
                'description': "voltage of the X-Ray source",
            } ],
        'current':
            [[PyTango.DevShort,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label': "current",
                'unit': "0.1 mA",
                'standard unit': "10E-4",
                'max value': "800",
                'min value': "20",
                'description': "current of the X-Ray source",
            } ],
        }


def main():
    try:
        py = PyTango.Util(sys.argv)
        py.add_class(XRaySourceClass,XRaySource,'XRaySource')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e

if __name__ == '__main__':
    main()
