# Sparki_Myro testing
from __future__ import print_function

from sparki_myro import *

init("COM4")
steps = 5
wait_time = .5

print("Increasing status brightness")
for b in range(0, 101):
    setStatusLED(b)
    wait(wait_time)

print("Decreasing status brightness")
for b in range(100, -1, -1):
    setStatusLED(b)
    wait(wait_time)

for r in range(0, 101, steps):
    for g in range(0, 101, steps):
        for b in range(0, 101, steps):
            setRGBLED(r, g, b)
            wait(wait_time)

setRGBLED(0, 0, 0)
