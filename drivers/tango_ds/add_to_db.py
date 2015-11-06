#!/usr/bin/env python

from PyTango import Database, DbDevInfo


def register(device_name, device_class, device_server):
    new_device_info = DbDevInfo()
    new_device_info.name = device_name
    new_device_info._class = device_class
    new_device_info.server = device_server

    print("Creating device: %s" % device_name)

    db.add_device(new_device_info)


def register_motor():
    register("tomo/motor/1", "Motor", "Motor/motor")


def register_angle_motor():
    register("tomo/angle_motor/1", "AngleMotor", "AngleMotor/angle_motor")


def register_horizontal_motor():
    register("tomo/horizontal_motor/1", "HorizontalMotor", "HorizontalMotor/horizontal_motor")


def register_detector():
    register("tomo/detector/1", "Detector", "Detector/detector")


def register_shutter():
    register("tomo/shutter/1", "XRayShutter", "XRayShutter/shutter")


def register_source():
    register("tomo/source/1", "XRaySource", "XRaySource/source")


def register_tomograph():
    register("tomo/tomograph/1", "Tomograph", "Tomograph/tomograph")


db = Database()

# register_motor()
register_angle_motor()
register_horizontal_motor()
register_detector()
register_shutter()
register_source()
register_tomograph()
