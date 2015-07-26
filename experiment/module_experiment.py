#!/usr/bin/python

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

import logging
from StringIO import StringIO
# logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment.log')
app = Flask(__name__)



STORAGE_IS_FICTITIOUS = False

WEBPAGE_OF_ADJUSTMENT_IS_FICTITIOUS = True

TOMOGRAPH_IS_FICTITIOUS = False


TIMEOUT_MILLIS = 200000


if STORAGE_IS_FICTITIOUS:
    STORAGE_URI = "http://109.234.34.140:5020/fictitious-storage"
    STORAGE_EXPERIMENT_URI = "http://109.234.34.140:5020/fictitious-storage"
else:
    STORAGE_URI = "http://188.166.66.37:5006/storage/frames/post"                     # To send frames
    STORAGE_EXPERIMENT_URI = "http://188.166.66.37:5006/storage/experiments/post"     # To send experiment parameters
    #STORAGE_URI = "http://109.234.34.140:5006/storage/frames/post"                     # To send frames
    #STORAGE_EXPERIMENT_URI = "http://109.234.34.140:5006/storage/experiments/post"     # To send experiment parameters

if WEBPAGE_OF_ADJUSTMENT_IS_FICTITIOUS:
    WEBPAGE_URI = "http://109.234.34.140:5021/fictitious-webpage"
else:
    WEBPAGE_URI = "http://109.234.34.140:5021/fictitious-webpage"

if TOMOGRAPH_IS_FICTITIOUS:
    TOMO_ADDR = '188.166.73.250:10000'
else:
    TOMO_ADDR = 'localhost:10000'




TOMOGRAPHS = (
    {
        'id': 1,
        'device': PyTango.DeviceProxy(TOMO_ADDR + '/tomo/tomograph/1'),
        'detector': PyTango.DeviceProxy(TOMO_ADDR + '/tomo/detector/1'),
        'experiment is running': False,
    },
)
TOMOGRAPHS[0]['device'].set_timeout_millis(TIMEOUT_MILLIS)
TOMOGRAPHS[0]['detector'].set_timeout_millis(TIMEOUT_MILLIS)



#is being used in     check_and_prepare_advanced_experiment_command(command)
ADVANCED_EXPERIMENT_COMMANDS = ('open shutter', 'close shutter', 'reset current position', 'go to position', 'get frame')
FRAME_PNG_FILENAME = 'image.png'

def try_thrice_function(func, args = None):
    success = True
    exception_message = ''
    for i in range(0, 3):
        try:
            answer = func(args)
        except PyTango.DevFailed as e:
            for stage in e:
                logging.debug(stage.desc)
            success = False
            exception_message = e[-1].desc
            answer = None
        else:
            break
    return success, answer, exception_message

def try_thrice_change_attr(device, attr_name, new_value):
    success = True
    exception_message = ''
    for i in range(0, 3):
        try:
            device.write_attribute(attr_name, new_value)
            set_value = device[attr_name].value
        except PyTango.DevFailed as e:
            success = False
            exception_message = e[-1].desc
            set_value = None
        else:
            break
    return success, set_value, exception_message


def create_response(success = True, exception_message = '', error = '', result = None):
    response_dict = {
        'success': success,
        'exception message': exception_message,
        'error': error,
        'result': result,
    }
    return json.dumps(response_dict)

def check_request(request_data):
    logging.debug('Checking request...')
    if not request_data:
        logging.debug('Request is empty!')
        return False, None, create_response(success= False, error= 'Request is empty')

    logging.debug('Request is NOT empty! Checking request\'s JSON...')
    try:
        request_data_dict = json.loads(request_data)
    except TypeError:
        logging.debug('Request has NOT JSON data!')
        return False, None, create_response(success= False, error= 'Request has not JSON data')
    else:
        logging.debug('Request has JSON data!')
        return True, request_data_dict, ''


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
            'exp_id': exp_id,
            'frame': MoF,
        }
        return frame_dict

    return None

def make_png(res):
    plt.ioff()
    plt.figure()
    plt.imshow(res, cmap=plt.cm.gray)
    plt.colorbar()
    return plt.savefig(FRAME_PNG_FILENAME, bbox_inches='tight')

def create_png_file(frame_dict):

    """ converts frame to png and save it, to send it to webpage of adjustment
    :param frame_dict:
    """

    try:
        image_list = frame_dict["image_data"]["image"]
        image_numpy = np.asarray(image_list)
        make_png(image_numpy)
    except Exception as e:
        logging.debug(e.message)
    return

# NEED TO ADD CHECKING STORAGE'S RESPONSE
def send_messages_to_storage_webpage(event):
    # 'event' must be dictionary with format that is returned by  'create_event()'
    logging.debug('Sending to storage...')
    try:
        message = json.dumps(event)
        req_storage = requests.post(STORAGE_URI, data = message)
    except requests.ConnectionError as e:
        logging.debug(e.message)
        # sending message to web page of adjustment
        exp_id = event['exp_id']

        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        exp_emergency_message = create_event(type = 'message' , exp_id = exp_id, MoF = 'Experiment was emergency stopped',
                                             exception_message= '' '''e.message''', error= 'Could not send to storage')

        logging.debug('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')
        logging.debug('Sending to web page that we could send to storage...')
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = exp_emergency_message)
        except requests.ConnectionError as e:
            logging.debug('Could not send to web page of adjustment')
        else:
            logging.debug(req_webpage.content)
        return False

    else:
        logging.debug(req_storage.content)                              #NEED TO CHANGE  TO LOG RESULT, NOT ALL

        # commented 22.05, because frames are too heavy
        """
        if event['type'] == 'frame':
            create_png_file(event['frame'])
            files = {'file': open(FRAME_PNG_FILENAME, 'rb')}
            logging.debug('Sending to web page...')
            try:
                req_webpage = requests.post(WEBPAGE_URI, files=files)
            except requests.ConnectionError as e:
                logging.debug('Could not send to web page of adjustment')
            else:
                logging.debug(req_webpage.content)
        """
        return True

"""
def send_frame_storage(frame_dict):
    frame_json = json.dumps(frame_dict)
    files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}

    r = requests.post(STORAGE_URI, files=files)
    r.text
"""


def handle_emergency_stop(**stop_event):
    # !in this function we SUPPOSE that 'stop_event' have fields  'exp_id', 'tomo_num', 'exception_message' and 'error'!
    stop_event['type'] = 'message'
    stop_event['message'] = 'Experiment was emergency stopped'
    TOMOGRAPHS[stop_event['tomo_num']] = False
    del stop_event['tomo_num']
    if send_messages_to_storage_webpage(stop_event) == False:
        return
    logging.debug('\nEXPERIMENT IS EMERGENCY STOPPED!!!\n')


# functions below (open_shutter, close_shutter, set_x, set_y, set_angle, reset_angle, move_away, move_back and
# get_frame) can be called during experiment or not. If not, then argument exp_id is empty and vice versa. In this cases
# functions return answer in different format
def open_shutter(tomo_num, time = 0, exp_id = ''):
    logging.debug('Opening shutter...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].OpenShutter, time)
    if success == False:
        error = 'Could not open shutter'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def close_shutter(tomo_num, time = 0, exp_id = ''):
    logging.debug('Closing shutter...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].CloseShutter, time)
    if success == False:
        error = 'Could not close shutter'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)


def set_x(tomo_num, new_x, exp_id = ''):
    logging.debug('Going to set new horizontal position...')
    if type(new_x) is not float:
        error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_x))
        logging.debug (error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False
        else:
            return create_response(success= False, error= error)

    # TO DELETE THIS LATER
    logging.debug('Setting value %.1f...' % (new_x))
    if new_x < -5000 or 2000 < new_x:
        error = 'Position must have value from -30 to 30'
        logging.debug(error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False
        else:
            return create_response(success= False, error= error)


    success, set_x, exception_message = try_thrice_change_attr(TOMOGRAPHS[tomo_num]['device'], "horizontal_position", new_x)
    if success == False:
        error = 'Could not set new position because of tomograph'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def set_y(tomo_num, new_y, exp_id = ''):
    logging.debug('Going to set new vertical position...')
    if type(new_y) is not float:
        error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_y))
        logging.debug (error)
        if exp_id:
            handle_emergency_stop(exp_id=exp_id, tomo_num=tomo_num, exception_message='', error=error)
            return False
        else:
            return create_response(success=False, error=error)

    # TO DELETE THIS LATER
    logging.debug('Setting value %.1f...' % (new_y))
    if new_y < -5000 or 2000 < new_y:
        error = 'Position must have value from -5000 to 2000'
        logging.debug(error)
        if exp_id:
            handle_emergency_stop(exp_id=exp_id, tomo_num=tomo_num, exception_message='', error=error)
            return False
        else:
            return create_response(success=False, error=error)

    success, set_y, exception_message = try_thrice_change_attr(TOMOGRAPHS[tomo_num]['device'], "vertical_position", new_y)
    if success == False:
        error = 'Could not set new position because of tomograph'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return False, create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def set_angle(tomo_num, new_angle, exp_id = ''):
    logging.debug('Going to set new angle position...')
    if type(new_angle) is not float:
        error = 'Incorrect type! Position type must be float, but it is ' + str(type(new_angle))
        logging.debug (error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False
        else:
            return create_response(success= False, error= error)

    logging.debug('Setting value %.1f...' % (new_angle))
    new_angle %= 360
    success, set_angle, exception_message = try_thrice_change_attr(TOMOGRAPHS[tomo_num]['device'], "angle_position", new_angle)
    if success == False:
        error = 'Could not set new position because of tomograph'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def reset_angle(tomo_num, exp_id = ''):
    logging.debug('Resetting angle position...')

    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].ResetAnglePosition)
    if success == False:
        error = 'Could not reset angle position because of tomograph'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def move_away(tomo_num, exp_id = ''):
    logging.debug('Moving object away...')

    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].MoveAway)
    if success == False:
        error = 'Could not move object away'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)

def move_back(tomo_num, exp_id = ''):
    logging.debug('Moving object back...')

    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].MoveBack)
    if success == False:
        error = 'Could not move object back'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False
        else:
            return create_response(success, exception_message, error= error)

    logging.debug('Success!')
    if exp_id: return True
    else:      return create_response(True)


def read_image_from_detector_attr(tomo_num):

    """
    returns frame attribute from detector as a numpy.array
    """
    det = TOMOGRAPHS[tomo_num]['detector']
    try:
        da = det.read_attribute("image", extract_as=PyTango.ExtractAs.Nothing)
    except PyTango.DevFailed as e:
        for stage in e:
            logging.debug(stage.desc)

    enc = PyTango.EncodedAttribute()
    data = enc.decode_gray16(da)
    return data

def join_image_with_metadata(image_numpy, frame_metadata_dict):
    """
    tmp_list_of_strs = []
    for lst in image_numpy.tolist():
        tmp_list_of_strs.append(' '.join(map(str,lst)))
    image_str = '\n'.join(tmp_list_of_strs)
    frame_metadata_dict['image_data']['image'] = image_str
    """
    #k = ''
    #for i in image_numpy:
    #    k = k + ' '.join(str(e) for e in i)
    #    k=k+'\n'

    s = StringIO()
    np.savetxt(s, image_numpy, fmt="%d")
    logging.debug(s.getvalue()[:10])
    frame_metadata_dict['image_data']['image'] = s.getvalue()

    #image_list = image_numpy.tolist()
    #frame_metadata_dict['image_data']['image'] = image_list
    return frame_metadata_dict



def get_frame(tomo_num, exposure, exp_id = ''):
    logging.debug('Going to get image...')
    if type(exposure) is not float:
        error = 'Incorrect type! Exposure type must be float, but it is ' + str(type(exposure))
        logging.debug (error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False, None
        else:
            return create_response(success= False, error= error)

    # TO DELETE THIS LATER
    logging.debug('Getting image with exposure %.1f milliseconds...' % (exposure))
    if exposure < 0.1 or 16000 < exposure:
        error = 'Exposure must have value from 0.1 to 16000'
        logging.debug(error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False, None
        else:
            return create_response(success= False, error= error)


    # Tomograph takes exposure multiplied by 10 and rounded
    exposure = round(exposure * 10)
    success, frame_metadata_json, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].GetFrame, exposure)
    if success == False:
        error = 'Could not get image because of tomograph'
        logging.debug(exception_message)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= exception_message, error= error)
            return False, None
        else:
            return create_response(success, exception_message, error= error)


    try:
        frame_metadata_dict = json.loads(frame_metadata_json)
    except TypeError:
        error = 'Could not convert frame\'s JSON into dict'
        logging.debug(error)
        if exp_id:
            handle_emergency_stop(exp_id= exp_id, tomo_num= tomo_num, exception_message= '', error= error)
            return False, None
        else:
            return create_response(success = False, error= error)

    image_numpy = read_image_from_detector_attr(tomo_num)

    logging.debug('Success!')
    if exp_id:
        frame_dict = join_image_with_metadata(image_numpy, frame_metadata_dict)
        return True, frame_dict
    else:
        logging.debug(1)
        make_png(image_numpy)
        logging.debug(2)
        return send_file(FRAME_PNG_FILENAME, mimetype= 'image/png')







# in almost every function below we have argument 'tomo_num' - number of tomograph in TOMOGRAPHS list
@app.route('/tomograph/<int:tomo_num>/source/power-on', methods=['GET'])  # NEED TO EDIT
def source_power_on(tomo_num):
    logging.debug('\n\nREQUEST: SOURCE/POWER ON')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    """
    logging.debug('Checking tomograph...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].ping)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not reach tomograph')"""

    logging.debug('Powering on source...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].PowerOn)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not power on source')

    logging.debug('Success!')
    return create_response(True)

@app.route('/tomograph/<int:tomo_num>/source/power-off', methods=['GET'])  # QUESTION, NEED TO EDIT
def source_power_off(tomo_num):
    logging.debug('\n\nREQUEST: SOURCE/POWER OFF')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0


    logging.debug('Powering off source...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].PowerOff)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not power off source')

    logging.debug('Success!')
    return create_response(True)




@app.route('/tomograph/<int:tomo_num>/source/set-voltage', methods=['POST'])
def source_set_voltage(tomo_num):
    logging.debug('\n\nREQUEST: SOURCE/SET VOLTAGE')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, voltage, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logging.debug('Checking format...')
    if type(voltage) is not float:
        logging.debug('Incorrect format! Voltage type must be float, but it is ' + str(type(voltage)))
        return create_response(success= False, error= 'Incorrect format: type must be float')


    # TO DELETE THIS LATER
    logging.debug('Format is correct, new voltage value is %.1f...' % (voltage))
    if voltage < 2 or 60 < voltage:
        logging.debug('Voltage must have value from 2 to 60!')
        return create_response(success= False, error= 'Voltage must have value from 2 to 60')

    logging.debug('Parameters are normal, setting new voltage...')
    success, set_voltage, exception_message = try_thrice_change_attr(TOMOGRAPHS[tomo_num]['device'], "xraysource_voltage", voltage)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not set voltage')

    logging.debug('Success!')
    return create_response(success= True)

@app.route('/tomograph/<int:tomo_num>/source/set-current', methods=['POST'])
def source_set_current(tomo_num):
    logging.debug('\n\nREQUEST: SOURCE/SET CURRENT')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, current, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logging.debug('Checking format...')
    if type(current) is not float:
        logging.debug('Incorrect format! Current type must be float, but it is ' + str(type(current)))
        return create_response(success= False, error= 'Incorrect format: type must be float')


    # TO DELETE THIS LATER
    logging.debug('Format is correct, new current value is %.1f...' % (current))
    if current < 2 or 80 < current:
        logging.debug('Current must have value from 2 to 60!')
        return create_response(success= False, error= 'Current must have value from 2 to 80')

    logging.debug('Parameters are normal, setting new current...')
    success, set_current, exception_message = try_thrice_change_attr(TOMOGRAPHS[tomo_num]['device'], "xraysource_current", current)
    if success == False:
        logging.debug(exception_message)
        return create_response(success, exception_message, error= 'Could not set current')

    logging.debug('Success!')
    return create_response(success= True)




@app.route('/tomograph/<int:tomo_num>/shutter/open/<int:time>', methods=['GET'])
def shutter_open(tomo_num, time):
    logging.debug('\n\nREQUEST: SHUTTER/OPEN')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    return open_shutter(tomo_num, time)


@app.route('/tomograph/<int:tomo_num>/shutter/close/<int:time>', methods=['GET'])
def shutter_close(tomo_num, time):
    logging.debug('\n\nREQUEST: SHUTTER/CLOSE')
    tomo_num -= 1          # because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success=False, error='On this tomograph experiment is running')

    return close_shutter(tomo_num, time)



@app.route('/tomograph/<int:tomo_num>/motor/set-horizontal-position', methods=['POST'])
def motor_set_horizontal_position(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/SET HORIZONTAL POSITION')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, hor_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return set_x(tomo_num, hor_pos)

@app.route('/tomograph/<int:tomo_num>/motor/set-vertical-position', methods=['POST'])
def motor_set_vertical_position(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/SET VERTICAL POSITION')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, ver_pos, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return set_y(tomo_num, ver_pos)

@app.route('/tomograph/<int:tomo_num>/motor/set-angle-position', methods=['POST'])
def motor_set_angle_position(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/SET ANGLE POSITION')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, angle, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return set_angle(tomo_num, angle)

@app.route('/tomograph/<int:tomo_num>/motor/move-away', methods=['GET'])
def motor_move_away(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/MOVE AWAY')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    return move_away(tomo_num)

@app.route('/tomograph/<int:tomo_num>/motor/move-back', methods=['GET'])
def motor_move_back(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/MOVE BACK')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    return move_back(tomo_num)


@app.route('/tomograph/<int:tomo_num>/motor/reset-angle-position', methods=['GET'])
def motor_reset_angle_position(tomo_num):
    logging.debug('\n\nREQUEST: MOTOR/RESET ANGLE POSITION')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0

    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    return reset_angle(tomo_num)



@app.route('/tomograph/<int:tomo_num>/detector/get-frame', methods=['POST'])
def detector_get_frame(tomo_num):
    logging.debug('\n\nREQUEST: DETECTOR/GET FRAME')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, exposure, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    return get_frame(tomo_num, exposure)



def stop_experiment_because_someone(exp_id):
    exp_stop_event = create_event('message', exp_id, 'Experiment was stopped by someone')
    if send_messages_to_storage_webpage(exp_stop_event) == False:
        return
    logging.debug('\nEXPERIMENT IS STOPPED BY SOMEONE!!!\n')
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


def loop_of_get_send_frames(tomo_num, exp_id, count, exposure, frame_num, getting_frame_message, mode):
    for i in range(0, count):
        if TOMOGRAPHS[tomo_num]['experiment is running'] == False:
            stop_experiment_because_someone(exp_id)
            return False, frame_num

        logging.debug(getting_frame_message % (i))
        success, frame_dict = get_frame(tomo_num, exposure, exp_id)
        if not success:
            return False, frame_num

        frame_dict['mode'] = mode
        frame_dict['number'] = frame_num
        frame_num += 1
        frame_with_data = create_event('frame', exp_id, frame_dict)
        if send_messages_to_storage_webpage(frame_with_data) == False:
            return False, frame_num
    return True, frame_num



def carry_out_simple_experiment(tomo_num, exp_param):
    exp_id = exp_param['experiment id']
    # Closing shutter to get DARK images
    if close_shutter(tomo_num, 0, exp_id) == False:
        return

    frame_num = 0
    logging.debug('Going to get DARK images!\n')
    success, frame_num = loop_of_get_send_frames(tomo_num, exp_id, exp_param['DARK']['count'], exp_param['DARK']['exposure'],
                                                 frame_num, getting_frame_message='Getting DARK image %d from tomograph...', mode="dark")
    if not success:
        return
    logging.debug('Finished with DARK images!\n')

    if open_shutter(tomo_num, 0, exp_id) == False:
        return
    if move_away(tomo_num, exp_id) == False:
        return

    logging.debug('Going to get EMPTY images!\n')
    success, frame_num = loop_of_get_send_frames(tomo_num, exp_id, exp_param['EMPTY']['count'], exp_param['EMPTY']['exposure'],
                                                 frame_num, getting_frame_message= 'Getting EMPTY image %d from tomograph...', mode="empty")
    if not success:
        return
    logging.debug('Finished with EMPTY images!\n')

    if move_back(tomo_num, exp_id) == False:
        return
    if reset_angle(tomo_num, exp_id) == False:
        return

    logging.debug('Going to get DATA images, step count is %d!\n' % (exp_param['DATA']['step count']))
    angle_step = exp_param['DATA']['angle step']
    for i in range(0, exp_param['DATA']['step count']):
        current_angle = (round( (i*angle_step) ,  2)) % 360
        logging.debug('Getting DATA images: angle is %.2f' % current_angle)

        success, frame_num = loop_of_get_send_frames(tomo_num, exp_id, exp_param['DATA']['count per step'], exp_param['DATA']['exposure'],
                                                     frame_num, getting_frame_message= 'Getting DATA image %d from tomograph...', mode="data")
        if not success:
            return
        # Rounding angles here, not in  check_and_prepare_exp_parameters(), cause it will be more accurately this way
        new_angle = (round( (i + 1)*angle_step ,  2)) % 360
        logging.debug('Finished with this angle, turning to new angle %.2f...' % (new_angle))
        if set_angle(tomo_num, new_angle, exp_id) == False:
            return
    logging.debug('Finished with DATA images!\n')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_messages_to_storage_webpage(exp_finish_message) == False:
        return
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
    logging.debug('Experiment is done successfully!')
    return
# NEED TO EDIT
def carry_out_advanced_experiment(tomo_num, exp_param):
    exp_id = exp_param['experiment id']
    cmd_num = 0
    for command in exp_param['instruction']:
        if TOMOGRAPHS[tomo_num]['experiment is running'] == False:
            return stop_experiment_because_someone(exp_id)
        cmd_num += 1
        logging.debug('Executing command %d:' % cmd_num)

        if command['type'] == 'open shutter':
            logging.debug('Opening shutter...')
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not open shutter')
            logging.debug('Success!')

        elif command['type'] == 'close shutter':
            logging.debug('Closing shutter...')
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].OpenShutter, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not close shutter')
            logging.debug('Success!')

        elif command['type'] == 'reset current position':
            logging.debug('Resetting current position...')
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].ResetCurrentPosition, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not reset current position')
            logging.debug('Success!')

        elif command['type'] == 'go to position':
            x = str(command['args'][0])
            y = str(command['args'][1])
            angle = str(command['args'][2]/10)
            logging.debug('Changing position to:  x = ' + x + ', y = ' + y + ', angle = ' + angle + '...')
            success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].GotoPosition, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not go to position: '
                                                                     'x = ' + x + ', y = ' + y + ', angle = ' + angle)
            logging.debug('Success!')

        elif command['type'] == 'get frame':
            logging.debug('Getting image...')
            success, frame_json, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].GetFrame, command['args'])
            if success == False:
                return handle_emergency_stop(exp_id= exp_id, exception_message= exception_message,
                                             error = 'Error in command ' + str(cmd_num) + ': Could not get frame')
            logging.debug('  Got!\nSending frame to storage and web page of adjustment...')
            frame_dict = json.loads(frame_json)
            frame_with_data = create_event('frame', exp_id, frame_dict)
            if send_messages_to_storage_webpage(frame_with_data) == False:
                return
            logging.debug('Success!')

    exp_finish_message = create_event('message', exp_id, 'Experiment was finished successfully')
    if send_messages_to_storage_webpage(exp_finish_message) == False:
        return
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
    logging.debug('Experiment is done successfully!')
    return




@app.route('/tomograph/<int:tomo_num>/experiment/start', methods=['POST'])
def experiment_start(tomo_num):
    logging.debug('\n\nREQUEST: EXPERIMENT/START')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    if TOMOGRAPHS[tomo_num]['experiment is running']:
        logging.debug('On this tomograph experiment is running')
        return create_response(success= False, error= 'On this tomograph experiment is running')

    success, data, response_if_fail = check_request(request.data)
    if not success:
        return response_if_fail

    logging.debug('Checking generous format...')
    if not (('experiment parameters' in data.keys()) and ('experiment id' in data.keys())):
        logging.debug('Incorrect format of keywords!')
        return create_response(success= False, error= 'Incorrect format of keywords')

    if not ((type(data['experiment parameters']) is dict) and (type(data['experiment id']) is unicode)):
        logging.debug('Incorrect format of types!')
        return create_response(success= False, error= 'Incorrect format: incorrect types')

    logging.debug('Generous format is normal!')
    exp_param = data['experiment parameters']
    exp_id = data['experiment id']
    exp_param['experiment id'] = exp_id

    logging.debug('Checking parameters...')
    success, error = check_and_prepare_exp_parameters(exp_param)
    if not success:
        logging.debug(error)
        return create_response(success, error)

    logging.debug('Parameters are normal!')
    logging.debug('Powering on tomograph...')
    success, useless, exception_message = try_thrice_function(TOMOGRAPHS[tomo_num]['device'].PowerOn)
    if success == False:
        return create_response(success= False, exception_message= exception_message, error= 'Could not power on source')

    logging.debug('Success!')
    logging.debug('Sending to storage leading to prepare...')
    try:
        storage_resp = requests.post(STORAGE_EXPERIMENT_URI, data = request.data)
    except requests.ConnectionError as e:
        logging.debug(e.message)
        #IF UNCOMMENT   exception_message= '' '''e.message''',    OCCURS PROBLEMS WITH JSON.DUMPS(...)
        return create_response(success= False, exception_message= '' '''e.message,''',
                               error= 'Could not send to storage signal of experiment start')


    logging.debug('Sent!')
    logging.debug(type(storage_resp.content))
    logging.debug(storage_resp.content)
    storage_resp_dict = json.loads(storage_resp.content)

    if not ('result' in storage_resp_dict.keys()):
        logging.debug('Storage\'s response has incorrect format!')
        return create_response(success= False, error= 'Storage is not ready: storage\'s response has incorrect format')

    logging.debug('Storage\'s response:')
    logging.debug (storage_resp_dict['result'])
    if storage_resp_dict['result'] != 'success':
        logging.debug('Storage is NOT ready!')
        return create_response(success= False, error= 'Storage is not ready: ' + storage_resp_dict['result'])

    logging.debug('Experiment begins!')
    TOMOGRAPHS[tomo_num]['experiment is running'] = True
    if exp_param['advanced']:
        thr = threading.Thread(target = carry_out_advanced_experiment, args = (tomo_num, exp_param))
    else:
        thr = threading.Thread(target = carry_out_simple_experiment, args = (tomo_num, exp_param))
    thr.start()

    return create_response(True)


@app.route('/tomograph/<int:tomo_num>/experiment/stop', methods=['GET'])
def experiment_stop(tomo_num):
    logging.debug('\n\nREQUEST: EXPERIMENT/STOP')
    tomo_num -= 1          #because in TOMOGRAPHS list numeration begins from 0
    TOMOGRAPHS[tomo_num]['experiment is running'] = False
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
    logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'experiment.log')
    app.run(host='0.0.0.0', port=5001)







