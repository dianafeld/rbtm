#!/usr/bin/python
from flask import Flask
from flask import request
from flask import make_response
import json
import PyTango
import requests
import threading
#import logging


#logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment.log')

app = Flask(__name__)


STORAGE_URI = "http://109.234.34.140:5020/fictitious-storage"
#STORAGE_URI = "http://109.234.34.140:5006/storage/frames/post"

WEBPAGE_URI = "http://109.234.34.140:5021/fictitious-webpage"



#is being used in     check_and_prepare_advanced_experiment_command(command)
ADVANCED_EXPERIMENT_COMMANDS = ('open shutter', 'close shutter', 'reset current position', 'go to position', 'get frame')


TOMOGRAPHS = (
    {
        'id': 1,
#        'address': '109.234.38.83:10000/tomo/tomograph/1',                      # real tomograph address
#        'device': PyTango.DeviceProxy('109.234.38.83:10000/tomo/tomograph/1'),  # real tomograph
        'address': '46.101.31.93:10000/tomo/tomograph/1',                       # fictitious tomograph address
        'device': PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1'),   # fictitious tomograph
        'experiment is running': False,
    },
)
TOMOGRAPHS[0]['device'].set_timeout_millis(25000)

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




def check_request(request_data):
    print('Checking request...')
    if not request_data:
        print('Request is empty!')
        return False, None, create_response(success= False, error= 'Request is empty')

    print('Request is NOT empty!')
    print('Checking request\'s JSON...')
    try:
        request_data_dict = json.loads(request_data)
    except TypeError:
        print('Request has NOT JSON data!')
        return False, None, create_response(success= False, error= 'Request has not JSON data')
    else:
        print('Request has JSON data!')
        return True, request_data_dict, ''




# in almost every function we have argument 'tomo_num' - number of tomograph in TOMOGRAPHS list
@app.route('/tomograph/<int:tomo_num>/source/power-on', methods=['GET'])  # QUESTION, NEED TO EDIT
def source_power_on(tomo_num):
    print('\n\nREQUEST: SOURCE/POWER ON')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    print('Powering on source...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].PowerOn)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not power on source')

    print('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomo_num>/source/power-off', methods=['GET'])  # QUESTION, NEED TO EDIT
def source_power_off(tomo_num):
    print('\n\nREQUEST: SOURCE/POWER OFF')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0


    print('Powering off source...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].PowerOff)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not power off source')

    print('Success!')
    return create_response(True)





@app.route('/tomograph/<int:tomo_num>/source/set-operating-mode', methods=['POST'])
def source_set_operating_mode(tomo_num):
    print('\n\nREQUEST: SOURCE/SET OPERATING MODE')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        print('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    success, new_mode, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    print('Checking format...')
    if not (('voltage' in new_mode.keys()) and ('current' in new_mode.keys())):
        print('Incorrect format!')
        return create_response(success= False, error= 'Incorrect format')

    if not ((type(new_mode['voltage']) is float) and (type(new_mode['current']) is float)):
        print('Incorrect format! Voltage and current types must be floats, but they are '
              + str(type(new_mode['voltage'])) + str(type(new_mode['current'])))
        return create_response(success= False, error= 'Incorrect format')


    # TO DELETE THIS LATER
    print('Format is normal, new mode: voltage is %f and current is %f...' % (new_mode['voltage'], new_mode['current']))
    if new_mode['voltage'] < 2 or 60 < new_mode['voltage']:
        print('Voltage must have value from 2 to 60')
        return create_response(success= False, error= 'Voltage must have value from 2 to 60')
    if new_mode['current'] < 2 or 80 < new_mode['current']:
        print('Current must have value from 2 to 80')
        return create_response(success= False, error= 'Current must have value from 2 to 80')

    print('Parameters are normal, setting operating mode...')
    # Tomograph takes values multiplied by 10 and rounded
    new_voltage = round(new_mode['voltage'] * 10)
    new_current = round(new_mode['current'] * 10)
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].SetOperatingMode, [new_voltage, new_current])
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not set operating mode')

    print('Success!')
    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/shutter/open/<int:time>', methods=['GET'])
def shutter_open(tomo_num, time):
    print('\n\nREQUEST: SHUTTER/OPEN')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        print('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    print('Opening shutter...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].OpenShutter, time)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not open shutter')

    print('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomo_num>/shutter/close/<int:time>', methods=['GET'])
def shutter_close(tomo_num, time):
    print('\n\nREQUEST: SHUTTER/CLOSE')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        print('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    print('Closing shutter...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].CloseShutter, time)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not close shutter')

    print('Success!')
    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/detector/get-frame/<float:exposure>', methods=['GET'])
def detector_get_frame(tomo_num, exposure):
    print('\n\nREQUEST: DETECTOR/GET FRAME')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        print('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    # Tomograph takes values multiplied by 10 and rounded
    exposure = round(exposure * 10)

    print('Success!')
    print('Getting frame with exposure %.1f milliseconds...' % (exposure/10))
    success, frame_json, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GetFrame, exposure)
    if success == False:
        print(exception_message)
        return create_response(success, exception_message, error= 'Could not get frame')

    frame_dict = json.loads(frame_json)
    print('Success!')
    # The only case, when we send response without using function  create_response()
    return json.dumps({'success': True, 'image': frame_dict})



def create_event(type, exp_id, MoF, exception_message = '', error = ''):
    # MoF - message or frame
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
            'experiment_id': exp_id,
            'frame': MoF,
        }
        return frame_dict

    return None

# MAYBE NEED TO EDIT (NEED TO ADD CHECKING STORAGE'S RESPONSE)
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
        print('Sending to web page...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = message)
        except requests.ConnectionError as e:
            print('Could not send to web page of adjustment')
        else:
            print(req_webpage.content)
        return True




def handle_emergency_stop(**stop_event):
    # !in this function we SUPPOSE that 'stop_event' have fields  'exp_id', 'exception_message' and 'error'!
    print(stop_event['exception_message'])

    stop_event['type'] = 'message'
    stop_event['message'] = 'Experiment was emergency stopped'
    if send_messages_to_storage_webpage(stop_event) == False:
        return
    print('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')

def stop_experiment_because_someone(exp_id):
    exp_stop_event = create_event('message', exp_id, 'Experiment was stopped by someone')
    if send_messages_to_storage_webpage(exp_stop_event) == False:
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
        return False, 'Incorrect format1'
    if not ((type(exp_param['experiment id']) is unicode) and (type(exp_param['advanced']) is bool)):
        return False, 'Incorrect format2'
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


        # Preparing parameters for tomograph
        # Tomograph takes values multiplied by 10 and rounded
        exp_param['DARK']['exposure']  *= 10
        exp_param['DARK']['exposure']  = round(exp_param['DARK']['exposure'])
        exp_param['EMPTY']['exposure'] *= 10
        exp_param['EMPTY']['exposure'] = round(exp_param['EMPTY']['exposure'])
        exp_param['DATA']['exposure']  *= 10
        exp_param['DATA']['exposure']  = round(exp_param['DATA']['exposure'])
        # we don't multiply and round  exp_param['DATA']['angle step'] here, we will do it during experiment,
        # because it will be more accurate this way
        return True, ''




def carry_out_simple_experiment(tomo_num, exp_param):
    exp_id = exp_param['experiment id']
    # Closing shutter to get DARK images
    print TOMOGRAPHS[tomo_num]['device'].ping
    print('Closing shutter...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].CloseShutter, 0)
    if success == False:
        return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= 'Could not close shutter')


    print('\nGoing to get DARK images!')
    for i in range(0, exp_param['DARK']['count']):
        if TOMOGRAPHS[tomo_num]['experiment is running'] == False:
            return stop_experiment_because_someone(exp_id)

        print('  Getting DARK image %d from tomograph...' % (i))
        success, frame_json, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GetFrame, exp_param['DARK']['exposure'])
        if success == False:
            return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error = 'Could not get frame')

        print('  Success!')
        frame_dict = json.loads(frame_json)
        frame_with_data = create_event('frame', exp_id, frame_dict)
        if send_messages_to_storage_webpage(frame_with_data) == False:
            return
    print('  Finished with DARK images!')


    print('Opening shutter...')
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].OpenShutter, 0)
    if success == False:
        return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error = 'Could not open shutter')

    print('Success!')
    print('Resetting current position...')
 #   success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].ResetCurrentPosition)
    if success == False:
        return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error = 'Could not reset current position')


    print('Success!')
    print('Going to get DATA images, step count is %d!\n' % (exp_param['DATA']['step count']))
    angle_step = exp_param['DATA']['angle step']
    for i in range(1, exp_param['DATA']['step count']):
        current_angle = (round( ((i-1)*angle_step) ,  1)) % 360
        print('  Getting DATA images: angle is %.1f' % current_angle)

        for j in range(0, exp_param['DATA']['count per step']):
            if TOMOGRAPHS[tomo_num]['experiment is running'] == False:
                return stop_experiment_because_someone(exp_id)

            print('    Getting image %d from tomograph...' % (j))
            success, frame_json, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GetFrame, exp_param['DARK']['exposure'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error = 'Could not get frame')

            print('    Success!')
            frame_dict = json.loads(frame_json)
            frame_with_data = create_event('frame', exp_id, frame_dict)
            if send_messages_to_storage_webpage(frame_with_data) == False:
                return
        # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
        new_angle = (round( i*angle_step ,  1)) % 360
        print('    Finished with this angle, turning to new angle %.1f...' % (new_angle))
        #success, frame_json, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GotoPosition, [0, 0,  new_angle * 10])  # x = 0, y = 0 ?
        if success == False:
            return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,  error = 'Could not turn motor')

        print('    Success!')
    print('  Finished with DATA images!')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_messages_to_storage_webpage(exp_finish_message) == False:
        return
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
    print('Experiment is done successfully!')
    return

def carry_out_advanced_experiment(tomo_num, exp_param):
    exp_id = exp_param['experiment id']
    cmd_num = 0
    for command in exp_param['instruction']:
        if TOMOGRAPHS[tomo_num]['experiment is running'] == False:
            return stop_experiment_because_someone(exp_id)
        cmd_num += 1
        print('Executing command %d:' % cmd_num)

        if command['type'] == 'open shutter':
            print('Opening shutter...')
            success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not open shutter')
            print('Success!')

        elif command['type'] == 'close shutter':
            print('Closing shutter...')
            success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not close shutter')
            print('Success!')

        elif command['type'] == 'reset current position':
            print('Resetting current position...')
            success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].ResetCurrentPosition, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not reset current position')
            print('Success!')

        elif command['type'] == 'go to position':
            x = str(command['args'][0])
            y = str(command['args'][1])
            angle = str(command['args'][2]/10)
            print('Changing position to:  x = ' + x + ', y = ' + y + ', angle = ' + angle + '...')
            success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GotoPosition, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not go to position: '
                                                                     'x = ' + x + ', y = ' + y + ', angle = ' + angle)
            print('Success!')

        elif command['type'] == 'get frame':
            print('Getting image...')
            success, frame_json, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].GetFrame, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not get frame')
            print('  Got!\nSending frame to storage and web page of adjustment...')
            frame_dict = json.loads(frame_json)
            frame_with_data = create_event('frame', exp_id, frame_dict)
            if send_messages_to_storage_webpage(frame_with_data) == False:
                return
            print('Success!')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_messages_to_storage_webpage(exp_finish_message) == False:
        return
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
    print('Experiment is done successfully!')
    return




@app.route('/tomograph/<int:tomo_num>/experiment/start', methods=['POST'])
def experiment_start(tomo_num):
    print('\n\nREQUEST: EXPERIMENT/START')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        print('On this tomograph experiment is running')
        return False, None, create_response(success= False, error= 'On this tomograph experiment is running')

    success, data, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    print('Checking generous format...')
    if not (('experiment parameters' in data.keys()) and ('experiment id' in data.keys())):
        print('Incorrect format1!')
        return create_response(success= False, error= 'Incorrect format')

    if not ((type(data['experiment parameters']) is dict) and (type(data['experiment id']) is unicode)):
        print('Incorrect format2!')
        return create_response(success= False, error= 'Incorrect format')

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
    success, useless, exception_message = try_something_thrice(TOMOGRAPHS[tomo_num]['device'].PowerOn)
    if success == False:
        return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message, error= 'Could not power on tomograph')

    print('Success!')
    print('Sending to storage leading to prepare...')
    try:
        storage_resp = requests.post(STORAGE_URI, data = request.data)
    except requests.ConnectionError as e:
        print(e.message)
        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        return create_response(success= False, exception_message= '' '''e.message,''',
                               error= 'Could not send to storage signal of experiment start')


    print('Sent!')
    print(type(storage_resp.content))
    print(storage_resp.content)
    storage_resp_dict = json.loads(storage_resp.content)

    if not ('result' in storage_resp_dict.keys()):
        print('Storage\'s response has incorrect format!')
        return create_response(success= False, error= 'Storage is not ready: storage\'s response has incorrect format')

    print('Storage\'s response:')
    print (storage_resp_dict['result'])
    if storage_resp_dict['result'] != 'success':
        print('Storage is NOT ready!')
        return create_response(success= False, error= 'Storage is not ready: ' + storage_resp_dict['result'])

    print('Experiment begins!')
    TOMOGRAPHS[tomo_num]['experiment is running'] = True
    if exp_param['advanced']:
        thr = threading.Thread(target = carry_out_advanced_experiment, args = (tomo_num, exp_param))
    else:
        thr = threading.Thread(target = carry_out_simple_experiment, args = (tomo_num, exp_param))
    thr.start()

    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/experiment/stop', methods=['GET'])
def experiment_stop(tomo_num):
    print('\n\nREQUEST: EXPERIMENT/STOP')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
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







