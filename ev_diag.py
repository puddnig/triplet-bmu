# -*- coding: utf-8 -*-
"""
"""

import serial
from triplet import *
serport = 'COM10'


class obdlink(serial.Serial):
    def reset(self):
        self.timeout = 5
        cmd = ('ATZ\n\r')
        self.write(cmd.encode())
        resp = self.read_until('a\r\r'.encode())
        resp = resp.decode()
        return resp

    def send_command(self, command):
        commandsend = command + '\n\r'
        self.timeout = 5
        self.write(commandsend.encode())
        resp = self.read_until(b'OK\r\r')
        if resp.decode().find('OK') == -1:
            print('Error executing command ', command,
                  '\nAnswer:', resp)

    def do_setup(self, commandlist):
        for i in commandlist:
            self.send_command(i)

    def get_answer(self, command):
        commandsend = command + '\n\r'
        self.timeout = 1
        self.write(commandsend.encode())
        resp = self.read_until('\r\r'.encode())
        return resp

    def reconnect(self):
        self.close()
        self.open()


ion = triplet()


def connect():
    global serialcon
    serialcon = obdlink(port=serport, baudrate=500000, timeout=5)


def disconnect():
    serialcon.close()


def switch_baudrate():
    br_old = 115200
    br_new = 500000
    test = obdlink(port=serport, baudrate=br_old, timeout=5)
    command = 'stsbr'+str(br_new)+'\n\r'
    test.write(command.encode())
    test.close()
    test = obdlink(port=serport, baudrate=br_new, timeout=5)
    test.send_command('stwbr')
    test.reset()
    test.close()


def is_baudrate_ok():
    test = obdlink(port=serport, baudrate=500000, timeout=5)
    try:
        answer = test.reset()
        # print(answer)
        if answer.find('ELM') != -1:
            ok = True
    except (UnicodeDecodeError, UnboundLocalError):
        ok = False
    test.close()
    return ok
