import json
import requests

experiment = json.dumps(
    {
        'experiment_id': '552aa5546c8dc50c93edacf0',
        'advanced': False,
        'specimen': 'Gekkonidae',
        'DARK':
            {
                'count': 1,
                'exposure': 3
            },
        'EMPTY':
            {
                'count': 20,
                'exposure': 3
            },
        'DATA':
            {
                'step count': 2,
                'exposure': 3,
                'angle step': 1,
                'count per step': 1
            }
    }
)

new_mode = json.dumps(
    {
        'voltage': 20,
        'current': 22
    }
)

req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/start-experiment", data = experiment)
#req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/source/set-operating-mode", data = new_mode)
#req = requests.get('http://109.234.34.140:5001/module-experiment/v1.0/detector/get-frame/3')
print req.content

