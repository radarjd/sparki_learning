# Sparki_Myro grid testing
from sparki_myro import *
import sparki_myro

init("COM3")        # change for your COM port (or /dev/)

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


##def drawFunction( function, xRange ):
##    for xCoord in xRange:
##        moveTo( xCoord, function(xCoord) )
##
##moveTo(0,0)
##
##print("Drawing y = x")
##
##drawFunction( lambda x: x, range(-20, 21) )
##
##print("finished y = x")
##
##moveTo(0,0)
##
##print("Drawing y = x ** 2")
##
##drawFunction( lambda x: x**2, range(-10, 10, .5) )
