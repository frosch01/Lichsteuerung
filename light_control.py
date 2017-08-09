#!/usr/bin/python3
'''
Documentation, License etc.

@package light_control
'''

try:
    f = open('/sys/firmware/devicetree/base/model', 'r')
except OSError:
    print("No Raspberry PI detected. Running with stub GPIO")
    from GPIO_stub import GPIO
else:
    print("Raspberry PI model %s detected. Running on real GPIO pins" % f.readline())
    from wiringpi import GPIO
    
import time
import atexit
import asyncio
import sys
import datetime
from operator import methodcaller
from enum import IntEnum
from threading import Thread
from astral import Location

class Detector(IntEnum):
    MOTION_SENSE_SOUTH   = 0
    MOTION_SENSE_NORTH   = 1
    MOTION_SENSE_TERRACE = 2
    UNUSED_SENSE_        = 3
    
class Relais(IntEnum):
    LAMP_WEST    = 0
    LAMP_SOUTH   = 1
    LAMP_TERRACE = 2
    LAMP_NORTH   = 3
    
class Pwm(IntEnum):
    LAMP_TERRACE = 0
    
class RelaisMode(IntEnum):
    Off  = 0
    On   = 1
    Auto = 2
    
class DetectorMode(IntEnum):
    Masked  = 0
    Active  = 1
    
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
        self.pinMode(MyGPIO.pwmPins,    GPIO.PWM_OUTPUT)
        self.pinMode(MyGPIO.inputPins,  GPIO.INPUT)
        self.pullUpDnControl(MyGPIO.relaisPins, GPIO.PUD_OFF)
        self.pullUpDnControl(MyGPIO.pwmPins,    GPIO.PUD_OFF)
        self.pullUpDnControl(MyGPIO.inputPins,  GPIO.PUD_OFF)
        self.pwmSetMode (GPIO.PWM_MODE_MS)
        self.pwmSetClock(1920)
        self.pwmSetRange(100)
        self.pwmWrite   (self.pwmPins[0], 20)
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
    def setPwm(self, pwm, value):
        intVal = int(value)
        if intVal < 0 or intVal > 100: raise ValueError
        self.pwmWrite(MyGPIO.pwmPins[pwm], intVal)
    def relaisTest(self):
        self.digitalWrite(MyGPIO.relaisPins, GPIO.LOW)
        time.sleep(1)
        self.digitalWrite(MyGPIO.relaisPins, GPIO.HIGH)
        time.sleep(1)
    def cleanup(self):
        self.pinMode(MyGPIO.relaisPins, GPIO.INPUT)
        self.pinMode(MyGPIO.inputPins,  GPIO.INPUT)
        self.pinMode(MyGPIO.pwmPins,    GPIO.INPUT)
        self.pullUpDnControl(MyGPIO.relaisPins, GPIO.PUD_DOWN)
        self.pullUpDnControl(MyGPIO.inputPins,  GPIO.PUD_DOWN)
        self.pullUpDnControl(MyGPIO.pwmPins,    GPIO.PUD_DOWN)
        
class RelaisActor:
    def __init__(self, gpio, relais, loop):
        self.gpio        = gpio
        self.loop        = loop
        self.task        = None
        self.turnOffTime = self.loop.time()
        self.turnOnTime  = sys.float_info.max
        self.relais      = relais
        self.mode        = RelaisMode.Auto
    def setMode(self, mode):
        self.mode = mode
        if self.mode == RelaisMode.On:     self.gpio.setRelais(self.relais, RelaisState.On)
        elif self.mode == RelaisMode.Off:  self.gpio.setRelais(self.relais, RelaisState.Off)
        elif self.mode == RelaisMode.Auto: self.gpio.setRelais(self.relais, RelaisState.Off)
    def getMode(self):
        return self.mode
    def turnOnTimeSpan(self, after, timeSpan):
        turnOnTime  = self.loop.time() + after 
        turnOffTime = turnOnTime + timeSpan
        if self.turnOnTime  > turnOnTime:  self.turnOnTime  = turnOnTime
        if self.turnOffTime < turnOffTime: self.turnOffTime = turnOffTime
        runTask = False
        try:
            runTask = self.task.done()
        except AttributeError:
            runTask = True
        if runTask:
            self.task = self.loop.create_task(self.turnOnOffTimeControl())
            print("Start of turnOnOffTimeControl for %s from %s until %s" %(self.relais, self.turnOnTime, self.turnOffTime))
        else:
            print("turnOnOffTimeControl for %s already running. From %s until %s" %(self.relais, self.turnOnTime, self.turnOffTime))
    @asyncio.coroutine
    def turnOnOffTimeControl(self):
        try:
            while True:
                now = self.loop.time()
                if now >= self.turnOffTime:
                    break
                if now >= self.turnOnTime and now < self.turnOnTime + 1:
                    if self.mode == RelaisMode.Auto: 
                        self.gpio.setRelais(self.relais, RelaisState.On)
                        print("%.1f: %s turned ON" % (now, self.relais))
                    else:
                        print("%.1f: %s is in mode %s" % (now, self.relais, self.mode))
                yield from asyncio.sleep(1)
            if self.mode == RelaisMode.Auto:
                self.gpio.setRelais(self.relais, RelaisState.Off)
                print("%.1f: %s turned OFF" % (now, self.relais))
            else:
                print("%.1f: %s is in mode %s" % (now, self.relais, self.mode))
        except asyncio.CancelledError: 
            print("%.1f: %s cancelled" % (now, self.relais)) 
        self.turnOnTime = sys.float_info.max
        
class LightControl(object):
    def __init__(self):
        self.gpio = MyGPIO(MyGPIO.WPI_MODE_PINS)
        self.gpio.relaisTest()
        self.loop = asyncio.new_event_loop()
        self.relaisList   = [RelaisActor(self.gpio, x, self.loop) for x in Relais]
        self.detectorList = [DetectorMode.Active for x in Detector]
        self.gpio.registerIsr(Detector.MOTION_SENSE_SOUTH,   lambda: self._MotionSensSouthTrigger())
        self.gpio.registerIsr(Detector.MOTION_SENSE_NORTH,   lambda: self._MotionSensNorthTrigger())
        self.gpio.registerIsr(Detector.MOTION_SENSE_TERRACE, lambda: self._MotionSensTerraceTrigger())
        self.gpio.registerIsr(Detector.UNUSED_SENSE_,        lambda: self._SpareTrigger())
        self.loopThread = Thread(target = self._LoopThread, args = ()).start()
    def TerminateLoopThread(self):
        print("Asyncio loop running in thread will be stopped")
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.gpio.cleanup()
    def setRelaisMode(self, relais, mode):
        self.relaisList[relais].setMode(mode)
    def getRelaisMode(self, relais):
        return self.relaisList[relais].getMode()
    def setDetectorMode(self, detector, mode):
        self.detectorList[detector] = mode
    def getDetectorMode(self, detector):
        return self.detectorList[detector]
    def setPwm(self, pwm, value):
        self.gpio.setPwm(pwm, value)
    def _LoopThread(self):
        print("Thread for asyncio loop started")
        asyncio.set_event_loop(self.loop)
        self._setSunTimes()
        self.loop.run_forever()
        
    def _MotionSensSouthTrigger(self):
        if self.detectorList[Detector.MOTION_SENSE_SOUTH] == DetectorMode.Active:
            print("MotionSensSouth triggered")
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_TERRACE].turnOnTimeSpan, 4, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_SOUTH].turnOnTimeSpan,   0, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_WEST].turnOnTimeSpan,    2, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_NORTH].turnOnTimeSpan,   6, 10)
            #asyncio.run_coroutine_threadsafe(self.keepRelaisOnFor(Relais.LAMP_SOUTH, 5), self.loop)
        else:
            print("MotionSensSouth masked")
    def _MotionSensTerraceTrigger(self):
        if self.detectorList[Detector.MOTION_SENSE_TERRACE] == DetectorMode.Active:
            print("MotionSensTerrace triggered")
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_TERRACE].turnOnTimeSpan, 0, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_SOUTH].turnOnTimeSpan,   5, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_WEST].turnOnTimeSpan,    3, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_NORTH].turnOnTimeSpan,   5, 10)
        else:
            print("MotionSensTerrace masked")
    def _MotionSensNorthTrigger(self):
        if self.detectorList[Detector.MOTION_SENSE_NORTH] == DetectorMode.Active:
            print("MotionSenseNorth triggered")
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_TERRACE].turnOnTimeSpan, 3, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_SOUTH].turnOnTimeSpan,   3, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_WEST].turnOnTimeSpan,    5, 10)
            self.loop.call_soon_threadsafe(self.relaisList[Relais.LAMP_NORTH].turnOnTimeSpan,   0, 10)
        else:
            print("MotionSensNorth masked")
    def _SpareTrigger(self):
        print("Spare triggered")
        
    def _getTimeDiff(self, t1, t2):
        return (t2.hour   - t1.hour)   * 3600 + \
               (t2.minute - t1.minute) * 60 + \
               (t2.second - t1.second)
           
    def _setIsNight(self, now):
        timeToSunrise = self._getTimeDiff(now.time(), self.sunrise.time())
        timeToSunset  = self._getTimeDiff(now.time(), self.sunset.time())
        if timeToSunrise < 300 and timeToSunset > 300 : self.isNight = False
        else: self.isNight = True
        if timeToSunrise < 0: timeToSunrise += 24*3600
        if timeToSunset  < 0: timeToSunset  += 24*3600
        if self.isNight: return timeToSunrise
        else: return timeToSunset
        
    def _setSunTimes(self):
        city = Location(info=('Stuttgart', 'Germany', 48.742211, 9.2068, 'Europe/Berlin', 430))
        city.solar_depression = 'civil'
        now = datetime.datetime.now(city.tz)
        sun = city.sun(date=datetime.date.today(), local=True)
        self.sunset  = sun['sunset']
        self.sunrise = sun['sunrise']
        print("Sunrise %s, Sunset %s" %(self.sunrise, self.sunset))
        #print("now %s" % now)
        #print("time %s, sunrise %s, sunset %s" % (now.time(), self.sunrise.time(), self.sunset.time()))
        #print("diff sunrise %d, diff sunset %d" %(self._getTimeDiff(now.time(), self.sunrise.time()),  self._getTimeDiff(now.time(), self.sunset.time())))
        timeToActivation = self._setIsNight(now)
        print("%s: It is " %(now), end = '')
        if self.isNight: print("night!")
        else: print("day!")
        self.loop.call_later(timeToActivation, self._setSunTimes)
