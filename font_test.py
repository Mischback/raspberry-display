#!/usr/bin/python
# coding: utf-8


import sys
import signal
import RPi.GPIO as GPIO

from lib.ea_dog import DOGM128


def handler(sig, frame):
    print 'You pressed Ctrl+C, I\'m cleaning up GPIO...'
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, GPIO.cleanup)
    lcd = DOGM128(16, 18, 22, 26, 24)

    # just print some text to the display... easy stuff
    lcd.print_text('This is working...', 1, 'left')
    lcd.print_text('by Mischback', 2, 'right')
    lcd.print_text('ABCDEFGHIJKLMNO', 3, 'left')
    lcd.print_text('PQRSTUVWXYZ', 4, 'left')
    lcd.print_text('abcdefghijklmno', 5, 'right')
    lcd.print_text('pqrstuvwxyz', 6, 'right')

    while True:
        pass

    GPIO.cleanup()
