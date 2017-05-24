#!/usr/bin/python

"""
Contains class 'Experiment', for storing information about experiment during time it runs
"""
# NEED TO EDIT DOCSTRINGS!
# NEED TO EDIT DOCSTRINGS!
# Need to look at checking types of arguments, which go to Tango-tomograph functions

import PyTango
import json
import requests
import numpy as np
from StringIO import StringIO
from scipy.ndimage import zoom
import threading
import time

import matplotlib.pyplot as plt

from experiment.conf import FRAME_PNG_FILENAME, STORAGE_EXP_FINISH_URI, STORAGE_FRAMES_URI


def get_logger():
    try:
        from flask import current_app
        logger = current_app.logger
    except RuntimeError:
        from experiment.views import app
        logger = app.logger
    except Exception as e:
        import logging
        logger = logging
    return logger


EMERGENCY_STOP_MSG = 'Experiment was emergency stopped'
SOMEONE_STOP_MSG = 'Experiment was stopped by someone'
SUCCESSFUL_STOP_MSG = 'Experiment was finished successfully'


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


def create_event(event_type, exp_id, MoF, exception_message='', error=''):
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
    if event_type == 'message':
        event_with_message_dict = {
            'type': event_type,
            'exp_id': exp_id,
            'message': MoF,
            'exception message': exception_message,
            'error': error,
        }
        return event_with_message_dict

    elif event_type == 'frame':
        frame_dict = {
            'type': event_type,
            'exp_id': exp_id,
            'frame': MoF,
        }
        return frame_dict

    return None


class ModExpError(Exception):
    def __init__(self, error, exception_message='', stop_msg=EMERGENCY_STOP_MSG):
        self.message = error
        self.error = error
        self.exception_message = exception_message
        self.stop_msg = stop_msg
        self.logger = get_logger()

    def __str__(self):
        return repr(self.message)

    def to_event_dict(self, exp_id):
        return create_event(event_type='message', exp_id=exp_id, MoF=self.stop_msg,
                            error=self.error, exception_message=self.exception_message)

    def create_response(self):
        response_dict = {
            'success': False,
            'exception message': self.exception_message,
            'error': self.error,
            'result': None,
        }
        return json.dumps(response_dict)

    def log(self, exp_id):
        if exp_id:
            self.logger.info(self.stop_msg + ', id: ' + exp_id)
        else:
            self.logger.info("ERROR: exp_id = {}".format(exp_id))

        if self.stop_msg == EMERGENCY_STOP_MSG:
            self.logger.info("   " + self.error)
            self.logger.info("   " + self.exception_message)
        else:
            self.logger.info("Reason:    " + self.error)


def make_png(image_numpy, png_filename=FRAME_PNG_FILENAME):
    """ Takes 2-dimensional numpy array and creates png file from it

    :arg: 'res' - image from tomograph in the form of 2-dimensional numpy array

    :return: 
    """
    get_logger().info("Converting image to png-file...")
    res = image_numpy
    try:
        small_res = zoom(np.rot90(res), zoom=0.25, order=0)
        plt.imsave(png_filename, small_res, cmap=plt.cm.gray)
    except Exception as e:
        raise ModExpError(error="Could not make png-file from image", exception_message=e.message)

    get_logger().info("Image was converted!")


# def send_event_to_webpage(event_dict):
#     """ Sends "event" to web-page of adjustment;
#         'event_dict' must be dictionary with format that is returned by  'create_event()'
#         if event type is "message", it sends it without changes,
#         if event type is "frame", it sends image part, converting it to png-file,
#         remain part (image data) is being sent without changes
#
#     :arg:  event_dict - event (message (for storage and web-page of adjustment) or frame with some data),
#            must be dictionary with format that is returned by  'create_event()'
#     :return: None
#     """
#     from experiment.conf import WEBPAGE_URI
#     data = None
#     files = None
#
#     if event_dict['type'] == 'frame':
#         make_png(event_dict['frame']['image_data']['image'])
#         files = {'file': open(FRAME_PNG_FILENAME, 'rb')}
#
#         del (event_dict['frame']['image_data']['image'])
#         # data = json.dumps(event_dict)
#         # WE DON'T SEND TO WEB-PAGE METADATA OF FRAME YET, IN FUTURE WE CAN ADD IT
#         # req_webpage = requests.post(WEBPAGE_URI, files=files, data= event_json)
#
#     elif event_dict['type'] == 'message':
#         data = json.dumps(event_dict)
#
#     get_logger().info('Sending to web-page of adjustment...')
#     try:
#         req_webpage = requests.post(WEBPAGE_URI, data=data, files=files)
#     except Exception as e:
#         raise ModExpError(error='Could not send to web-page of adjustment', exception_message=str(e))
#
#     get_logger().info(req_webpage.content)


def send_to_storage(storage_uri, data, files=None):
    """ Sends  to storage

    :arg:
    :return:
    """

    get_logger().info('Sending to storage...')
    try:
        storage_resp = requests.post(storage_uri, files=files, data=data)
    except Exception as e:
        get_logger().info(e.message)
        raise ModExpError(error='Problems with storage', exception_message='Could not send to storage' """e.message""")
        # IF UNCOMMENT   #exception_message,    OCCURS PROBLEMS WITH JSON.DUMPS(...) LATER

    get_logger().info(storage_resp.content)
    try:
        storage_resp_dict = json.loads(storage_resp.content)
    except (ValueError, TypeError):
        raise ModExpError(error='Problems with storage', exception_message='Storage\'s response is not JSON')

    if not ('result' in storage_resp_dict.keys()):
        raise ModExpError(error='Problems with storage',
                          exception_message="Storage\'s response has incorrect format (no 'result' key)")

    if storage_resp_dict['result'] != 'success':
        raise ModExpError(error='Problems with storage',
                          exception_message='Storage\'s response:  ' + str(storage_resp_dict['result']))


def send_message_to_storage_webpage(event_dict):
    """ Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
        'event_dict' must be dictionary with format that is returned by  'create_event()'

    :arg:  'event_dict' - event (message (for storage and web-page of adjustment) or frame with some data),
                          must be dictionary with format that is returned by  'create_event()'
    :return: success of sending, type is bool
    """
    # we don't do anything serious if we fail with sending to message
    event_json_for_storage = json.dumps(event_dict)
    try:
        send_to_storage(STORAGE_EXP_FINISH_URI, data=event_json_for_storage)
    except ModExpError as e:
        e.log(exp_id='')
    # finally:
    #     try:
    #         send_event_to_webpage(event_dict)
    #     except ModExpError as e:
    #         e.log(exp_id='')


def send_frame_to_storage_webpage(frame_metadata_event, image_numpy, send_to_webpage):
    """ Sends "event" to storage and if argument 'send_to_webpage is True, also to web-page of adjustment;
        'frame_dict' must be dictionary with format that is returned by  'create_event()'

    :arg:
    :return: success of sending, type is bool
    """
    s = StringIO()

    np.savez_compressed(s, frame_data=image_numpy)
    s.seek(0)
    data = {'data': json.dumps(frame_metadata_event)}
    files = {'file': s}
    send_to_storage(storage_uri=STORAGE_FRAMES_URI, data=data, files=files)

    # if send_to_webpage == True:
    #     frame_event = frame_metadata_event
    #     frame_event['frame']['image_data']['image'] = image_numpy
    #     try:
    #         send_event_to_webpage(frame_event)
    #     except ModExpError as e:
    #         e.log()
    # return success


def prepare_send_frame(raw_image_with_metadata, experiment, send_to_webpage=False):
    raw_image = raw_image_with_metadata['image_data']['raw_image']
    del raw_image_with_metadata['image_data']['raw_image']
    frame_metadata = raw_image_with_metadata

    try:
        get_logger().info("Image was red, preparing the image to send...")
        try:
            enc = PyTango.EncodedAttribute()
            image_numpy = enc.decode_gray16(raw_image)
            # image_numpy = numpy.zeros((10, 10))
        except Exception as e:
            raise ModExpError(error='Could not convert raw image to numpy.array', exception_message=e.message)

        if experiment:
            pass
            frame_metadata_event = create_event(event_type='frame', exp_id=experiment.exp_id, MoF=frame_metadata)
            send_frame_to_storage_webpage(frame_metadata_event=frame_metadata_event,
                                          image_numpy=image_numpy,
                                          send_to_webpage=send_to_webpage)
        else:
            make_png(image_numpy)

    except ModExpError as e:
        if experiment is not None:
            experiment.stop_exception = e
            experiment.to_be_stopped = True
        return False, e

    return True, None


# from experiment.tomograph import Tomograph


class Experiment:
    """ For storing information about experiment during time it runs """

    def __init__(self, tomograph, exp_param, FOSITW=5):
        # FOSITW - 'Frequency Of Sending Images To Webpage '

        # self.tomograph = Tomograph(1,2)
        self.tomograph = tomograph
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
        self.to_be_stopped = False
        self.stop_exception = None

        self.logger = get_logger()

    def get_and_send_frame(self, exposure, mode):

        getting_frame_message = 'Getting image, number: %d, mode: %s ...\n' % (self.frame_num, mode)
        self.logger.info(getting_frame_message)

        if mode == 'dark':
            raw_image_with_metadata = self.tomograph.get_frame(exposure=exposure, with_open_shutter=False,
                                                               from_experiment=True)
        else:
            raw_image_with_metadata = self.tomograph.get_frame(exposure=exposure, with_open_shutter=True,
                                                               from_experiment=True)
        # frame_dict = {  u'image_data':  {   'image': np.empty((10, 10)),    },  }

        raw_image_with_metadata['mode'] = mode
        raw_image_with_metadata['number'] = self.frame_num
        send_to_webpage = (self.frame_num % self.FOSITW == 0)
        self.frame_num += 1

        # prepare_send_frame(raw_image_with_metadata,self,send_to_webpage)
        thr = threading.Thread(target=prepare_send_frame, args=(raw_image_with_metadata, self, send_to_webpage))
        thr.start()

    def run(self):
        # Closing shutter to get DARK images
        self.to_be_stopped = False
        self.stop_exception = None
        self.tomograph.source_power_on(from_experiment=True)
        self.collect_dark_frames()
        self.collect_empty_frames()

        self.collect_data_frames()

        # self.collect_empty_frames()
        # self.collect_dark_frames()


        self.tomograph.source_power_off(from_experiment=True)
        return

    def collect_data_frames(self):
        self.logger.info('Going to get DATA images, step count is %d!\n' % self.DATA_step_count)
        initial_angle = self.tomograph.get_angle(from_experiment=True)
        self.logger.info('Initial angle is %.2f' % initial_angle)
        self.tomograph.set_exposure(self.DATA_exposure, from_experiment=True)
        # reference_angles = np.arange(0, 361, 45) + initial_angle

        # Rounding angles here, not in  check_and_prepare_exp_parameters(),
        # cause it will be more accurately this way

        data_angles = np.round((np.arange(0, self.DATA_step_count)) * self.DATA_angle_step + initial_angle, 2) % 360
        # exp_angles = np.hstack([reference_angles, data_angles])

        exp_angles = data_angles
        self.logger.info('Angles for DATA experiments: {}'.format(exp_angles))

        self.tomograph.move_back(from_experiment=True)
        self.tomograph.open_shutter(0, from_experiment=True)
        for current_angle in exp_angles:
            self.logger.info('Checking X-ray source state')
            self.check_source()
            self.logger.info('Starting with this angle, turning to new angle %.2f...' % current_angle)
            self.tomograph.set_angle(float(current_angle), from_experiment=True)
            # TODO: check angle after rotation
            self.logger.info('Getting DATA images: angle is %.2f' % current_angle)

            for j in range(0, self.DATA_count_per_step):
                self.get_and_send_frame(exposure=None, mode='data')

            self.logger.info('Finished with this angle, turning to new angle ...')
        self.tomograph.close_shutter(0, from_experiment=True)
        self.logger.info('Finished with DATA images!\n')

    def collect_empty_frames(self):
        self.tomograph.move_away(from_experiment=True)
        self.logger.info('Going to get EMPTY images!\n')
        self.tomograph.set_exposure(self.EMPTY_exposure, from_experiment=True)
        self.tomograph.open_shutter(0, from_experiment=True)
        for i in range(0, self.EMPTY_count):
            self.logger.info('Checking X-ray source state')
            self.check_source()
            self.get_and_send_frame(exposure=None, mode='empty')
        self.tomograph.close_shutter(0, from_experiment=True)
        self.tomograph.move_back(from_experiment=True)
        self.logger.info('Finished with EMPTY images!\n')

    def collect_dark_frames(self):
        self.tomograph.close_shutter(0, from_experiment=True)
        time.sleep(1.0)
        self.logger.info('Going to get DARK images!\n')
        self.tomograph.set_exposure(self.DARK_exposure, from_experiment=True)
        for i in range(0, self.DARK_count):
            self.get_and_send_frame(exposure=None, mode='dark')
        self.logger.info('Finished with DARK images!\n')

    def check_source(self):
        if self.tomograph.source_get_current(from_experiment=True) < 2 or self.tomograph.source_get_voltage(from_experiment=True) < 2:
            self.logger.info('X-ray source in wrong mode, try restart (off/on)')
            self.tomograph.source_power_off(from_experiment=True)
            time.sleep(5)
            self.tomograph.source_power_on(from_experiment=True)
            time.sleep(5)
        else:
            self.logger.info('X-ray source in good mode')