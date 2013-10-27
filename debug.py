#!/usr/bin/python
# coding: utf-8


import sys
import signal
import RPi.GPIO as GPIO

from lib.ea_dog import DOG


if __name__ == '__main__':
    signal.signal(signal.SIGINT, GPIO.cleanup)
    lcd = DOG(16, 18, 22, 26, 24)

    while True:
        for i in range(8):
            lcd.set_pos(i, 0)
            lcd.send_data_seq([0xAA]*128)
        lcd.clear_lcd()

    GPIO.cleanup()
