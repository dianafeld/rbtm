import json
import requests

experiment = json.dumps(
    {
    'specimen': 'Gekkonidae',
    'DARK':
        {
            'count': 100,
            'exposure':3
        },
    'EMPTY':
        {
            'count': 20,
            'exposure': 3
        },
    'DATA':
        {
            'step count': 10,
            'exposure':3,
            'angle step': 1,
            'count per step': 100
        }
    }
)

new_mode = json.dumps(
    {
        'voltage': 22,
        'current': 22
    }
)

req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/start-experiment", data = experiment)
#req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/source/set-operating-mode", data = new_mode)
#req = requests.get('http://109.234.34.140:5001/module-experiment/v1.0/detector/get-frame/3')
print req.content

