import json
import requests

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

advanced_experiment = json.dumps({
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
        })

new_voltage = json.dumps(25)
new_current = json.dumps(25)
exposure = json.dumps(3.6)
new_y = json.dumps(3.6)

try:
    req = requests.post("http://109.234.34.140:5001/tomograph/1/experiment/start", data = simple_experiment)
    #req = requests.post("http://109.234.34.140:5001/tomograph/1/source/set-voltage", data = new_voltage)
    #req = requests.post("http://109.234.34.140:5001/tomograph/1/source/set-current", data = new_current)
    #req = requests.post('http://109.234.34.140:5001/tomograph/1/motor/set-vertical-position', data = new_y)
    #req = requests.post('http://109.234.34.140:5001/tomograph/1/detector/get-frame', data = exposure)
except requests.ConnectionError as e:
    print "Could not connect", e.message
else:
    print req.content

