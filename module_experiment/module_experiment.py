#!/usr/bin/python
from flask import Flask
from flask import request
from flask import make_response
import json
import PyTango
import requests
import threading
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment_logfile.log')



app = Flask(__name__)


#STORAGE_URI = "http://109.234.34.140:5020/fictitious-storage"
STORAGE_URI = "http://109.234.34.140:5006/storage/frames/post"

WEBPAGE_URI = "http://109.234.34.140:5021/fictitious-webpage"



#is being used in     check_and_prepare_advanced_experiment_command(command)
ADVANCED_EXPERIMENT_COMMANDS = (u'open shutter', u'close shutter', u'reset current position', u'go to position', u'get frame')


TOMOGRAPHS = (
    {
        'id': 1,
        'address': '46.101.31.93:10000/tomo/tomograph/1',
        'experiment is running': False,
        'experiment id': '',
        'experiment state': 'Experiment was finished successfully',
        'error': '',
        'exception message': ''
    },
)





def try_something_thrice(func, args = None):
    success = True
    exception_message = ''
    for i in range(0, 3):
        try:
            answer = func(args)
        except PyTango.DevFailed as e:
            success = False
            exception_message = e[-1].desc
            answer = None
        else:
            break
    return success, answer, exception_message


def create_response(success = True, exception_message = '', error = ''):
    response_dict = {
        'success': success,
        'exception message': exception_message,
        'error': error,
    }
    return json.dumps(response_dict)

def create_message(message, exp_id, exception_message = '', error = ''):
    message_dict = {
        'type': 'message',
        'message': message,
        'experiment id': exp_id,
        'exception message': exception_message,
        'error': error,
    }
    return json.dumps(message_dict)



def check_and_connect_tomograph(tomograph_num):
    if TOMOGRAPHS[tomograph_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    logging.debug('Connecting to tomograph...')
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[tomograph_num]['address'])
    if success == False:
        logging.debug(exception_message)
        return False, None, create_response(success, exception_message, error= 'Could not connect to tomograph')

    logging.debug('Success!')
    return True, tomograph, ''

def check_request(request_data):
    logging.debug('Checking request...')
    if not request_data:
        logging.debug('Request is empty!')
        return False, None, create_response(success= False, error= 'Request is empty')

    logging.debug('Request is NOT empty!')
    logging.debug('Checking request\'s JSON...')
    try:
        request_data_dict = json.loads(request_data)
    except TypeError:
        logging.debug('Request has NOT JSON data!')
        return False, None, create_response(success= False, error= 'Request has not JSON data')
    else:
        logging.debug('Request has JSON data!')
        return True, request_data_dict, ''



@app.route('/tomograph/<int:tomograph_num>/source/power-on', methods=['GET'])
def source_power_on(tomograph_num):
    logging.debug('REQUEST: SOURCE/POWER ON\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    logging.debug('Powering on source...')
    success, useless, exception_message = try_something_thrice(tomograph.PowerOn)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not power on source')

    logging.debug('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomograph_num>/source/power-off', methods=['GET'])
def source_power_off(tomograph_num):
    logging.debug('REQUEST: SOURCE/POWER OFF\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    logging.debug('Powering off source...')
    success, useless, exception_message = try_something_thrice(tomograph.PowerOff)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not power off source')

    logging.debug('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomograph_num>/source/set-operating-mode', methods=['POST'])
def source_set_operating_mode(tomograph_num):
    logging.debug('REQUEST: SOURCE/SET OPERATING MODE\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    success, new_mode, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logging.debug('Checking format...')
    if not ((u'voltage' in new_mode.keys()) and (u'current' in new_mode.keys())):
        logging.debug('Incorrect format!')
        return create_response(success= False, error= 'Incorrect format')

    if not ((type(new_mode[u'voltage']) is float) and (type(new_mode[u'current']) is float)):
        logging.debug('Incorrect format! Voltage and current types must be floats, but they are' + str(type(new_mode[u'voltage'])) + str(type(new_mode[u'current'])))
        return create_response(success= False, error= 'Incorrect format')


    logging.debug('Format is normal, new mode id: voltage is %f and current is %f...' % (new_mode[u'voltage'], new_mode[u'current']))
    if new_mode[u'voltage'] < 2 or 60 < new_mode[u'voltage']:
        logging.debug('Voltage must have value from 2 to 60')
        return create_response(success= False, error= 'Voltage must have value from 2 to 60')
    if new_mode[u'current'] < 2 or 80 < new_mode[u'current']:
        logging.debug('Current must have value from 2 to 80')
        return create_response(success= False, error= 'Current must have value from 2 to 80')

    logging.debug('Parameters are normal, setting operating mode...')
    # Tomograph takes values multiplied by 10 and rounded
    new_voltage = round(new_mode[u'voltage'] * 10)
    new_current = round(new_mode[u'current'] * 10)
    success, useless, exception_message = try_something_thrice(tomograph.SetOperatingMode, [new_voltage, new_current])
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not set operating mode')

    logging.debug('Success!')
    return create_response(True)



@app.route('/tomograph/<int:tomograph_num>/shutter/open/<int:time>', methods=['GET'])
def shutter_open(tomograph_num, time):
    logging.debug('REQUEST: SHUTTER/OPEN\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    logging.debug('Opening shutter...')
    success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, time)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not open shutter')

    logging.debug('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomograph_num>/shutter/close/<int:time>', methods=['GET'])
def shutter_close(tomograph_num, time):
    logging.debug('REQUEST: SHUTTER/CLOSE\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    logging.debug('Closing shutter...')
    success, useless, exception_message = try_something_thrice(tomograph.CloseShutter, time)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not close shutter')

    logging.debug('Success!')
    return create_response(True)



@app.route('/tomograph/<int:tomograph_num>/detector/get-frame/<float:exposure>', methods=['GET'])
def detector_get_frame(tomograph_num, exposure):
    logging.debug('REQUEST: DETECTOR/GET FRAME\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    logging.debug('Powering on source...')                                                   # EDIT
    success, useless, exception_message = try_something_thrice(tomograph.PowerOn)
    if success == False:
        handle_emergency_stop(tomograph_num, exception_message, error = 'Could not power on source')
        return


    # Tomograph takes values multiplied by 10 and rounded
    exposure = int(round(exposure * 10))

    logging.debug('Success!')
    logging.debug('Getting frame with exposure %.1f milliseconds...' % (exposure/10))
    success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exposure)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not get frame')

    frame_dict = json.loads(frame_json)
    logging.debug('Success!')
    # The only case, when we send response without using function  create_response()
    return json.dumps({'success': True, 'image': frame_dict})





def prepare_frame_to_send(frame_json, exp_id):
    frame_dict = json.loads(frame_json)
    frame_dict[u'type'] = 'frame'
    frame_dict[u'experiment id'] = exp_id
    return json.dumps(frame_dict)

def send_messages_to_storage_webpage(message, tomograph_num):    #  NEED TO EDIT
    logging.debug('Sending to storage...')
    try:
        req_storage = requests.post(STORAGE_URI, data = message)
    except requests.ConnectionError as e:
        logging.debug(e.message)
        TOMOGRAPHS[tomograph_num]['experiment is running'] = False
        TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was emergency stopped'
        TOMOGRAPHS[tomograph_num]['error'] = 'Could not send to storage'
        TOMOGRAPHS[tomograph_num]['exception message'] = e.message
        # sending message to web page of adjustment

        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        exp_emergency_message = create_message(message= 'Experiment was emergency stopped', exp_id= TOMOGRAPHS[tomograph_num]['experiment id'],
                                               exception_message= '' '''e.message''', error= 'Could not send to storage')
        logging.debug('EXPERIMENT IS EMERGENCY STOPPED!!!\n\n')
        logging.debug('Sending to web page that we could send to storage...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = exp_emergency_message)
        except requests.ConnectionError as e:
            logging.debug('Could not send to web page of adjustment')
        else:
            logging.debug(req_webpage.content)
        return False

    else:
        logging.debug(req_storage.content)
        logging.debug('Sending to web page...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = message)
        except requests.ConnectionError as e:
            logging.debug('Could not send to web page of adjustment')
        else:
            logging.debug(req_webpage.content)
        return True




def handle_emergency_stop(tomograph_num, exp_id, exception_message, error):
    logging.debug(exception_message)
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was emergency stopped'
    TOMOGRAPHS[tomograph_num]['error'] = error
    TOMOGRAPHS[tomograph_num]['exception message'] = exception_message

    exp_emergency_message = create_message(message= 'Experiment was emergency stopped',
                                           exp_id= exp_id, exception_message= exception_message, error= error)
    if send_messages_to_storage_webpage(exp_emergency_message, tomograph_num) == False:
        return
    logging.debug('EXPERIMENT IS EMERGENCY STOPPED!!!\n\n')

def stop_experiment_because_someone(tomograph_num, exp_id):
    exp_stop_message = create_message(message= 'Experiment was stopped by someone', exp_id= exp_id)
    if send_messages_to_storage_webpage(exp_stop_message, tomograph_num) == False:
        return
    logging.debug('EXPERIMENT IS STOPPED BY SOMEONE!!!\n\n')
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was stopped by someone'
    return




def check_and_prepare_advanced_experiment_command(command):
    # Checking parameters
    if not ((u'type' in command.keys()) and (u'args' in command.keys())):
        return False, 'Incorrect format in '
    if not (command[u'type'] in ADVANCED_EXPERIMENT_COMMANDS):
        return False, 'Incorrect format in '
    if (command[u'type'] == u'open shutter') or (command[u'type'] == u'close shutter'):
        if command[u'args'] < 0:
            return False, 'Bad parameters in '
    if command[u'type'] == u'get frame':
        if command[u'args'] <= 0:
            return False, 'Bad parameters in '

    # Preparing parameters for tomograph
    # Tomograph takes values multiplied by 10 and rounded
        command[u'args'] *= 10
        command[u'args'] = round(command[u'args'])
    elif command[u'type'] == u'go to position':
        # Tomograph takes values multiplied by 10 and rounded
        command[u'args'][2] *= 10
        command[u'args'][2] = round(command[u'args'][2])
        command[u'args'][2] %= 3600
    return True, ''

def check_and_prepare_exp_parameters(exp_param):
    if not ((u'experiment id' in exp_param.keys()) and (u'advanced' in exp_param.keys()) and (u'specimen' in exp_param.keys())):
        return False, 'Incorrect format'
    if exp_param[u'advanced']:
        if not (u'instruction' in exp_param.keys()):
            return False, 'Incorrect format'
        cmd_num = 0
        for command in exp_param[u'instruction']:
            cmd_num += 1
            cmd_is_normal, error = check_and_prepare_advanced_experiment_command(command)
            if not cmd_is_normal:
                return False, error + str(cmd_num) + ' command'
        return True, ''
    else:
        # Checking parameters
        if not ((u'DARK' in exp_param.keys()) and (u'EMPTY' in exp_param.keys()) and (u'DATA' in exp_param.keys())):
            return False
        DARK_format_normal = (u'count' in exp_param[u'DARK'].keys()) and (u'exposure' in exp_param[u'DARK'].keys())
        EMPTY_format_normal = (u'count' in exp_param[u'EMPTY'].keys()) and (u'exposure' in exp_param[u'EMPTY'].keys())
        DATA_format_normal_1 = (u'step count' in exp_param[u'DATA'].keys()) and (u'exposure' in exp_param[u'DATA'].keys())
        DATA_format_normal_2 = (u'angle step' in exp_param[u'DATA'].keys()) and (u'count per step' in exp_param[u'DATA'].keys())
        if not (DARK_format_normal and EMPTY_format_normal and DATA_format_normal_1 and DATA_format_normal_2):
            return False, 'Incorrect format'

        if exp_param[u'DARK'][u'exposure'] < 0.1:
            return False, 'Bad parameters in \'DARK\' parameters'
        if exp_param[u'EMPTY'][u'exposure'] < 0.1:
            return False, 'Bad parameters in \'EMPTY\' parameters'
        if exp_param[u'DATA'][u'exposure'] < 0.1:
            return False, 'Bad parameters in \'DATA\' parameters'


        # Preparing parameters for tomograph
        # Tomograph takes values multiplied by 10 and rounded
        exp_param[u'DARK'][u'exposure']  *= 10
        exp_param[u'DARK'][u'exposure']  = round(exp_param[u'DARK'][u'exposure'])
        exp_param[u'EMPTY'][u'exposure'] *= 10
        exp_param[u'EMPTY'][u'exposure'] = round(exp_param[u'EMPTY'][u'exposure'])
        exp_param[u'DATA'][u'exposure']  *= 10
        exp_param[u'DATA'][u'exposure']  = round(exp_param[u'DATA'][u'exposure'])
        # We don't multiply and round  exp_param[u'DATA'][u'angle step'] here, we will do it during experiment
        return True, ''




def carry_out_simple_experiment(tomograph, tomograph_num, exp_param):
    # Closing shutter to get DARK images
    logging.debug('Closing shutter...')
    success, useless, exception_message = try_something_thrice(tomograph.CloseShutter, 0)
    if success == False:
        return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not close shutter')


    logging.debug ('Going to get DARK images!\n\n')
    for i in range(0, exp_param[u'DARK'][u'count']):
        if TOMOGRAPHS[tomograph_num]['experiment is running'] == False:
            return stop_experiment_because_someone(tomograph_num, exp_param[u'experiment id'])

        logging.debug('  Getting DARK image %d from tomograph...' % (i))
        success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exp_param[u'DARK'][u'exposure'])
        if success == False:
            return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not get frame')

        logging.debug('  Success!')
        frame_json = prepare_frame_to_send(frame_json, exp_param[u'experiment id'])
        if send_messages_to_storage_webpage(frame_json, tomograph_num) == False:
            return
    logging.debug('  Finished with DARK images!')


    logging.debug('Opening shutter...')
    success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, 0)
    if success == False:
        return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not open shutter')

    logging.debug('Success!')
    logging.debug('Resetting current position...')
    success, useless, exception_message = try_something_thrice(tomograph.ResetCurrentPosition)
    if success == False:
        return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not reset current position')


    logging.debug('Success!')
    logging.debug('Going to get DATA images, step count is %d!\n\n' % (exp_param[u'DATA'][u'step count']))
    angle_step = exp_param[u'DATA'][u'angle step']
    for i in range(1, exp_param[u'DATA'][u'step count']):
        current_angle = (round( ((i-1)*angle_step) ,  1)) % 360
        logging.debug('  Getting DATA images: angle is %.1f' % current_angle)

        for j in range(0, exp_param[u'DATA'][u'count per step']):
            if TOMOGRAPHS[tomograph_num]['experiment is running'] == False:
                return stop_experiment_because_someone(tomograph_num, exp_param[u'experiment id'])

            logging.debug('    Getting image %d from tomograph...' % (j))
            success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exp_param[u'DARK'][u'exposure'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not get frame')

            logging.debug('    Success!')
            frame_json = prepare_frame_to_send(frame_json, exp_param[u'experiment id'])
            if send_messages_to_storage_webpage(frame_json, tomograph_num) == False:
                return
        # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
        new_angle = (round( i*angle_step ,  1)) % 360
        logging.debug('    Finished with this angle, turning to new angle %.1f...' % (new_angle))
        success, frame_json, exception_message = try_something_thrice(tomograph.GotoPosition, [0, 0,  new_angle * 10])  # x = 0, y = 0 ?
        if success == False:
            return handle_emergency_stop(tomograph_num, exception_message, error = 'Could not turn motor')

        logging.debug('    Success!')
    logging.debug('  Finished with DATA images!')

    exp_finish_message = create_message(message= 'Experiment was finished successfully', exp_id= exp_param[u'experiment id'])
    if send_messages_to_storage_webpage(exp_finish_message, tomograph_num) == False:
        return
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was finished successfully'
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    logging.debug('Experiment is done successfully!')
    return

def carry_out_advanced_experiment(tomograph, tomograph_num, exp_param):
    cmd_num = 0
    for command in exp_param[u'instruction']:
        if TOMOGRAPHS[tomograph_num]['experiment is running'] == False:
            return stop_experiment_because_someone(tomograph_num, exp_param[u'experiment id'])
        cmd_num += 1
        logging.debug('Executing command %d:' % cmd_num)

        if command[u'type'] == u'open shutter':
            logging.debug('Opening shutter...')
            success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, command[u'args'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not open shutter')
            logging.debug('Success!')

        elif command[u'type'] == u'close shutter':
            logging.debug('Closing shutter...')
            success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, command[u'args'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not close shutter')
            logging.debug('Success!')

        elif command[u'type'] == u'reset current position':
            logging.debug('Resetting current position...')
            success, useless, exception_message = try_something_thrice(tomograph.ResetCurrentPosition, command[u'args'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not reset current position')
            logging.debug('Success!')

        elif command[u'type'] == u'go to position':
            x = command[u'args'][0]
            y = command[u'args'][1]
            angle = command[u'args'][2]/10
            logging.debug('Changing position to:  x = %.1f, y = %.1f, angle = %.1f...' % (x, y, angle))
            success, useless, exception_message = try_something_thrice(tomograph.GotoPosition, command[u'args'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not change position to:'
                                                                                          'x = %.1f, y = %.1f, angle = %.1f...' % (x, y, angle))
            logging.debug('Success!')

        # NEED TO ADD COUNT OF FRAMES !!!!!!!!!!!!!!!!!!
        elif command[u'type'] == u'get frame':
            logging.debug('Getting image...')
            success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, command[u'args'])
            if success == False:
                return handle_emergency_stop(tomograph_num, exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not get frame')
            logging.debug('  Got!')
            logging.debug('Sending frame to storage and web page of adjustment...')
            frame_json = prepare_frame_to_send(frame_json, exp_param[u'experiment id'])
            if send_messages_to_storage_webpage(frame_json, tomograph_num) == False:
                return
            logging.debug('Success!')

    exp_finish_message = create_message(message= 'Experiment was finished successfully', exp_id= exp_param[u'experiment id'])
    if send_messages_to_storage_webpage(exp_finish_message, tomograph_num) == False:
        return
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was finished successfully'
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    logging.debug('Experiment is done successfully!')
    return




@app.route('/tomograph/<int:tomograph_num>/experiment/start', methods=['POST'])
def experiment_start(tomograph_num):
    logging.debug('REQUEST: EXPERIMENT/START\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    connected, tomograph, response_if_fail = check_and_connect_tomograph(tomograph_num)
    if not connected:
        return response_if_fail

    success, data, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logging.debug('Checking format...')
    if not (('for storage' in data.keys()) and ('experiment parameters' in data.keys()) and ('experiment id' in data.keys())):
        logging.debug('Incorrect format!')
        return create_response(success= False, error= 'Incorrect format')

    if not ((type(data['for storage']) is dict) and (type(data['experiment parameters']) is dict) and (type(data['experiment parameters']) is unicode)):
        logging.debug('Incorrect format!')
        return create_response(success= False, error= 'Incorrect format')

    logging.debug('Format is normal!')
    exp_param = data['experiment parameters']
    exp_id = data['experiment id']
    exp_param['experiment id'] = exp_id

    logging.debug('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        logging.debug(error)
        return create_response(success, error)

    logging.debug('Parameters are normal!')
    logging.debug('Sending to storage leading to prepare...')
    for_storage_dict = data['for storage']
    for_storage_dict['type'] = 'experiment'
    for_storage_dict['experiment id'] = exp_id
    for_storage_json = json.dumps(for_storage_dict)
    try:
        storage_resp = requests.post(STORAGE_URI, data = for_storage_json)
    except requests.ConnectionError as e:
        logging.debug(e.message)
        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        return create_response(success= False, exception_message= '' '''e.message,''',
                               error= 'Could not send to storage signal of experiment start')


    logging.debug('Sent!')
    storage_resp_dict = json.loads(storage_resp.content)
    if not ('result' in storage_resp_dict.keys()):
        logging.debug('Storage\'s response has incorrect format!')
        return create_response(success= False, error= 'Storage is not ready: storage\'s response has incorrect format')

    logging.debug('Storage\'s response:')
    logging.debug (storage_resp_dict['result'])
    if storage_resp_dict['result'] != 'success':
        logging.debug('Storage is NOT ready!')
        return create_response(success= False, error= 'Storage is not ready: ' + storage_resp_dict['result'])












    '''logging.debug('Checking request...')
    if not request.data:
        logging.debug('Request is empty!')
        return create_response(success= False, error= 'Request is empty')

    logging.debug('Request is not empty!')
    exp_param = json.loads(request.data)
    logging.debug('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        logging.debug(error)
        return create_response(success, error)

    logging.debug('Parameters are normal!')
    logging.debug('Powering on source...')
    success, useless, exception_message = try_something_thrice(tomograph.PowerOn)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not power on source')'''

    logging.debug('Success!')
    logging.debug('Experiment begins!')
    TOMOGRAPHS[tomograph_num]['experiment is running'] = True
    TOMOGRAPHS[tomograph_num]['experiment id'] = exp_param[u'experiment id']
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment is running'
    if exp_param[u'advanced']:
        thr = threading.Thread(target = carry_out_advanced_experiment, args = (tomograph, tomograph_num, exp_param))
    else:
        thr = threading.Thread(target = carry_out_simple_experiment, args = (tomograph, tomograph_num, exp_param))
    thr.start()

    return create_response(True)

@app.route('/tomograph/<int:tomograph_num>/experiment/get-state', methods=['GET'])
def experiment_get_state(tomograph_num):
    logging.debug('REQUEST: EXPERIMENT/GET STATE\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    state_message = create_message(message= TOMOGRAPHS[tomograph_num]['experiment state'], exp_id= TOMOGRAPHS[tomograph_num]['experiment id'],
                                   exception_message= TOMOGRAPHS[tomograph_num]['exception message'], error= TOMOGRAPHS[tomograph_num]['error'])
    return state_message

@app.route('/tomograph/<int:tomograph_num>/experiment/stop', methods=['GET'])
def experiment_stop(tomograph_num):
    logging.debug('REQUEST: EXPERIMENT/STOP\n\n')
    tomograph_num -= 1          #because in list numeration begins from 0
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    return create_response(True)




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







