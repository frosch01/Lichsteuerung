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
        
class RelaisActor:
    def __init__(self, gpio, relais):
        self.gpio        = gpio
        self.loop        = asyncio.get_event_loop()
        self.task        = None
        self.turnOffTime = self.loop.time()
        self.relais      = relais
    def turnOnTimeSpan(self, timeSpan):
        self.gpio.setRelais(self.relais, RelaisState.On)
        turnOffTime = self.loop.time() + timeSpan
        if self.turnOffTime < turnOffTime: self.turnOffTime = turnOffTime
        runTask = False
        try:
            runTask = self.task.done()
        except AttributeError:
            runTask = True
        if runTask:
            self.task = self.loop.create_task(self.turnOffAfter())
            print("Start of turnOffAfter for %s until %s" %(self.relais, self.turnOffTime))
        else:
            print("turnOffAfter for %s already running. Until %s" %(self.relais, turnOffTime))
    @asyncio.coroutine
    def turnOffAfter(self):
        try:
            while True:
                now = self.loop.time()
                print(now)
                if (now) >= self.turnOffTime:
                    break
                yield from asyncio.sleep(1)
            self.gpio.setRelais(self.relais, RelaisState.Off)
        except asyncio.CancelledError: 
            print("turnOffAfter for %s cancelled" % self.relais) 
        else:
            print("turnOffAfter for %s done" % self.relais)
        
class LightControl(object):    
    def __init__(self, gpio):
        self.gpio = gpio
        self.loop = asyncio.get_event_loop()
        self.relaisList = [RelaisActor(gpio, x) for x in Relais]
        gpio.registerIsr(Trigger.MOTION_SENSE_SOUTH,   lambda: self.MotionSensSouthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_NORTH,   lambda: self.MotionSensNorthTrigger())
        gpio.registerIsr(Trigger.MOTION_SENSE_TERRACE, lambda: self.MotionSensTerraceTrigger())
        gpio.registerIsr(Trigger.UNUSED_SENSE_,        lambda: self.SpareTrigger())
    def MotionSensSouthTrigger(self):
        print("MOTION_SENSE_SOUTH triggered")
        self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_SOUTH].turnOnTimeSpan, 10)
        self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_WEST].turnOnTimeSpan,  10)
        #self.loop.call_soon_threadsafe(self.keepRelaisOnFor, Relais.LAMP_WEST, 10)
        #asyncio.run_coroutine_threadsafe(self.keepRelaisOnFor(Relais.LAMP_SOUTH, 5), self.loop)
    def MotionSensTerraceTrigger(self):
        print("MotionSensTerrace triggered")
        self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_TERRACE].turnOnTimeSpan, 10)
    def MotionSensNorthTrigger(self):
        print("MotionSenseNorth triggered")
        self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_NORTH].turnOnTimeSpan, 10)
    def SpareTrigger(self):
        print("Spare triggered")

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
