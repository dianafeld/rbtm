import json
import requests

simple_experiment = json.dumps(
    {
        'experiment id': '553e898c6c8dc562738e925a',
        'advanced': False,
        'specimen': 'Gekkonidae',
        'DARK':
            {
                'count': 2,
                'exposure': 0.12
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
                'angle step': 1.34,
                'count per step': 2
            }
    }
)

advanced_experiment = json.dumps({
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

new_simple_experiment = json.dumps(
    {
        'experiment id': '553e898c6c8dc562738e925a',
        'for storage':
            {
              'something': 'bla bla',
            },
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
                        'count': 20,
                        'exposure': 3
                    },
                'DATA':
                    {
                        'step count': 2,
                        'exposure': 3,
                        'angle step': 1.34,
                        'count per step': 2
                    }
            },
    }
)

new_mode = json.dumps(
    {
        'voltage': 'd',
        'current': 10.1
    }
)
try:
    #req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/experiment/start", data = experiment)
    #req = requests.post("http://109.234.34.140:5001/module-experiment/v1.0/source/set-operating-mode", data = new_mode)
    #req = requests.get('http://109.234.34.140:5001/module-experiment/v1.0/detector/get-frame/3')


    req = requests.post("http://109.234.34.140:5001/tomograph/1/experiment/start", data = advanced_experiment)
    #req = requests.post("http://109.234.34.140:5001/tomograph/1/source/set-operating-mode", data = new_mode)
    #req = requests.get('http://109.234.34.140:5001/tomograph/1/detector/get-frame/3.0')
except requests.ConnectionError as e:
    print "Could not connect", e.message
else:
    print req.content

