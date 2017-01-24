from __future__ import print_function
from __future__ import print_function
import json
import requests

MODULE_EXPERIMENT_URI = "http://109.234.38.83:5001"
# MODULE_EXPERIMENT_URI = "http://localhost:5001"


simple_experiment = json.dumps(
    {
        # SOMETHING FOR STORAGE (tags, username, description of experiment, number of tomograph)
        # .........
        'exp_id': '553e898c6c8dc562738e9294',
        'experiment parameters':
            {
                'advanced': False,
                'DARK':
                    {
                        'count': 1,
                        'exposure': 1000.0,
                    },
                'EMPTY':
                    {
                        'count': 1,
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
"""
advanced_experiment = json.dumps(
    {
        'exp_id': '553e898c6c8dc562738e9294',
        'experiment parameters':
            {
                'advanced': True,
                'instruction':"open_shutter(0)\nclose_shutter(0)\nif(1 == 0):\n get_frame(1.0)\nelse:\n get_frame(2.0)\n"
                              "for i in range(1, 5):\n  get_frame(3.0)"
                # FOR NOW PROBLEM WITH "range()" - BECAUSE IT IS IN "__builtins__"
            }

    }
)
"""

new_voltage = json.dumps(50.0)
new_current = json.dumps(20.0)
exposure = json.dumps(1000.0)
new_pos = json.dumps(7.0)

try:

    req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/state")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-on")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/power-off")

    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-voltage", data = new_voltage)
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/source/set-current", data = new_current)
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/get-voltage")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/source/get-current")

    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/shutter/open/0")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/shutter/close/0")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/shutter/state")

    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-horizontal-position", data = new_pos)
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-vertical-position", data = new_pos)
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/set-angle-position", data = new_pos)

    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/get-horizontal-position")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/get-vertical-position")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/get-angle-position")

    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/reset-angle-position", data = new_pos)
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/move-away")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/motor/move-back")

    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/chip_temp")
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/hous_temp")
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/get-frame", data = exposure)
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/detector/get-frame-with-closed-shutter", data = exposure)

    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/start", data = simple_experiment)
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/start", data = advanced_experiment)
    # req = requests.get(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/stop")

    # Future "Experiment stop"
    # req = requests.post(MODULE_EXPERIMENT_URI + "/tomograph/1/experiment/stop", data = json.dumps("prosto"))


except requests.ConnectionError as e:
    print("Could not connect", e.message)
else:
    print(req.content)
