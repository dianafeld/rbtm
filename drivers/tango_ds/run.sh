#!/usr/bin/env bash

source tango_env/bin/activate

# python Motor/Motor.py motor -v4 &
python AngleMotor/AngleMotor.py angle_motor -v4 &
python HorizontalMotor/HorizontalMotor.py horizontal_motor -v4 &
python Detector/Detector.py detector -v4 &
python XRayShutter/XRayShutter.py shutter -v4 &
python XRaySource/XRaySource.py source -v4 &
sleep 4
python Tomograph/Tomograph.py tomograph -v4 &
