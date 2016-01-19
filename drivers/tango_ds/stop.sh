#!/usr/bin/env bash

# killall -v python

pkill -e -f Tomograph/Tomograph.py
pkill -e -f AngleMotor/AngleMotor.py
pkill -e -f HorizontalMotor/HorizontalMotor.py
pkill -e -f Detector/Detector.py
pkill -e -f XRayShutter/XRayShutter.py
pkill -e -f XRaySource/XRaySource.py
