import json
import requests

MODULE_EXPERIMENT_URI = "http://109.234.34.140:5002"
#MODULE_EXPERIMENT_URI = "http://109.234.34.140:5002"


simple_experiment = json.dumps(
    {
        # SOMETHING FOR STORAGE (tags, username, description of experiment, number of tomograph)
        # .........
        'experiment id': '553e898c6c8dc562738e925a',
        'experiment parameters':
            {
                'advanced': False,
                'DARK':
                    {
                        'count': 2,
                        'exposure': 0.12
                    },
                'EMPTY':
                    {
                        'count': 2,
                        'exposure': 3.9
                    },
                'DATA':
                    {
                        'step count': 2,
                        'exposure': 3.9,
                        'angle step': 40.5,
                        'count per step': 2
                    }
            },
    }
)

advanced_experiment = json.dumps(
    {
        'experiment id': '552aa5546c8dc50c93edacf0',
        'experiment parameters':
            {
            'advanced': True,
            'instruction':
                [
                    {'type': 'open shutter', 'args': 0},
                    {'type': 'get frame', 'args': 3.5},
                    {'type': 'close shutter', 'args': 0},
                    {'type': 'reset current position', 'args': None},
                    {'type': 'get frame', 'args': 0.5},
                ]
            }
        }
)

new_voltage = json.dumps(25.5)
new_current = json.dumps(25.5)
exposure = json.dumps(3.6)
new_pos = json.dumps(5.5)

try:

    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-on")
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-off")
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-voltage", data = new_voltage)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-current", data = new_current)

    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-horizontal-position", data = new_pos)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-vertical-position", data = new_pos)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-angle-position", data = new_pos)
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/reset-angle-position", data = new_pos)

    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/get-frame", data = exposure)
    req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/start", data = simple_experiment)
    #req = requests.get("http://109.234.34.140:5005/get-image")
except requests.ConnectionError as e:
    print "Could not connect", e.message
else:
    print req.content


future_advanced_experiment = json.dumps(
    {
        # something for storage#
        ########################

        'experiment id': '552aa5546c8dc50c93edacf0',
        'experiment parameters':
            {
            'advanced': True,
            'instruction':
                [
                    5,                # repeat times
                    {'type': 'open shutter', 'args': 0},
                    {'type': 'get frame', 'args': 3.5, 'repeat': 10},
                    [
                        3,
                        {'type': 'get frame', 'args': 3.5, 'repeat': 10},
                        {'type': 'set angle', 'args': 10.6},
                        {'type': 'reset current position', 'args': None},
                    ],
                    [
                        4,
                        {'type': 'get frame', 'args': 3.5, 'repeat': 10},
                        {'type': 'set angle', 'args': 20},
                        {'type': 'reset current position', 'args': None},
                    ],
                ]
            }
        }
)