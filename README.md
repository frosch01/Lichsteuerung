# Lichtsteuerung

## Hardware setup

Prepare you PI for the S0-Shield by adding GPIO configuration to the config.txt.

```
echo "
# GPIO and PWM configuration for S0 shield
dtoverlay=pwm,pin=13,func=4,clock=500000
gpio=4,5,6,17,19,22,26,27=ip,pu
gpio=12,16,18,20,21,23,24,25=op,dh
" | sudo tee -a /boot/config.txt

```


## Amount of Meter Pulses per year

One HVAC takes about 300kwh per year. This means 300k pulses. 3 HVAC systems 
result in <1M pulses per year.

In the log, a world timestamp, and the power shall be stored. The 
timestamp takes 11 bytes including space 11. The power takes 5 bytes including
newline. So 16 bytes to store. Let's go for 20 in calculation....

Amount of bytes expected per year: 20MByte

It seems to be feasible to keep a cache inside the program for online visualization.

Big data part should be kept separated from the tool.

For fast search a FS based directory structure based on year, and month with a file 
per day seems to be a valid data base idea.

TinyFLux seems to be a nice idea to use as a file based time series DB.

