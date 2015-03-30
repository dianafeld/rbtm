#!/usr/bin/env bash

python Motor/Motor.py motor &
python Detector/Detector.py detector &
python XRayShutter/XRayShutter.py shutter &
python XRaySource/XRaySource.py source &
sleep 5
python Tomograph/Tomograph.py tomograph &
