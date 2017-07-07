class GPIO(object):
  WPI_MODE_PINS = 0
  WPI_MODE_GPIO = 1
  WPI_MODE_GPIO_SYS = 2
  WPI_MODE_PHYS = 3
  WPI_MODE_PIFACE = 4
  WPI_MODE_UNINITIALISED = -1

  INPUT = 0
  OUTPUT = 1
  PWM_OUTPUT = 2
  GPIO_CLOCK = 3

  LOW = 0
  HIGH = 1

  PUD_OFF = 0
  PUD_DOWN = 1
  PUD_UP = 2

  PWM_MODE_MS = 0
  PWM_MODE_BAL = 1

  INT_EDGE_SETUP = 0
  INT_EDGE_FALLING = 1
  INT_EDGE_RISING = 2
  INT_EDGE_BOTH = 3

  LSBFIRST = 0
  MSBFIRST = 1

  MODE = 0
  def __init__(self,pinmode=0):
      print("Simulated GPIO class initialized")

  def piBoardRev(self):
    pass
  def wpiPinToGpio(self,*args):
    pass
  def setPadDrive(self,*args):
    pass
  def getAlt(self,*args):
    pass
  def digitalWriteByte(self,*args):
    pass

  def pwmSetMode(self,*args):
    pass
  def pwmSetRange(self,*args):
    pass
  def pwmSetClock(self,*args):
    pass
  def gpioClockSet(self,*args):
    pass
  def pwmWrite(self,*args):
    pass

  def pinMode(self,*args):
    pass

  def digitalWrite(self,*args):
    print("GPIO %d set to %d" % (args[0], args[1]))
  def digitalRead(self,*args):
    pass
  def digitalWriteByte(self,*args):
    pass

  def analogWrite(self,*args):
    pass
  def analogRead(self,*args):
    pass

  def shiftOut(self,*args):
    pass
  def shiftIn(self,*args):
    pass

  def pullUpDnControl(self,*args):
    pass

  def waitForInterrupt(self,*args):
    pass
  def wiringPiISR(self,*args):
    pass

  def softPwmCreate(self,*args):
    pass
  def softPwmWrite(self,*args):
    pass

  def softToneCreate(self,*args):
    pass
  def softToneWrite(self,*args):
    pass
