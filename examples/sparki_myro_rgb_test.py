# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while com_port == None:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

steps = 5
wait_time = .05

# the below isn't very useful when we use the statusLED to communicate that
# we're receiving or executing a command
print("Increasing status brightness")
for b in range(0, 101):
    setStatusLED(b)
    wait(wait_time)

print("Decreasing status brightness")
for b in range(100, -1, -1):
    setStatusLED(b)
    wait(wait_time)
# the above isn't very useful when we use the statusLED to communicate that
# we're receiving or executing a command

for r in range(0, 101, steps):
    for g in range(0, 101, steps):
        for b in range(0, 101, steps):
            setRGBLED(r, g, b)
            wait(wait_time)

setRGBLED(0, 0, 0)
