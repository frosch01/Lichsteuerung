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
        
class LightControl(object):
    
    def __init__(self):
        trigger = [False for x in range(Trigger.MAX_TRIGGER)]
    
    def MotionSensSouthTrigger(self):
        trigger[Trigger.MOTION_SENSE_SOUTH]   = True
    def MotionSensTerraceTrigger(self):
        trigger[Trigger.MOTION_SENSE_TERRACE] = True
    def MotionSenseNothTrigger(self):
        trigger[Trigger.MOTION_SENSE_NORTH]   = True
    def SpareTrigger(self):
        trigger[Trigger.UNUSED_SENSE_]        = True
        
trigger=[False, False, False, False]
gpio=MyGPIO(MyGPIO.WPI_MODE_PINS);
lightControl = LightControl();

def CallbackIsrIn0():
    print("Input 0 triggered")
    gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    lightControl.MotionSensSouthTrigger()
    trigger[0]=True
    
def CallbackIsrIn1():
    print("Input 1 triggered")
    gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    lightControl.MotionSensTerraceTrigger()
    trigger[1]=True
def CallbackIsrIn2():
    print("Input 2 triggered")
    gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    lightControl.MotionSenseNothTrigger()
    trigger[2]=True
def CallbackIsrIn3():
    print("Input 3 triggered")
    gpio.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
    lightControl.SpareTrigger()
    trigger[3]=True
    
def shutdown():
    print("Lichsteuerung terminating...", )
    gpio.cleanup()
    print("done")

if __name__ == "__main__":
    
    atexit.register(shutdown)
         
    gpio.wiringPiISR(MyGPIO.inputPins[0], GPIO.INT_EDGE_FALLING, CallbackIsrIn0)
    gpio.wiringPiISR(MyGPIO.inputPins[1], GPIO.INT_EDGE_FALLING, CallbackIsrIn1)
    gpio.wiringPiISR(MyGPIO.inputPins[2], GPIO.INT_EDGE_FALLING, CallbackIsrIn2)
    gpio.wiringPiISR(MyGPIO.inputPins[3], GPIO.INT_EDGE_FALLING, CallbackIsrIn3)
    
    gpio.relaisTest()
    
    timer=0
    while True:
        print(timer, " ", trigger)
        time.sleep(1)
        if trigger[0] or trigger[1] or trigger[2] or trigger[3]:
            trigger=[False, False, False, False]
            timer=5
            
        if timer != 0:
            timer-=1
            if (0 == timer):
                gpio.digitalWrite(MyGPIO.relaisPins, GPIO.HIGH)
            
