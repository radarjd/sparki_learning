# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

##print("Using turnLeft")
##turnLeft(.5, 3)
##print("Using motors to turn left")
##motors(-.5, .5, 3)
##print("Using turnRight")
##turnRight(.5, 3)
##print("Using backward")
##backward(1, 3)
##print("Using forward")
##forward(1, 3)

##motors(1, 1)
##wait(3)
##stop()

#print("Using a different motors to turn left")
#motors(.1, .5, 3)

music_sunrise()

print("Printing some text")
LCDprint("test print")
LCDupdate()

print("Printing some more text")
LCDprintLn("test println")
LCDupdate()

print("Using turnBy at 90 degrees")
turnBy(90)

print("Using turnBy at -90 degrees")
turnBy(-90)

print("Moving forward by 10 cm")
moveForwardcm(10)

print("Moving backward by 10 cm")
moveBackwardcm(10)

print("Getting obstacles")
print( getObstacle() )
