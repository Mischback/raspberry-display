#!/usr/bin/python
# coding: utf-8

"""
@file   ea_dog.py
@brief  This library is used to control EA-DOG displays

Most of this code was taken from "atlasz"@raspberrypiforums.com (http://www.raspberrypiforums.com/forums/topic/565-ea-dog-glcd-on-raspberrypi/)

This will be improved as far as it is necessary.
"""

import time
import RPi.GPIO as GPIO

class DOG():
    """
    """

    def __init__(self, si, clk, a0, cs, res):
        """
        """
        self.si = si
        self.clk = clk
        self.a0 = a0
        self.cs = cs
        self.res = res

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.si, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.a0, GPIO.OUT)
        GPIO.setup(self.cs, GPIO.OUT)
        GPIO.setup(self.res, GPIO.OUT)

        self.init_lcd()
        self.clear_lcd()

    def set_pos(self, page, column):
        """
        """
        self.send_cmd(0xB0 + page)
        self.send_cmd(0x10 + ((column&0xF0)>>4))
        self.send_cmd(0x00 + (column&0x0F))

    def clear_lcd(self):
        """
        """
        for i in range(8):
            self.set_pos(i, 0)
            self.send_data_seq([0x00]*128)

    def init_lcd(self):
        """
        """
        GPIO.output(self.res, 0)
        time.sleep(0.01)
        GPIO.output(self.res, 1)
        time.sleep(0.01)
        init_seq = [ 0x40, 0xA1, 0xC0, 0xA6, 0xA2, 0x2F, 0xF8, 0x00, 0x27, 0x81, 0x16, 0xAC, 0x00, 0xAF ]
        self.send_cmd_seq(init_seq)

    def send_byte(self, data):
        """
        """
        if type(data) == type('a'):
            data = ord(data)
        GPIO.output(self.cs, 0)
        for i in range(8):
            if data&128 > 0:
                GPIO.output(self.si, 1)
            else:
                GPIO.output(self.si, 0)
            data = data<<1
            GPIO.output(self.clk, 0)
            time.sleep(0.00001)
            GPIO.output(self.clk, 1)
            time.sleep(0.00001)
        GPIO.output(self.cs, 1)
        time.sleep(0.01)

    def send_cmd(self, cmd):
        """
        """
        GPIO.output(self.a0, 0)
        self.send_byte(cmd)
        time.sleep(0.001)

    def send_cmd_seq(self, seq):
        """
        """
        for i in seq:
            self.send_cmd(i)

    def send_data(self, data):
        """
        """
        GPIO.output(self.a0, 1)
        self.send_byte(data)

    def send_data_seq(self, seq):
        """
        """
        for i in seq:
            self.send_data(i)
