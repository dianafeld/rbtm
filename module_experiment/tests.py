#!/usr/bin/python
import os
import unittest
import json
import module_experiment
import tempfile
import xmlrunner



SIMPLE_EXPERIMENT = json.dumps(
    {
        'experiment id': '552aa5546c8dc50c93edacf0',
        'advanced': False,
        'specimen': 'Gekkonidae',
        'DARK':   { 'count': 1,   'exposure': 0.12  },
        'EMPTY':  { 'count': 20,   'exposure': 3   },
        'DATA':   { 'step count': 1,   'exposure': 3,    'angle step': 1.34,    'count per step': 1  }
    }
)

ADVANCED_EXPERIMENT = json.dumps({
        'experiment id': '552aa5546c8dc50c93edacf0',
        'advanced': True,
        'specimen': 'Gekkonidae',
        'instruction':
            [
                {'type': 'open shutter', 'args': 0},
                {'type': 'get frame', 'args': 3.5},
                {'type': 'go to position', 'args': [0, 0, -1.495]},
                {'type': 'close shutter', 'args': 0},
                {'type': 'reset current position', 'args': None},
                {'type': 'get frame', 'args': 0.5},
            ]
        })


# New modes for source_set_operating_mode()
NEW_MODE_NORMAL = json.dumps({ 'voltage': 20,   'current': 2.2  })
NEW_MODE_LOW = json.dumps({ 'voltage': 0.1,   'current': 2.2  })
NEW_MODE_HIGH = json.dumps({ 'voltage': 85.7,   'current': 2.2  })

def response_format_is_normal(response_dict):
    RD = response_dict
    if not ('success' in RD.keys()) and ('exception message' in RD.keys()) and ('error' in RD.keys()):
        return False
    return  (type(RD['success']) is bool) and (type(RD['exception message']) is unicode) and (type(RD['error']) is unicode)

def GET_IMAGE_response_format_is_normal(response_dict):
    RD = response_dict
    if not ('success' in RD.keys()):
        return False
    if RD['success']:
        if not ('image' in RD.keys()):
            return False
        return (type(RD['success']) is bool) and (type(RD['image']) is dict)

    else:
        if not (('exception message' in RD.keys()) and ('error' in RD.keys())):
            return False
        return (type(RD['exception message']) is unicode) and (type(RD['error']) is unicode)


class ModuleExperimentTestCase2(unittest.TestCase):

    def setUp(self):
        module_experiment.app.config['TESTING'] = True
        self.app = module_experiment.app.test_client()

    def tearDown(self):
        pass


    def test_SOURCE_POWER_ON_response_format(self):
        response = self.app.get('tomograph/1/source/power-on')
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_POWER_OFF_response_format(self):
        response = self.app.get('tomograph/1/source/power-off')
        assert response_format_is_normal(json.loads(response.data))

    def test_EXPERIMENT_STOP_response_format(self):
        response = self.app.get('tomograph/1/experiment/stop')
        assert response_format_is_normal(json.loads(response.data))




    def test_SOURCE_SET_OPERATING_MODE_response_format_when_NORMAL_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-operating-mode', data= NEW_MODE_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_OPERATING_MODE_response_format_when_LOW_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-operating-mode', data= NEW_MODE_LOW)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_OPERATING_MODE_response_format_when_HIGH_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-operating-mode', data= NEW_MODE_HIGH)
        assert response_format_is_normal(json.loads(response.data))






    def test_SHUTTER_OPEN_response_format_when_POSITIVE_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/open/1')
        assert response_format_is_normal(json.loads(response.data))

    def test_SHUTTER_OPEN_response_format_when_ZERO_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/open/0')
        assert response_format_is_normal(json.loads(response.data))

    def test_SHUTTER_OPEN_response_format_when_NEGATIVE_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/open/-1')
        assert response_format_is_normal(json.loads(response.data))


    def test_SHUTTER_CLOSE_response_format_when_POSITIVE_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/close/1')
        assert response_format_is_normal(json.loads(response.data))

    def test_SHUTTER_CLOSE_response_format_when_ZERO_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/close/0')
        assert response_format_is_normal(json.loads(response.data))

    def test_SHUTTER_CLOSE_response_format_when_NEGATIVE_PARAM(self):
        response = self.app.get('/tomograph/1/shutter/close/-1')
        assert response_format_is_normal(json.loads(response.data))


    def test_DETECTOR_GET_FRAME_response_format_when_POSITIVE_PARAM(self):
        response = self.app.get('/tomograph/1/detector/get-frame/1.0')
        GET_IMAGE_response_format_is_normal(json.loads(response.data))

    def test_DETECTOR_GET_FRAME_response_format_when_NEGATIVE_PARAM(self):
        response = self.app.get('/tomograph/1/detector/get-frame/-1.0')
        GET_IMAGE_response_format_is_normal(json.loads(response.data))

    def test_DETECTOR_GET_FRAME_response_format_when_INT_INSTEAD_FLOAT_PARAM(self):
        response = self.app.get('/tomograph/1/detector/get-frame/1')
        GET_IMAGE_response_format_is_normal(json.loads(response.data))


    def test_EXPERIMENT_START_response_format_when_SIMPLE_EXPERIMENT(self):
        response = self.app.post('tomograph/1/experiment/start', data= SIMPLE_EXPERIMENT)
        assert response_format_is_normal(json.loads(response.data))

    def test_EXPERIMENT_START_response_format_when_ADVANCED_EXPERIMENT(self):
        response = self.app.post('tomograph/1/experiment/start', data= ADVANCED_EXPERIMENT)
        assert response_format_is_normal(json.loads(response.data))


if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )

