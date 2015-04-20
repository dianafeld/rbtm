# -*- coding: utf-8 -*-
__author__ = 'arlen'
import serial
import sys
import re


class Shutter:
    TIMEOUT = 1

    def close_port(self):
        self.port.close()

    def open_port(self):
        # инициализировать порт
        # '/dev/ttyACM0'
        self.port = serial.Serial('/dev/pts/9', timeout=Shutter.TIMEOUT)

        # проверить работоспособность модуля
        self.port.write('$KE\r\n')
        if self.port.readline() != '#OK\r\n':
            sys.stderr.write("Module isn't in workable state\n")

    def __init__(self):
        self.port = serial.Serial()
        # открыть порт
        self.open_port()

    def answer_is_correct(self, message, regex):
        pattern = re.compile(regex)
        answer = pattern.match(message)
        if answer is not None:
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
            sys.stderr.write("Unexpected answer from module, should be '#RDR,1,<Value>', got '" + relay_state + "'\n")

        return [False, True][int(relay_state)]

    def set_value(self, val):
        # 1 открыть заслону, 0 закрыть заслонку
        if not val in [0, 1]:
            sys.stderr.write("Trying to set incorrect value to shutter: expected 0 or 1, got " + str(val) + "\n")

        # установить значение на реле (1 замкнуть, 0 разомкнуть)
        self.port.write("$KE,REL,1," + str(val) + "\r\n")

        # проверить, что значение установилось
        if self.port.readline() != "#REL,OK\r\n":
            sys.stderr.write("Can't set value " + str(val) + " to relay\n")

    def open(self):
        self.set_value(1)

    def close(self):
        self.set_value(0)
