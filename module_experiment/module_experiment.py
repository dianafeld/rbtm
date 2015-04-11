#!/usr/bin/python
from flask import Flask, jsonify
from flask import url_for
from flask import abort
from flask import request
from flask import make_response
import PyTango
import requests





app = Flask(__name__)

tomographs = (
    {
        'id': 1,
		'address': '46.101.31.93:10000/tomo/tomograph/1',
		'is busy': False,
        'current': 1,
		'voltage': 1,
		'current experiment':
			{
				'user': 'Malay',
			}
    },
)




@app.route('/module-experiment/v1.0/source/power-on', methods=['GET'])
def source_power_on():
    print 'Try to power on...'
    try:
        tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomoraph/1')
    except PyTango.DevFailed as e:
        print 'Fail!'
        return jsonify({"Failed to create proxy to 46.101.31.93:10000/tomo/tomoraph/1:\n": e.message})
    else:
        tomograph.PowerOn()
        print 'Powered on!'
        return jsonify({'result': True})


@app.route('/module-experiment/v1.0/source-power-off', methods=['GET'])
def source_power_off():
    tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    tomograph.PowerOff()
    print 'power off, paskuda'
    return jsonify({'result': True})


@app.route('/module-experiment/v1.0/shutter/open/<int:time>', methods=['GET'])
def shutter_open(time):
    tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    tomograph.OpenShutter(time)
    print 'open shutter'
    return jsonify({'result': True})


@app.route('/module-experiment/v1.0/shutter/close/<int:time>', methods=['GET'])
def shutter_close(time):
    tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    tomograph.CloseShutter(time)
    print 'shut up shutter'
    return jsonify({'result': True})


@app.route('/module-experiment/v1.0/detector/get-frame/<int:exposure>', methods=['GET'])
def detector_get_frame(exposure):
    tomograph = PyTango.DeviceProxy('46.101.31.93:10000/tomo/tomograph/1')
    print 'get frame'
    return tomograph.GetFrame(exposure)






@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Vasya, ara, cho za huynya, brat?'}), 500)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)






