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

    # yeah, show an image...
    lcd.show_image('sample_mischback.bmp')

    print 'Demo finished!'

    GPIO.cleanup()
