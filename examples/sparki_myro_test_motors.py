# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

# for the DEBUG version of the library

print("initializing -- may get an error below due to library version")
com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while com_port == None:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

print("Your python library version is {} and your sparki library version is {}".format(getVersion[0],getVersion[1]))

setSparkiDebug(DEBUG_DEBUG)

print("moving forward")
forward(1, 1.5)

print("moving backward")
backward(1, 1.5)

print("turning left")
turnLeft(1, 1)

print("turning right")
turnRight(1, 1)

print("testing motors (should go forward)")
motors(1, 1, 1)

print("testing motors (should go backward)")
motors(-1, -1, 1)

print("testing motors (should turn left / counter-clockwise)")
motors(-1, 1, 1)

print("testing motors (should turn right / clockwise)")
motors(1, -1, 1)

print("done")
