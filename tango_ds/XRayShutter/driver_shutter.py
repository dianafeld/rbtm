# -*- coding: utf-8 -*-
__author__ = 'arlen'
import serial
import sys
import re
import PyTango


class Shutter:
    TIMEOUT = 1

    def close_port(self):
        self.port.close()

    def open_port(self):
        # инициализировать порт
        # '/dev/ttyACM0'
        try:
            self.port = serial.Serial('/dev/pts/9', timeout=Shutter.TIMEOUT)
        except serial.SerialException:
            python_exception = PyTango.Except.to_dev_failed(*sys.exc_info())
            PyTango.Except.re_throw_exception(python_exception,
                                              "XRayShutter_ConnectionFailed",
                                              "Can't open a port",
                                              "Shutter::open_port()")

        # проверить работоспособность модуля
        self.port.write('$KE\r\n')
        if self.port.readline() != '#OK\r\n':
            PyTango.Except.throw_exception("XRayShutter_ConnectionFailed",
                                           "Module isn't in workable state",
                                           "Shutter::open_port()")

    def __init__(self):
        self.port = serial.Serial()
        # открыть порт
        self.open_port()

    def answer_is_correct(self, message, regex):
        pattern = re.compile(regex)
        answer = pattern.match(message)
        if answer != None:
            if answer.group() == message:
                return True
        return False

    def is_open(self):
        # послать запрос на считывание состояния реле
        self.port.write("$KE,RDR,1\r\n")

        # считать состояние реле и проверить на корректность
        relay_state = self.port.readline().strip()
        if self.answer_is_correct(relay_state, "#RDR,(1|01),(1|0)"):
            # взять значение из строчки
            relay_state = relay_state.split(',')[2]
        else:
            PyTango.Except.throw_exception("XRayShutter_UnexpectedValue",
                                           "Unexpected answer from module, should be '#RDR,1,<Value>', got '" + relay_state + "'",
                                           "Shutter::is_open()")
        return [False, True][int(relay_state)]

    def set_value(self, val):
        # 1 открыть заслону, 0 закрыть заслонку
        if not val in [0, 1]:
            PyTango.Except.throw_exception("XRayShutter_IllegalArgument",
                                       "Trying to set incorrect value to shutter: expected 0 or 1, got '" + str(val) + "'",
                                       "Shutter::set_value()")

        # установить значение на реле (1 замкнуть, 0 разомкнуть)
        self.port.write("$KE,REL,1," + str(val) + "\r\n")

        # проверить, что значение установилось
        if self.port.readline() != "#REL,OK\r\n":
            PyTango.Except.throw_exception("XRayShutter_IOException",
                                           "Can't set value " + str(val) + " to relay",
                                           "Shutter::set_value()")

    def open(self):
        try:
            self.set_value(1)
        except PyTango.DevFailed as df:
            PyTango.Except.re_throw_exception(df, df[-1].reason, df[-1].desc, "Shutter::open()\n\t" + df[-1].origin)

    def close(self):
        try:
            self.set_value(0)
        except PyTango.DevFailed as df:
            PyTango.Except.re_throw_exception(df, df[-1].reason, df[-1].desc, "Shutter::close()\n\t" + df[-1].origin)
