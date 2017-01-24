#!/usr/bin/python
import unittest
import json
import experiment
import xmlrunner

SIMPLE_EXPERIMENT = json.dumps(
    {
        'experiment id': '552aa5546c8dc50c93edacf0',
        'advanced': False,
        'DARK': {'count': 1, 'exposure': 0.12},
        'EMPTY': {'count': 20, 'exposure': 3},
        'DATA': {'step count': 1, 'exposure': 3, 'angle step': 1.34, 'count per step': 1}
    }
)

ADVANCED_EXPERIMENT = json.dumps({
    'experiment id': '552aa5546c8dc50c93edacf0',
    'advanced': True,
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

VOLTAGE_NORMAL = json.dumps(40.0)
VOLTAGE_LOW = json.dumps(0.1)
VOLTAGE_HIGH = json.dumps(85.7)

CURRENT_NORMAL = json.dumps(40.0)
CURRENT_LOW = json.dumps(0.1)
CURRENT_HIGH = json.dumps(85.7)

EXPOSURE_NORMAL = json.dumps(1000.0)
EXPOSURE_NEGATIVE = json.dumps(-1000.0)

X_NORMAL = json.dumps(40.0)
X_HIGH = json.dumps(10000.0)
X_LOW = json.dumps(-10000.0)

Y_NORMAL = json.dumps(40.0)
Y_HIGH = json.dumps(10000.0)
Y_LOW = json.dumps(-10000.0)

ANGLE = json.dumps(-5690.0)


def response_format_is_normal(response_dict):
    RD = response_dict
    if not ('success' in RD.keys()) and ('exception message' in RD.keys()) and (
                    'error' in RD.keys() and ('result' in RD.keys())):
        return False
    return (type(RD['success']) is bool) and (type(RD['exception message']) is unicode) and (
        type(RD['error']) is unicode)


class ModuleExperimentTestCase2(unittest.TestCase):
    def setUp(self):
        experiment.app.config['TESTING'] = True
        self.app = experiment.app.test_client()

    def tearDown(self):
        pass

    def test_SOURCE_POWER_ON_response_format(self):
        response = self.app.get('tomograph/1/source/power-on')
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_POWER_OFF_response_format(self):
        response = self.app.get('tomograph/1/source/power-off')
        assert response_format_is_normal(json.loads(response.data))

    #    def test_EXPERIMENT_STOP_response_format(self):
    #       response = self.app.get('tomograph/1/experiment/stop')
    #      assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_VOLTAGE_response_format_when_NORMAL_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-voltage', data=VOLTAGE_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_VOLTAGE_response_format_when_LOW_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-voltage', data=VOLTAGE_LOW)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_VOLTAGE_response_format_when_HIGH_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-voltage', data=VOLTAGE_HIGH)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_CURRENT_response_format_when_NORMAL_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-current', data=CURRENT_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_CURRENT_response_format_when_LOW_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-current', data=CURRENT_LOW)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_SET_CURRENT_response_format_when_HIGH_PARAM(self):
        response = self.app.post('/tomograph/1/source/set-current', data=CURRENT_HIGH)
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_GET_VOLTAGE_response(self):
        response = self.app.get('/tomograph/1/source/get-voltage')
        assert response_format_is_normal(json.loads(response.data))

    def test_SOURCE_GET_CURRENT_response(self):
        response = self.app.get('/tomograph/1/source/get-current')
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
        response = self.app.post('/tomograph/1/detector/get-frame/1.0', data=EXPOSURE_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_DETECTOR_GET_FRAME_response_format_when_NEGATIVE_PARAM(self):
        response = self.app.post('/tomograph/1/detector/get-frame/1.0', data=EXPOSURE_NEGATIVE)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_X_response_format_when_NORMAL_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-horizontal-position', data=X_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_X_response_format_when_HIGH_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-horizontal-position', data=X_HIGH)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_X_response_format_when_LOW_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-horizontal-position', data=X_LOW)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_Y_response_format_when_NORMAL_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-vertical-position', data=Y_NORMAL)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_Y_response_format_when_HIGH_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-vertical-position', data=Y_HIGH)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_Y_response_format_when_LOW_PARAM(self):
        response = self.app.post('/tomograph/1/motor/set-vertical-position', data=Y_LOW)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_SET_ANGLE_response_format(self):
        response = self.app.post('/tomograph/1/motor/set-angle-position', data=ANGLE)
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_GET_X_response_format(self):
        response = self.app.get('/tomograph/1/motor/get-horizontal-position')
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_GET_Y_response_format(self):
        response = self.app.get('/tomograph/1/motor/get-vertical-position')
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_GET_ANGLE_response_format(self):
        response = self.app.get('/tomograph/1/motor/get-angle-position')
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_RESET_ANGLE_response_format(self):
        response = self.app.get('/tomograph/1/motor/reset-angle-position')
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_MOVE_AWAY_response_format(self):
        response = self.app.get('/tomograph/1/motor/move-away')
        assert response_format_is_normal(json.loads(response.data))

    def test_MOTOR_MOVE_BACK_response_format(self):
        response = self.app.get('/tomograph/1/motor/move-back')
        assert response_format_is_normal(json.loads(response.data))

    def test_EXPERIMENT_START_response_format_when_SIMPLE_EXPERIMENT(self):
        response = self.app.post('tomograph/1/experiment/start', data=SIMPLE_EXPERIMENT)
        assert response_format_is_normal(json.loads(response.data))

        # def test_EXPERIMENT_START_response_format_when_ADVANCED_EXPERIMENT(self):
        #    response = self.app.post('tomograph/1/experiment/start', data= ADVANCED_EXPERIMENT)
        #    assert response_format_is_normal(json.loads(response.data))


if __name__ == '__main__':
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )
