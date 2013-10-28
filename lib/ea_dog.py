#!/usr/bin/python
# coding: utf-8

"""
@file   ea_dog.py
@brief  This library is used to control EA-DOG displays

Most of this code was taken from "atlasz"@raspberrypiforums.com (http://www.raspberrypiforums.com/forums/topic/565-ea-dog-glcd-on-raspberrypi/)

This will be improved as far as it is necessary.
"""

import sys
import time
import RPi.GPIO as GPIO

import lib.font
from lib.image_processor import BitmapProcessor

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

        self.bitmap_processor = None
        self.display_width = 128
        self.display_height = 64
        self.color_depth = 1

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

    def send_text(self, text):
        """
        """
        font = lib.font.tempesta
        for char in text:
            data = ord(char)
            if not font.has_key(data):
                data = 0x20
            self.send_data_seq(font[data][0])

    def print_text(self, text, line, align='left'):
        """
        """
        font = lib.font.tempesta
        length = 0
        for char in text:
            data = ord(char)
            if not font.has_key(data):
                data = 0x20
            length += font[data][1]

        if length > 128:
            raise RuntimeError

        if align == 'left':
            self.set_pos(line, 0)
            self.send_text(text)
        elif align == 'right':
            self.set_pos(line, 128 - length)
            self.send_text(text)
        elif align == 'center':
            self.set_pos(line, (128 - length) / 2)
            self.send_text(text)

    def show_image(self, filename):
        if not self.bitmap_processor:
            self.bitmap_processor = BitmapProcessor(self.display_width, self.display_height, self.color_depth, 0)

        try:
            img_lines = self.bitmap_processor.process_image(filename)
        except ImageProcessorException, e:
            print 'Exception:', e

        for line in range(8):
            seq = []
            for i in range(16):
                for j in range(8):
                    mask = pow(2, 7 - j)
                    byte = 0
                    for k in range(8):
                        bit = ord(img_lines[line * 8 + k][i]) & mask
                        if bit:
                            byte += pow(2, k)
                    seq.append(byte)
            self.set_pos(line, 0)
            self.send_data_seq(seq)
