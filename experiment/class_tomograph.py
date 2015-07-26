#!/usr/bin/python

""" Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph """

import json
import PyTango
from PyTango import ExtractAs
import requests
import threading
import csv
import numpy as np
import pylab as plt
from flask import send_file
import copy
from StringIO import StringIO
import base64

from conf import STORAGE_URI
from conf import WEBPAGE_URI
from conf import TIMEOUT_MILLIS
from conf import FRAME_PNG_FILENAME



def try_thrice_function(func, args = None):
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
            answer = func(args)
        except PyTango.DevFailed as e:
            for stage in e:
                print stage.desc
            success = False
            exception_message = e[-1].desc
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
            'exception_message': exception_message,
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
            # DIANA
            # PROBLEM IS HERE, ERROR THAT 'DATA' MUST NOT BE A STRING
            req_webpage = requests.post(WEBPAGE_URI, files=files, data= event_json)
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

def send_json_to_storage(message_json):
    """ Sends json-string to storage

    :arg:  message, type is string
    :return: list of 2 elements;
             1 element is success of sending, type is bool
             2 element is information about problem, if success is false;
                          empty string if success is true; type is string
        """

    print('Sending to storage...')
    try:
        storage_resp = requests.post(STORAGE_URI, data = message_json)
    except requests.ConnectionError as e:
        exception_message = e.message
        print(exception_message)

        #IF UNCOMMENT   #exception_message,    OCCURS PROBLEMS WITH JSON.DUMPS(...) LATER
        return False, 'Could not send to storage' #exception_message

    else:
        try:
            storage_resp_dict = json.loads(storage_resp.content)
        except TypeError:
            exception_message = 'Storage\'s response is not JSON'
            print exception_message
            return False, exception_message

        if not ('result' in storage_resp_dict.keys()):
            exception_message = 'Storage\'s response has incorrect format'
            print exception_message
            return False, exception_message

        print('Storage\'s response:')
        print(storage_resp_dict['result'])
        if storage_resp_dict['result'] != 'success':
            return False, storage_resp_dict['result']


        return True, ''

# Here is converting to text
def send_event_to_storage_webpage(event_dict, send_to_webpage = True):
    """ Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
        'event_dict' must be dictionary with format that is returned by  'create_event()'

    :arg:  'event_dict' - event (message (for storage and web-page of adjustment) or frame with some data),
                          must be dictionary with format that is returned by  'create_event()'
           'send_to_webpage' - boolean; if False, it sends event to only storage;
                               if False it sends also to web-page of adjustment
    :return: success of sending, type is bool"""

    if event_dict['type'] == 'frame':
        image_numpy = event_dict['frame']['image_data']['image']
        del(event_dict['frame']['image_data']['image'])
        event_dict_for_storage = copy.deepcopy(event_dict)

        event_dict = event_dict
        event_dict['frame']['image_data']['image'] = image_numpy

        s = StringIO()

        np.savez_compressed(s, image_numpy)
        #np.savetxt(s, image_numpy, fmt="%d")

        print(s.getvalue()[:10])
        event_dict_for_storage['frame']['image_data']['image'] = base64.b64encode(s.getvalue())

    exp_id = event_dict['exp_id']
    event_json_for_storage = json.dumps(event_dict_for_storage)
    success, exception_message = send_json_to_storage(event_json_for_storage)
    if not success:
        exp_emergency_event = create_event(type= 'message', exp_id= exp_id, MoF= 'Experiment was emergency stopped',
                                             exception_message= exception_message, error= 'Problems with storage')
        exp_emergency_event_json = json.dumps(exp_emergency_event)

        print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
        print('Sending to web page that we could send to storage...')
        send_event_to_webpage(exp_emergency_event_json)
    else:
        if send_to_webpage == True:
            send_event_to_webpage(event_dict)


    return success


class Tomograph:
    """ Wrapper of interaction with Tango tomograph server"""

    tomograph_proxy = None
    experiment_is_running = False

    def __init__(self, tomograph_proxy_addr, timeout_millis = TIMEOUT_MILLIS):
        """
        :arg:  'tomograph_proxy_addr' - type is string
               'timeout_millis' - time that tomograph waits after command, type is int
        """
        self.tomograph_proxy = PyTango.DeviceProxy(tomograph_proxy_addr)
        self.tomograph_proxy.set_timeout_millis(timeout_millis)

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


    def handle_emergency_stop(self, **stop_event):
        """ Warns storage and webpage of adjustment about emergency stop of experiment (also changes value of field
            experiment_is_running' to False)

        :arg: 'stop_event' - "half" of "event" ("event" is dictionary with format that is returned by  'create_event()');
                             dictionary with fields 'exp_id', 'exception_message', 'error'
        :return: None
        """
        stop_event['type'] = 'message'
        stop_event['message'] = 'Experiment was emergency stopped'
        self.experiment_is_running = False
        if send_event_to_storage_webpage(stop_event) == False:
            return
        print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')

# --------------------------------METHODS FOR INTERACTION WITH TOMOGRAPH----------------------------------------#
# methods below (open_shutter, close_shutter, set_x, set_y, set_angle, reset_angle, move_away, move_back and
# get_frame) can be called during experiment or not. If not, then argument exp_id is empty and vice versa. In this cases
# functions return answer in different format
#---------------------------------------------------------------------------------------------------------------#
    def open_shutter(self, time = 0, exp_id = ''):
        """ Tries to open shutter

        :arg: 'time' - time that shutter must be opened for, in seconds; if 'time' equals 0, then opens for
                       unlimited time; type is float
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Opening shutter...')
        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.OpenShutter, time)
        if success == False:
            error = 'Could not open shutter'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id:
            return True
        else:
            return create_response(True)

    def close_shutter(self, time = 0, exp_id = ''):
        """ Tries to close shutter

        :arg: 'time' - time that shutter must be closed for, in seconds; if 'time' equals 0, then closes for
                       unlimited time; type is float
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Closing shutter...')
        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.CloseShutter, time)
        if success == False:
            error = 'Could not close shutter'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)


    def set_x(self, new_x, exp_id = ''):
        """ Tries to set new horizontal position of object

        :arg: 'new_x' - value of new horizontal position, in 'popugaychiki', type is int
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

            :return: depends on "emptiness" of argument 'exp_id';
                     if 'exp_id' is NOT empty, function returns success of function, type is bool
                     if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                     type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new horizontal position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if type(new_x) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_x))
            print (error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Setting value %.1f...' % (new_x))
        if new_x < -5000 or 2000 < new_x:
            error = 'Position must have value from -30 to 30'
            print(error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)


        success, set_x, exception_message = self.try_thrice_change_attr("horizontal_position", new_x)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)

    def set_y(self, new_y, exp_id = ''):
        """ Tries to set new vertical position of object

        :arg: 'new_y' - value of new vertical position, in 'popugaychiki', type is int
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new vertical position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if type(new_y) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_y))
            print (error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Setting value %.1f...' % (new_y))
        if new_y < -5000 or 2000 < new_y:
            error = 'Position must have value from -30 to 30'
            print(error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        success, set_y, exception_message = self.try_thrice_change_attr("vertical_position", new_y)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return False, create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)

    def set_angle(self, new_angle, exp_id = ''):
        """ Tries to set new angle position of object

        :arg: 'new_angle' - value of new angle position, in 'grades', type is float
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Going to set new angle position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if type(new_angle) is not float:
            error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_angle))
            print (error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False
            else:
                return create_response(success= False, error= error)

        print('Setting value %.1f...' % (new_angle))
        new_angle %= 360
        success, set_angle, exception_message = self.try_thrice_change_attr("angle_position", new_angle)
        if success == False:
            error = 'Could not set new position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)


    def get_x(self, exp_id = ''):
        """ Tries to get horizontal position of object

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

            :return: depends on "emptiness" of argument 'exp_id';
                     if 'exp_id' is NOT empty, function returns list of 2 elements:
                        1 - success of function, type is bool
                        2 - value of horizontal position in "popugaychiki", if 'success' is True, type is int;
                            None, if 'success' is False
                     if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                     type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get horizontal position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)


        success, x_attr, exception_message = self.try_thrice_read_attr("horizontal_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        x_value = x_attr.value
        print('Horizontal position is %d' % x_value)
        if exp_id: return True, x_value
        else:      return create_response(success= True, result= x_value)

    def get_y(self, exp_id = ''):
        """ Tries to get vertical position of object

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

            :return: depends on "emptiness" of argument 'exp_id';
                     if 'exp_id' is NOT empty, function returns list of 2 elements:
                        1 - success of function, type is bool
                        2 - value of vertical position in "popugaychiki", if 'success' is True, type is int;
                            None, if 'success' is False
                     if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                     type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get vertical position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)


        success, y_attr, exception_message = self.try_thrice_read_attr("vertical_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        y_value = y_attr.value
        print('Vertical position is %.2f' % y_value)
        if exp_id: return True, y_value
        else:      return create_response(success= True, result= y_value)

    def get_angle(self, exp_id = ''):
        """ Tries to get angle position of object

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

            :return: depends on "emptiness" of argument 'exp_id';
                     if 'exp_id' is NOT empty, function returns list of 2 elements:
                        1 - success of function, type is bool
                        2 - value of angle position in grades, if 'success' is True, type is float;
                            None, if 'success' is False
                     if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                     type is json-string with format that is returned by  'create_response()'
        """
        print('Going to get angle position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)


        success, angle_attr, exception_message = self.try_thrice_read_attr("vertical_position")
        if success == False:
            error = 'Could not get position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)

        angle_value = angle_attr.value
        print('Angle position is %.2f' % angle_value)
        if exp_id: return True, angle_value
        else:      return create_response(success= True, result= angle_value)


    def reset_angle(self, exp_id = ''):
        """ Tries to set current angle position as 0

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Resetting angle position...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.ResetAnglePosition)
        if success == False:
            error = 'Could not reset angle position because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)


    def move_away(self, exp_id = ''):
        """ Tries to move object away from detector

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Moving object away...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.MoveAway)
        if success == False:
            error = 'Could not move object away'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)

    def move_back(self, exp_id = ''):
        """ Tries to move object "back" to the detector, in front of detector

        :arg: 'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

        :return: depends on "emptiness" of argument 'exp_id';
                 if 'exp_id' is NOT empty, function returns success of function, type is bool
                 if 'exp_id' IS empty, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()'
        """
        print('Moving object back...')

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        success, useless, exception_message = try_thrice_function(self.tomograph_proxy.MoveBack)
        if success == False:
            error = 'Could not move object back'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False
            else:
                return create_response(success, exception_message, error= error)

        print('Success!')
        if exp_id: return True
        else:      return create_response(True)





    #  CHANGE FOR TEST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! (image_dict)
    def get_frame(self, exposure, exp_id = ''):
        """ Tries get frame with some exposure

        :arg: 'exposure' - exposure, which frame should get with
              'exp_id' - ID of experiment, during that function is called.
                         If 'exp_id' is empty string, that means that function is called during adjustment, not
                         experiment, in this case function return answer in different format;
                         Type is string

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

        if not exp_id and self.experiment_is_running:
            error = 'On this tomograph experiment is running'
            print(error)
            return create_response(success= False, error= error)

        if type(exposure) is not float:
            error = 'Incorrect type! Exposure type must be float, but it is ' + str(type(exposure))
            print (error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success= False, error= error)

        # TO DELETE THIS LATER
        print('Getting image with exposure %.1f milliseconds...' % (exposure))
        if exposure < 0.1 or 16000 < exposure:
            error = 'Exposure must have value from 0.1 to 16000'
            print(error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success= False, error= error)


        # Tomograph takes exposure multiplied by 10 and rounded
        exposure = round(exposure * 10)
        success, frame_metadata_json, exception_message = try_thrice_function(self.tomograph_proxy.GetFrame, exposure)
        if success == False:
            error = 'Could not get image because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)


        try:
            frame_dict = json.loads(frame_metadata_json)
        except TypeError:
            error = 'Could not convert frame\'s JSON into dict'
            print(error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success = False, error= error)

        # DIANA
        # COMMENTED BECAUSE COULD NOT READ ATTRIBUTE "IMAGE" FROM TOMOGRAPH DEVICE
        """success, image, exception_message = self.try_thrice_read_attr("image", extract_as=PyTango.ExtractAs.Nothing)
        if success == False:
            error = 'Could not get image because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)
        """
        # FICTITIOUS IMAGE
        image_numpy = np.array([[1, 2, 3],[4, 5, 6]])

        if exp_id:
            # Joining numpy array of image and frame metadata
            frame_dict['image_data']['image'] = image_numpy
            return True, frame_dict
        else:
            success, response_if_fail = make_png(image_numpy)
            if not success:
                return response_if_fail
            else:
                return send_file(FRAME_PNG_FILENAME, mimetype= 'image/png')







