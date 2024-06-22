import time
from rpi_hardware_pwm import HardwarePWM

pwm = HardwarePWM(pwm_channel=1, hz=2000, chip=0)
pwm.start(50)

time.sleep(10)

pwm.stop()
