#!/usr/bin/python
from flask import Flask, jsonify
from flask import url_for
from flask import abort
from flask import request
from flask import make_response
import json
import PyTango
import requests
import threading

app = Flask(__name__)


STORAGE_URI = "http://109.234.34.140:5020/fictitious-storage"
#STORAGE_URI = "http://109.234.34.140:5000/storage/frames"

WEBPAGE_URI = "http://109.234.34.140:5021/fictitious-webpage"


EXP_FINISH_MESSAGE = json.dumps({u'type': 'message', u'message': 'Experiment was finished successfully'})
EXP_STOP_MESSAGE = json.dumps({u'type': 'message', u'message': 'Experiment was stopped by someone'})
EXP_EMERGENCY_DICT_TEMPLATE = {u'type': 'message', u'message': 'Experiment was emergency stopped', u'error': '', u'exception message': ''}


TOMOGRAPHS = (
    {
        'id': 1,
        'address': '46.101.31.93:10000/tomo/tomograph/1',
        'experiment is running': False,
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

'''def try_connect_tomograph(tomograph_URI):
    success = True
    error = ''
    exception_message = ''
    for i in range(0, 3):
        try:
            tomograph = PyTango.DeviceProxy(tomograph_URI)
        except PyTango.DevFailed as e:
            success = False
            error = 'Could not connect to tomograph'
            exception_message = e[0].desc
        else:
            break
    return success, tomograph, error, exception_message

def try_source_power_on(tomograph):
    success = True
    error = ''
    exception_message = ''
    for i in range(0, 3):
        try:
            tomograph.PowerOn()
        except PyTango.DevFailed as e:
            success = False
            error = 'Could not power on source'
            exception_message = e[0].desc
        else:
            break
    return success, error, exception_message

def try_source_power_off(tomograph):
    success = True
    error = ''
    exception_message = ''
    for i in range(0, 3):
        try:
            tomograph.PowerOff()
        except PyTango.DevFailed as e:
            success = False
            error = 'Could not power on source'
            exception_message = e[0].desc
        else:
            break
    return success, error, exception_message'''


@app.route('/module-experiment/v1.0/source/power-on', methods=['GET'])
def source_power_on():
    print '\n\nREQUEST: SOURCE/POWER ON'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nPowering on...'
        success, useless, exception_message = try_something_thrice(tomograph.PowerOn)
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not power on source',
                            'exception message': exception_message})
        else:
            print 'Powered on!'
            return jsonify({'success': True})

@app.route('/module-experiment/v1.0/source/power-off', methods=['GET'])
def source_power_off():
    print '\n\nREQUEST: SOURCE/POWER OFF'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nPowering on...'
        success, useless, exception_message = try_something_thrice(tomograph.PowerOff)
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not power off source',
                            'exception message': exception_message})
        else:
            print 'Powered off!'
            return jsonify({'success': True})

@app.route('/module-experiment/v1.0/source/set-operating-mode', methods=['POST'])
def source_set_operating_mode():
    print '\n\nREQUEST: SOURCE/SET OPERATING MODE'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nChecking request...'
        if not request.data:
            print 'Request\'s JSON is empty!'
            abort(400)
        print 'Request is not empty!'
        req_dict = json.loads(request.data)
        print 'Checking parameters...'
        if not ((u'voltage' in req_dict.keys()) and (u'current' in req_dict.keys())):
            print 'Incorrect format!'
            abort(400)
        print 'Request is not empty, setting operating mode...'
        success, useless, exception_message = try_something_thrice(tomograph.SetOperatingMode, [req_dict[u'voltage'], req_dict[u'current']])
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not set operating mode',
                            'exception message': exception_message})
        else:
            print 'New mode is set!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/shutter/open/<int:time>', methods=['GET'])
def shutter_open(time):
    print '\n\nREQUEST: SHUTTER/OPEN'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nOpening shutter...'
        success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, time)
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not open shutter',
                            'exception message': exception_message})
        else:
            print 'Shutter is opened!'
            return jsonify({'success': True})

@app.route('/module-experiment/v1.0/shutter/close/<int:time>', methods=['GET'])
def shutter_close(time):
    print '\n\nREQUEST: SHUTTER/CLOSE'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nClosing shutter...'
        success, useless, exception_message = try_something_thrice(tomograph.CloseShutter, time)
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not close shutter',
                            'exception message': exception_message})
        else:
            print 'Shutter is closed!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/detector/get-frame/<int:exposure>', methods=['GET'])
def detector_get_frame(exposure):
    print '\n\nREQUEST: DETECTOR/GET FRAME'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})

    else:
        print 'Connected!\nGetting frame...'
        success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exposure)
        if success == False:
            print exception_message
            return jsonify({'success': False,
                            'error' : 'Could not get frame',
                            'exception message': exception_message})
        else:
            frame_dict = json.loads(frame_json)
            print 'Frame is got!'
            return jsonify({'success': True,
                            'image' : frame_dict})




def send_messages_to_storage_webpage(message, tomograph_num):    # MAYBE NEED TO EDIT
    print 'Sending to storage...'
    try:
        req_storage = requests.post(STORAGE_URI, data = message)
    except requests.ConnectionError as e:
        print e.message
        TOMOGRAPHS[tomograph_num]['experiment is running'] = False
        TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was emergency stopped'
        TOMOGRAPHS[tomograph_num]['error'] = 'Could not send to storage'
        TOMOGRAPHS[tomograph_num]['exception message'] = e.message
        # sending message to web page of adjustment
        exp_emergency_dict = EXP_EMERGENCY_DICT_TEMPLATE.copy()
        exp_emergency_dict[u'error'] = 'Could not send to storage'
        #exp_emergency_dict[u'exception message'] = e.message  -IF UNCOMMENT THIS, OCCURS PROBLEMS WITH JSON.DUMPS(...)
        exp_emergency_message = json.dumps(exp_emergency_dict)
        print '\nEXPERIMENT IS EMERGENCY STOPPED!!!\n'
        print 'Sending to web page that we could send to storage...'
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = exp_emergency_message)
        except requests.ConnectionError as e:
            pass
        else:
            print req_webpage.content
        return False

    else:
        print req_storage.content
        print 'Sending to web page...'
        try:
            req_webpage = requests.post(WEBPAGE_URI, data = message)
        except requests.ConnectionError as e:
            pass
        else:
            print req_webpage.content
        return True

def handle_emergency_stop(tomograph_num, exception_message, error):
    print exception_message
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was emergency stopped'
    TOMOGRAPHS[tomograph_num]['error'] = error
    TOMOGRAPHS[tomograph_num]['exception message'] = exception_message
    # sending emergency messages to storage and web page of adjustment
    exp_emergency_dict = EXP_EMERGENCY_DICT_TEMPLATE.copy()
    exp_emergency_dict[u'error'] = error
    exp_emergency_dict[u'exception message'] = exception_message
    exp_emergency_message = json.dumps(exp_emergency_dict)
    send_messages_to_storage_webpage(exp_emergency_message)
    print '\nEXPERIMENT IS EMERGENCY STOPPED!!!\n'

def check_exp_parameters(exp_param):
    if not ((u'experiment_id' in exp_param.keys()) and (u'advanced' in exp_param.keys()) and (u'specimen' in exp_param.keys())):
        return False, 'Incorrect format'
    if exp_param[u'advanced']:
        return False, 'Incorrect format'                       #TO DO
    else:
        if not ((u'DARK' in exp_param.keys()) and (u'EMPTY' in exp_param.keys()) and (u'DATA' in exp_param.keys())):
            return False
        DARK_format_normal = (u'count' in exp_param[u'DARK'].keys()) and (u'exposure' in exp_param[u'DARK'].keys())
        EMPTY_format_normal = (u'count' in exp_param[u'EMPTY'].keys()) and (u'exposure' in exp_param[u'EMPTY'].keys())
        DATA_format_normal_1 = (u'step count' in exp_param[u'DATA'].keys()) and (u'exposure' in exp_param[u'DATA'].keys())
        DATA_format_normal_2 = (u'angle step' in exp_param[u'DATA'].keys()) and (u'count per step' in exp_param[u'DATA'].keys())
        if not (DARK_format_normal and EMPTY_format_normal and DATA_format_normal_1 and DATA_format_normal_2):
            return False, 'Incorrect format'

        DARK_param_normal = exp_param[u'DARK'][u'exposure'] > 0
        EMPTY_param_normal = exp_param[u'EMPTY'][u'exposure'] > 0
        DATA_param_normal = exp_param[u'DATA'][u'exposure'] > 0
        if not (DARK_param_normal and EMPTY_param_normal and DATA_param_normal):
            return False, 'Bad parameters'
        else:
            return True, ''

def prepare_frame_to_send(frame_json, exp_id, specimen):
    frame_dict = json.loads(frame_json)
    frame_dict[u'type'] = 'image'
    frame_dict[u'experiment_id'] = exp_id
    frame_dict[u'specimen'] = specimen
    return json.dumps(frame_dict)



def carry_out_experiment(tomograph, tomograph_num, exp_param):
    exp_id = exp_param[u'experiment_id']
    print 'Connected!\nPowering on...'
    success, useless, exception_message = try_something_thrice(tomograph.PowerOn)
    if success == False:
        handle_emergency_stop(tomograph_num, exception_message, error = 'Could not power on source')
        return

    print 'Powered on!\nClosing shutter...'
    success, useless, exception_message = try_something_thrice(tomograph.CloseShutter, 0)
    if success == False:
        handle_emergency_stop(tomograph_num, exception_message, error = 'Could not close shutter')
        return

    print '\nGoing to get DARK images!'
    for i in range(0, exp_param[u'DARK'][u'count']):
        if TOMOGRAPHS[0]['experiment is running'] == False:
            if send_messages_to_storage_webpage(EXP_STOP_MESSAGE, tomograph_num) == False:
                return
            print '\nEXPERIMENT IS STOPPED BY SOMEONE!!!\n'
            TOMOGRAPHS[0]['experiment state'] = 'Experiment was stopped by someone'
            return

        print '  Getting DARK image %d from tomograph...' % (i)
        success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exp_param[u'DARK'][u'exposure'])
        if success == False:
            handle_emergency_stop(tomograph_num, exception_message, error = 'Could not get frame')
            return

        print '  Got image!'
        frame_json = prepare_frame_to_send(frame_json, exp_id, exp_param[u'specimen'])
        if send_messages_to_storage_webpage(frame_json, tomograph_num) == False:
            return
    print '  Finished with DARK images!'

    print 'Opening shutter...'
    success, useless, exception_message = try_something_thrice(tomograph.OpenShutter, 0)
    if success == False:
        handle_emergency_stop(tomograph_num, exception_message, error = 'Could not open shutter')
        return

    print 'Resetting current position...'
    success, useless, exception_message = try_something_thrice(tomograph.ResetCurrentPosition)
    if success == False:
        handle_emergency_stop(tomograph_num, exception_message, error = 'Could not reset current position')
        return

    angle_step = exp_param[u'DATA'][u'angle step']
    print '\nGoing to get DATA images, step count is %d!' % (exp_param[u'DATA'][u'step count'])
    for i in range(1, exp_param[u'DATA'][u'step count']):
        print '  Getting DATA images: angle is %d' % (((i-1) * angle_step)%3600)
        for j in range(0, exp_param[u'DATA'][u'count per step']):
            if TOMOGRAPHS[tomograph_num]['experiment is running'] == False:
                if send_messages_to_storage_webpage(EXP_STOP_MESSAGE, tomograph_num) == False:
                    return
                print '\nEXPERIMENT IS STOPPED BY SOMEONE!!!\n'
                TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was stopped by someone'
                return

            print '    Getting image %d from tomograph...' % (j)
            success, frame_json, exception_message = try_something_thrice(tomograph.GetFrame, exp_param[u'DARK'][u'exposure'])
            if success == False:
                handle_emergency_stop(tomograph_num, exception_message, error = 'Could not get frame')
                return

            print '    Got image!'
            frame_json = prepare_frame_to_send(frame_json, exp_id, exp_param[u'specimen'])
            if send_messages_to_storage_webpage(frame_json, tomograph_num) == False:
                return
        print '    Finished with this angle, turning to new angle %d...' % ((i * angle_step)%3600)
        success, frame_json, exception_message = try_something_thrice(tomograph.GotoPosition, [0, 0, (i * angle_step)%3600])
        if success == False:
            handle_emergency_stop(tomograph_num, exception_message, error = 'Could not turn motor')
            return

        print '    Turned!'
    print '  Finished with DATA images!'
    if send_messages_to_storage_webpage(EXP_FINISH_MESSAGE, tomograph_num) == False:
        return
    TOMOGRAPHS[tomograph_num]['experiment state'] = 'Experiment was finished successfully'
    TOMOGRAPHS[tomograph_num]['experiment is running'] = False
    print 'Experiment is done successfully!'
    return




@app.route('/module-experiment/v1.0/experiment/start', methods=['POST'])
def experiment_start():
    print '\n\nREQUEST: EXPERIMENT/START'
    if TOMOGRAPHS[0]['experiment is running']:
        print 'On this tomograph experiment is running'
        return jsonify({'success': False,
                        'error'  : 'On this tomograph experiment is running',
                        'exception message': ''})

    print 'Connecting to tomograph...'
    success, tomograph, exception_message = try_something_thrice(PyTango.DeviceProxy, TOMOGRAPHS[0]['address'])
    if success == False:
        print exception_message
        return jsonify({'success': False,
                        'error'  : 'Could not connect to tomograph',
                        'exception message': exception_message})
    else:
        print 'Connected!\nChecking request...'
        if not request.data:
            print 'Request\'s JSON is empty!'
            abort(400)
        print 'Request is not empty!'
        exp_param = json.loads(request.data)
        print 'Checking parameters...'
        success, error = check_exp_parameters(exp_param)
        if not success:
            print error
            return jsonify({'success': False,
                            'error' : error})
        else:
            print 'Parameters are normal, experiment begins!'
            TOMOGRAPHS[0]['experiment is running'] = True
            TOMOGRAPHS[0]['experiment state'] = 'Experiment is running'
            thr = threading.Thread(target = carry_out_experiment, args = (tomograph, 0, exp_param))
            thr.start()

            return jsonify({'success': True,
                            'result' : 'Experiment has begun'})

@app.route('/module-experiment/v1.0/experiment/get-state', methods=['GET'])
def experiment_get_state():
    print '\n\nREQUEST: EXPERIMENT/GET STATE'
    return jsonify({'is running': TOMOGRAPHS[0]['experiment is running'],
                    'state': TOMOGRAPHS[0]['experiment state']})

@app.route('/module-experiment/v1.0/experiment/stop', methods=['GET'])
def experiment_stop():
    print '\n\nREQUEST: EXPERIMENT/STOP'
    TOMOGRAPHS[0]['experiment is running'] = False
    return jsonify({'success': True})




@app.errorhandler(400)
def incorrect_format(error):
    return make_response(jsonify({'success': False,
                                  'error' : 'Incorrect format'}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'success': False,
                                  'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'success': False,
                                  'error': 'Internal Server Error'}), 500)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5001)







