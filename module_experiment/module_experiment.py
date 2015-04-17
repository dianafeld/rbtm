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


STORAGE_URI = "http://109.234.34.140:5020/fictitious-storage"
#STORAGE_URI = "http://109.234.34.140:5000/storage/frames"


app = Flask(__name__)

tomographs = (
    {
        'id': 1,
        'address': '46.101.31.93:10000/tomo/tomograph/1',
        'stop experiment': False,
        'experiment result': 'Experiment is finished successfully'
    },
)





@app.route('/module-experiment/v1.0/source/power-on', methods=['GET'])
def source_power_on():
    print '\n\nREQUEST: SOURCE/POWER ON'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!'
        try:
            print 'Powering on...'
            tomograph.PowerOn()
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'Powered on!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/source/power-off', methods=['GET'])
def source_power_off():
    print '\n\nREQUEST: SOURCE/POWER OFF'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!'
        try:
            print 'Powering off...'
            tomograph.PowerOff()
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'Powered off!'
            return jsonify({'success': True})


@app.route('/module-experiment/v1.0/source/set-operating-mode', methods=['POST'])
def source_set_operating_mode():
    print '\n\nREQUEST: SOURCE/SET OPERATING MODE'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!\nChecking request...'
        if not request.data:
            print 'Request\'s JSON is empty!'
            abort(400)
        print 'Request is not empty, setting operating mode...'
        req_dict = json.loads(request.data)
        try:
            tomograph.SetOperatingMode([req_dict[u'voltage'], req_dict[u'current']])
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'New mode is set!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/shutter/open/<int:time>', methods=['GET'])
def shutter_open(time):
    print '\n\nREQUEST: SHUTTER/OPEN'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!'
        try:
            print 'Opening shutter...'
            tomograph.OpenShutter(time)
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'Shutter is opened!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/shutter/close/<int:time>', methods=['GET'])
def shutter_close(time):
    print '\n\nREQUEST: SHUTTER/CLOSE'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!'
        try:
            print 'Closing shutter...'
            tomograph.CloseShutter(time)
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'Shutter is closed!'
            return jsonify({'success': True})



@app.route('/module-experiment/v1.0/detector/get-frame/<int:exposure>', methods=['GET'])
def detector_get_frame(exposure):
    print '\n\nREQUEST: DETECTOR/GET FRAME'
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!'
        try:
            print 'Getting frame...'
            frame_dict = json.loads(tomograph.GetFrame(exposure))
        except PyTango.DevFailed as e:
            print e[0].desc
            return jsonify({'success': False,
                            'error' : e[0].desc})
        else:
            print 'Frame is got!'
            return jsonify({'success': True,
                            'image' : frame_dict})


def carry_out_experiment(tomograph, exp_param):
    tomograph.PowerOff()
    tomograph.CloseShutter(0)
    print '\nGoing to get DARK images!'
    for i in range(0, exp_param[u'DARK'][u'count']):
        if tomographs[0]['stop experiment']:
            print '\nEXPERIMENT IS STOPPED!!!\n'
            tomographs[0]['experiment result'] = 'Experiment was stopped'
            return

        print '  Getting DARK image %d from tomograph...'%(i)
        image_json = tomograph.GetFrame(exp_param[u'DARK'][u'exposure'])
        print '  Got image!\n  Sending it to storage...'
        image_dict = json.loads(image_json)
        image_dict[u'experiment_id'] = '552aa5546c8dc50c93edacf0'
        image_json = json.dumps(image_dict)
        req = requests.post(STORAGE_URI, data = image_json)
        print '  Sent! Response from storage:'
        print req.content
    print '  Finished with DARK images!'

    tomograph.PowerOn()
    tomograph.OpenShutter(0)
    x, y, start_angle = tomograph.CurrentPosition()
    angle_step = exp_param[u'DATA'][u'angle step']
    print '\nGoing to get DATA images, step count is %d!'% (exp_param[u'DATA'][u'step count'])
    for i in range(1, exp_param[u'DATA'][u'step count']):
        print '  Getting DATA images: angle is %d' %(start_angle - (i-1) * angle_step)
        for j in range(0, exp_param[u'DATA'][u'count per step']):
            if tomographs[0]['stop experiment']:
                print '\nEXPERIMENT IS STOPPED!!!\n'
                tomographs[0]['experiment result'] = 'Experiment was stopped'
                return
            print '    Getting image %d from tomograph...'%(j)
            image_json = tomograph.GetFrame(exp_param[u'DATA'][u'exposure'])
            print '    Got image!\n    Sending it to storage...'
            image_dict = json.loads(image_json)
            image_dict[u'experiment_id'] = '552aa5546c8dc50c93edacf0'
            image_json = json.dumps(image_dict)
            req = requests.post(STORAGE_URI, data = image_json)
            print '    Sent! Response from storage:'
            print req.content
        print '    Finished with this angle, turning to new angle %d...' %(start_angle - i * angle_step)
        try:
            tomograph.GotoPosition([x, y, start_angle - i * angle_step])
        except PyTango.DevFailed as e:
            print '    Couldn\'t turn: ' + e[0].desc
        else:
            print '    Turned!'
    print '  Finished with DATA images!'
    print 'Experiment is done successfully!'
    tomographs[0]['experiment result'] = 'Experiment is finished successfully'
    return



@app.route('/module-experiment/v1.0/start-experiment', methods=['POST'])
def start_experiment():
    print '\n\nREQUEST: START EXPERIMENT'
    tomographs[0]['stop experiment'] = False
    try:
        print 'Connecting to tomograph...'
        tomograph = PyTango.DeviceProxy(tomographs[0]['address'])
    except PyTango.DevFailed as e:
        print e[0].desc
        return jsonify({'success': False,
                        'error' : e[0].desc})
    else:
        print 'Connected!\nChecking request...'
        if not request.data:
            print 'Request\'s JSON is empty!'
            abort(400)
        print 'Request is not empty, experiment begins!'
        exp_param = json.loads(request.data)
        thr = threading.Thread(target = carry_out_experiment, args = (tomograph, exp_param))
        thr.start()

        return jsonify({'success': True,
                        'result' : 'experiment has begun'})


@app.route('/module-experiment/v1.0/get-experiment-result', methods=['GET'])
def get_experiment_result():
    print '\n\nREQUEST: GET EXPERIMENT RESULT'
    return jsonify({'success': True,
                    'result': tomographs[0]['experiment result']})


@app.route('/module-experiment/v1.0/stop-experiment', methods=['GET'])
def stop_experiment():
    print '\n\nREQUEST: STOP EXPERIMENT'
    tomographs[0]['stop experiment'] = True
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







