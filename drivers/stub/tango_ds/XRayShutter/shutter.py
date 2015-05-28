import serial
import PyTango
import re


class Shutter(object):

    """Shutter for X-ray source """

    def __init__(self, tty_name, relay_number):
        """
        Init shutter object

        :param tty_name: COM port name to connect
        :param relay_number: number of relay 1-4
        
        """
        super(Shutter, self).__init__()
        self.tty_name = tty_name
        self.relay_number = relay_number
        #self.check_module()

    def check_module(self):
        """
        Is controller alive?
        """
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("$KE\r\n")
            if serial_port.readline() != '#OK\r\n':
                raise RuntimeError("XRayShutter_ConnectionFailed")

    def open(self):
        """
        Open relay

        """
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("$KE,REL,{},1\r\n".format(self.relay_number))
            if serial_port.readline() != "#REL,OK\r\n":
                PyTango.Except.throw_exception("XRayShutter_IOException",
                                               "Can't set value 1 to relay",
                                               "Shutter::open()")

    def close(self):
        """
        Close relay

        """
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("$KE,REL,{},0\r\n".format(self.relay_number))
            if serial_port.readline() != "#REL,OK\r\n":
                PyTango.Except.throw_exception("XRayShutter_IOException",
                                               "Can't set value 0 to relay",
                                               "Shutter::close()")

    def answer_is_correct(self, message, regex):
        pattern = re.compile(regex)
        answer = pattern.match(message)
        if answer != None:
            if answer.group() == message:
                return True
        return False

    def is_open(self):
        with serial.Serial(self.tty_name) as serial_port:
            serial_port.write("$KE,RDR,{}\r\n".format(self.relay_number))
            relay_state = serial_port.readline().strip()

        #if self.answer_is_correct(relay_state, "#RDR,(1|01),(1|0)"):
        relay_state = int(relay_state.split(',')[2])
        #else:
            #PyTango.Except.throw_exception("XRayShutter_UnexpectedValue",
            #                               "Unexpected answer from module, should be '#RDR,1,<Value>', got '" + relay_state + "'",
            #                               "Shutter::is_open()")

        return bool(relay_state)