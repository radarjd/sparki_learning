# Sparki_Myro grid testing
from __future__ import print_function

from sparki_learning import *

init("COM4")        # change for your COM port (or /dev/)

print("Drawing first right triangle")

coordinates = [ [0, 10], [10, 10], [0, 0] ]

setDebug(DEBUG_INFO)

for coords in coordinates:
    print("Our current position is:", getPosition())

    newX = coords[0]
    newY = coords[1]

    print("Moving to", newX, ",", newY)
    moveTo(newX, newY)


print("Drawing second right triangle")

coordinates = [ [-10, 0], [-10, -10], [0, 0] ]

setDebug(DEBUG_INFO)

for coords in coordinates:
    print("Our current position is:", getPosition())

    newX = coords[0]
    newY = coords[1]

    print("Moving to", newX, ",", newY)
    moveTo(newX, newY)
