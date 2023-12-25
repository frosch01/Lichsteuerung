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

