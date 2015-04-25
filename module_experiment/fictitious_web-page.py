import json
import requests
import exceptions

experiment = json.dumps(
    {
        'experiment_id': '552aa5546c8dc50c93edacf0',
        'advanced': False,
        'specimen': 'Gekkonidae',
        'DARK':
            {
                'count': 4,
                'exposure': 5
            },
        'EMPTY':
            {
                'count': 20,
                'exposure': 3
            },
        'DATA':
            {
                'step count': 20,
                'exposure': 3,
                'angle step': 1,
                'count per step': 20
            }
    }
)

new_mode = json.dumps(
    {
        'voltage': 20,
        'current': 22
    }
)
try:
    req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/experiment/start", data = experiment)
    #req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/source/set-operating-mode", data = new_mode)
    #req = requests.get('http://109.234.34.140:5001/module-experiment/v1.0/detector/get-frame/3')
except requests.ConnectionError as e:
    print "Could not connect", e.message
else:
    print req.content

