# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

speeds = (.5, 1, 1.5, 2, 2.5)
angle = 90

for speed in speeds:
    forward( 1, speed )
    turnBy(angle)
    forward(1,1)
    turnBy(angle)
    angle = -angle
