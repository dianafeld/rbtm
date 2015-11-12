#!/usr/bin/python

"""
created for refactoring using class 'Message'

Contains the main part of module "Experiment"
More exactly - some supporting functions and functions for receiving queries
"""

import json
import threading
import time

from flask import request
from flask import Response
from flask import make_response

from tomograph import Tomograph
from tomograph import try_thrice_function
from tomograph import create_event
from tomograph import create_response
from tomograph import send_to_storage
from conf import STORAGE_FRAMES_URI
from conf import STORAGE_EXP_START_URI
from conf import TOMO_ADDR
from conf import MAX_EXPERIMENT_TIME


# logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment.log')
from experiment import app

logger = app.logger

TOMOGRAPHS = (
    Tomograph(TOMO_ADDR + "/tomo/tomograph/1", TOMO_ADDR + "/tomo/detector/1"),
)


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
    logger.info('Checking request...')
    if not request_data:
        logger.info('Request is empty!')
        return False, None, create_response(success=False, error='Request is empty')

    logger.info('Request is NOT empty! Checking request\'s JSON...')
    try:
        request_data_dict = json.loads(request_data)
    except TypeError:
        logger.info('Request has NOT JSON data!')
        return False, None, create_response(success=False, error='Request has not JSON data')
    else:
        logger.info('Request has JSON data!')
        return True, request_data_dict, ''


# in almost every function below we have argument 'tomo_num' - number of tomograph in TOMOGRAPHS list

@app.route('/tomograph/<int:tomo_num>/state', methods=['GET'])
def check_state(tomo_num):
    logger.info('\n\nREQUEST: CHECK STATE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0


    logger.info('Checking tomograph...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.ping)
    if not success:
        logger.info("Tomograph is unavailable")
        logger.info(exception_message)
        return create_response(True, exception_message, result="unavailable")

    if tomograph.experiment_is_running:
        logger.info("Tomograph is available; experiment IS running")
        return create_response(success=True, result="experiment")
    else:
        logger.info("Tomograph is available; experiment is NOT running")
        return create_response(success=True, result="ready")


# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-on', methods=['GET'])
def source_power_on(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/POWER ON')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Powering on source...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOn)
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not power on source')

    logger.info('Source was powered ON!')
    return create_response(True)


# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-off', methods=['GET'])
def source_power_off(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/POWER OFF')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Powering off source...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOff)
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not power off source')

    logger.info('Source was powered OFF!')
    return create_response(True)


# ---------------------------------------------------------#
# Functions for adjustment of tomograph
#---------------------------------------------------------#


@app.route('/tomograph/<int:tomo_num>/source/set-voltage', methods=['POST'])
def source_set_voltage(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/SET VOLTAGE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Going to set voltage on source...')
    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        logger.info(error)
        return create_response(success=False, error=error)

    success, new_voltage, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logger.info('Checking format...')
    if type(new_voltage) is not float:
        logger.info('Incorrect format! Voltage type must be float, but it is ' + str(type(new_voltage)))
        return create_response(success=False, error='Incorrect format: type must be float')


    # TO DELETE THIS LATER
    logger.info('Format is correct, new voltage value is %.1f...' % (new_voltage))
    if new_voltage < 2 or 60 < new_voltage:
        logger.info('Voltage must have value from 2 to 60!')
        return create_response(success=False, error='Voltage must have value from 2 to 60')

    logger.info('Parameters are normal, setting new voltage...')
    success, set_voltage, exception_message = tomograph.try_thrice_change_attr("xraysource_voltage", new_voltage)
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not set voltage')

    logger.info('New value of voltage was set!')
    return create_response(success=True)


@app.route('/tomograph/<int:tomo_num>/source/set-current', methods=['POST'])
def source_set_current(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/SET CURRENT')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Going to set current on source...')
    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        logger.info(error)
        return create_response(success=False, error=error)

    success, current, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logger.info('Checking format...')
    if type(current) is not float:
        logger.info('Incorrect format! Current type must be float, but it is ' + str(type(current)))
        return create_response(success=False, error='Incorrect format: type must be float')


    # TO DELETE THIS LATER
    logger.info('Format is correct, new current value is %.1f...' % (current))
    if current < 2 or 80 < current:
        logger.info('Current must have value from 2 to 60!')
        return create_response(success=False, error='Current must have value from 2 to 80')

    logger.info('Parameters are normal, setting new current...')
    success, set_current, exception_message = tomograph.try_thrice_change_attr("xraysource_current", current)
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not set current')

    logger.info('New value of current was set!')
    return create_response(success=True)


@app.route('/tomograph/<int:tomo_num>/source/get-voltage', methods=['GET'])
def source_get_voltage(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/GET VOLTAGE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Going to get voltage...')
    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        logger.info(error)
        return create_response(success=False, error=error)

    success, voltage_attr, exception_message = tomograph.try_thrice_read_attr("xraysource_voltage")
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not get voltage')

    voltage = voltage_attr.value
    logger.info("Voltage is %.2f" % voltage)
    return create_response(success=True, result=voltage)


@app.route('/tomograph/<int:tomo_num>/source/get-current', methods=['GET'])
def source_get_current(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/GET CURRENT')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    logger.info('Going to get current...')
    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        logger.info(error)
        return create_response(success=False, error=error)

    success, current_attr, exception_message = tomograph.try_thrice_read_attr("xraysource_current")
    if success == False:
        logger.info(exception_message)
        return create_response(success, exception_message, error='Could not get current')

    current = current_attr.value
    logger.info("Current is %.2f" % current)
    return create_response(success=True, result=current)


@app.route('/tomograph/<int:tomo_num>/shutter/open/<int:time>', methods=['GET'])
def shutter_open(tomo_num, time):
    logger.info('\n\nREQUEST: SHUTTER/OPEN')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    return tomograph.open_shutter(time)


@app.route('/tomograph/<int:tomo_num>/shutter/state', methods=['GET'])
def shutter_state(tomo_num):
    logger.info('\n\nREQUEST: SHUTTER/STATE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    return tomograph.shutter_state(time)


@app.route('/tomograph/<int:tomo_num>/shutter/close/<int:time>', methods=['GET'])
def shutter_close(tomo_num, time):
    logger.info('\n\nREQUEST: SHUTTER/CLOSE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    return tomograph.close_shutter(time)


@app.route('/tomograph/<int:tomo_num>/motor/set-horizontal-position', methods=['POST'])
def motor_set_horizontal_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET HORIZONTAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_x(new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/set-vertical-position', methods=['POST'])
def motor_set_vertical_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET VERTICAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_y(new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/set-angle-position', methods=['POST'])
def motor_set_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.set_angle(new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/get-horizontal-position', methods=['GET'])
def motor_get_horizontal_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET HORIZONTAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_x()


@app.route('/tomograph/<int:tomo_num>/motor/get-vertical-position', methods=['GET'])
def motor_get_vertical_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET VERTICAL POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_y()


@app.route('/tomograph/<int:tomo_num>/motor/get-angle-position', methods=['GET'])
def motor_get_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.get_angle()


@app.route('/tomograph/<int:tomo_num>/motor/move-away', methods=['GET'])
def motor_move_away(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/MOVE AWAY')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.move_away()


@app.route('/tomograph/<int:tomo_num>/motor/move-back', methods=['GET'])
def motor_move_back(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/MOVE BACK')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.move_back()


@app.route('/tomograph/<int:tomo_num>/motor/reset-angle-position', methods=['GET'])
def motor_reset_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/RESET ANGLE POSITION')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    return tomograph.reset_to_zero_angle()


@app.route('/tomograph/<int:tomo_num>/detector/get-frame', methods=['POST'])
def detector_get_frame(tomo_num):
    logger.info('\n\nREQUEST: DETECTOR/GET FRAME')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    success, exposure, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return tomograph.get_frame(exposure)


#---------------------------------------------------------#
#    Functions for running experiment
#---------------------------------------------------------#

# NEED TO EDIT
def check_and_prepare_exp_parameters(exp_param):
    if not (('exp_id' in exp_param.keys()) and ('advanced' in exp_param.keys())):
        return False, 'Incorrect format of keywords'
    if not ((type(exp_param['exp_id']) is unicode) and (type(exp_param['advanced']) is bool)):
        return False, 'Incorrect format: incorrect types'
    if exp_param['advanced']:

        if not ('instruction' in exp_param.keys()):
            return False, 'Incorrect format'
        if not (type(exp_param['instruction']) is unicode):
            return False, 'Type of instruction must be unicode'
        if exp_param['instruction'].find(".__") != -1:
            return False, 'Unacceptable instruction, there must not be substring ".__"'
        if exp_param['instruction'].find("t_0M_o_9_r_") != -1:
            return False, 'Unacceptable instruction, there must not be substring "t_0M_o_9_r_"'
    else:
        if not (('DARK' in exp_param.keys()) and ('EMPTY' in exp_param.keys()) and ('DATA' in exp_param.keys())):
            return False, 'Incorrect format3'
        if not ((type(exp_param['DARK']) is dict) and (type(exp_param['EMPTY']) is dict) and (
                    type(exp_param['DATA']) is dict)):
            return False, 'Incorrect format4'

        if not ('count' in exp_param['DARK'].keys()) and ('exposure' in exp_param['DARK'].keys()):
            return False, 'Incorrect format in \'DARK\' parameters'
        if not ((type(exp_param['DARK']['count']) is int) and (type(exp_param['DARK']['exposure']) is float)):
            return False, 'Incorrect format in \'DARK\' parameters'

        if not ('count' in exp_param['EMPTY'].keys()) and ('exposure' in exp_param['EMPTY'].keys()):
            return False, 'Incorrect format in \'EMPTY\' parameters'
        if not ((type(exp_param['EMPTY']['count']) is int) and (type(exp_param['EMPTY']['exposure']) is float)):
            return False, 'Incorrect format in \'EMPTY\' parameters'

        if not ('step count' in exp_param['DATA'].keys()) and ('exposure' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'
        if not ((type(exp_param['DATA']['step count']) is int) and (type(exp_param['DATA']['exposure']) is float)):
            return False, 'Incorrect format in \'DATA\' parameters'

        if not ('angle step' in exp_param['DATA'].keys()) and ('count per step' in exp_param['DATA'].keys()):
            return False, 'Incorrect format in \'DATA\' parameters'
        if not (
                    (type(exp_param['DATA']['angle step']) is float) and (
                            type(exp_param['DATA']['count per step']) is int)):
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


def loop_of_get_send_frames(tomograph, count, exposure, getting_frame_message, mode):
    for i in range(0, count):

        logger.info(getting_frame_message % (i))
        success, frame_dict = tomograph.get_frame(exposure, send_to_webpage=True, exp_is_advanced=False)
        if not success:
            return False

        frame_dict['mode'] = mode
        frame_with_data = create_event('frame', tomograph.exp_id, frame_dict)
        if tomograph.send_event_to_storage_webpage(STORAGE_FRAMES_URI, frame_with_data) == False:
            return False
    return True


def carry_out_simple_experiment(tomograph, exp_param):
    time_of_experiment_start = time.time()
    exp_id = exp_param['exp_id']
    # Closing shutter to get DARK images
    if tomograph.close_shutter(0, exp_is_advanced=False) == False:
        return

    logger.info('Going to get DARK images!\n')
    if loop_of_get_send_frames(tomograph, exp_param['DARK']['count'], exp_param['DARK']['exposure'],
                               getting_frame_message='Getting DARK image %d from tomograph...', mode="dark") == False:
        return
    logger.info('Finished with DARK images!\n')

    if tomograph.open_shutter(0, exp_is_advanced=False) == False:
        return
    if tomograph.move_away(exp_is_advanced=False) == False:
        return

    logger.info('Going to get EMPTY images!\n')
    if loop_of_get_send_frames(tomograph, exp_param['EMPTY']['count'], exp_param['EMPTY']['exposure'],
                               getting_frame_message='Getting EMPTY image %d from tomograph...', mode="empty") == False:
        return
    logger.info('Finished with EMPTY images!\n')

    if tomograph.move_back(exp_is_advanced=False) == False:
        return

    success, initial_angle = tomograph.get_angle(exp_is_advanced=False)
    if not success:
        return
    logger.info('Initial angle is %.2f' % initial_angle)

    logger.info('Going to get DATA images, step count is %d!\n' % (exp_param['DATA']['step count']))
    angle_step = exp_param['DATA']['angle step']
    for i in range(0, exp_param['DATA']['step count']):
        current_angle = (round((i * angle_step) + initial_angle, 2)) % 360
        logger.info('Getting DATA images: angle is %.2f' % current_angle)

        if loop_of_get_send_frames(tomograph, exp_param['DATA']['count per step'], exp_param['DATA']['exposure'],
                                   getting_frame_message='Getting DATA image %d from tomograph...',
                                   mode="data") == False:
            return
        # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
        new_angle = (round((i + 1) * angle_step + initial_angle, 2)) % 360
        logger.info('Finished with this angle, turning to new angle %.2f...' % (new_angle))
        if tomograph.set_angle(new_angle, exp_is_advanced=False) == False:
            return
    logger.info('Finished with DATA images!\n')

    tomograph.handle_successful_stop(time_of_experiment_start)
    return


def time_counter_of_experiment(tomograph, exp_id, exp_time=MAX_EXPERIMENT_TIME):
    time.sleep(exp_time)
    if (tomograph.experiment_is_running and tomograph.exp_id == exp_id):
        logger.info("\nEXPERIMENT TAKES TOO LONG, GOING TO STOP IT!\n")
        tomograph.experiment_is_running = False
        tomograph.exp_stop_reason = "# MODULE EXPERIMENT: EXPERIMENT TAKES TOO LONG #"
    return


def carry_out_advanced_experiment(tomograph, exp_param):
    exp_id = exp_param['exp_id']
    exp_code_string = exp_param['instruction']
    # 't_0M_o_9_r_' - strange name of object, because using user of this "word" in instruction is unlikely
    exp_code_string = exp_code_string.replace("open_shutter", "t_0M_o_9_r_.open_shutter")
    exp_code_string = exp_code_string.replace("close_shutter", "t_0M_o_9_r_.close_shutter")
    exp_code_string = exp_code_string.replace("set_x", "t_0M_o_9_r_.set_x")
    exp_code_string = exp_code_string.replace("set_y", "t_0M_o_9_r_.set_y")
    # rename method 'reset_angle' to 'reset_to_zero_angle' because 'set_angle' is substring of 'reset_angle'
    exp_code_string = exp_code_string.replace("reset_angle", "t_0M_o_9_r_.reset_to_zero_angle")
    exp_code_string = exp_code_string.replace("set_angle", "t_0M_o_9_r_.set_angle")
    exp_code_string = exp_code_string.replace("get_x", "t_0M_o_9_r_.get_x")
    exp_code_string = exp_code_string.replace("get_y", "t_0M_o_9_r_.get_y")
    exp_code_string = exp_code_string.replace("get_angle", "t_0M_o_9_r_.get_angle")
    exp_code_string = exp_code_string.replace("move_away", "t_0M_o_9_r_.move_away")
    exp_code_string = exp_code_string.replace("move_back", "t_0M_o_9_r_.move_back")
    exp_code_string = exp_code_string.replace("get_frame", "t_0M_o_9_r_.get_frame")
    exp_code_string = exp_code_string.replace("send_frame", "t_0M_o_9_r_.se")
    print
    exp_code_string
    time_of_experiment_start = time.time()
    thr = threading.Thread(target=time_counter_of_experiment, args=(tomograph, exp_id))
    thr.start()
    try:
        exec (exp_code_string, {'__builtins__': {}, 't_0M_o_9_r_': tomograph})
    except tomograph.ExpStopException as e:
        return
    except SyntaxError as e:
        print
        repr(e)
        tomograph.handle_emergency_stop(exp_is_advanced=False, exp_id=exp_id,
                                        error="Syntax of experiment instruction is NOT correct",
                                        exception_message=e.message)
        return

    except Exception as e:
        print
        repr(e)
        tomograph.handle_emergency_stop(exp_is_advanced=False, exp_id=exp_id, error="Exception during experiment",
                                        exception_message=e.message)
        return

    tomograph.handle_successful_stop(time_of_experiment_start)
    return


# NEED TO EDIT (COMMENT BEFORE POWERING ON SOURCE)
@app.route('/tomograph/<int:tomo_num>/experiment/start', methods=['POST'])
def experiment_start(tomo_num):
    logger.info('\n\nREQUEST: EXPERIMENT/START')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    if tomograph.experiment_is_running:
        error = 'On this tomograph experiment is running'
        logger.info(error)
        return create_response(success=False, error=error)

    success, data, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logger.info('Checking generous format...')
    if not (('experiment parameters' in data.keys()) and ('exp_id' in data.keys())):
        logger.info('Incorrect format of keywords!')
        return create_response(success=False, error='Incorrect format of keywords')

    if not ((type(data['experiment parameters']) is dict) and (type(data['exp_id']) is unicode)):
        logger.info('Incorrect format of types!')
        return create_response(success=False, error='Incorrect format: incorrect types')

    logger.info('Generous format is normal!')
    exp_param = data['experiment parameters']
    exp_id = data['exp_id']
    exp_param['exp_id'] = exp_id

    logger.info('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        logger.info(error)
        return create_response(success, error)

    logger.info('Parameters are normal!')
    logger.info('Powering on tomograph...')
    success, useless, exception_message = try_thrice_function(tomograph.tomograph_proxy.PowerOn)
    if success == False:
        return create_response(success=False, exception_message=exception_message, error='Could not power on source')

    # NEED TO CHANGE MAYBE, TO ADD CHECKING STATE
    logger.info('Was powered on!')
    logger.info('Sending to storage leading to prepare...')
    success, exception_message = send_to_storage(STORAGE_EXP_START_URI, data=request.data)
    if not success:
        return create_response(success=False, exception_message=exception_message, error='Problems with storage')

    logger.info('Experiment begins!')
    tomograph.experiment_is_running = True
    tomograph.exp_id = exp_id
    if exp_param['advanced']:
        thr = threading.Thread(target=carry_out_advanced_experiment, args=(tomograph, exp_param))
    else:
        thr = threading.Thread(target=carry_out_simple_experiment, args=(tomograph, exp_param))
    thr.start()

    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/experiment/stop', methods=['GET'])
def experiment_stop(tomo_num):
    logger.info('\n\nREQUEST: EXPERIMENT/STOP')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    # success, exp_stop_reason_txt, response_if_fail = check_request(request.data)
    # if not success:
    #    return response_if_fail

    #if not exp_stop_reason_txt:
    #    exp_stop_reason_txt = "unknown"
    exp_stop_reason_txt = "unknown"

    tomograph.exp_stop_reason = exp_stop_reason_txt
    tomograph.experiment_is_running = False
    resp = Response(response=json.dumps({'success': True}),
                    status=200,
                    mimetype="application/json")

    return resp


"""
@app.before_request
def limit_remote_addr():
	if request.remote_addr != '10.20.30.40':
		abort(403)  # Forbidden
"""


@app.errorhandler(400)
def incorrect_format(exception):
    logger.exception(exception)
    return make_response(create_response(success=False, error='Incorrect Format'), 400)


@app.errorhandler(404)
def not_found(exception):
    logger.exception(exception)
    return make_response(create_response(success=False, error='Not Found'), 404)


@app.errorhandler(500)
def internal_server_error(exception):
    logger.exception(exception)
    return make_response(create_response(success=False, error='Internal Server Error'), 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
