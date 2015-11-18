#!/usr/bin/python

""" 
created for refactoring using class 'Message' and exceptions

Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph """
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# Need to look at checking types of arguments, which go to Tango-tomograph functions

import json
import requests
import numpy as np
import copy
from StringIO import StringIO
import time
from scipy.ndimage import zoom

import PyTango
from PyTango import ExtractAs
import pylab as plt
from flask import send_file

from conf import STORAGE_FRAMES_URI
from conf import STORAGE_EXP_FINISH_URI
from conf import WEBPAGE_URI
from conf import TIMEOUT_MILLIS
from conf import FRAME_PNG_FILENAME
from experiment import app


logger = app.logger


EMERGENCY_STOP_MSG = 'Experiment has been emergency stopped!'
SOMEONE_STOP_MSG = 'Experiment has been stopped by someone!'
SUCCESS_MSG = 'Experiment has been done successfully!'




def create_response(success=True, exception_message='', error='', result=None):
    """ Creates response for queries in one format

    :return: dictionary with data converted to string
    :rtype: string
    """
    response_dict = {
        'success': success,
        'exception message': exception_message,
        'error': error,
        'result': result,
    }
    return json.dumps(response_dict)


def create_event(type, exp_id, MoF, exception_message='', error=''):
    # MoF - Message or Frame

    """ quite bydlocode
        "event" - It is message (for storage and web-page of adjustment) or frame with some data.
                This thing is the being sent most often to storage and web-page of adjustment

    :arg: 'type' - string, 2 variants, 'message' or 'frame'
          'exp_id' - type is string
          'MoF' - message, type is string, if argument 'type' has value 'message'
                - frame with some data, type is dict, if argument 'type' has value 'frame'
          'error' - error message, when argument 'type' has value 'message', type is string
          'exception_message' - exception message, when argument 'type' has value 'message', type is string
    :return: "event", dictionary with data converted to string
    :rtype: string
    """
    if type == 'message':
        event_with_message_dict = {
            'type': type,
            'exp_id': exp_id,
            'message': MoF,
            'exception message': exception_message,
            'error': error,
        }
        return event_with_message_dict

    elif type == 'frame':
        frame_dict = {
            'type': type,
            'exp_id': exp_id,
            'frame': MoF,
        }
        return frame_dict

    return None


def frame_to_png(frame_dict, png_filename=FRAME_PNG_FILENAME):
    """ Takes 2-dimensional numpy array and creates png file from it

    :arg: 'res' - image from tomograph in the form of 2-dimensional numpy array

    :return: 
    """
    logger.info("Converting image to png-file...")
    image_numpy = frame_dict['frame']['image_data']['image']
    res = image_numpy
    try:
        small_res = zoom(res, zoom=0.25, order=2)
        plt.imsave(png_filename, small_res, cmap=plt.cm.gray)
    except Exception as e:
        return False, Tomograph.TomoError(error="Could not convert image to png-file",
                                          exception_message='' '''e.message''')

    logger.info("Image was converted!")
    return True, None


def send_event_to_webpage(event_dict):
    """ Sends "event" to web-page of adjustment;
        'event_dict' must be dictionary with format that is returned by  'create_event()'
        if event type is "message", it sends it without changes,
        if event type is "frame", it sends image part, converting it to png-file,
        remain part (image data) is being sent without changes

    :arg:  event_dict - event (message (for storage and web-page of adjustment) or frame with some data),
           must be dictionary with format that is returned by  'create_event()'
    :return: None
    """

    if event_dict['type'] == 'frame':
        success, ModExpError_if_fail = frame_to_png(event_dict)
        if not success:
            files = None
            event_json = json.dumps(ModExpError_if_fail.to_dict())
            logger.info('Sending error message to web-page of adjustment...')

        else:
            files = {'file': open(FRAME_PNG_FILENAME, 'rb')}

            del (event_dict['frame']['image_data']['image'])
            event_json = json.dumps(event_dict)
            logger.info('Sending frame to web-page of adjustment...')

        try:
            req_webpage = requests.post(WEBPAGE_URI, files=files)
            # WE DON'T SEND TO WEB-PAGE METADATA OF FRAME YET, IN FUTURE WE CAN ADD IT
            # req_webpage = requests.post(WEBPAGE_URI, files=files, data= event_json)
        except requests.ConnectionError as e:
            logger.info('Could not send to web-page of adjustment')
        else:
            logger.info(req_webpage.content)

    if event_dict['type'] == 'message':
        event_json = json.dumps(event_dict)
        logger.info('Sending message to web-page of adjustment...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data=event_json)
        except requests.ConnectionError as e:
            logger.info('Could not send to web-page of adjustment')
        else:
            logger.info(req_webpage.content)


def send_to_storage(storage_uri, data, files=None):
    """ Sends  to storage

    :arg:  message, type is string
    :return: list of 2 elements;
             1 element is success of sending, type is bool
             2 element is information about problem, if success is false;
                          empty string if success is true; type is string
    """

    logger.info('Sending to storage...')
    try:
        storage_resp = requests.post(storage_uri, files=files, data=data)
    except requests.ConnectionError as e:
        exception_message = e.message
        logger.info(exception_message)

        # IF UNCOMMENT   #exception_message,    OCCURS PROBLEMS WITH JSON.DUMPS(...) LATER
        return False, 'Could not send to storage'  # exception_message

    else:
        try:
            logger.info(storage_resp.content)
            storage_resp_dict = json.loads(storage_resp.content)
        except (ValueError, TypeError):
            exception_message = 'Storage\'s response is not JSON'
            logger.info(exception_message)
            return False, exception_message

        if not ('result' in storage_resp_dict.keys()):
            exception_message = 'Storage\'s response has incorrect format'
            logger.info(exception_message)
            logger.info(storage_resp_dict)
            return False, exception_message

        logger.info('Storage\'s response:')
        logger.info(storage_resp_dict['result'])
        if storage_resp_dict['result'] != 'success':
            return False, storage_resp_dict['result']

        return True, ''


def send_message_to_storage_webpage(event_dict):        
	""" Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
        'event_dict' must be dictionary with format that is returned by  'create_event()'

    :arg:  'event_dict' - event (message (for storage and web-page of adjustment) or frame with some data),
                          must be dictionary with format that is returned by  'create_event()'
    :return: success of sending, type is bool
    """
    event_json_for_storage = json.dumps(event_dict)
    success, exception_message = send_to_storage(STORAGE_EXP_FINISH_URI, data=event_json_for_storage)
    send_event_to_webpage(event_dict)
    return success

def send_frame_to_storage_webpage(frame_metadata_dict, image_numpy, send_to_webpage=True):
        """ Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
            'frame_dict' must be dictionary with format that is returned by  'create_event()'

        :arg:
        :return: success of sending, type is bool
        """
        s = StringIO()

        np.savez_compressed(s, frame_data=image_numpy)
        s.seek(0)
        data = {'data': json.dumps(frame_metadata_dict)}
        files = {'file': s}
        success, exception_message = send_to_storage(STORAGE_FRAMES_URI, data, files)

        if not success:
            raise Tomograph.TomoError(error='Problems with storage', exception_message=exception_message)
        # commented 27.07.15 for tests with real storage, because converting to png file in
        # function 'send_event_to_webpage()' takes a lot of time    
        else:
            if send_to_webpage == True:
                frame_dict = frame_metadata_dict
                frame_dict['frame']['image_data']['image'] = image_numpy
                send_event_to_webpage(frame_dict)
        #return success


def try_thrice_function(error_str, func, args=()):
    """ Tries to call some TANGO function three times

    :arg: 'func' - called function
        'args' - function 'func' is being called with arguments 'args'
    :return:
    """
    if type(args) not in (tuple, list):
    	args = tuple(args)
    exception_message = ''
    for i in range(0, 3):
        try:
            answer = func(*args)
        except PyTango.DevFailed as e:
            for stage in e:
                logger.info(stage.desc)
            exception_message = e[-1].desc
        except Exception as e:
            logger.info(e.message)
            # Can be problems with converting to JSON e.message
            exception_message = e.message
        else:
            return answer
    raise TomoError(error=error_str, exception_message=exception_message)

class Tomograph:
    """ Wrapper of interaction with Tango tomograph server"""
    tomograph_proxy = None
    detector_proxy = None
    current_experiment = None

    class ModExpError(Exception):

        def __init__(self, error=''):
            self.message = error
            self.error = error

        def __str__(self):
            return repr(self.message)

        def to_event_dict(self, exp_id):
            pass

        def log(self):
            pass
        
    class SomeoneStoppedError(ModExpError):
        reason = "unknown"

        def __init__(self, reason='unknown'):
            Tomograph.ModExpError.__init__(self, error=reason)
            self.reason = reason

        def to_event_dict(self, exp_id):
            return create_event(type='message', exp_id=exp_id, MoF=SOMEONE_STOP_MSG, error=self.reason)

        def log(self):
            logger.info(SOMEONE_STOP_MSG)
            logger.info("reason:    " + self.reason)

    class TomoError(ModExpError):
        exception_message = ''

        def __init__(self, error='', exception_message=''):
            Tomograph.ModExpError.__init__(self, error=error)
            self.exception_message = exception_message

        def to_event_dict(self, exp_id):
            return create_event(type='message', exp_id=exp_id, MoF=EMERGENCY_STOP_MSG,
            					error=self.error, exception_message=self.exception_message)

        def create_response(self):
            response_dict = {
                'success': False,
                'exception message': self.exception_message,
                'error': self.error,
                'result': None,
            }
            return json.dumps(response_dict)

        def log(self, exp_id=''):
        	if exp_id:
            	logger.info("ERROR IN EXPERIMENT %s:" % exp_id)
            else:
            	logger.info("ERROR:")
            logger.info("   " + self.error)
            logger.info("   " + self.exception_message)






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
        """ Try to change some attribute of Tango device three times

        :arg: 'attr_name' - type is string
              'new_value' - type is type of attribute

        :return:
        """
        exception_message = ''
        for i in range(0, 3):
            try:
                attr = self.tomograph_proxy.read_attribute(attr_name, extract_as)
            except PyTango.DevFailed as e:
                exception_message = e[-1].desc
                attr = None
            else:
                return attr
        raise TomoError(error=error_str, exception_message=exception_message)

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
        raise TomoError(error=error_str, exception_message=exception_message)
	'''
    def send_event_to_storage_webpage(self, storage_uri, event_dict, send_to_webpage=True):
        """ Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
            'event_dict' must be dictionary with format that is returned by  'create_event()'

        :arg:  'event_dict' - event (message (for storage and web-page of adjustment) or frame with some data),
                              must be dictionary with format that is returned by  'create_event()'
               'send_to_webpage' - boolean; if False, it sends event to only storage;
                                   if False it sends also to web-page of adjustment
        :return: success of sending, type is bool"""
        success = False
        exception_message = ''
        exp_id = event_dict['exp_id']
        event_dict_for_storage = event_dict
        if event_dict['type'] == 'frame':
            image_numpy = event_dict['frame']['image_data']['image']
            del (event_dict['frame']['image_data']['image'])
            event_dict_for_storage = copy.deepcopy(event_dict)

            event_dict = event_dict
            event_dict['frame']['image_data']['image'] = image_numpy

            s = StringIO()

            np.savez_compressed(s, frame_data=image_numpy)
            s.seek(0)
            data = {'data': json.dumps(event_dict_for_storage)}
            files = {'file': s}
            success, exception_message = send_to_storage(storage_uri, data, files)

        else:
            event_json_for_storage = json.dumps(event_dict_for_storage)
            success, exception_message = send_to_storage(storage_uri, data=event_json_for_storage)
        if not success:
            exp_emergency_event = create_event(type='message', exp_id=exp_id, MoF='Experiment was emergency stopped',
                                               exception_message=exception_message, error='Problems with storage')

            logger.info('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
            self.experiment_is_running = False
            self.exp_id = ''
            logger.info('Sending to web page about problems with storage storage...')
            send_event_to_webpage(exp_emergency_event)
        # commented 27.07.15 for tests with real storage, because converting to png file in
        # function 'send_event_to_webpage()' takes a lot of time
        """
        else:
            if send_to_webpage == True:
                send_event_to_webpage(event_dict)
        """

        return success
	'''

    def basic_tomo_check(self, from_experiment):
        if not from_experiment:
        	if self.current_experiment != None:
            	raise TomoError(error='On this tomograph experiment is running')

        else:
        	if self.current_experiment.to_be_stopped == True:
            	raise SomeoneStoppedError(reason=self.current_experiment.reason_of_stop)



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

        status = try_thrice_function(func=tself.tomograph_proxy.ShutterStatus, args=time,
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
            raise TomoError(error='Incorrect format: type must be float')

	    # TO DELETE THIS LATER
	    logger.info('Format is correct, new voltage value is %.1f...' % (new_voltage))
	    if new_voltage < 2 or 60 < new_voltage:
            raise Tomograph.TomoError(error='Voltage must have value from 2 to 60!')

	    logger.info('Parameters are normal, setting new voltage...')
        set_voltage = self.try_thrice_change_attr("xraysource_voltage", new_voltage,
        										  error_str='Could not set voltage')

	    logger.info('New value of voltage was set!')

	def source_set_current(tomo_num, current):
	    logger.info('Going to set current on source...')
    	self.basic_tomo_check(from_experiment=False)

	    logger.info('Checking format...')
	    if type(current) is not float:
	        logger.info('Incorrect format! Current type must be float, but it is ' + str(type(current)))
            raise TomoError(error='Incorrect format: type must be float')

	    # TO DELETE THIS LATER
	    logger.info('Format is correct, new current value is %.1f...' % (current))
	    if current < 2 or 80 < current:
            raise Tomograph.TomoError(error='Current must have value from 2 to 80!')

	    logger.info('Parameters are normal, setting new current...')
        set_current = self.try_thrice_change_attr("xraysource_current", current,
        										  error_str='Could not set current')

	    logger.info('New value of current was set!')

	def source_get_voltage(tomo_num):
	    logger.info('Going to get voltage...')
    	self.basic_tomo_check(from_experiment=False)

        voltage_attr = self.try_thrice_read_attr("xraysource_voltage",
										   		 error_str='Could not get voltage')

	    voltage = voltage_attr.value
	    logger.info("Voltage is %.2f" % voltage)
	    return voltage

	def source_get_current(tomo_num):
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
            raise Tomograph.TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_x)))

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_x))
        if new_x < -5000 or 2000 < new_x:
            raise Tomograph.TomoError(error='Position must have value from -30 to 30')

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
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_y)))

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_y))
        if new_x < -5000 or 2000 < new_x:
            raise TomoError(error='Position must have value from -30 to 30')

        set_x = self.try_thrice_change_attr("horizontal_position", new_y,
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
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_angle)))

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

        self.try_thrice_function(func=self.tomograph_proxy.ResetAnglePosition,
        						 error_str='Could not reset angle position because of tomograph')

        logger.info('Angle position was reset!')


    def move_away(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to move object away from detector
        :arg:
        :return:
        """
        logger.info('Moving object away...')

       	self.basic_tomo_check(from_experiment)

        self.try_thrice_function(func=self.tomograph_proxy.MoveAway, error_str='Could not move object away')

        logger.info('Object was moved away!')

    def move_back(self, from_experiment=False, exp_is_advanced=True):
        """ Tries to move object "back" to the detector, in front of detector
        :arg:
        :return:
        """
        logger.info('Moving object back...')

        self.basic_tomo_check(from_experiment)

        self.try_thrice_function(func=self.tomograph_proxy.MoveBack, error_str='Could not move object back')

        logger.info('Object was moved back!')

    def get_frame(self, exposure, send_to_webpage=False, from_experiment=True, exp_is_advanced=True):
        """ Tries get frame with some exposure
        :arg: 'exposure' - exposure, which frame should get with
        :return:
        """
        logger.info('Going to get image...')

        self.basic_tomo_check(from_experiment)

        if type(exposure) not in (float, int):
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_angle)))

        # TO DELETE THIS LATER
        logger.info('Getting image with exposure %.1f milliseconds...' % (exposure))
        if exposure < 0.1 or 16000 < exposure:
            raise TomoError(error='Exposure must have value from 0.1 to 16000')

        # Tomograph takes exposure multiplied by 10 and rounded
        exposure = round(exposure)
        frame_metadata_json = self.try_thrice_function(func=self.tomograph_proxy.GetFrame, args=exposure,
        											   error_str='Could not get image because of tomograph')

        try:
            frame_dict = json.loads(frame_metadata_json)
        except TypeError:
            raise TomoError(error='Could not convert frame\'s JSON into dict')
        det = self.detector_proxy

        
        image = self.try_thrice_read_attr("image", extract_as=PyTango.ExtractAs.Nothing,
        								  error_str='Could not get image because of tomograph')


        logger.info("Image was get, preparing image to send to storage...")

        try:
            enc = PyTango.EncodedAttribute()
            image_numpy = enc.decode_gray16(image)
        except Exception as e:
            raise TomoError(error='Could not convert image to numpy.array', exception_message='' '''e.message''')

        frame_dict['image_data']['image'] = image_numpy
        return frame_dict
