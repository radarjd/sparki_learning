# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

# for version 1.1.1 of the library

print("initializing")
init("COM3")            # change to your COM port (or /dev/)

print("Sparki's name is " + getName())

print("moving forward")
forward(1, 1)

print("moving backward")
backward(1, 1)

print("testing motors (should turn left / counter-clockwise)")
motors(-1, 1, 1)

print("beep")
beep()

print("testing motors (should turn right / clockwise)")
motors(1, -1, 1)

print("Battery power is " + str( getBattery() ) )

print("Left light sensor is " + str( getLight( LIGHT_SENS_LEFT ) ) )
print("Center light sensor is " + str( getLight( LIGHT_SENS_MID ) ) )
print("Right light sensor is " + str( getLight( LIGHT_SENS_RIGHT ) ) )

print("Left edge line sensor is " + str( getLine( LINE_EDGE_LEFT ) ) )
print("Left line sensor is " + str( getLine( LINE_MID_LEFT ) ) )
print("Center line sensor is " + str( getLine( LINE_MID ) ) )
print("Right line sensor is " + str( getLine( LINE_MID_RIGHT ) ) )
print("Right edge line sensor is " + str( getLine( LINE_EDGE_RIGHT ) ) )

print("X accel sensor is " + str( getAccelX() ) )
print("Y accel sensor is " + str( getAccelY() ) )
print("Z accel sensor is " + str( getAccelZ() ) )

print("X mag sensor is " + str( getMagX() ) )
print("Y mag sensor is " + str( getMagY() ) )
print("Z mag sensor is " + str( getMagZ() ) )

print("compass heading is " + str( compass() ) )

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

print("turning -90 degrees (left / counter-clockwise)")
turnBy(-90)

print("turning to 0 degrees (probably incorrect - compass is inconsistent)")
turnTo(0)

print("Brightening RGB LED")
for i in range(0,101, 5):
    wait(.01)
    setLEDBack(i)

print("Dimming RGB LED")
for i in range(100, -1, -5):
    wait(.01)
    setLEDBack(i)

print("done")
