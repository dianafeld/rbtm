#!/usr/bin/python

"""
Contains the main part of module "Experiment"
More exactly - some supporting functions and functions for receiving queries
"""
import os
import json
import threading

import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from flask import Flask, make_response, request, send_file

from experiment.experiment_class import create_response, ModExpError, prepare_send_frame, send_to_storage, SOMEONE_STOP_MSG
from experiment.conf import REAL_TOMOGRAPH_STORAGE_WEBPAGE, TOMO_ADDR, FRAME_PNG_FILENAME, STORAGE_EXP_START_URI
from experiment.tomograph import Tomograph

app = Flask(__name__)

logs_path = os.path.join('logs', 'experiment.log')
if not os.path.exists(os.path.dirname(logs_path)):
    os.makedirs(os.path.dirname(logs_path))

app.logger.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler(logs_path, maxBytes=1280000, backupCount=10)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - [LINE:%(lineno)d]# - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

stream_handler = StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
app.logger.addHandler(stream_handler)

# Dublicated logger?
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.DEBUG)
# log.addHandler(file_handler)

logger = app.logger

if REAL_TOMOGRAPH_STORAGE_WEBPAGE:
    logger.info(' !! Tomograph, storage, web-page are REAL !! ')
else:
    logger.info(' !! Tomograph, storage, web-page are STUBS !! ')

TOMOGRAPHS = (
    Tomograph(TOMO_ADDR + "/tomo/tomograph/1", TOMO_ADDR + "/tomo/detector/1"),
)


def check_request(request_data):
    """ Checks body part of request, if it is not empty and has JSON string try to load it to python object

    :arg: 'request_data' - body part of request, type is undetermined in common case
    :return: 
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


def call_method_create_response(tomo_num, method_name, args=(), GET_FRAME_method=False):
    if type(args) not in (tuple, list):
        args = (args,)

    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

    try:
        result = getattr(tomograph, method_name)(*args)
    except ModExpError as e:
        e.log(exp_id='')
        return e.create_response()
    """
    except Exception as e:
        logger.info(e.message)
        try:
            return create_response(success=False, error="unexpected exception", exception_message=e.message)
        except Exception as e2:
            logger.info(e.message)
            return create_response(success=False, error="unexpected exception")
    """
    if not GET_FRAME_method:
        return create_response(success=True, result=result)
    else:
        success, ModExpError_if_fail = prepare_send_frame(raw_image_with_metadata=result, experiment=None)
        if not success:
            return ModExpError_if_fail.create_response()

        return send_file('../' + FRAME_PNG_FILENAME, mimetype='image/png')


# in almost every function below we have argument 'tomo_num' - number of tomograph in TOMOGRAPHS list

@app.route('/tomograph/<int:tomo_num>/state', methods=['GET'])
def check_state(tomo_num):
    logger.info('\n\nREQUEST: CHECK STATE')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0
    tomo_state, exception_message = tomograph.tomo_state()
    return create_response(success=True, result=tomo_state, exception_message=exception_message)


# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-on', methods=['GET'])
def source_power_on(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/POWER ON')
    return call_method_create_response(tomo_num, method_name='source_power_on')


# NEED TO EDIT(GENERALLY)
@app.route('/tomograph/<int:tomo_num>/source/power-off', methods=['GET'])
def source_power_off(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/POWER OFF')
    return call_method_create_response(tomo_num, method_name='source_power_off')


# ---------------------------------------------------------#
# Functions for adjustment of tomograph
# ---------------------------------------------------------#


@app.route('/tomograph/<int:tomo_num>/source/set-voltage', methods=['POST'])
def source_set_voltage(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/SET VOLTAGE')
    success, new_voltage, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='source_set_voltage', args=new_voltage)


@app.route('/tomograph/<int:tomo_num>/source/set-current', methods=['POST'])
def source_set_current(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/SET CURRENT')
    success, new_current, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='source_set_current', args=new_current)


@app.route('/tomograph/<int:tomo_num>/source/get-voltage', methods=['GET'])
def source_get_voltage(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/GET VOLTAGE')
    return call_method_create_response(tomo_num, method_name='source_get_voltage')


@app.route('/tomograph/<int:tomo_num>/source/get-current', methods=['GET'])
def source_get_current(tomo_num):
    logger.info('\n\nREQUEST: SOURCE/GET CURRENT')
    return call_method_create_response(tomo_num, method_name='source_get_current')


@app.route('/tomograph/<int:tomo_num>/shutter/open/<int:time_>', methods=['GET'])
def shutter_open(tomo_num, time_):
    logger.info('\n\nREQUEST: SHUTTER/OPEN')
    return call_method_create_response(tomo_num, method_name='open_shutter', args=time_)


@app.route('/tomograph/<int:tomo_num>/shutter/close/<int:time_>', methods=['GET'])
def shutter_close(tomo_num, time_):
    logger.info('\n\nREQUEST: SHUTTER/CLOSE')
    return call_method_create_response(tomo_num, method_name='close_shutter', args=time_)


@app.route('/tomograph/<int:tomo_num>/shutter/state', methods=['GET'])
def shutter_state(tomo_num):
    logger.info('\n\nREQUEST: SHUTTER/STATE')
    return call_method_create_response(tomo_num, method_name='shutter_state')


@app.route('/tomograph/<int:tomo_num>/motor/set-horizontal-position', methods=['POST'])
def motor_set_horizontal_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET HORIZONTAL POSITION')
    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='set_x', args=new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/set-vertical-position', methods=['POST'])
def motor_set_vertical_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET VERTICAL POSITION')
    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='set_y', args=new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/set-angle-position', methods=['POST'])
def motor_set_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/SET ANGLE POSITION')
    success, new_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='set_angle', args=new_pos)


@app.route('/tomograph/<int:tomo_num>/motor/get-horizontal-position', methods=['GET'])
def motor_get_horizontal_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET HORIZONTAL POSITION')
    return call_method_create_response(tomo_num, method_name='get_x')


@app.route('/tomograph/<int:tomo_num>/motor/get-vertical-position', methods=['GET'])
def motor_get_vertical_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET VERTICAL POSITION')
    return call_method_create_response(tomo_num, method_name='get_y')


@app.route('/tomograph/<int:tomo_num>/motor/get-angle-position', methods=['GET'])
def motor_get_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/GET ANGLE POSITION')
    return call_method_create_response(tomo_num, method_name='get_angle')


@app.route('/tomograph/<int:tomo_num>/motor/move-away', methods=['GET'])
def motor_move_away(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/MOVE AWAY')
    return call_method_create_response(tomo_num, method_name='move_away')


@app.route('/tomograph/<int:tomo_num>/motor/move-back', methods=['GET'])
def motor_move_back(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/MOVE BACK')
    return call_method_create_response(tomo_num, method_name='move_back')


@app.route('/tomograph/<int:tomo_num>/motor/reset-angle-position', methods=['GET'])
def motor_reset_angle_position(tomo_num):
    logger.info('\n\nREQUEST: MOTOR/RESET ANGLE POSITION')
    return call_method_create_response(tomo_num, method_name='reset_to_zero_angle')


@app.route('/tomograph/<int:tomo_num>/detector/get-frame', methods=['POST'])
def detector_get_frame(tomo_num):
    logger.info('\n\nREQUEST: DETECTOR/GET FRAME')
    success, exposure, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='get_frame', args=(exposure, True), GET_FRAME_method=True)


@app.route('/tomograph/<int:tomo_num>/detector/get-frame-with-closed-shutter', methods=['POST'])
def detector_get_frame_with_closed_shutter(tomo_num):
    logger.info('\n\nREQUEST: DETECTOR/GET FRAME WITH CLOSED SHUTTER')
    success, exposure, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail
    return call_method_create_response(tomo_num, method_name='get_frame', args=(exposure, False), GET_FRAME_method=True)


@app.route('/tomograph/<int:tomo_num>/detector/chip_temp', methods=['GET'])
def detector_get_chip_temperature(tomo_num):
    logger.info('\n\nREQUEST: DETECTOR/GET CHIP TEMPERATURE')
    return call_method_create_response(tomo_num, method_name='get_detector_chip_temperature')


@app.route('/tomograph/<int:tomo_num>/detector/hous_temp', methods=['GET'])
def detector_get_hous_temperature(tomo_num):
    logger.info('\n\nREQUEST: DETECTOR/GET HOUS TEMPERATURE')
    return call_method_create_response(tomo_num, method_name='get_detector_hous_temperature')


# ---------------------------------------------------------#
#    Functions for running experiment
# ---------------------------------------------------------#

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


# def time_counter_of_experiment(tomograph, exp_id, exp_time=MAX_EXPERIMENT_TIME):
#     time.sleep(exp_time)
#     cur_exp = tomograph.current_experiment
#     if (cur_exp != None and cur_exp.exp_id == exp_id):
#         logger.info("\nEXPERIMENT TAKES TOO LONG, GOING TO STOP IT!\n")
#         cur_exp.to_be_stopped = True
#         cur_exp.exp_stop_reason = "# MODULE EXPERIMENT: EXPERIMENT TAKES TOO LONG #"
#     return
#
#
# def carry_out_advanced_experiment(tomograph, exp_param):
#     exp_id = exp_param['exp_id']
#     exp_code_string = exp_param['instruction']
#     # 't_0M_o_9_r_' - strange name of object, because using user of this "word" in instruction is unlikely
#     exp_code_string = exp_code_string.replace("open_shutter", "t_0M_o_9_r_.open_shutter")
#     exp_code_string = exp_code_string.replace("close_shutter", "t_0M_o_9_r_.close_shutter")
#     exp_code_string = exp_code_string.replace("set_x", "t_0M_o_9_r_.set_x")
#     exp_code_string = exp_code_string.replace("set_y", "t_0M_o_9_r_.set_y")
#     # rename method 'reset_angle' to 'reset_to_zero_angle' because 'set_angle' is substring of 'reset_angle'
#     exp_code_string = exp_code_string.replace("reset_angle", "t_0M_o_9_r_.reset_to_zero_angle")
#     exp_code_string = exp_code_string.replace("set_angle", "t_0M_o_9_r_.set_angle")
#     exp_code_string = exp_code_string.replace("get_x", "t_0M_o_9_r_.get_x")
#     exp_code_string = exp_code_string.replace("get_y", "t_0M_o_9_r_.get_y")
#     exp_code_string = exp_code_string.replace("get_angle", "t_0M_o_9_r_.get_angle")
#     exp_code_string = exp_code_string.replace("move_away", "t_0M_o_9_r_.move_away")
#     exp_code_string = exp_code_string.replace("move_back", "t_0M_o_9_r_.move_back")
#     exp_code_string = exp_code_string.replace("get_frame", "t_0M_o_9_r_.get_frame")
#     exp_code_string = exp_code_string.replace("send_frame", "t_0M_o_9_r_.se")
#     print
#     exp_code_string
#     time_of_experiment_start = time.time()
#     thr = threading.Thread(target=time_counter_of_experiment, args=(tomograph, exp_id))
#     thr.start()
#     try:
#         exec (exp_code_string, {'__builtins__': {}, 't_0M_o_9_r_': tomograph})
#     except tomograph.ExpStopException as e:
#         return
#     except SyntaxError as e:
#         print
#         repr(e)
#         tomograph.handle_emergency_stop(exp_is_advanced=False, exp_id=exp_id,
#                                         error="Syntax of experiment instruction is NOT correct",
#                                         exception_message=e.message)
#         return
#
#     except Exception as e:
#         print
#         repr(e)
#         tomograph.handle_emergency_stop(exp_is_advanced=False, exp_id=exp_id, error="Exception during experiment",
#                                         exception_message=e.message)
#         return
#
#     tomograph.handle_successful_stop(time_of_experiment_start)
#     return


# NEED TO EDIT (COMMENT BEFORE POWERING ON SOURCE)
@app.route('/tomograph/<int:tomo_num>/experiment/start', methods=['POST'])
def experiment_start(tomo_num):
    logger.info('\n\nREQUEST: EXPERIMENT/START')
    tomograph = TOMOGRAPHS[tomo_num - 1]
    # tomo_num - 1, because in TOMOGRAPHS list numeration begins from 0

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
    exp_param['exp_id'] = data['exp_id']

    logger.info('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        logger.info(error)
        return create_response(success=success, error=error)
    logger.info('Parameters are normal!')

    tomo_state, exception_message = tomograph.tomo_state()
    if tomo_state == 'unavailable':
        return create_response(success=False, error="Could not connect with tomograph",
                               exception_message=exception_message)
    elif tomo_state == 'experiment':
        return create_response(success=False, error="On this tomograph experiment is running")
    elif tomo_state != 'ready':
        return create_response(success=False, error="Undefined tomograph state")

    logger.info('Sending to storage leading to prepare...')
    try:
        send_to_storage(STORAGE_EXP_START_URI, data=request.data)
    except ModExpError as e:
        e.log(exp_id=exp_param['exp_id'])
        return e.create_response()

    logger.info('Experiment begins!')
    if exp_param['advanced']:
        pass
        # thr = threading.Thread(target=carry_out_advanced_experiment, args=(tomograph, exp_param))
    else:
        thr = threading.Thread(target=tomograph.carry_out_simple_experiment, args=(exp_param,))
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

    # if not exp_stop_reason_txt:
    #    exp_stop_reason_txt = "unknown"
    exp_stop_reason_txt = "unknown"

    if tomograph.current_experiment is not None:
        tomograph.current_experiment.to_be_stopped = True
        tomograph.current_experiment.stop_exception = ModExpError(error=exp_stop_reason_txt, stop_msg=SOMEONE_STOP_MSG)

    return create_response(True)


# @app.before_request
# def limit_remote_addr():
# 	if request.remote_addr != '10.20.30.40':
# 		abort(403)  # Forbidden


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
