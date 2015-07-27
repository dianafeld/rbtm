#!/usr/bin/python

# CREATED 13.07.15 BY RUSTAM, FOR REFACTORING USING CLASS TOMOGRAPH
"""
Contains the main part of module "Experiment"
More exactly - some supporting functions and functions for receiving queries
"""


from flask import Flask
from flask import request
from flask import abort
from flask import send_file
from flask import make_response
import json
import PyTango
import requests
import threading
import csv
import numpy as np
import pylab as plt
import zlib
from class_tomograph import Tomograph
from class_tomograph import try_thrice_function
from class_tomograph import create_event
from class_tomograph import create_response
from class_tomograph import send_json_to_storage
from class_tomograph import send_event_to_storage_webpage

from conf import STORAGE_EXPERIMENT_URI
from conf import TOMO_ADDR

import logging
from StringIO import StringIO
#logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment.log')
app = Flask(__name__)





TOMOGRAPHS = (
        Tomograph(TOMO_ADDR),
)



#is being used in     check_and_prepare_advanced_experiment_command(command)
ADVANCED_EXPERIMENT_COMMANDS = ('open shutter', 'close shutter', 'reset current position', 'go to position', 'get frame')
FRAME_PNG_FILENAME = 'image.png'




def check_request(request_data):
    """ Checks body part of request, if it is not empty and has JSON string try to load it to python object

    :arg: 'request_data' - body part of request, type is undetermined in common case
    :return: list of 3 elements,
             1 - success of finding JSON string and loading it to python object, type is bool
             2 - JSON-string loaded to python object, type is undetermined, if 'success' is True; None if False
             3 - if 'success' is False, function returns prepared response for web-page of adjustment,
                 type is json-string with format that is returned by  'create_response()';
                 if 'success' is True, empty string
    """
    print('Checking request...')
    if not request_data:
        print('Request is empty!')
        return False, None, create_response(success= False, error= 'Request is empty')

    print('Request is NOT empty! Checking request\'s JSON...')
    try:
        request_data_dict = json.loads(request_data)
    except TypeError:
        print('Request has NOT JSON data!')
        return False, None, create_response(success= False, error= 'Request has not JSON data')
    else:
        print('Request has JSON data!')
        return True, request_data_dict, ''


"""
def send_frame_storage(frame_dict):
    frame_json = json.dumps(frame_dict)
    files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}

    r = requests.post(STORAGE_URI, files=files)
    r.text
"""




# in almost every function below we have argument 'tomo_num' - number of tomograph in TOMOGRAPHS list

# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-on', methods=['GET'])
def source_power_on(tomo_num):
    print('\n\nREQUEST: SOURCE/POWER ON')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0


    print('Checking tomograph...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.ping)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not reach tomograph')

    print('Powering on source...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOn)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not power on source')

    print('Success!')
    return create_response(True)

# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-off', methods=['GET'])
def source_power_off(tomo_num):
    print('\n\nREQUEST: SOURCE/POWER OFF')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    print('Powering off source...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOff)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not power off source')

    print('Success!')
    return create_response(True)


#---------------------------------------------------------#
#    Functions for adjustment of tomograph
#---------------------------------------------------------#


@app.route('/tomograph/<int:tomo_num>/source/set-voltage', methods=['POST'])
def source_set_voltage(tomo_num):
    print('\n\nREQUEST: SOURCE/SET VOLTAGE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        print(error)
        return create_response(success= False, error= error)

    success, new_voltage, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    print('Checking format...')
    if type(new_voltage) is not float:
        print('Incorrect format! Voltage type must be float, but it is ' + str(type(new_voltage)))
        return create_response(success= False, error= 'Incorrect format: type must be float')


    # TO DELETE THIS LATER
    print('Format is correct, new voltage value is %.1f...' % (new_voltage))
    if new_voltage < 2 or 60 < new_voltage:
        print('Voltage must have value from 2 to 60!')
        return create_response(success= False, error= 'Voltage must have value from 2 to 60')

    print('Parameters are normal, setting new voltage...')
    success, set_voltage, exception_message = tomograph.try_thrice_change_attr("xraysource_voltage", new_voltage)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not set voltage')

    print('Success!')
    return create_response(success= True)

@app.route('/tomograph/<int:tomo_num>/source/set-current', methods=['POST'])
def source_set_current(tomo_num):
    print('\n\nREQUEST: SOURCE/SET CURRENT')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        print(error)
        return create_response(success= False, error= error)

    success, current, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    print('Checking format...')
    if type(current) is not float:
        print('Incorrect format! Current type must be float, but it is ' + str(type(current)))
        return create_response(success= False, error= 'Incorrect format: type must be float')


    # TO DELETE THIS LATER
    print('Format is correct, new current value is %.1f...' % (current))
    if current < 2 or 80 < current:
        print('Current must have value from 2 to 60!')
        return create_response(success= False, error= 'Current must have value from 2 to 80')

    print('Parameters are normal, setting new current...')
    success, set_current, exception_message = tomograph.try_thrice_change_attr("xraysource_current", current)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not set current')

    print('Success!')
    return create_response(success= True)



@app.route('/tomograph/<int:tomo_num>/source/get-voltage', methods=['GET'])
def source_get_voltage(tomo_num):
    print('\n\nREQUEST: SOURCE/GET VOLTAGE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        print(error)
        return create_response(success= False, error= error)


    print('Going to get voltage...')
    success, voltage_attr, exception_message = tomograph.try_thrice_read_attr("xraysource_voltage")
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not get voltage')

    voltage = voltage_attr.value
    print("Voltage is %.2f" % voltage)
    return create_response(success= True, result= voltage)

@app.route('/tomograph/<int:tomo_num>/source/get-current', methods=['GET'])
def source_get_current(tomo_num):
    print('\n\nREQUEST: SOURCE/GET CURRENT')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        print(error)
        return create_response(success= False, error= error)


    print('Going to get current...')
    success, current_attr, exception_message = tomograph.try_thrice_read_attr("xraysource_current")
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not get current')

    current = current_attr.value
    print("Current is %.2f" % current)
    return create_response(success= True, result= current)




@app.route('/tomograph/<int:tomo_num>/shutter/open/<int:time>', methods=['GET'])
def shutter_open(tomo_num, time):
    print('\n\nREQUEST: SHUTTER/OPEN')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    return tomograph.open_shutter(time)

@app.route('/tomograph/<int:tomo_num>/shutter/close/<int:time>', methods=['GET'])
def shutter_close(tomo_num, time):
    print('\n\nREQUEST: SHUTTER/CLOSE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    return tomograph.close_shutter(time)



@app.route('/tomograph/<int:tomo_num>/motor/set-horizontal-position', methods=['POST'])
def motor_set_horizontal_position(tomo_num):
    print('\n\nREQUEST: MOTOR/SET HORIZONTAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_x(new_pos)

@app.route('/tomograph/<int:tomo_num>/motor/set-vertical-position', methods=['POST'])
def motor_set_vertical_position(tomo_num):
    print('\n\nREQUEST: MOTOR/SET VERTICAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_y(new_pos)

@app.route('/tomograph/<int:tomo_num>/motor/set-angle-position', methods=['POST'])
def motor_set_angle_position(tomo_num):
    print('\n\nREQUEST: MOTOR/SET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_angle(new_pos)



@app.route('/tomograph/<int:tomo_num>/motor/get-horizontal-position', methods=['GET'])
def motor_get_horizontal_position(tomo_num):
    print('\n\nREQUEST: MOTOR/GET HORIZONTAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_x()

@app.route('/tomograph/<int:tomo_num>/motor/get-vertical-position', methods=['GET'])
def motor_get_vertical_position(tomo_num):
    print('\n\nREQUEST: MOTOR/GET VERTICAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_y()

@app.route('/tomograph/<int:tomo_num>/motor/get-angle-position', methods=['GET'])
def motor_get_angle_position(tomo_num):
    print('\n\nREQUEST: MOTOR/GET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_angle()



@app.route('/tomograph/<int:tomo_num>/motor/move-away', methods=['GET'])
def motor_move_away(tomo_num):
    print('\n\nREQUEST: MOTOR/MOVE AWAY')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.move_away()

@app.route('/tomograph/<int:tomo_num>/motor/move-back', methods=['GET'])
def motor_move_back(tomo_num):
    print('\n\nREQUEST: MOTOR/MOVE BACK')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.move_back()



@app.route('/tomograph/<int:tomo_num>/motor/reset-angle-position', methods=['GET'])
def motor_reset_angle_position(tomo_num):
    print('\n\nREQUEST: MOTOR/RESET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.reset_angle()



@app.route('/tomograph/<int:tomo_num>/detector/get-frame', methods=['POST'])
def detector_get_frame(tomo_num):
    print('\n\nREQUEST: DETECTOR/GET FRAME')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, exposure, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.get_frame(exposure)



#---------------------------------------------------------#
#    Functions for running experiment
#---------------------------------------------------------#


def stop_experiment_because_someone(exp_id):
    exp_stop_event = create_event('message', exp_id, 'Experiment was stopped by someone')
    if send_event_to_storage_webpage(exp_stop_event) == False:
        return
    print('\nEXPERIMENT IS STOPPED BY SOMEONE!!!\n')
    return



def check_and_prepare_advanced_experiment_command(command):
    # Checking parameters
    if not (type(command) is dict):
        return False, 'Incorrect format in '
    if not (('type' in command.keys()) and ('args' in command.keys())):
        return False, 'Incorrect format in '
    if not (command['type'] in ADVANCED_EXPERIMENT_COMMANDS):
        return False, 'Incorrect format in '
    if (command['type'] == 'open shutter') or (command['type'] == 'close shutter'):
        if command['args'] < 0:
            return False, 'Bad parameters in '
    if command['type'] == 'get frame':
        if command['args'] <= 0:
            return False, 'Bad parameters in '

    # Preparing parameters for tomograph
    # Tomograph takes values multiplied by 10 and rounded
        command['args'] *= 10
        command['args'] = round(command['args'])
    elif command['type'] == 'go to position':
        # Tomograph takes values multiplied by 10 and rounded
        command['args'][2] *= 10
        command['args'][2] = round(command['args'][2])
        command['args'][2] %= 3600
    return True, ''
# NEED TO EDIT
def check_and_prepare_exp_parameters(exp_param):
    if not (('experiment id' in exp_param.keys()) and ('advanced' in exp_param.keys())):
        return False, 'Incorrect format of keywords'
    if not ((type(exp_param['experiment id']) is unicode) and (type(exp_param['advanced']) is bool)):
        return False, 'Incorrect format: incorrect types'
    if exp_param['advanced']:
        if not ('instruction' in exp_param.keys()):
            return False, 'Incorrect format'
        cmd_num = 0
        for command in exp_param['instruction']:
            cmd_num += 1
            cmd_is_normal, error = check_and_prepare_advanced_experiment_command(command)
            if not cmd_is_normal:
                return False, error + str(cmd_num) + ' command'
        return True, ''
    else:
        if not (('DARK' in exp_param.keys()) and ('EMPTY' in exp_param.keys()) and ('DATA' in exp_param.keys())):
            return False, 'Incorrect format3'
        if not ((type(exp_param['DARK']) is dict) and(type(exp_param['EMPTY']) is dict) and(type(exp_param['DATA']) is dict)):
            return False, 'Incorrect format4'

        if not ('count' in exp_param['DARK'].keys()) and ('exposure' in exp_param['DARK'].keys()):
            return False, 'Incorrect format in \'DARK\' parameters'
        if not ((type(exp_param['DARK']['count']) is int) and(type(exp_param['DARK']['exposure']) is float)):
            return False, 'Incorrect format in \'DARK\' parameters'

        if not ('count' in exp_param['EMPTY'].keys()) and ('exposure' in exp_param['EMPTY'].keys()):
            return False, 'Incorrect format in \'EMPTY\' parameters'
        if not ((type(exp_param['EMPTY']['count']) is int) and(type(exp_param['EMPTY']['exposure']) is float)):
            return False, 'Incorrect format in \'EMPTY\' parameters'

        if not ('step count' in exp_param['DATA'].keys()) and ('exposure' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'
        if not ((type(exp_param['DATA']['step count']) is int) and(type(exp_param['DATA']['exposure']) is float)):
            return False, 'Incorrect format in \'DATA\' parameters'

        if not ('angle step' in exp_param['DATA'].keys()) and ('count per step' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'
        if not ((type(exp_param['DATA']['angle step']) is float) and(type(exp_param['DATA']['count per step']) is int)):
            return False, 'Incorrect format in \'DATA\' parameters'


        # TO DELETE AFTER WEB-PAGE OF ADJUSTMENT START CHECK PARAMETERS
        if exp_param['DARK']['exposure'] < 0.1:
            return False, 'Bad parameters in \'DARK\' parameters'
        if exp_param['EMPTY']['exposure'] < 0.1:
            return False, 'Bad parameters in \'EMPTY\' parameters'
        if exp_param['DATA']['exposure'] < 0.1:
            return False, 'Bad parameters in \'DATA\' parameters'


        # we don't multiply and round  exp_param['DATA']['angle step'] here, we will do it during experiment,
        # because it will be more accurate this way
        return True, ''


def loop_of_get_send_frames(tomograph, exp_id, count, exposure, frame_num, getting_frame_message, mode):
    for i in range(0, count):
        if tomograph.experiment_is_running == False:
            stop_experiment_because_someone(exp_id)
            return False, frame_num

        print(getting_frame_message % (i))
        success, frame_dict = tomograph.get_frame(exposure, exp_id)
        if not success:
            return False, frame_num

        frame_dict['mode'] = mode
        frame_dict['number'] = frame_num
        frame_num += 1
        frame_with_data = create_event('frame', exp_id, frame_dict)
        if send_event_to_storage_webpage(frame_with_data) == False:
            return False, frame_num
    return True, frame_num



def carry_out_simple_experiment(tomograph, exp_param):
    exp_id = exp_param['experiment id']
    # Closing shutter to get DARK images
    if tomograph.close_shutter(0, exp_id) == False:
        return

    frame_num = 0
    print('Going to get DARK images!\n')
    success, frame_num = loop_of_get_send_frames(tomograph, exp_id, exp_param['DARK']['count'], exp_param['DARK']['exposure'],
                                                 frame_num, getting_frame_message='Getting DARK image %d from tomograph...', mode="dark")
    if not success:
        return
    print('Finished with DARK images!\n')

    if tomograph.open_shutter(0, exp_id) == False:
        return
    if tomograph.move_away(exp_id) == False:
        return

    print('Going to get EMPTY images!\n')
    success, frame_num = loop_of_get_send_frames(tomograph, exp_id, exp_param['EMPTY']['count'], exp_param['EMPTY']['exposure'],
                                                 frame_num, getting_frame_message= 'Getting EMPTY image %d from tomograph...', mode="empty")
    if not success:
        return
    print('Finished with EMPTY images!\n')

    if tomograph.move_back(exp_id) == False:
        return

    success, initial_angle = tomograph.get_angle(exp_id)
    if not success:
        return
    print('Initial angle is %.2f' % initial_angle)

    if tomograph.reset_angle(exp_id) == False:
        return

    print('Going to get DATA images, step count is %d!\n' % (exp_param['DATA']['step count']))
    angle_step = exp_param['DATA']['angle step']
    for i in range(0, exp_param['DATA']['step count']):
        current_angle = (round( (i*angle_step) + initial_angle,  2)) % 360
        print('Getting DATA images: angle is %.2f' % current_angle)

        success, frame_num = loop_of_get_send_frames(tomograph, exp_id, exp_param['DATA']['count per step'], exp_param['DATA']['exposure'],
                                                     frame_num, getting_frame_message= 'Getting DATA image %d from tomograph...', mode="data")
        if not success:
            return
        # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
        new_angle = (round( (i + 1)*angle_step + initial_angle ,  2)) % 360
        print('Finished with this angle, turning to new angle %.2f...' % (new_angle))
        if tomograph.set_angle(new_angle, exp_id) == False:
            return
    print('Finished with DATA images!\n')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_event_to_storage_webpage(exp_finish_message) == False:
        return
    tomograph.experiment_is_running = False
    print('Experiment is done successfully!')
    return
# NEED TO EDIT(GENERALLY)
def carry_out_advanced_experiment(tomo_num, exp_param):
    tomograph = TOMOGRAPHS[tomo_num]
    exp_id = exp_param['experiment id']
    cmd_num = 0
    for command in exp_param['instruction']:
        if tomograph.experiment_is_running == False:
            return stop_experiment_because_someone(exp_id)
        cmd_num += 1
        print('Executing command %d:' % cmd_num)

        if command['type'] == 'open shutter':
            print('Opening shutter...')

            # NEED TO EDIT(USING TOMOGRAPH CLASS)
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return tomograph.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not open shutter')
            print('Success!')

        elif command['type'] == 'close shutter':
            print('Closing shutter...')

            # NEED TO EDIT(USING TOMOGRAPH CLASS)
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return tomograph.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not close shutter')
            print('Success!')

        elif command['type'] == 'reset current position':
            print('Resetting current position...')

            # NEED TO EDIT(USING TOMOGRAPH CLASS)
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].ResetCurrentPosition, command['args'])
            if success == False:
                return tomograph.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not reset current position')
            print('Success!')

        elif command['type'] == 'go to position':
            x = str(command['args'][0])
            y = str(command['args'][1])
            angle = str(command['args'][2]/10)
            print('Changing position to:  x = ' + x + ', y = ' + y + ', angle = ' + angle + '...')

            # NEED TO EDIT(USING TOMOGRAPH CLASS)
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].GotoPosition, command['args'])
            if success == False:
                return tomograph.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not go to position: '
                                                                     'x = ' + x + ', y = ' + y + ', angle = ' + angle)
            print('Success!')

        elif command['type'] == 'get frame':
            print('Getting image...')

            # NEED TO EDIT(USING TOMOGRAPH CLASS)
            success, frame_json, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].GetFrame, command['args'])
            if success == False:
                return tomograph.handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not get frame')
            print('  Got!\nSending frame to storage and web page of adjustment...')
            frame_dict = json.loads(frame_json)
            frame_with_data = create_event('frame', exp_id, frame_dict)
            if send_event_to_storage_webpage(frame_with_data) == False:
                return
            print('Success!')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_event_to_storage_webpage(exp_finish_message) == False:
        return
    tomograph.experiment_is_running = False
    print('Experiment is done successfully!')
    return




@app.route('/tomograph/<int:tomo_num>/experiment/start', methods=['POST'])
def experiment_start(tomo_num):
    print('\n\nREQUEST: EXPERIMENT/START')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        print(error)
        return create_response(success= False, error= error)

    success, data, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    print('Checking generous format...')
    if not (('experiment parameters' in data.keys()) and ('experiment id' in data.keys())):
        print('Incorrect format of keywords!')
        return create_response(success= False, error= 'Incorrect format of keywords')

    if not ((type(data['experiment parameters']) is dict) and (type(data['experiment id']) is unicode)):
        print('Incorrect format of types!')
        return create_response(success= False, error= 'Incorrect format: incorrect types')

    print('Generous format is normal!')
    exp_param = data['experiment parameters']
    exp_id = data['experiment id']
    exp_param['experiment id'] = exp_id

    print('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        print(error)
        return create_response(success, error)

    print('Parameters are normal!')
    print('Powering on tomograph...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOn)
    if success == False:
        return create_response(success= False, exception_message= exception_message, error= 'Could not power on source')

    print('Success!')
    print('Sending to storage leading to prepare...')
    success, exception_message = send_json_to_storage(request.data, storage_url= STORAGE_EXPERIMENT_URI)
    if not success:
        return create_response(success= False, exception_message= exception_message, error= 'Problems with storage')

    print('Experiment begins!')
    tomograph.experiment_is_running = True
    if exp_param['advanced']:
        thr = threading.Thread(target = carry_out_advanced_experiment, args = (tomograph, exp_param))
    else:
        thr = threading.Thread(target = carry_out_simple_experiment, args = (tomograph, exp_param))
    thr.start()

    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/experiment/stop', methods=['GET'])
def experiment_stop(tomo_num):
    print('\n\nREQUEST: EXPERIMENT/STOP')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    tomograph.experiment_is_running = False
    return create_response(True)


"""
@app.before_request
def limit_remote_addr():
    if request.remote_addr != '10.20.30.40':
        abort(403)  # Forbidden
"""

@app.errorhandler(400)
def incorrect_format(error):
    return make_response(create_response(success= False, error= 'Incorrect Format'), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(create_response(success= False, error= 'Not Found'), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(create_response(success= False, error= 'Internal Server Error'), 500)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5001)








