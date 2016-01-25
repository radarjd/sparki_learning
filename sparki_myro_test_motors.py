# Sparki_Myro testing
from sparki_myro import *
import sparki_myro

# for the DEBUG version of the library

print("initializing -- may get an error below due to library version")
init("COM3")            # change to your COM port (or /dev/)

print("moving forward")
forward(1, 1)
wait(1)

print("moving backward")
backward(1, 1)
wait(1)

print("turning left")
turnLeft(1, 1)
wait(1)

print("turning right")
turnRight(1, 1)
wait(1)

print("testing motors (should go forward)")
motors(1, 1, 1)
wait(1)

print("testing motors (should go backward)")
motors(-1, -1, 1)
wait(1)

print("testing motors (should turn left / counter-clockwise)")
motors(-1, 1, 1)
wait(1)

print("testing motors (should turn right / clockwise)")
motors(1, -1, 1)
wait(1)

print("done")
