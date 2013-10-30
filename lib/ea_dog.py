#!/usr/bin/python
# coding: utf-8

"""
@file   ea_dog.py
@brief  This library is used to control EA-DOG displays

The base of this code was taken from "atlasz"@raspberrypiforums.com
(http://www.raspberrypiforums.com/forums/topic/565-ea-dog-glcd-on-raspberrypi/)

This will be improved as far as it is necessary.
"""

import time
import RPi.GPIO as GPIO

import lib.font
from lib.image_processor import BitmapProcessor, ImageProcessorException


class DOGM128():
    """
    @class  DOGM128
    @brief  Controls an EA-DOGM128-series display

    This display uses the ST7567R controller, so the class might be usable for
    all displays with this controller.
    """

    def __init__(self, si, clk, a0, cs, res):
        """
        @brief  Initialises a display object for usage with the Raspberry Pi
        @param  si INT The number of the GPIO pin for Si input
        @param  clk INT The number of the GPIO pin for the SCL input
        @param  a0 INT The number of the GPIO pin for the A0 input
        @param  cs INT The number of the GPIO pin for CS input
        @param  res INT The number of the GPIO pin for RESET input
        """
        self.si = si
        self.clk = clk
        self.a0 = a0
        self.cs = cs
        self.res = res

        # set some internal variables
        self.bitmap_processor = None
        self.display_width = 128
        self.display_height = 64
        self.color_depth = 1
        self.ctrl_pages = 64 / 8

        # setup GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.si, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT)
        GPIO.setup(self.a0, GPIO.OUT)
        GPIO.setup(self.cs, GPIO.OUT)
        GPIO.setup(self.res, GPIO.OUT)

        # let the magic happen
        self.init_lcd()
        self.clear_lcd()

    def set_pos(self, page, column):
        """
        @brief  Moves the display's internal cursor to a given position
        @param  page INT The page, or line, of the display [range 0-7]
        @param  column INT The column of the display [range 0-127]
        """
        self.send_cmd(0xB0 + page)
        self.send_cmd(0x10 + ((column & 0xF0) >> 4))
        self.send_cmd(0x00 + (column & 0x0F))

    def clear_lcd(self):
        """
        @brief  Clears the display, removes all existing pixels
        """
        for i in range(self.ctrl_pages):
            self.set_pos(i, 0)
            self.send_data_seq([0x00] * 128)

    def init_lcd(self):
        """
        @brief  Initialises the display
        @todo   Initialisation sequence differs from dualpower and single supply
        """
        GPIO.output(self.res, 0)
        time.sleep(0.01)
        GPIO.output(self.res, 1)
        time.sleep(0.01)
        init_seq = [0x40, 0xA1, 0xC0, 0xA6, 0xA2, 0x2F, 0xF8, 0x00, 0x27, 0x81,
                    0x16, 0xAC, 0x00, 0xAF]
        self.send_cmd_seq(init_seq)

    def send_byte(self, data):
        """
        @brief  Sends one byte to the display
        @param  data INT The byte to be sent
        """
        if type(data) == type('a'):
            data = ord(data)
        GPIO.output(self.cs, 0)
        for i in range(8):
            if data & 128 > 0:
                GPIO.output(self.si, 1)
            else:
                GPIO.output(self.si, 0)
            data <<= 1
            GPIO.output(self.clk, 0)
            time.sleep(0.00001)
            GPIO.output(self.clk, 1)
            time.sleep(0.00001)
        GPIO.output(self.cs, 1)
        time.sleep(0.01)

    def send_cmd(self, cmd):
        """
        @brief  Sends one command to the display
        @param  cmd INT The command to be sent
        """
        GPIO.output(self.a0, 0)
        self.send_byte(cmd)
        time.sleep(0.001)

    def send_cmd_seq(self, seq):
        """
        @brief  Sends various commands to the display
        @param  seq LIST A list of commands
        """
        for i in seq:
            self.send_cmd(i)

    def send_data(self, data):
        """
        @brief  Sends one byte of data to the display
        @param  data INT The byte of data
        """
        GPIO.output(self.a0, 1)
        self.send_byte(data)

    def send_data_seq(self, seq):
        """
        @brief  Sends a chunk of data to the display
        @param  seq LIST A chunk of data
        """
        for i in seq:
            self.send_data(i)

    def send_text(self, text):
        """
        @brief  Sends a string to the display
        @param  text STRING The text to be sent
        """
        font = lib.font.tempesta
        for char in text:
            data = ord(char)
            if not data in font:
                data = 0x20
            self.send_data_seq(font[data][0])

    def print_text(self, text, line, align='left'):
        """
        @brief  Prints a given text to the string with an alignment
        @param  text STRING The text to be sent
        @param  line INT The line the text should be sent to [range 0-7]
        @param  align STRING Either of 'left', 'right' or 'center'
        """
        font = lib.font.tempesta
        length = 0
        for char in text:
            data = ord(char)
            if not data in font:
                data = 0x20
            length += font[data][1]

        if length > self.display_width:
            # @todo Handle this a little more clever than this...
            raise RuntimeError('Text is too long')

        if align == 'left':
            self.set_pos(line, 0)
        elif align == 'right':
            self.set_pos(line, self.display_width - length)
        elif align == 'center':
            self.set_pos(line, (self.display_width - length) / 2)
        self.send_text(text)

    def show_image(self, filename):
        """
        @brief  Shows an image on the display
        @param  filename STRING The name of the file

        The file must be a bitmap image with color depth of 1 (means: black and
        white) and must not exceed the dimensions of the display.

        The BitmapProcessor will return the image data linewise. This function
        will translate this to display-data. It will take 8 lines of the image
        data, iterate the bits and calculate the needed data bytes.
        """
        if not self.bitmap_processor:
            self.bitmap_processor = BitmapProcessor(self.display_width,
                                                    self.display_height,
                                                    self.color_depth, 0)

        try:
            img_lines = self.bitmap_processor.process_image(filename)
        except ImageProcessorException, e:
            # @todo: Handle this a little more clever than this...
            print 'Exception:', e

        for line in range(self.ctrl_pages):
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