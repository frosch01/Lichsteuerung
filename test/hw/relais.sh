#!/bin/bash

function finish {
  for PIN in $PINS; do
    gpio mode $PIN tri
    gpio mode $PIN in
    gpio write $PIN 0
  done
}

trap finish EXIT

PINS="1 4 5 6 26 27 28 29"

for PIN in $PINS; do 
  gpio mode $PIN tri
  gpio mode $PIN out
  gpio write $PIN 0
done

while true; do  
  for PIN in $PINS; do gpio write $PIN 1; sleep 1; done
  for PIN in $PINS; do gpio write $PIN 0; sleep 1; done
done

