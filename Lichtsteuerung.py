#!/usr/bin/python3
'''
Documentation, License etc.

@package Lichtsteuerung
'''

#import RPi.GPIO as GPIO
from wiringpi import GPIO
from operator import methodcaller
import time

relais_pins_wp = [1, 4, 5, 6, 26, 27, 28, 29]

class MyGPIO(GPIO):
    def IterateCall(self, call, pins, *args):
        try:
            for pin in pins:
                call(pin, *args)
        except TypeError:
            call(pins, *args)
            
    def pullUpDnControl(self, pins, *args):
        self.IterateCall(super(MyGPIO, self).pullUpDnControl, pins, *args)
    def pinMode(self, pins, *args):
        self.IterateCall(super(MyGPIO, self).pinMode, pins, *args)
    def digitalWrite(self, pins, *args):
        self.IterateCall(super(MyGPIO, self).digitalWrite, pins, *args)

if __name__ == "__main__":
    gpio=MyGPIO(GPIO.WPI_MODE_PINS);
    rev = gpio.piBoardRev();
    print("Board Rev is %d" % rev)
     
    gpio.pullUpDnControl(relais_pins_wp, GPIO.PUD_OFF)
    gpio.pinMode(relais_pins_wp, GPIO.OUTPUT)
    gpio.digitalWrite(relais_pins_wp, GPIO.LOW)
    time.sleep(1)
    gpio.digitalWrite(relais_pins_wp, GPIO.HIGH)
    time.sleep(1)
    gpio.pinMode(relais_pins_wp, GPIO.INPUT)
    gpio.pullUpDnControl(relais_pins_wp, GPIO.PUD_DOWN)
    
#    GPIO.setmode(GPIO.BOARD)
#    GPIO.setup (relais_pins, GPIO.OUT)
#    GPIO.output(relais_pins, GPIO.HIGH)
    
#    for pin in relais_pins:
#        GPIO.output(pin, GPIO.LOW)
#        time.sleep(1)
#    for pin in relais_pins:
#        GPIO.output(pin, GPIO.HIGH)
#        time.sleep(1)
#    GPIO.cleanup(relais_pins)
