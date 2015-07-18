#!/usr/bin/python

""" Contains supporting functions and class "Tomograph" with methods for comfortable interaction with tomograph """

import json
import PyTango
import requests
import threading
import csv
import numpy as np
import pylab as plt
from flask import send_file
from StringIO import StringIO

from conf import STORAGE_URI
from conf import WEBPAGE_URI
from conf import TIMEOUT_MILLIS
from conf import FRAME_PNG_FILENAME



def try_thrice_function(func, args = None):
    """ Try to call some Tango function three times

        :return: list of 3 elements: the first is success of fail, the second is answer of called
                function in case of success, the third is exception message in case of fail
        :rtype: list of 3 elements: boolean, rtype of called function, string"""
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
        :rtype: string"""
    response_dict = {
        'success': success,
        'exception message': exception_message,
        'error': error,
        'result': result,
    }
    return json.dumps(response_dict)


def create_event(type, exp_id, MoF, exception_message = '', error = ''):
    # MoF - message or frame

    """ quite bydlocode
        event - it is message (for storage and web-page of adjustment) or frame with some data

        :arg: 'type' - string, 2 variants, 'message' or 'frame'
              'exp_id' - type is string
              'MoF' - message, type is string, if argument 'type' has value 'message'
                    - frame with some data, type is dict, if argument 'type' has value 'frame'
              'error' - error message, when argument 'type' has value 'message', type is string
              'exception_message' - exception message, when argument 'type' has value 'message', type is string
        :return: dictionary with data converted to string
        :rtype: string"""
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

def make_png(res):
    """ Takes 2-dimensional numpy array and creates png file from it

        :arg: 'res' - image from tomograph in the form of 2-dimensional numpy array
        :return: nothing"""
    plt.ioff()
    plt.figure()
    plt.imshow(res, cmap=plt.cm.gray)
    plt.colorbar()
    plt.savefig(FRAME_PNG_FILENAME, bbox_inches='tight')
    return

def create_png_file(frame_dict):

    """ converts frame to png and save it, to send it to webpage of adjustment
    :param frame_dict:
    """

    try:
        image_list = frame_dict["image_data"]["image"]
        image_numpy = np.asarray(image_list)
        make_png(image_numpy)
    except Exception as e:
        print e.message
    return

# NEED TO ADD CHECKING STORAGE'S RESPONSE
def send_messages_to_storage_webpage(event):
    # 'event' must be dictionary with format that is returned by  'create_event()'
    print('Sending to storage...')
    try:
        message = json.dumps(event)
        req_storage = requests.post(STORAGE_URI, data = message)
    except requests.ConnectionError as e:
        print(e.message)
        # sending message to web page of adjustment
        exp_id = event['exp_id']

        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        exp_emergency_message = create_event(type = 'message' , exp_id = exp_id, MoF = 'Experiment was emergency stopped',
                                             exception_message= '' '''e.message''', error= 'Could not send to storage')

        print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
        print('Sending to web page that we could send to storage...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = exp_emergency_message)
        except requests.ConnectionError as e:
            print('Could not send to web page of adjustment')
        else:
            print(req_webpage.content)
        return False

    else:
        print(req_storage.content)                              #NEED TO CHANGE  TO LOG RESULT, NOT ALL

        # commented 22.05, because frames are too heavy
        """
        if event['type'] == 'frame':
            create_png_file(event['frame'])
            files = {'file': open(FRAME_PNG_FILENAME, 'rb')}
            print('Sending to web page...')
            try:
                req_webpage = requests.post(WEBPAGE_URI, files=files)
            except requests.ConnectionError as e:
                print('Could not send to web page of adjustment')
            else:
                print(req_webpage.content)
        """
        return True



def join_image_with_metadata(image_numpy, frame_metadata_dict):

    s = StringIO()
    np.savetxt(s, image_numpy, fmt="%d")
    print(s.getvalue()[:10])
    frame_metadata_dict['image_data']['image'] = s.getvalue()

    return frame_metadata_dict


class Tomograph:

    tomograph_proxy = None
    detector_proxy = None
    experiment_is_running = False

    def __init__(self, tomograph_proxy_addr, detector_proxy_addr, timeout_millis = TIMEOUT_MILLIS):
        self.tomograph_proxy = PyTango.DeviceProxy(tomograph_proxy_addr)
        self.tomograph_proxy.set_timeout_millis(timeout_millis)

        self.detector_proxy = PyTango.DeviceProxy(detector_proxy_addr)
        self.detector_proxy.set_timeout_millis(timeout_millis)

    def try_thrice_change_attr(self, attr_name, new_value):
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
        # !in this method we SUPPOSE that 'stop_event' have fields  'exp_id', 'exception_message' and 'error'!
        stop_event['type'] = 'message'
        stop_event['message'] = 'Experiment was emergency stopped'
        self.experiment_is_running = False
        if send_messages_to_storage_webpage(stop_event) == False:
            return
        print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')

# methods below (open_shutter, close_shutter, set_x, set_y, set_angle, reset_angle, move_away, move_back and
# get_frame) can be called during experiment or not. If not, then argument exp_id is empty and vice versa. In this cases
# functions return answer in different format
    def open_shutter(self, time = 0, exp_id = ''):
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
        if exp_id: return True
        else:      return create_response(True)

    def close_shutter(self, time = 0, exp_id = ''):
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

    def reset_angle(self, exp_id = ''):
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


    def read_image_from_detector_attr(self):

        """
        returns frame attribute from detector as a numpy.array
        """

        det = self.detector_proxy
        try:
            da = det.read_attribute("image", extract_as=PyTango.ExtractAs.Nothing)
        except PyTango.DevFailed as e:
            for stage in e:
                print stage.desc

        enc = PyTango.EncodedAttribute()
        data = enc.decode_gray16(da)
        return data




    def get_frame(self, exposure, exp_id = ''):
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
        success, frame_metadata_json, exception_message = try_thrice_function(self.GetFrame, exposure)
        if success == False:
            error = 'Could not get image because of tomograph'
            print(exception_message)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= error)
                return False, None
            else:
                return create_response(success, exception_message, error= error)


        try:
            frame_metadata_dict = json.loads(frame_metadata_json)
        except TypeError:
            error = 'Could not convert frame\'s JSON into dict'
            print(error)
            if exp_id:
                self.handle_emergency_stop(exp_id= exp_id, exception_message= '', error= error)
                return False, None
            else:
                return create_response(success = False, error= error)

        image_numpy = self.read_image_from_detector_attr()

        print('Success!')
        if exp_id:
            frame_dict = join_image_with_metadata(image_numpy, frame_metadata_dict)
            return True, frame_dict
        else:
            print(1)
            make_png(image_numpy)
            print(2)
            return send_file(FRAME_PNG_FILENAME, mimetype= 'image/png')






