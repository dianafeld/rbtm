#!/usr/bin/python

""" Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph """
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!

import os
import json
import PyTango
from PyTango import ExtractAs
import requests
import csv
import numpy as np
import pylab as plt
from flask import send_file
import copy
from StringIO import StringIO

from conf import STORAGE_FRAMES_URI
from conf import STORAGE_EXP_FINISH_URI
from conf import WEBPAGE_URI
from conf import TIMEOUT_MILLIS
from conf import FRAME_PNG_FILENAME


# MAYBE NEED TO EDIT (COMMENT IN FUNCTION)
def try_thrice_function(func, *args):
    """ Tries to call some TANGO function three times

    :arg: 'func' - called function
          'args' - function 'func' is being called with arguments 'args'
    :return: list of 3 elements,
             1 - success of calling function, type is bool
             2 - answer of called function in case of success (None in case of fail), rtype of called function
             3 - exception message in case of fail (empty string in case of success), type is string
    """
    success = True
    exception_message = ''
    for i in range(0, 3):
        try:
            answer = func(*args)
        except PyTango.DevFailed as e:
            for stage in e:
                print stage.desc
            success = False
            exception_message = e[-1].desc
            answer = None
        except Exception as e:
            print e.message
            success = False
            # Can be problems with converting to JSON e.message
            exception_message = e.message
            answer = None
        else:
            break
    return success, answer, exception_message


def create_response(success = True, exception_message = '', error = '', result = None):
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


def create_event(type, exp_id, MoF, exception_message = '', error = ''):
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

def make_png(res, exp_id = ''):
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
    print("Converting image to png-file...")
    try:
        plt.ioff()
        plt.figure()
        plt.imshow(res, cmap=plt.cm.gray)
        plt.colorbar()
        plt.savefig(FRAME_PNG_FILENAME, bbox_inches='tight')
    except Exception as e:
        error = "Could not convert image to png-file"
        print(error)
        if not exp_id:
            return False, create_response(success= False, error= "Could not convert image to png-file", exception_message= '' '''e.message''')
        else:
            # In this case, we suppose that our function was called from 'send_event_to_webpage()'
            error_event_dict = create_event("message", exp_id, MoF = "Problems with sending to web-page of adjustment",
                                       exception_message= '' '''e.message''', error= error)
            error_event_json = json.dumps(error_event_dict)
            return False, error_event_json

    print("Success!")
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
            print('Sending error message to web-page of adjustment...')

        else:
            files = {'file': open(FRAME_PNG_FILENAME, 'rb')}

            del (event_dict['frame'])
            event_json = json.dumps(event_dict)
            print('Sending frame to web-page of adjustment...')


        try:
            req_webpage = requests.post(WEBPAGE_URI, files=files)
            # WE DON'T SEND TO WEB-PAGE METADATA OF FRAME YET, IN FUTURE WE CAN ADD IT
            #req_webpage = requests.post(WEBPAGE_URI, files=files, data= event_json)
        except requests.ConnectionError as e:
            print('Could not send to web-page of adjustment')
        else:
            print(req_webpage.content)

    if event_dict['type'] == 'message':
        event_json = json.dumps(event_dict)
        print('Sending message to web-page of adjustment...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = event_json)
        except requests.ConnectionError as e:
            print('Could not send to web-page of adjustment')
        else:
            print(req_webpage.content)
# NEED TO EDIT DOCSTRING
def send_to_storage(storage_uri, data, files = None):
    """ Sends  to storage

    :arg:  message, type is string
    :return: list of 2 elements;
             1 element is success of sending, type is bool
             2 element is information about problem, if success is false;
                          empty string if success is true; type is string
    """

    print('Sending to storage...')
    try:
        storage_resp = requests.post(storage_uri, files= files, data = data)
    except requests.ConnectionError as e:
        exception_message = e.message
        print(exception_message)

        #IF UNCOMMENT   #exception_message,    OCCURS PROBLEMS WITH JSON.DUMPS(...) LATER
        return False, 'Could not send to storage' #exception_message

    else:
        try:
            storage_resp_dict = json.loads(storage_resp.content)
        except (ValueError, TypeError):
            exception_message = 'Storage\'s response is not JSON'
            print exception_message
            return False, exception_message

        if not ('result' in storage_resp_dict.keys()):
            exception_message = 'Storage\'s response has incorrect format'
            print exception_message
            print storage_resp_dict
            return False, exception_message

        print('Storage\'s response:')
        print(storage_resp_dict['result'])
        if storage_resp_dict['result'] != 'success':
            return False, storage_resp_dict['result']


        return True, ''


class Tomograph:
    """ Wrapper of interaction with Tango tomograph server"""
    tomograph_proxy = None
    detector_proxy = None
    experiment_is_running = False
    exp_id = ""

    class ExpStopException(Exception):
        exception_message = ''
        def __init__(self, error='', exception_message=''):
            self.message = error
            self.error = error
            self.exception_message = exception_message
        def __str__(self):
            return repr(self.message)


    def __init__(self, tomograph_proxy_addr, detector_proxy_addr, timeout_millis = TIMEOUT_MILLIS):
        """
        :arg:  'tomograph_proxy_addr' - type is string
               'detector_proxy_addr' - type is string
               'timeout_millis' - time that tomograph waits after command, type is int
        """
        self.tomograph_proxy = PyTango.DeviceProxy(tomograph_proxy_addr)
        self.tomograph_proxy.set_timeout_millis(timeout_millis)

        self.detector_proxy = PyTango.DeviceProxy(detector_proxy_addr)
        self.detector_proxy.set_timeout_millis(timeout_millis)



    def try_thrice_read_attr(self, attr_name, extract_as = ExtractAs.Numpy):
        """ Try to change some attribute of Tango device three times

        :arg: 'attr_name' - type is string
              'new_value' - type is type of attribute

        :return: list of 3 elements,
                 1 - success of changing attribute, type is bool
                 2 - set value of attribute, type is type of attribute
                 3 - exception message in case of fail (empty string in case of success), type is string
        """
        success = True
        exception_message = ''
        for i in range(0, 3):
            try:
                attr = self.tomograph_proxy.read_attribute(attr_name, extract_as)
            except PyTango.DevFailed as e:
                success = False
                exception_message = e[-1].desc
                attr = None
            else:
                break
        return success, attr, exception_message

    def try_thrice_change_attr(self, attr_name, new_value):
        """ Try to change some attribute of Tango device three times

        :arg: 'attr_name' - type is string
              'new_value' - type is type of attribute

        :return: list of 3 elements,
                 1 - success of changing attribute, type is bool
                 2 - set value of attribute, type is type of attribute
                 3 - exception message in case of fail (empty string in case of success), type is string
        """
        success = True
        exception_message = ''
        for i in range(0, 3):
            try:
                self.tomograph_proxy.write_attribute(attr_name, new_value)
                set_value = self.tomograph_proxy[attr_name].value
            except PyTango.DevFailed as e:
                success = False
                exception_message = e[-1].desc
                set_value = None
            else:
                break
        return success, set_value, exception_message

    # NEED TO EDIT (ADD MAKING FIELD 'experiment_is_running' FALSE, IF EXPERIMENT IS STOPPED)
    # Here is converting to text
    def send_event_to_storage_webpage(self, storage_uri, event_dict, send_to_webpage = True):
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
            del(event_dict['frame']['image_data']['image'])
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
            exp_emergency_event = create_event(type= 'message', exp_id= exp_id, MoF= 'Experiment was emergency stopped',
                                                 exception_message= exception_message, error= 'Problems with storage')

            print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
            self.experiment_is_running = False
            self.exp_id = ''
            print('Sending to web page about problems with storage storage...')
            send_event_to_webpage(exp_emergency_event)
        # commented 27.07.15 for tests with real storage, because converting to png file in
        # function 'send_event_to_webpage()' takes a lot of time
        """
        else:
            if send_to_webpage == True:
                send_event_to_webpage(event_dict)
        """

        return success

    def handle_emergency_stop(self, exp_is_advanced, **stop_event):
        """ Warns storage and webpage of adjustment about emergency stop of experiment (also changes value of field
            experiment_is_running' to False)

        :arg: 'stop_event' - "half" of "event" ("event" is dictionary with format that is returned by  'create_event()');
                             dictionary with fields 'exp_id', 'exception_message', 'error'
        :return: None
        """
        stop_event['type'] = 'message'
        stop_event['message'] = 'Experiment was emergency stopped'
        self.experiment_is_running = False
        self.exp_id = ''
        if self.send_event_to_storage_webpage(STORAGE_EXP_FINISH_URI, stop_event) == False:
            if not exp_is_advanced:
                return
            else:
                raise self.ExpStopException('Experiment was emergency stopped', 'Problems with storage')
        print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
        if exp_is_advanced:
            raise self.ExpStopException(stop_event['error'], stop_event['exception_message'])

    def stop_experiment_because_someone(self, exp_is_advanced):
        exp_stop_event = create_event('message', self.exp_id, 'Experiment was stopped by someone')
        if self.send_event_to_storage_webpage(STORAGE_EXP_FINISH_URI, exp_stop_event) == False:
            if exp_is_advanced:
                return
            else:
                raise self.ExpStopException('Experiment was emergency stopped', 'Problems with storage')
        self.exp_id = ''
        print('\nEXPERIMENT IS STOPPED BY SOMEONE!!!\n')
        if not exp_is_advanced:
            return
        else:
            raise self.ExpStopException('Experiment was stopped by someone')

# --------------------------------METHODS FOR INTERACTION WITH TOMOGRAPH----------------------------------------#
# methods below (open_shutter, close_shutter, set_x, set_y, set_angle, reset_to_zero_angle, move_away, move_back and
# get_frame) can be called during experiment or not. If not, then argument exp_id is empty and vice versa. In this cases
# functions return answer in different format
#---------------------------------------------------------------------------------------------------------------#

    def open_shutter(self, time = 0, exp_is_advanced = True):
        """ Tries to open shutter

        :arg: 'time' - time that shutter must be opened for, in seconds; if 'time' equals 0, then opens for
                       unlimited time; type is float

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Opening shutter...')
        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.OpenShutter, time)
        if success == False:
            error = 'Could not open shutter'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id,
                                           exception_message=exception_message, error=error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id:
            return True
        else:
            return create_response(True)

    def close_shutter(self, time = 0, exp_is_advanced = True):
        """ Tries to close shutter

        :arg: 'time' - time that shutter must be closed for, in seconds; if 'time' equals 0, then closes for
                       unlimited time; type is float

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Closing shutter...')
        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.CloseShutter, time)
        if success == False:
            error = 'Could not close shutter'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)


    def set_x(self, new_x, exp_is_advanced = True):
        """ Tries to set new horizontal position of object

        :arg: 'new_x' - value of new horizontal position, in 'popugaychiki', type is int

            :return: depends on "emptiness" of argument 'exp_id';
                     if 'exp_id' is NOT empty, function returns success of function, type is bool
                     if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                     type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new horizontal position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        if type(new_x) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_x))
            print (error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Setting value %.1f...' % (new_x))
        if new_x < -5000 or 2000 < new_x:
            error = 'Position must have value from -30 to 30'
            print(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)


        success, set_x, exception_message = self.try_thrice_change_attr("horizontal_position", new_x)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)

    def set_y(self, new_y, exp_is_advanced = True):
        """ Tries to set new vertical position of object

        :arg: 'new_y' - value of new vertical position, in 'popugaychiki', type is int

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new vertical position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        if type(new_y) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_y))
            print (error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Setting value %.1f...' % (new_y))
        if new_y < -5000 or 2000 < new_y:
            error = 'Position must have value from -30 to 30'
            print(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        success, set_y, exception_message = self.try_thrice_change_attr("vertical_position", new_y)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return False, create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)

    def set_angle(self, new_angle, exp_is_advanced = True):
        """ Tries to set new angle position of object

        :arg: 'new_angle' - value of new angle position, in 'grades', type is float

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new angle position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        if type(new_angle) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_angle))
            print (error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        print('Setting value %.1f...' % (new_angle))
        new_angle %= 360
        success, set_angle, exception_message = self.try_thrice_change_attr("angle_position", new_angle)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id, exception_message= exception_message, error=error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)


    def get_x(self, exp_is_advanced = True):
        """ Tries to get horizontal position of object

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                if 'exp_id' is NOT empty, function returns list of 2 elements:
                    1 - success of function, type is bool
                    2 - value of horizontal position in "popugaychiki", if 'success' is True, type is int;
                        None, if 'success' is False
                if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get horizontal position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)


        success, x_attr, exception_message = self.try_thrice_read_attr("horizontal_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id=self.exp_id, exception_message=exception_message, error=error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        x_value = x_attr.value
        print('Horizontal position is %d' % x_value)
        if self.exp_id: return True, x_value
        else:      return create_response(success= True, result= x_value)

    def get_y(self, exp_is_advanced = True):
        """ Tries to get vertical position of object

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                if 'exp_id' is NOT empty, function returns list of 2 elements:
                    1 - success of function, type is bool
                    2 - value of vertical position in "popugaychiki", if 'success' is True, type is int;
                        None, if 'success' is False
                if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get vertical position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)


        success, y_attr, exception_message = self.try_thrice_read_attr("vertical_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        y_value = y_attr.value
        print('Vertical position is %.2f' % y_value)
        if self.exp_id: return True, y_value
        else:      return create_response(success= True, result= y_value)

    def get_angle(self, exp_is_advanced = True):
        """ Tries to get angle position of object

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                if 'exp_id' is NOT empty, function returns list of 2 elements:
                    1 - success of function, type is bool
                    2 - value of angle position in grades, if 'success' is True, type is float;
                        None, if 'success' is False
                if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get angle position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)


        success, angle_attr, exception_message = self.try_thrice_read_attr("vertical_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        angle_value = angle_attr.value
        print('Angle position is %.2f' % angle_value)
        if self.exp_id: return True, angle_value
        else:      return create_response(success= True, result= angle_value)


    def reset_to_zero_angle(self, exp_is_advanced = True):
        """ Tries to set current angle position as 0

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Resetting angle position...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.ResetAnglePosition)
        if success == False:
            error = 'Could not reset angle position because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)


    def move_away(self, exp_is_advanced = True):
        """ Tries to move object away from detector

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Moving object away...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.MoveAway)
        if success == False:
            error = 'Could not move object away'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)

    def move_back(self, exp_is_advanced = True):
        """ Tries to move object "back" to the detector, in front of detector

        :arg:

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Moving object back...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.MoveBack)
        if success == False:
            error = 'Could not move object back'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if self.exp_id: return True
        else:      return create_response(True)





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
        print('Going to get image...')

        if not self.exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if self.exp_id and not self.experiment_is_running:
            self.stop_experiment_because_someone(exp_is_advanced, self.exp_id)

        if type(exposure) is not float:
            error = 'Incorrect type! Exposure type must be float, but it is ' + str(type(exposure))
            print (error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Getting image with exposure %.1f milliseconds...' % (exposure))
        if exposure < 0.1 or 16000 < exposure:
            error = 'Exposure must have value from 0.1 to 16000'
            print(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success= False, error= error)

        # Tomograph takes exposure multiplied by 10 and rounded
        exposure = round(exposure * 10)
        success, frame_metadata_json, exception_message = try_thrice_function(self.tomograph_proxy.GetFrame, exposure)
        if success == False:
            error = 'Could not get image because of tomograph'
            print(exception_message)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)


        try:
            frame_dict = json.loads(frame_metadata_json)
        except TypeError:
            error = 'Could not convert frame\'s JSON into dict'
            print(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success = False, error= error)


        det = self.detector_proxy
        try:
            image = det.read_attribute("image", extract_as=PyTango.ExtractAs.Nothing)
        except PyTango.DevFailed as e:
            for stage in e:
                print stage.desc

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

        try:
            enc = PyTango.EncodedAttribute()
            image_numpy = enc.decode_gray16(image)
            #print 'Type of image after decoding:\n', type(image_numpy)
            #print 'Image after decoding:\n', image_numpy
        except Exception as e:
            error = 'Could convert image to numpy.array'
            print(error)
            if self.exp_id:
                self.handle_emergency_stop(exp_is_advanced=exp_is_advanced, exp_id= self.exp_id,
                                           exception_message= '' '''e.message''', error= error)
                return False, None
            else:
                return create_response(success = False, error= error, exception_message = '' '''e.message''')

        if self.exp_id:
            # Joining numpy array of image and frame metadata
            frame_dict['image_data']['image'] = image_numpy
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
                return send_file(FRAME_PNG_FILENAME, mimetype='image/png')







