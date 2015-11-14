#!/usr/bin/python

""" 
created for refactoring using class 'Message'

Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph """
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!

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


def make_png(res, exp_id=''):
    """ Takes 2-dimensional numpy array and creates png file from it

    :arg: 'res' - image from tomograph in the form of 2-dimensional numpy array
          'exp_id' - ID of experiment, during that function is called.
                     If 'exp_id' is empty string, that means that function is called during adjustment, not
                     experiment, in this case function return answer in different format;
                     Type is string

    :return: list of 2 elements:
             1 - success of function, type is bool
             2 - depends on "emptiness" of argument 'exp_id';
             if 'exp_id' is NOT empty, function returns "event"(dictionary with format that is returned by
                 'create_event()'), converted to JSON-string
             if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
             type is json-string with format that is returned by  'create_response()'
    """
    logger.info("Converting image to png-file...")
    try:
        small_res = zoom(res, zoom=0.25, order=2)
        plt.imsave(FRAME_PNG_FILENAME, small_res, cmap=plt.cm.gray)
    except Exception as e:
        error = "Could not convert image to png-file"
        logger.info(error)
        if not exp_id:
            return False, create_response(success=False, error="Could not convert image to png-file",
                                          exception_message='' '''e.message''')
        else:
            # In this case, we suppose that our function was called from 'send_event_to_webpage()'
            error_event_dict = create_event("message", exp_id, MoF="Problems with sending to web-page of adjustment",
                                            exception_message='' '''e.message''', error=error)
            error_event_json = json.dumps(error_event_dict)
            return False, error_event_json

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

        image_numpy = event_dict['frame']['image_data']['image']
        exp_id = event_dict['exp_id']
        success, error_event_json_if_fail = make_png(image_numpy, exp_id)
        if not success:
            files = None
            event_json = error_event_json_if_fail
            logger.info('Sending error message to web-page of adjustment...')

        else:
            files = {'file': open(FRAME_PNG_FILENAME, 'rb')}

            del (event_dict['frame'])
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

class Message:
    exp_id = ''
    exception_message=''
    error=''


    def __init__(self, exp_id='', exception_message='', error=''):

        self.exp_id = exp_id
        self.exception_message = exception_message
        self.error = error

    def to_dict():
        pass

class InfoMessage(Message):
    info = ''
    def __init__(self, exp_id='', info='', exception_message='', error=''):

        self.exp_id = exp_id
        self.info = info
        self.exception_message = exception_message
        self.error = error

class FrameMessage(Message):
    pass


class Tomograph:
    """ Wrapper of interaction with Tango tomograph server"""
    tomograph_proxy = None
    detector_proxy = None
    experiment_is_running = False
    exp_id = ""
    exp_frame_num = 0
    exp_stop_reason = "unknown"

    class ModExpError(Exception):
        exp_id = ''

        def __init__(self, error='', exp_id=''):
            self.message = error
            self.error = error
            self.exp_id = exp_id

        def __str__(self):
            return repr(self.message)

        def create_Message(self):
            pass

        def log(self):
            pass
        
    class SomeoneStoppedError(ModExpError):
        reason = "unknown"

        def __init__(self, exp_id, reason='unknown'):
            Tomograph.ModExpError.__init__(self, error=reason, exp_id=exp_id)
            self.reason = reason

        def create_Message(self):
            return InfoMessage(exp_id=self.exp_id, info=SOMEONE_STOP_MSG, error=self.reason)

        def log(self):
            logger.info(SOMEONE_STOP_MSG)
            logger.info("reason:    " + self.reason)

    class TomoError(ModExpError):
        exception_message = ''

        def __init__(self, error='', exception_message='', exp_id=''):
            Tomograph.ModExpError.__init__(self, error=error, exp_id=exp_id)
            self.exception_message = exception_message

        def create_Message(self):
            return InfoMessage(exp_id=self.exp_id, info=EMERGENCY_STOP_MSG, error=self.error, 
                               exception_message=self.exception_message)

        def create_response(self):
            response_dict = {
                'success': False,
                'exception message': self.exception_message,
                'error': self.error,
                'result': None,
            }
            return json.dumps(response_dict)

        def log(self):
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
        raise TomoError(error=error_str, exception_message=exception_message, exp_id=self.exp_id)

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
        raise TomoError(error=error_str, exception_message=exception_message, exp_id=self.exp_id)

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
        raise TomoError(error=error_str, exception_message=exception_message, exp_id=self.exp_id)

    # NEED TO EDIT (ADD MAKING FIELD 'experiment_is_running' FALSE, IF EXPERIMENT IS STOPPED)
    # Here is converting to text
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


    def basic_tomo_check(self):
        if not self.exp_id and self.experiment_is_running:
            raise TomoError(error='On this tomograph experiment is running')

        if self.exp_id and not self.experiment_is_running:
            raise TomoError(error=error, exception_message='', exp_id=self.exp_id)


    def open_shutter(self, time=0, exp_is_advanced=True):
        """ Tries to open shutter

        :arg: 
        :return: 
        """
        logger.info('Opening shutter...')

        self.basic_tomo_check()

        try_thrice_function(func=self.tomograph_proxy.OpenShutter, args=time, error_str='Could not open shutter')
        logger.info('Shutter has been opened!')

    def close_shutter(self, time=0, exp_is_advanced=True):
        """ Tries to close shutter

        :arg: 
        :return: 
        """
        logger.info('Closing shutter...')

        self.basic_tomo_check()

        try_thrice_function(func=self.tomograph_proxy.CloseShutter, args=time, error_str='Could not close shutter')
        logger.info('Shutter has been closed!')

    def shutter_state(self, exp_is_advanced=True):
        #TODO documentation
        """ Tries to get tomo state

        :return: 
        """
        logger.info('Getting shutter state...')

        self.basic_tomo_check()

        status = try_thrice_function(func=tself.tomograph_proxy.ShutterStatus, args=ttime, error_str='Could not get shutter status')

        logger.info('Shutter return status successfully!')

        return status


    def set_x(self, new_x, exp_is_advanced=True):
        """ Tries to set new horizontal position of object
        :arg:
            :return:
        """
        logger.info('Going to set new horizontal position...')

    	self.basic_tomo_check()

        if type(new_x) not in (int, float):
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_x)), exp_id=self.exp_id)

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_x))
        if new_x < -5000 or 2000 < new_x:
            raise Tomograph.TomoError(error='Position must have value from -30 to 30', exp_id=self.exp_id)

        set_x = self.try_thrice_change_attr("horizontal_position", new_x, error_str='Could not set new position because of tomograph')

        logger.info('Position was set!')

    def set_y(self, new_y, exp_is_advanced=True):
        """ Tries to set new vertical position of object

        :arg: 'new_y' - value of new vertical position, in 'popugaychiki', type is int

        :return:
        """
        logger.info('Going to set new vertical position...')

        self.basic_tomo_check()

        if type(new_y) not in (int, float):
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_y)), exp_id=self.exp_id)

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_y))
        if new_x < -5000 or 2000 < new_x:
            raise TomoError(error='Position must have value from -30 to 30', exp_id=self.exp_id)

        set_x = self.try_thrice_change_attr("horizontal_position", new_y, error_str='Could not set new position because of tomograph')

        logger.info('Position was set!')

    def set_angle(self, new_angle, exp_is_advanced=True):
        """ Tries to set new angle position of object

        :arg: 'new_angle' - value of new angle position, in 'grades', type is float

        :return:
        """
        logger.info('Going to set new angle position...')

        self.basic_tomo_check()


        if type(new_angle) not in (int, float):
            raise TomoError(error='Incorrect type! Position type must be int, but it is ' + str(type(new_angle)), exp_id=self.exp_id)

        # TO DELETE THIS LATER
        logger.info('Setting value %.1f...' % (new_angle))
        new_angle %= 360


        set_angle = self.try_thrice_change_attr("angle_position", new_angle, error_str='Could not set new position because of tomograph')

        logger.info('Position was set!')


    def get_x(self, exp_is_advanced=True):
        """ Tries to get horizontal position of object
        :arg:
        :return:
        """
        logger.info('Going to get horizontal position...')

        self.basic_tomo_check()

        x_attr = self.try_thrice_read_attr("horizontal_position", error_str='Could not get position because of tomograph')

		x_value = x_attr.value
        logger.info('Horizontal position is %d' % x_value)
        return x_value

    def get_y(self, exp_is_advanced=True):
        """ Tries to get vertical position of object
        :arg:
        :return:
        """
        logger.info('Going to get vertical position...')

        self.basic_tomo_check()

        y_attr = self.try_thrice_read_attr("vertical_position", error_str='Could not get position because of tomograph')

		y_value = y_attr.value
        logger.info('Vertical position is %d' % y_value)
        return y_value


    def get_angle(self, exp_is_advanced=True):
        """ Tries to get vertical position of object
        :arg:
        :return:
        """
        logger.info('Going to get angle position...')

        self.basic_tomo_check()

        angle_attr = self.try_thrice_read_attr("angle_position", error_str='Could not get position because of tomograph')

		angle_value = angle_attr.value
        logger.info('Angle position is %.2f' % angle_value)
        return angle_value


    def reset_to_zero_angle(self, exp_is_advanced=True):
        """ Tries to set current angle position as 0
        :arg:
        :return:
        """
        logger.info('Resetting angle position...')

        self.basic_tomo_check()

        self.try_thrice_function(func=self.tomograph_proxy.ResetAnglePosition, error_str='Could not reset angle position because of tomograph')

        logger.info('Angle position was reset!')


    def move_away(self, exp_is_advanced=True):
        """ Tries to move object away from detector
        :arg:
        :return:
        """
        logger.info('Moving object away...')

       	self.basic_tomo_check()

        self.try_thrice_function(func=self.tomograph_proxy.MoveAway, error_str='Could not move object away')

        logger.info('Object was moved away!')

    def move_back(self, exp_is_advanced=True):
        """ Tries to move object "back" to the detector, in front of detector
        :arg:
        :return:
        """
        logger.info('Moving object back...')

        self.basic_tomo_check()

        self.try_thrice_function(func=self.tomograph_proxy.MoveBack, error_str='Could not move object back')

        logger.info('Object was moved back!')
'''
    def get_frame(self, exposure, send_to_webpage=True, exp_is_advanced=True):
        """ Tries get frame with some exposure

        :arg: 'exposure' - exposure, which frame should get with

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns list of 2 elements:
                    1 - success of function, type is bool
                    2 - frame with metadata, if 'success' is True, type is dict
                        None, if 'success' is False
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                    type is json-string with format that is returned by  'create_response()', if 'success' is False
                    type is rtype of function 'send_file()', if 'success' is True

        """
        logger.info('Going to get image...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            logger.info(error)
            return create_response(success=False, error=error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced)
            return False, None

        if type(exposure) is not float:
            error = 'Incorrect type! Exposure type must be float, but it is ' + str(type(exposure))
            logger.info(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id, exception_message='',
                                           error=error)
                return False, None
            else:
                return create_response(success=False, error=error)

        # TO DELETE THIS LATER
        logger.info('Getting image with exposure %.1f milliseconds...' % (exposure))
        if exposure < 0.1 or 16000 < exposure:
            error = 'Exposure must have value from 0.1 to 16000'
            logger.info(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id, exception_message='',
                                           error=error)
                return False, None
            else:
                return create_response(success=False, error=error)

        # Tomograph takes exposure multiplied by 10 and rounded
        exposure = round(exposure)
        success, frame_metadata_json, exception_message = try_thrice_function(self.tomograph_proxy.GetFrame, exposure)
        if success == False:
            error = 'Could not get image because of tomograph'
            logger.info(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id,
                                           exception_message=exception_message, error=error)
                return False, None
            else:
                return create_response(success, exception_message, error=error)

        try:
            frame_dict = json.loads(frame_metadata_json)
        except TypeError:
            error = 'Could not convert frame\'s JSON into dict'
            logger.info(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id, exception_message='',
                                           error=error)
                return False, None
            else:
                return create_response(success=False, error=error)

        det = self.detector_proxy
        try:
            image = det.read_attribute("image", extract_as=PyTango.ExtractAs.Nothing)
        except PyTango.DevFailed as e:
            for stage in e:
                logger.info(stage.desc)

        """
        success, image, exception_message = self.try_thrice_read_attr("image", extract_as=PyTango.ExtractAs.Nothing)
        print 'Type of image before decoding:\n', type(image)
        print 'Image before decoding:\n', image
        if success == False:
            error = 'Could not get image because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)
        """
        logger.info("Image was get, preparing image to send to storage...")
        try:
            enc = PyTango.EncodedAttribute()
            image_numpy = enc.decode_gray16(image)
        except Exception as e:
            error = 'Could not convert image to numpy.array'
            logger.info(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id,
                                           exception_message='' ''e.message'', error=error)
                return False, None
            else:
                return create_response(success=False, error=error, exception_message='' ''e.message'')

        if self.exp_id:
            # Joining numpy array of image and frame metadata
            frame_dict['image_data']['image'] = image_numpy
            frame_dict['number'] = self.exp_frame_num
            self.exp_frame_num += 1
            # POKA KOSTYL
            if exp_is_advanced:
                frame_event = create_event('frame', self.exp_id, frame_dict)
                self.send_event_to_storage_webpage(STORAGE_FRAMES_URI, frame_event, send_to_webpage)
                return True, frame_dict
            else:
                return True, frame_dict
        else:
            success, response_if_fail = make_png(image_numpy)
            if not success:
                return response_if_fail
            else:
                return send_file('../' + FRAME_PNG_FILENAME, mimetype='image/png')
'''