# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

# for version 1.1.1 and above of the library

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

print("initializing")
init(com_port)

print("Sparki's name is " + getName())

print("moving forward for 1 second")
forward(1, 1)

print("moving backward for 1 second")
backward(1, 1)

print("testing motors (should turn left / counter-clockwise)")
motors(-1, 1, 1)

print("turning head left")
servo(-90)

print("turning head right")
servo(90)

print("facing forward")
servo(0)

print("moving forward 5cm")
moveForwardcm(5)

print("moving backward 5cm")
moveBackwardcm(5)

print("beep")
beep()

print("testing motors (should turn right / clockwise)")
motors(1, -1, 1)

print("Battery power is {}".format( getBattery() ) )

print("Distance to nearest object is {} (-1 means Sparki didn't see anything)".format( ping() ))

print("Left light sensor is {}" .format( getLight( LIGHT_SENS_LEFT ) ) )
print("Center light sensor is {}".format( getLight( LIGHT_SENS_MID ) ) )
print("Right light sensor is {}".format( getLight( LIGHT_SENS_RIGHT ) ) )

print("Left edge line sensor is {}".format( getLine( LINE_EDGE_LEFT ) ) )
print("Left line sensor is {}".format( getLine( LINE_MID_LEFT ) ) )
print("Center line sensor is {}".format( getLine( LINE_MID ) ) )
print("Right line sensor is {}".format( getLine( LINE_MID_RIGHT ) ) )
print("Right edge line sensor is {}".format( getLine( LINE_EDGE_RIGHT ) ) )

print("X accel sensor is {}".format( getAccelX() ) )
print("Y accel sensor is {}".format( getAccelY() ) )
print("Z accel sensor is {}".format( getAccelZ() ) )

print("X mag sensor is {}".format( getMagX() ) )
print("Y mag sensor is {}".format( getMagY() ) )
print("Z mag sensor is {}".format( getMagZ() ) )

print("compass heading is {}".format( compass() ) )

print("turning right")
turnRight(1, 2)

print("Waiting 5...")
wait(5)

print("turning left")
turnLeft(1, 2)

print("Opening gripper")
gripperOpen()

print("Closing gripper")
gripperClose()

print("turning 90 degrees (right / clockwise)")
turnBy(90)

print("turning -30 degrees (left / counter-clockwise)")
turnBy(-30)

print("turning to 0 degrees (the original orientation of the robot)")
turnTo(0)

testLED = input("Should I run the RGB LED test (y to do it)? ")
if testLED == "y":
    print("Brightening RGB LED")
    for i in range(0, 101, 5):
        wait(.01)
        setLEDBack(i)

    print("Dimming RGB LED")
    for i in range(100, -1, -5):
        wait(.01)
        setLEDBack(i)

print("done")
