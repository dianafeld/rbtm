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

    def try_run():
        time_of_experiment_start = time.time()
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

        self.tomograph.handle_successful_stop(time_of_experiment_start)
        return
   
    def run():

        try:
            self.try_run()
        except Tomograph.ModExpError as e:
            e.log(self.exp_id)
            send_message_to_storage_webpage(e.to_event_dict(self.exp_id))
        else:
            pass

print 1