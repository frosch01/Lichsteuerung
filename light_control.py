#!/usr/bin/python3
'''
My house mapped to Raspberry PI I/O

@package light_controlqa
'''
# pylint: disable=unused-import, disable=consider-using-with
try:
    f = open('/sys/firmware/devicetree/base/model', 'r', encoding="ascii")
except OSError:
    print("No Raspberry PI detected. Running with stub GPIO")
    from GPIO_stub import GPIO
else:
    print(f"Raspberry PI model {f.readline()} detected. Running on real GPIO pins")
    from moat import gpio
    from rpi_hardware_pwm import HardwarePWM

import asyncio
import sys
import datetime
from enum import IntEnum
from threading import Thread
from astral import LocationInfo

class Detector(IntEnum):
    """Assign indexes to motion detectors"""
    MOTION_SENSE_SOUTH   = 0
    MOTION_SENSE_TERRACE = 1
    MOTION_SENSE_NORTH   = 2
    UNUSED_SENSE_        = 3

class S0(IntEnum):
    """Assign indexes to energy meters in use"""
    S0_HP_A = 0
    S0_HP_B = 1
    S0_HP_C = 2
    S0_LIGHT = 3

class Relais(IntEnum):
    """Assign indexes to lamps around the house"""
    LAMP_WEST    = 0
    LAMP_SOUTH   = 1
    LAMP_TERRACE = 2
    LAMP_NORTH   = 3

class Pwm(IntEnum):
    """Assign indexes to dim controls"""
    LAMP_TERRACE = 0

class RelaisMode(IntEnum):
    """Assign names to relais modes"""
    OFF  = 0
    ON   = 1
    AUTO = 2

class DetectorMode(IntEnum):
    """Assign names to detector modes"""
    MASKED  = 0
    ACTIVE  = 1

class RelaisState(IntEnum):
    """Assign names to relais states"""
    ON  = 0
    OFF = 1

class IoControl():
    """Map HW design to RPI GPIOs"""
    RELAIS_PINS = [18, 23, 24, 25, 12, 16, 20, 21]
    DETECTOR_PINS = [4, 17, 27, 22]
    SO_PINS = [5, 6, 19, 26]
    PWM_CHANNELS = [(1, 2000)]

    def __init__(self):
        self.chip = chip = gpio.Chip(label="pinctrl-bcm2711").__enter__()
        self.relais = list(map(
            lambda x : chip.line(x).open(gpio.DIRECTION_OUTPUT), self.RELAIS_PINS))
        self.detectors = list(map(
            lambda x : chip.line(x).monitor(), self.DETECTOR_PINS))
        self.s0s = list(map(
            lambda x : chip.line(x).monitor(), self.SO_PINS))
        self.pwms = list(map(
            lambda x: HardwarePWM(*x), self.PWM_CHANNELS))

    def __enter__(self):
        list(map(lambda l : l.__enter__(), self.relais + self.detectors + self.s0s))
        list(map(lambda p : p.start(100), self.pwms))
        return self

    def __exit__(self, exp_type, value, traceback):
        # This is an emergency handler. Allow any exception, do not react on it
        # pylint: disable=broad-exception-caught
        try:
            list(map(lambda l : self.set_relais(l, RelaisState.OFF), range(len(self.RELAIS_PINS))))
        except Exception:
            pass

        # Dispatching errors is hard to do as errors can come from any source and assigning is
        # a difficult task. So None of the execpetions signalled to be handled
        list(map(lambda l : l.__exit__(), self.relais + self.detectors + self.s0s))
        list(map(lambda p : p.stop(), self.pwms))
        self.chip.__exit__()
        return exp_type is None

    def set_relais(self, relais, state):
        """Set the state of a relais"""
        self.relais[relais].value = int(state)

    async def timed_on(self, relais, duration):
        """Turn the relais on to a given time"""
        self.set_relais(relais, RelaisState.ON)
        await asyncio.sleep(duration)
        self.set_relais(relais, RelaisState.OFF)

    def set_pwm(self, pwm, value):
        """Set the duty cycle of a PWM"""
        self.pwms[pwm].change_duty_cycle = int(value)

    async def relais_test(self):
        """Test sequence for all relais. The on time is derived from the gpio offset"""
        await asyncio.gather(*list(map(lambda r : self.timed_on(r, 1 + self.relais[r].offset / 10),
                                       range(len(self.RELAIS_PINS)))))

class RelaisScheduler:
    """Control a relais based on a given schedule"""
    def __init__(self, ioc, relais, loop):
        self.ioc        = ioc
        self.loop        = loop
        self.task        = None
        self.off_time = self.loop.time()
        self.on_time  = sys.float_info.max
        self.relais      = relais
        self.mode        = RelaisMode.AUTO

    def set_mode(self, mode):
        """Set the mode of the Relais"""
        if self.mode != mode:
            self.mode = mode
            if self.mode == RelaisMode.ON:
                self.ioc.setRelais(self.relais, RelaisState.ON)
            elif self.mode == RelaisMode.OFF:
                self.ioc.setRelais(self.relais, RelaisState.OFF)
            elif self.mode == RelaisMode.AUTO:
                self.ioc.setRelais(self.relais, RelaisState.OFF)

    def get_mode(self):
        """Return the current mode of the relais"""
        return self.mode

    def update_schedule(self, on_delay, on_duration):
        """ Set the time when relais shall next turned on and later off again. Run an async task
        that realizes the switchiung"""
        on_time  = self.loop.time() + on_delay
        off_time = on_time + on_duration
        self.on_time = max((self.on_time, on_time))
        self.off_time = min((self.off_time, off_time))
        run_task = False
        try:
            run_task = self.task.done()
        except AttributeError:
            run_task = True
        if run_task:
            self.task = self.loop.create_task(self.scheduler())
            print(f"Start of scheduler for {self.relais} from {self.on_time} "
                  f"until {self.off_time}")
        else:
            print(f"scheduler for {self.relais} already running. From {self.on_time}"
                  f"until {self.off_time}")

    async def scheduler(self):
        """ Background task function that realized relais on/off schedule. Once relais was
        turned off, the task exits. """

        try:
            while True:
                now = self.loop.time()
                if now >= self.off_time:
                    break
                if self.on_time <= now < self.on_time + 1:
                    if self.mode == RelaisMode.AUTO:
                        self.ioc.setRelais(self.relais, RelaisState.ON)
                        print(f"{now:.1f}: {self.relais} turned ON")
                    else:
                        print(f"{now:.1f}: {self.relais} is in mode {self.mode}")
                await asyncio.sleep(1)
            if self.mode == RelaisMode.AUTO:
                self.ioc.setRelais(self.relais, RelaisState.OFF)
                print(f"{now:.1f}: {self.relais} turned OFF")
            else:
                print(f"{now:.1f}: {self.relais} is in mode {self.mode}")
        finally:
            print(f"{now:.1f}: {self.relais} cancelled")
        self.on_time = sys.float_info.max

class LightControl:
    """
    The main logic from light automation

    This class receives the callouts from UI implementation to trigger the
    activation of lights.
    """
    def __init__(self):
        self.gpio = IoControl(IoControl.WPI_MODE_PINS)
        self.gpio.relaisTest()
        self.loop = asyncio.new_event_loop()
        self.relais_list   = [RelaisScheduler(self.gpio, x, self.loop) for x in Relais]
        self.detector_list = [DetectorMode.ACTIVE for x in Detector]
        self.gpio.registerIsr(Detector.MOTION_SENSE_SOUTH,
                              lambda: self._MotionSensSouthTrigger())
        self.gpio.registerIsr(Detector.MOTION_SENSE_NORTH,
                              lambda: self._MotionSensNorthTrigger())
        self.gpio.registerIsr(Detector.MOTION_SENSE_TERRACE,
                              lambda: self._MotionSensTerraceTrigger())
        self.gpio.registerIsr(Detector.UNUSED_SENSE_,
                              lambda: self._SpareTrigger())
        self.loop_thread = Thread(target = self._LoopThread, args = ()).start()
        self.is_night = False
    def TerminateLoopThread(self):
        print("Asyncio loop running in thread will be stopped")
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.gpio.cleanup()
    def setRelaisMode(self, relais, mode):
        self.relais_list[relais].set_mode(mode)
    def getRelaisMode(self, relais):
        return self.relais_list[relais].get_mode()
    def setDetectorMode(self, detector, mode):
        self.detector_list[detector] = mode
    def getDetectorMode(self, detector):
        return self.detector_list[detector]
    def setPwm(self, pwm, value):
        self.gpio.setPwm(pwm, value)
    def _LoopThread(self):
        print("Thread for asyncio loop started")
        asyncio.set_event_loop(self.loop)
        self._setSunTimes()
        self._setDefaultModes()
        self.loop.run_forever()

    def _MotionSensSouthTrigger(self):
        if self.detector_list[Detector.MOTION_SENSE_SOUTH] != DetectorMode.ACTIVE:
            print("MotionSensSouth trigger masked by UI")
        elif not self.is_night:
            print("MotionSensSouth trigger ignored, it is day!")
        else:
            print("MotionSensSouth triggered")
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_TERRACE].update_schedule, 4, 120)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_SOUTH].update_schedule,   0, 60)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_WEST].update_schedule,    2, 180)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_NORTH].update_schedule,   6, 120)
            #asyncio.run_coroutine_threadsafe(self.keepRelaisOnFor(Relais.LAMP_SOUTH, 5), self.loop)
    def _MotionSensTerraceTrigger(self):
        if self.detector_list[Detector.MOTION_SENSE_TERRACE] != DetectorMode.ACTIVE:
            print("MotionSensTerrace trigger masked by UI")
        elif not self.is_night:
            print("MotionSensTerrace trigger ignored, it is day!")
        else:
            print("MotionSensTerrace triggered")
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_TERRACE].update_schedule, 0, 120)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_SOUTH].update_schedule,   5, 60)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_WEST].update_schedule,    3, 60)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_NORTH].update_schedule,   5, 60)
    def _MotionSensNorthTrigger(self):
        if self.detector_list[Detector.MOTION_SENSE_NORTH] != DetectorMode.ACTIVE:
            print("MotionSenseNorth trigger masked by UI")
        elif not self.is_night:
            print("MotionSenseNorth trigger ignored, it is day!")
        else:
            print("MotionSenseNorth triggered")
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_TERRACE].update_schedule, 3, 120)
            #self.loop.call_soon_threadsafe(
                #self.relais_list[Relais.LAMP_SOUTH].update_schedule,   3, 10)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_WEST].update_schedule,    5, 120)
            self.loop.call_soon_threadsafe(
                self.relais_list[Relais.LAMP_NORTH].update_schedule,   0, 180)
    def _SpareTrigger(self):
        print("Spare triggered")

    def _getTimeDiff(self, t1, t2):
        return (t2.hour   - t1.hour)   * 3600 + \
            (t2.minute - t1.minute) * 60 + \
            (t2.second - t1.second)

    def _setDefaultModes(self):
        for relais in Relais:
            self.setRelaisMode(relais, RelaisMode.AUTO)
        for detector in Detector:
            self.setDetectorMode(detector, DetectorMode.ACTIVE)
        now = datetime.datetime.today()
        nextResetTime = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if now.hour > 5:
            nextResetTime += datetime.timedelta(days=1)
        seconds_to_reset = (nextResetTime - now).total_seconds()
        print("%s: Next reset of modes at %s, in %d seconds"
              %(now, nextResetTime, seconds_to_reset))
        self.loop.call_later(seconds_to_reset, self._setDefaultModes)

    def _setIsNight(self, now):
        time_to_sunrise = self._getTimeDiff(now.time(), self.sunrise.time())
        time_to_sunset  = self._getTimeDiff(now.time(), self.sunset.time())
        if time_to_sunrise < 300 and time_to_sunset > 300 : self.is_night = False
        else: self.is_night = True
        if time_to_sunrise < 0: time_to_sunrise += 24*3600
        if time_to_sunset  < 0: time_to_sunset  += 24*3600
        if self.is_night: return time_to_sunrise
        else: return time_to_sunset

    def _setSunTimes(self):
        city = LocationInfo(info=('Stuttgart', 'Germany', 48.742211, 9.2068, 'Europe/Berlin', 430))
        city.solar_depression = 'civil'
        now = datetime.datetime.now(city.tz)
        sun = city.sun(date=datetime.date.today(), local=True)
        self.sunset  = sun['sunset']
        self.sunrise = sun['sunrise']
        print("Sunrise %s, Sunset %s" %(self.sunrise, self.sunset))
        #print("now %s" % now)
        #print("time %s, sunrise %s, sunset %s" %
            #(now.time(), self.sunrise.time(), self.sunset.time()))
        #print("diff sunrise %d, diff sunset %d" %
            #(self._getTimeDiff(now.time(), self.sunrise.time()),
            # self._getTimeDiff(now.time(), self.sunset.time())))
        timeToActivation = self._setIsNight(now)
        print("%s: It is " %(now), end = '')
        if self.is_night: print("night!")
        else: print("day!")
        self.loop.call_later(timeToActivation, self._setSunTimes)
