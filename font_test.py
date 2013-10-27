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

    lcd.print_text('FOOBAR', 1, 'center')
    lcd.print_text('THIS IS WORKING', 2, 'left')
    lcd.print_text('BY MISCHBACK', 3, 'right')

    while True:
        pass

    GPIO.cleanup()
