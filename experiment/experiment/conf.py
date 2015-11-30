#!/usr/bin/python
"""
29.11.15 - Rustam
Configuration file for module "Experiment"
Contains web-addresses of storage, of web-page of adjustment(of tomograph), of tomograph,
also contains name of png-file, creating for storing current image during experiment,
finally contains time that tomograph waits for commands during advanced experiments with exec,

If STORAGE_IS_STUB and/or WEBPAGE_OF_ADJUSTMENT_IS_STUB variables are set True, it launches stub servers
for storage and/or web-page of adjustment
"""

import subprocess

STORAGE_IS_STUB = True

WEBPAGE_OF_ADJUSTMENT_IS_STUB = True

TOMOGRAPH_IS_STUB = True



FRAME_PNG_FILENAME = 'image.png'

TIMEOUT_MILLIS = 200000

MAX_EXPERIMENT_TIME = 100
# MAX_EXPERIMENT_TIME is currently used only in advanced experiments with exec








if STORAGE_IS_STUB:
    STORAGE_FRAMES_URI     = "http://localhost:5020/stub_storage"               # To send frames
    STORAGE_EXP_START_URI  = "http://localhost:5020/stub_storage"               # To send experiment parameters
    STORAGE_EXP_FINISH_URI = "http://localhost:5020/stub_storage"               # To send messages about experiment stops

    subprocess.Popen(["./experiment/stubs/stub_storage.py"])
    # launch stub storage server on port 5020 - just for recieving messages from 'experiment' and answering 'success'
else:
    STORAGE_FRAMES_URI     = "http://109.234.34.140:5006/storage/frames/post"           
    STORAGE_EXP_START_URI  = "http://109.234.34.140:5006/storage/experiments/create"
    STORAGE_EXP_FINISH_URI = "http://109.234.34.140:5006/storage/experiments/finish"



if WEBPAGE_OF_ADJUSTMENT_IS_STUB:
    WEBPAGE_URI = "http://localhost:5021/stub_webpage"
    
    subprocess.Popen(["./experiment/stubs/stub_webpage.py"])
    # launch stub web-page server on port 5021 - just for recieving messages from 'experiment' and answering 'success'
else:
    WEBPAGE_URI = "http://109.234.34.140:5021/take_image"



if TOMOGRAPH_IS_STUB:
    TOMO_ADDR = '188.166.73.250:10000'
else:
    TOMO_ADDR = 'localhost:10000'