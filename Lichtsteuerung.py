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
import asyncio

class Trigger(IntEnum):
    MOTION_SENSE_SOUTH   = 0
    MOTION_SENSE_NORTH   = 1
    MOTION_SENSE_TERRACE = 2
    UNUSED_SENSE_        = 3
    MAX_TRIGGER          = 4
    
class Relais(IntEnum):
    LAMP_WEST    = 0
    LAMP_SOUTH   = 1
    LAMP_NORTH   = 2
    LAMP_TERRACE = 3
    MAX_RELAIS   = 4
    
class RelaisState(IntEnum):
    On  = GPIO.LOW
    Off = GPIO.HIGH
    
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
    def setRelais(self, relais, state):
        self.digitalWrite(MyGPIO.relaisPins[relais], state)
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
    def __init__(self, gpio):
        self.gpio = gpio
        self.loop = asyncio.get_event_loop()
        self.tasks   = [None for x in range(Relais.MAX_RELAIS)]
        self.offTime = [self.loop.time() for x in range(Relais.MAX_RELAIS)]
        gpio.registerIsr(Trigger.MOTION_SENSE_SOUTH,   lambda: self.MotionSensSouthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_NORTH,   lambda: self.MotionSensNorthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_TERRACE, lambda: self.MotionSensTerraceTrigger())
        gpio.registerIsr(Trigger.UNUSED_SENSE_,        lambda: self.SpareTrigger())
    def MotionSensSouthTrigger(self):
        print("MOTION_SENSE_SOUTH triggered")
        self.loop.call_soon_threadsafe(self.keepRelaisOnFor, Relais.LAMP_SOUTH, 10)
        self.loop.call_soon_threadsafe(self.keepRelaisOnFor, Relais.LAMP_WEST, 10)
        #asyncio.run_coroutine_threadsafe(self.keepRelaisOnFor(Relais.LAMP_SOUTH, 5), self.loop)
    def MotionSensTerraceTrigger(self):
        print("MotionSensTerrace triggered")
        self.loop.call_soon_threadsafe(self.keepRelaisOnFor, Relais.LAMP_TERRACE, 10)
    def MotionSensNorthTrigger(self):
        print("MotionSenseNorth triggered")
        self.loop.call_soon_threadsafe(self.keepRelaisOnFor, Relais.LAMP_NORTH, 10)
    def SpareTrigger(self):
        print("Spare triggered")
    def keepRelaisOnFor(self, lamp, time):
        self.gpio.setRelais(lamp, RelaisState.On)
        offTime = self.loop.time() + time
        if self.offTime[lamp] < offTime: self.offTime[lamp] = offTime
        runTask = False
        try:
            runTask = self.tasks[lamp].done()
        except AttributeError:
            runTask = True
        if runTask:
            self.tasks[lamp] = self.loop.create_task(self.turnOffAfter(lamp))
            print("Start of turnOffAfter for %s until %s" %(lamp, self.offTime[lamp]))
        else:
            print("turnOffAfter for %s already running until %s" %(lamp, self.offTime[lamp]))
    @asyncio.coroutine
    def turnOffAfter(self, lamp):
        try:
            while True:
                now = self.loop.time()
                print(now)
                if (now) >= self.offTime[lamp]:
                    break
                yield from asyncio.sleep(1)
            self.gpio.setRelais(lamp, RelaisState.Off)
        except asyncio.CancelledError: 
            print("turnOffAfter for %s cancelled" % lamp) 
        else:
            print("turnOffAfter for %s done" % lamp)

gpio=MyGPIO(MyGPIO.WPI_MODE_PINS);
lightControl = LightControl(gpio);

def shutdown():
    print("Lichsteuerung terminating...", )
    gpio.cleanup()
    print("done")

if __name__ == "__main__":
    
    atexit.register(shutdown)
    gpio.relaisTest()
    
    loop = asyncio.get_event_loop()
    loop.run_forever()
