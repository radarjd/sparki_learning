# Sparki_Myro testing
from __future__ import print_function
from sparki_learning import *
from random import randint

com_port = None     # replace with your COM port or /dev/

#setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

print("waiting random periods")

for x in range(10):
    time = randint(1, 20)
    print("time period is", time)
    startTime = currentTime()
    waitNoop(time)
    print("waitNoop took", currentTime() - startTime, "seconds")
