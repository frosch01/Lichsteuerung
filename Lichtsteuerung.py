#!/usr/bin/python3
'''
Documentation, License etc.

@package Lichtsteuerung
'''

from wiringpi import GPIO
from operator import methodcaller
from enum import IntEnum
import time
import atexit

class Trigger(IntEnum):
    MOTION_SENSE_SOUTH   = 0
    MOTION_SENSE_NORTH   = 1
    MOTION_SENSE_TERRACE = 2
    UNUSED_SENSE_        = 3
    MAX_TRIGGER          = 4
    
class MyGPIO(GPIO):
    relaisPins = [1, 4, 5, 6, 26, 27, 28, 29]
    inputPins  = [0, 2, 3, 21]
    pwmPins    = [23]
    
    def __init__(self, mode):
        super().__init__(mode)
        self.pinMode(MyGPIO.relaisPins, GPIO.OUTPUT)
        self.pinMode(MyGPIO.pwmPins, GPIO.OUTPUT)
        self.pinMode(MyGPIO.inputPins, GPIO.INPUT)
        self.pullUpDnControl(MyGPIO.relaisPins, GPIO.PUD_OFF)
        self.pullUpDnControl(MyGPIO.inputPins, GPIO.PUD_OFF)
        
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
        
    def registerIsr(self, input, func):
        self.wiringPiISR(MyGPIO.inputPins[input], GPIO.INT_EDGE_FALLING, func)
        
    def relaisTest(self):
        self.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
        time.sleep(1)
        self.digitalWrite(MyGPIO.relaisPins, GPIO.HIGH)
        time.sleep(1)
        
    def cleanup(self):
        self.pinMode(MyGPIO.relaisPins, GPIO.INPUT)
        self.pinMode(MyGPIO.inputPins,  GPIO.INPUT)
        self.pinMode(MyGPIO.pwmPins,  GPIO.INPUT)
        self.pullUpDnControl(MyGPIO.relaisPins, GPIO.PUD_DOWN)
        self.pullUpDnControl(MyGPIO.inputPins,  GPIO.PUD_DOWN)
        self.pullUpDnControl(MyGPIO.pwmPins,  GPIO.PUD_DOWN)
        
gpio=MyGPIO(MyGPIO.WPI_MODE_PINS);

class LightControl(object):
    
    def __init__(self, gpio):
        self.trigger = [False for x in range(Trigger.MAX_TRIGGER)]
        gpio.registerIsr(Trigger.MOTION_SENSE_SOUTH,   lambda: self.MotionSensSouthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_NORTH,   lambda: self.MotionSensNorthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_TERRACE, lambda: self.MotionSensTerraceTrigger())
        gpio.registerIsr(Trigger.UNUSED_SENSE_,        lambda: self.SpareTrigger())
    
    def MotionSensSouthTrigger(self):
        print("MOTION_SENSE_SOUTH triggered")
        self.trigger[Trigger.MOTION_SENSE_SOUTH]   = True
        gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    def MotionSensTerraceTrigger(self):
        print("MotionSensTerrace triggered")
        self.trigger[Trigger.MOTION_SENSE_TERRACE] = True
        gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    def MotionSensNorthTrigger(self):
        print("MotionSenseNorth triggered")
        self.trigger[Trigger.MOTION_SENSE_NORTH]   = True
        gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    def SpareTrigger(self):
        print("Spare triggered")
        self.trigger[Trigger.UNUSED_SENSE_]        = True
        gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
        
lightControl = LightControl(gpio);

def shutdown():
    print("Lichsteuerung terminating...", )
    gpio.cleanup()
    print("done")

if __name__ == "__main__":
    
    atexit.register(shutdown)
    gpio.relaisTest()

    timer=0
    while True:
        print(timer)
        time.sleep(1)
        if lightControl.trigger[Trigger.MOTION_SENSE_SOUTH] or \
           lightControl.trigger[Trigger.MOTION_SENSE_NORTH] or \
           lightControl.trigger[Trigger.MOTION_SENSE_TERRACE] or \
           lightControl.trigger[Trigger.UNUSED_SENSE_]:
            lightControl.trigger = [False for x in range(Trigger.MAX_TRIGGER)]
            timer=5
            
        if timer != 0:
            timer-=1
            if (0 == timer):
                gpio.digitalWrite(MyGPIO.relaisPins, GPIO.HIGH)
            
