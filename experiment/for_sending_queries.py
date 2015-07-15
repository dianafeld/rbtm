import json
import requests

MODULE_EXPERIMENT_URI = "http://109.234.34.140:5001"
#MODULE_EXPERIMENT_URI = "http://109.234.34.140:5002"


simple_experiment = json.dumps(
    {
        # SOMETHING FOR STORAGE (tags, username, description of experiment, number of tomograph)
        # .........
        'experiment id': '553e898c6c8dc562738e9271',
        'experiment parameters':
            {
                'advanced': False,
                'DARK':
                    {
                        'count': 2,
                        'exposure': 1000.0,
                        },
                'EMPTY':
                    {
                        'count': 2,
                        'exposure': 1000.0,
                    },
                'DATA':
                    {
                        'step count': 2,
                        'exposure': 1000.0,
                        'angle step': 40.5,
                        'count per step': 2,
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

new_voltage = json.dumps(50.0)
new_current = json.dumps(20.0)
exposure = json.dumps(1000.0)
new_pos = json.dumps(5.0)

try:

    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-on")
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-off")
    req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-voltage", data = new_voltage)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-current", data = new_current)

    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/shutter/open/0")
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-horizontal-position", data = new_pos)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-vertical-position", data = new_pos)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-angle-position", data = new_pos)
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/reset-angle-position", data = new_pos)
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/move-away")
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/move-back")

    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/get-frame", data = exposure)
    #req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/start", data = simple_experiment)
    #req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/stop")


    #req = requests.get("http://109.234.34.140:5005/get-image")
except requests.ConnectionError as e:
    print "Could not connect", e.message
else:
    print req.content


