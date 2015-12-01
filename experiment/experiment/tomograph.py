#!/usr/bin/python

""" 
Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph
"""
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# Need to look at checking types of arguments, which go to Tango-tomograph functions

import json
import time

import PyTango
import numpy
from PyTango import ExtractAs
from flask import send_file

from experiment_class import *

from experiment import app
logger = app.logger



def try_thrice_function(func, args=(), error_str=''):
    """ Tries to call some TANGO function three times

    :arg: 'func' - called function
        'args' - function 'func' is being called with arguments 'args'
    :return:
    """
    if type(args) not in (tuple, list):
        args = (args,)
    exception_message = ''
    for i in range(0, 3):
        try:
            answer = func(*args)
        except PyTango.DevFailed as e:

            # (24.11.15) Not very mature place: logging exception description before logging common 
            # error info (error_str), which will be logged after catching ModExpError exception
            for stage in e:
                logger.info(stage.desc)
            exception_message = e[-1].desc
        except Exception as e:
            logger.info(e.message)
            # Can be problems with converting to JSON e.message
            exception_message = e.message
        else:
            return answer
    raise ModExpError(error=error_str, exception_message=exception_message)
    
class Tomograph:
    """ Wrapper of interaction with Tango tomograph server"""
    tomograph_proxy = None
    detector_proxy = None
    current_experiment = None


    def __init__(self, tomograph_proxy_addr, detector_proxy_addr, timeout_millis=TIMEOUT_MILLIS):
        """
        :arg:  'tomograph_proxy_addr' - type is string
               'detector_proxy_addr' - type is string
               'timeout_millis' - time that tomograph waits after command, type is int
        """
        self.tomograph_proxy = PyTango.DeviceProxy(tomograph_proxy_addr)
        self.tomograph_proxy.set_timeout_millis(timeout_millis)

        self.detector_proxy = PyTango.DeviceProxy(detector_proxy_addr)
        self.detector_proxy.set_timeout_millis(timeout_millis)


    def try_thrice_read_attr(self, attr_name, extract_as=ExtractAs.Numpy, error_str=''):
        """ Try to read some attribute of Tango device three times
        :arg: 'attr_name' - type is string
              'extract-as' - method of extraction
        :return:

        """
        exception_message = ''
        for i in range(0, 3):
            try:
                attr = self.tomograph_proxy.read_attribute(attr_name, extract_as)
            except PyTango.DevFailed as e:
                exception_message = e[-1].desc
            else:
                return attr
        raise ModExpError(error=error_str, exception_message=exception_message)

    def try_thrice_change_attr(self, attr_name, new_value, error_str=''):
        """ Try to change some attribute of Tango device three times

        :arg: 'attr_name' - type is string
              'new_value' - type is type of attribute

        :return:
        """
        exception_message = ''
        for i in range(0, 3):
            try:
                self.tomograph_proxy.write_attribute(attr_name, new_value)
                set_value = self.tomograph_proxy[attr_name].value
            except PyTango.DevFailed as e:
                exception_message = e[-1].desc
            else:
                return set_value
        raise ModExpError(error=error_str, exception_message=exception_message)

    def tomo_state(self):
        logger.info('Checking tomograph...')
        try:
            try_thrice_function(func=self.tomograph_proxy.ping, error_str="Tomograph is unavailable")
        except ModExpError as e:
            e.log()
            return 'unavailable', e.exception_message
            #return create_response(success=True, exception_message=exception_message, result=)

        if self.current_experiment != None:
            logger.info("Tomograph is available; experiment IS running")
            return 'experiment', ""
            #return create_response(success=True, result="experiment")
        else:
            logger.info("Tomograph is available; experiment is NOT running")
            return 'ready', ""
            #return create_response(success=True, result="ready")

    def basic_tomo_check(self, from_experiment):
        if not from_experiment:
            if self.current_experiment != None:
                raise ModExpError(error='On this tomograph experiment is running')
        else:
            if self.current_experiment.to_be_stopped == True:
                # someone called experiment_stop() function
                raise ModExpError(error=self.current_experiment.reason_of_stop, stop_msg=SOMEONE_STOP_MSG)



    def open_shutter(self, time=0, from_experiment=False, exp_is_advanced=True):
        """ Tries to open shutter
        :arg: 
        :return: 
        """
        logger.info('Opening shutter...')
        self.basic_tomo_check(from_experiment)

        try_thrice_function(func=self.tomograph_proxy.OpenShutter, args=time, error_str='Could not open shutter')
        logger.info('Shutter has been opened!')

    def close_shutter(self, time=0, from_experiment=False, exp_is_advanced=True):
        """ Tries to close shutter

        :arg: 
        :return: 
        """
        logger.info('Closing shutter...')
        self.basic_tomo_check(from_experiment)

        try_thrice_function(func=self.tomograph_proxy.CloseShutter, args=time, error_str='Could not close shutter')
        logger.info('Shutter has been closed!')

    def shutter_state(self, time=0, from_experiment=False, exp_is_advanced=True):
        #TODO documentation
        """ Tries to get tomo state

        :return: 
        """
        logger.info('Getting shutter state...')
        self.basic_tomo_check(from_experiment)

        status = try_thrice_function(func=self.tomograph_proxy.ShutterStatus, args=time,
        							 error_str='Could not get shutter status')
        logger.info('Shutter return status successfully!')
        return status


	######################################## (14.11.15  10:37)
	########## One needs to look at checking types of arguments, which go to Tango-tomograph functions
	##############################
    
    def source_power_on(self):
        """
        :arg:
        :return:
        """
        logger.info('Powering on source...')
        self.basic_tomo_check(from_experiment=False)

        try_thrice_function(func=self.tomograph_proxy.PowerOn,
        					error_str='Could not power on source')
        logger.info('Source was powered ON!')

    def source_power_off(self):
        """
        :arg:
        :return:
        """
        logger.info('Powering off source...')
        self.basic_tomo_check(from_experiment=False)

        try_thrice_function(func=self.tomograph_proxy.PowerOff,
        					error_str='Could not power off source')
        logger.info('Source was powered OFF!')

    def source_set_voltage(self, new_voltage):
        logger.info('Going to set voltage on source...')
        self.basic_tomo_check(from_experiment=False)

        logger.info('Checking format...')
        if type(new_voltage) is not float: 
            logger.info('Incorrect format! Voltage type must be float, but it is ' + str(type(new_voltage)))  
            raise ModExpError(error='Incorrect format: type must be float')

	    # TO DELETE THIS LATER
        logger.info('Format is correct, new voltage value is %.1f...' % (new_voltage))
        if new_voltage < 2 or 60 < new_voltage:
            raise ModExpError(error='Voltage must have value from 2 to 60!')

        logger.info('Parameters are normal, setting new voltage...')
        set_voltage = self.try_thrice_change_attr("xraysource_voltage", new_voltage,
        										  error_str='Could not set voltage')
        
        logger.info('New value of voltage was set!')

    def source_set_current(self, new_current):
        logger.info('Going to set current on source...')
        self.basic_tomo_check(from_experiment=False)

        logger.info('Checking format...')
        if type(new_current) is not float:
            logger.info('Incorrect format! Current type must be float, but it is ' + str(type(new_current)))
            raise ModExpError(error='Incorrect format: type must be float')

	    # TO DELETE THIS LATER
        logger.info('Format is correct, new current value is %.1f...' % (new_current))
        if new_current < 2 or 80 < new_current:
            raise ModExpError(error='Current must have value from 2 to 80!')

        logger.info('Parameters are normal, setting new current...')
        set_current = self.try_thrice_change_attr("xraysource_current", new_current,
        										  error_str='Could not set current')

        logger.info('New value of current was set!')


    def source_get_voltage(self):
        logger.info('Going to get voltage...')
        self.basic_tomo_check(from_experiment=False)

        voltage_attr = self.try_thrice_read_attr("xraysource_voltage",
										   		 error_str='Could not get voltage')

        voltage = voltage_attr.value
        logger.info("Voltage is %.2f" % voltage)
        return voltage

    def source_get_current(self):
        logger.info('Going to get current...')
        self.basic_tomo_check(from_experiment=False)

        current_attr = self.try_thrice_read_attr("xraysource_current",
										   		 error_str='Could not get current')
        current = current_attr.value
        logger.info("Current is %.2f" % current)
        return current



    def set_x(self, new_x, from_experiment=False, exp_is_advanced=True):
        """ Tries to set new horizontal position of object
        :arg:
            :return:
        """
        logger.info('Going to set new horizontal position...')

    	self.basic_tomo_check(from_experiment)

        if type(new_x) not in (int, float):
            raise ModExpError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_x)))

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_x))
        if new_x < -5000 or 2000 < new_x:
            raise ModExpError(error='Position must have value from -5000 to 2000')

        set_x = self.try_thrice_change_attr("horizontal_position", new_x,
        									error_str='Could not set new position because of tomograph')
        logger.info('Position was set!')

    def set_y(self, new_y, from_experiment=False, exp_is_advanced=True):
        """ Tries to set new vertical position of object

        :arg: 'new_y' - value of new vertical position, in 'popugaychiki', type is int

        :return:
        """
        logger.info('Going to set new vertical position...')

        self.basic_tomo_check(from_experiment)

        if type(new_y) not in (int, float):
            raise ModExpError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_y)))

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_y))
        if new_y < -5000 or 2000 < new_y:
            raise ModExpError(error='Position must have value from -30 to 30')

        set_y = self.try_thrice_change_attr("vertical_position", new_y,
        									error_str='Could not set new position because of tomograph')

        logger.info('Position was set!')

    def set_angle(self, new_angle, from_experiment=False, exp_is_advanced=True):
        """ Tries to set new angle position of object

        :arg: 'new_angle' - value of new angle position, in 'grades', type is float

        :return:
        """
        logger.info('Going to set new angle position...')

        self.basic_tomo_check(from_experiment)


        if type(new_angle) not in (int, float):
            raise ModExpError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_angle)))

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_angle))
        new_angle %= 360


        set_angle = self.try_thrice_change_attr("angle_position", new_angle,
        										error_str='Could not set new position because of tomograph')

        logger.info('Position was set!')


    def get_x(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to get horizontal position of object
        :arg:
        :return:
        """
        logger.info('Going to get horizontal position...')
        self.basic_tomo_check(from_experiment)

        x_attr = self.try_thrice_read_attr("horizontal_position",
										   error_str='Could not get position because of tomograph')
        x_value = x_attr.value
        logger.info('Horizontal position is %d' % x_value)
        return x_value

    def get_y(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to get vertical position of object
        :arg:
        :return:
        """
        logger.info('Going to get vertical position...')
        self.basic_tomo_check(from_experiment)

        y_attr = self.try_thrice_read_attr("vertical_position",
        								   error_str='Could not get position because of tomograph')
        y_value = y_attr.value
        logger.info('Vertical position is %d' % y_value)
        return y_value

    def get_angle(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to get vertical position of object
        :arg:
        :return:
        """
        logger.info('Going to get angle position...')
        self.basic_tomo_check(from_experiment)

        angle_attr = self.try_thrice_read_attr("angle_position",
        										error_str='Could not get position because of tomograph')
        angle_value = angle_attr.value
        logger.info('Angle position is %.2f' % angle_value)
        return angle_value


    def reset_to_zero_angle(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to set current angle position as 0
        :arg:
        :return:
        """
        logger.info('Resetting angle position...')
        self.basic_tomo_check(from_experiment)

        try_thrice_function(func=self.tomograph_proxy.ResetAnglePosition,
                            error_str='Could not reset angle position because of tomograph')
        logger.info('Angle position was reset!')


    def move_away(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to move object away from detector
        :arg:
        :return:
        """
        logger.info('Moving object away...')
       	self.basic_tomo_check(from_experiment)

        try_thrice_function(func=self.tomograph_proxy.MoveAway, error_str='Could not move object away')
        logger.info('Object was moved away!')

    def move_back(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to move object "back" to the detector, in front of detector
        :arg:
        :return:
        """
        logger.info('Moving object back...')

        self.basic_tomo_check(from_experiment)

        try_thrice_function(func=self.tomograph_proxy.MoveBack, error_str='Could not move object back')

        logger.info('Object was moved back!')

    def get_frame(self, exposure, send_to_webpage=False, from_experiment=False, exp_is_advanced=True):
        """ Tries get frame with some exposure
        :arg: 'exposure' - exposure, which frame should get with
        :return:
        """
        logger.info('Going to get image...')

        self.basic_tomo_check(from_experiment)

        if type(exposure) not in (float, int):
            raise ModExpError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_angle)))

        # TO DELETE THIS LATER
        logger.info('Getting an image with exposure %.1f milliseconds...' % (exposure))
        if exposure < 0.1 or 16000 < exposure:
            raise ModExpError(error='Exposure must have value from 0.1 to 16000')

        # Tomograph takes exposure multiplied by 10 and rounded
        exposure = round(exposure)
        frame_metadata_json = try_thrice_function(func=self.tomograph_proxy.GetFrame, args=exposure,
        										  error_str='Could not get image because of tomograph')

        try:
            frame_dict = json.loads(frame_metadata_json)
        except TypeError:
            raise ModExpError(error='Could not convert frame\'s JSON into dict')
        det = self.detector_proxy

        
        logger.info('Image was get, reading the image from detector...')
        try:
            image = self.detector_proxy.read_attribute("image", extract_as=PyTango.ExtractAs.Nothing)
        except Exception as e:
            logger.info(e.message)
            repr(e)

        logger.info("Image was red, preparing the image to send to storage...")

        try:
            enc = PyTango.EncodedAttribute()
            image_numpy = enc.decode_gray16(image)
            #image_numpy = numpy.zeros((10, 10))
        except Exception as e:
            raise ModExpError(error='Could not convert the image to numpy.array', exception_message='' '''e.message''')

        frame_dict['image_data']['image'] = image_numpy
        return frame_dict

    def carry_out_simple_experiment(self, exp_param):
        time_of_experiment_start = time.time()
        self.current_experiment = Experiment(tomograph=self, exp_param=exp_param)

        exp_id = self.current_experiment.exp_id
        event_for_send = {}
        stop_msg = ""

        try:
           self.current_experiment.run()
        except ModExpError as e:
            e.log(exp_id)
            event_for_send = e.to_event_dict(exp_id)
            stop_msg = e.stop_msg
            """
        except Exception as e:
            error = "unexpected exception"
            exception_message = e.message
            logger.info(error)
            logger.info(exception_message)
            stop_msg = EMERGENCY_STOP_MSG


            try:
                event_for_send = create_event(type='message', exp_id=exp_id, MoF=EMERGENCY_STOP_MSG, error=error,
                                              exception_message=exception_message)
            except Exception as e2:
                event_for_send = create_event(type='message', exp_id=exp_id, MoF=EMERGENCY_STOP_MSG, error=error)
            """
        else:
            event_for_send = create_event(type='message', exp_id=exp_id, MoF=SUCCESSFULL_STOP_MSG)
            stop_msg = SUCCESSFULL_STOP_MSG

        logger.info(stop_msg + ', id: ' + exp_id)
        logger.info("Sending messages about stop of experiment...")
        send_message_to_storage_webpage(event_for_send)

        self.current_experiment = None
        experiment_time = time.time() - time_of_experiment_start
        logger.info("Experiment took %.4f seconds" % experiment_time)

#-----------------------------------------------------------------------------------------------


    def try_thrice_read_attr_detector(self, attr_name, extract_as=ExtractAs.Numpy, error_str=''):
        """ Try to read some attribute of Tango device three times

        :arg: 'attr_name' - type is string
              'extract-as' - method of extraction
        :return:
        """
        exception_message = ''
        for i in range(0, 3):
            try:
                attr = self.detector_proxy.read_attribute(attr_name, extract_as)
            except PyTango.DevFailed as e:
                exception_message = e[-1].desc
            else:
                return attr
        raise ModExpError(error=error_str, exception_message=exception_message)

    def get_detector_chip_temperature(self, from_experiment=False, exp_is_advanced=True):

        logger.info('Going to get detector chip temperature...')
        self.basic_tomo_check(from_experiment)

        chip_temp_attr = self.try_thrice_read_attr_detector("chip_temp",
                                                            error_str='Could not chip temperature because of tomograph')
        chip_temp = chip_temp_attr.value
        logger.info('Chip temperature is %.2f' % chip_temp)
        return chip_temp


    def get_detector_hous_temperature(self, from_experiment=False, exp_is_advanced=True):
        logger.info('Going to get detector hous temperature...')
        self.basic_tomo_check(from_experiment)

        hous_temp_attr = self.try_thrice_read_attr_detector("hous_temp",
                                                            error_str='Could not hous temperature because of tomograph')

        hous_temp = hous_temp_attr.value
        logger.info('Hous temperature is %.2f' % hous_temp)
        return hous_temp
        