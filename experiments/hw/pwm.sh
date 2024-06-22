#!/bin/bash

PIN="23"

function finish {
    gpio mode $PIN tri
    gpio mode $PIN in
    gpio write $PIN 0
}

trap finish EXIT

# it is important to first activate the PWM and then configure the parametes
gpio mode $PIN pwm
gpio pwm-ms
gpio pwmc 1920
gpio pwmr 100
gpio pwm $PIN 10

declare -i i
declare -i pwm
i=0
while true; do
  pwm=i*10
  gpio pwm $PIN $pwm 
  echo $i: $pwm %
  sleep 2
  i+=1
  i=i%11
done

