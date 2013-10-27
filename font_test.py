#!/usr/bin/python
# coding: utf-8


import sys
import signal
import RPi.GPIO as GPIO

from lib.ea_dog import DOG

def handler(sig, frame):
    print 'You pressed Ctrl+C, I\'m cleaning up GPIO...'
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, GPIO.cleanup)
    lcd = DOG(16, 18, 22, 26, 24)

    lcd.set_pos(1, 5)
    lcd.send_text('ABCDEFGHIJKLM')
    lcd.set_pos(2, 5)
    lcd.send_text('NOPQRSTUVWXYZ')
    lcd.set_pos(3, 0)
    lcd.send_data_seq([0xff]*128)
    lcd.set_pos(4, 0)
    lcd.send_data_seq([0xff]*128)
    lcd.set_pos(5, 0)
    lcd.send_data_seq([0xff]*128)
    lcd.set_pos(6, 0)
    lcd.send_data_seq([0xff]*128)
    lcd.set_pos(7, 0)
    lcd.send_data_seq([0xff]*128)
    lcd.set_pos(0, 0)
    lcd.send_data_seq([0xff]*128)

    while True:
        pass

    GPIO.cleanup()
