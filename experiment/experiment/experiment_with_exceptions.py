#!/usr/bin/python

""" 
created for refactoring using class 'Message' and exceptions

Contains class "Experiment" """
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
from tomograph import Tomograph
from tomograph import send_frame_to_storage_webpage
from tomograph import send_message_to_storage_webpage


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
        return False, ModExpError(error="Could not convert image to png-file",
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
            raise ModExpError(error='Problems with storage', exception_message=exception_message)
        # commented 27.07.15 for tests with real storage, because converting to png file in
        # function 'send_event_to_webpage()' takes a lot of time    
        else:
            if send_to_webpage == True:
                frame_dict = frame_metadata_dict
                frame_dict['frame']['image_data']['image'] = image_numpy
                send_event_to_webpage(frame_dict)
        #return success

class ModExpError(Exception):
    exception_message = ""
    type_of_stop = EMERGENCY_STOP_MSG

    def __init__(self, error='', exception_message='', type_of_stop=EMERGENCY_STOP_MSG):
        self.message = error
        self.error = error
        self.exception_message = exception_message

    def __str__(self):
        return repr(self.message)

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
            logger.info(("EXPERIMENT %s: " + SOMEONE_STOP_MSG) % exp_id)
        else:
            logger.info("ERROR:")

        if type_of_stop == EMERGENCY_STOP_MSG:
            logger.info("   " + self.error)
            logger.info("   " + self.exception_message)
        else:
            logger.info("Reason:    " + self.error)


class Experiment:
    """ For storing information about experiment during time it runs """

    exp_id = ''
    to_be_stopped = False
    reason_of_stop = ''

    def __init__(self, tomograph, exp_param, FOSITW=5):
        # FOSITW - 'Frequency Of Sending Images To Webpage '

        self.tomograph=tomograph
        self.exp_id = exp_param['exp_id']

        self.DARK_count = exp_param['DARK']['count']
        self.DARK_exposure = exp_param['DARK']['exposure']

        self.EMPTY_count = exp_param['EMPTY']['count']
        self.EMPTY_exposure = exp_param['EMPTY']['exposure']

        self.DATA_step_count = exp_param['DATA']['step count']
        self.DATA_exposure = exp_param['DATA']['exposure']
        self.DATA_angle_step = exp_param['DATA']['angle step']
        self.DATA_count_per_step = exp_param['DATA']['count per step']

        self.FOSITW = FOSITW

        self.frame_num = 0

    def get_and_send_frame():

        getting_frame_message = 'Getting image, number: %d, mode: %s ...' % (self.frame_num, self.mode)
        logger.info(getting_frame_message)
    
        frame_dict = tomograph.get_frame(exposure=exposure, exp_is_advanced=False)

        frame_dict['mode'] = self.mode
        frame_dict['number'] = self.number

        send_to_webpage = (self.number % self.FOSITW == self.FOSITW - 1)
        
        frame_metadata_dict = frame_dict
        del(frame_metadata_dict['frame']['image_data']['image'])

        send_frame_to_storage_webpage(frame_metadata_dict=frame_metadata_dict,
                                      image_numpy=frame_dict['frame']['image_data']['image'],
                                      send_to_webpage=send_to_webpage)
        #send_frame_to_storage_webpage(frame_dict=frame_dict, send_to_webpage=send_to_webpage)


    def run():
        # Closing shutter to get DARK images
        self.to_be_stopped = False
        self.reason_of_stop = ''
        self.tomograph.close_shutter(0, exp_is_advanced=False)

        logger.info('Going to get DARK images!\n')
        self.mode = 'dark'
        for i in range(0, self.DARK_count):
            get_and_send_frame()
        logger.info('Finished with DARK images!\n')

        self.tomograph.open_shutter(0, exp_is_advanced=False)
        self.tomograph.move_away(exp_is_advanced=False)

        logger.info('Going to get EMPTY images!\n')
        self.mode = 'empty'
        for i in range(0, self.EMPTY_count):
            get_and_send_frame()
        logger.info('Finished with EMPTY images!\n')

        self.tomograph.move_back(exp_is_advanced=False)



        logger.info('Going to get DATA images, step count is %d!\n' % (self.DATA_step_count))
        self.mode = 'data'
        initial_angle = self.tomograph.get_angle(exp_is_advanced=False)
        logger.info('Initial angle is %.2f' % initial_angle)
        angle_step = self.DATA_angle_step

        for i in range(0, self.EMPTY_step_count):
            current_angle = (round((i * angle_step) + initial_angle, 2)) % 360
            logger.info('Getting DATA images: angle is %.2f' % current_angle)

            for i in range(0, self.DATA_count_per_step):
                get_and_send_frame()

            # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
            new_angle = (round((i + 1) * angle_step + initial_angle, 2)) % 360
            logger.info('Finished with this angle, turning to new angle %.2f...' % (new_angle))
            self.tomograph.set_angle(new_angle, exp_is_advanced=False)

        logger.info('Finished with DATA images!\n')
        return
   

print 1