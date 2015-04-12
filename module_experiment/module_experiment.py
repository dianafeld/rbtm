#!/usr/bin/python
from flask import Flask, jsonify
from flask import url_for
from flask import abort
from flask import request
from flask import make_response
import json
import PyTango
import requests





app = Flask(__name__)

tomographs = (
    {
        'id': 1,
        'address': '46.101.31.93:10000/tomo/tomograph/1',
    },
)





@app.route('/module-experiment/v1.0/source/power-on', methods=['GET'])
def source_power_on():
    print 'Try to power on...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        tomograph.PowerOn()
        print 'Powered on!'
        return jsonify({'result': True})



@app.route('/module-experiment/v1.0/source-power-off', methods=['GET'])
def source_power_off():
    print 'Try to power off...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        tomograph.PowerOff()
        print 'Powered off!'
        return jsonify({'result': True})



@app.route('/module-experiment/v1.0/shutter/open/<int:time>', methods=['GET'])
def shutter_open(time):
    print 'Try to open shutter...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        tomograph.OpenShutter(time)
        print 'Shutter is opened!'
        return jsonify({'result': True})



@app.route('/module-experiment/v1.0/shutter/close/<int:time>', methods=['GET'])
def shutter_close(time):
    print 'Try to close shutter...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        tomograph.CloseShutter(time)
        print 'Shutter is closed!'
        return jsonify({'result': True})



@app.route('/module-experiment/v1.0/detector/get-frame/<int:exposure>', methods=['GET'])
def detector_get_frame(exposure):
    print 'Try to get frame...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        print 'Frame is got!'
        return tomograph.GetFrame(exposure)





@app.route('/module-experiment/v1.0/start-experiment', methods=['POST'])
def start_experiment():
    print 'Experiment must start!\nConnenting to tomograph...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    except PyTango.DevFailed as e:
        print 'Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1 !' 
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomograph/1:\n": e[-1].desc})
    else:
        print 'Connected!\nChecking request...'
        if not request.data:
            print 'Request\'s JSON is empty!'
            abort(400)
        print 'Request is not empty, experiment begins!'
        exData = json.loads(request.data)
        tomograph.PowerOff()
        tomograph.CloseShutter(0)
        print '\nGoing to get DARK images!'
        for i in range(0, exData[u'DARK'][u'count']):
            print '  Getting DARK image %d from tomograph...'%(i)
            exImage = tomograph.GetFrame(exData[u'DARK'][u'exposure'])
            print '  Got image!\n  Sending it to storage...'
            req = requests.post("http://109.234.34.140:5001/instead-of-storage", data = exImage)
            req_dict = json.loads(req.content)
            print '  Sent! Response from storage:'
            print '  ' + req_dict['result']
        print '  Finished with DARK images!'
            
        tomograph.PowerOn()
        tomograph.OpenShutter(0)
        x, y, start_angle = tomograph.CurrentPosition()
        angle_step = exData[u'DATA'][u'angle step']
        print '\nGoing to get DATA images, step count is %d!'% (exData[u'DATA'][u'step count'])
        for i in range(1, exData[u'DATA'][u'step count']):
            print '  Getting DATA images: angle is %d' %(start_angle - (i-1) * angle_step)
            for j in range(0, exData[u'DATA'][u'count per step']):
                print '    Getting image %d from tomograph...'%(j)
                exImage = tomograph.GetFrame(exData[u'DATA'][u'exposure'])
                print '    Got image!\n    Sending it to storage...'
                req = requests.post("http://109.234.34.140:5001/instead-of-storage", data = exImage)
                req_dict = json.loads(req.content) 
                print '    Sent! Response from storage:'
                print '    ' + req_dict[u'result']
            print '    Finished with this angle, turning to new angle %d...' %(start_angle - i * angle_step)
            try:
                tomograph.GotoPosition([x, y, start_angle - i * angle_step])
            except PyTango.DevFailed as e:
                print '    Couldn\'t turn: ' + e[-1].desc
            else:
                print '    Turned!'
        print '  Finished with DATA images!'
        print 'Experiment is done successfully!'
        return jsonify({'result': 'Experiment is done successfully'})








@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)



if __name__ == '__main__':
    app.run(host='0.0.0.0')






