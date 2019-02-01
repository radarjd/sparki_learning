# Sparki_Myro testing
from __future__ import print_function
from sparki_learning import *

com_port = ""     # replace with your COM port or /dev/

#setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

print("Starting forward motion")

count = 0
sum_x = sum_y = sum_z = 0

forward(1)

while isMoving():
    x, y, z = getAccel()
    sum_x = sum_x + x
    sum_y = sum_y + y
    sum_z = sum_z + z
    
    print("Accel sensors - X:", x, ", Y:", y, ", Z:", z)

    wait(1)
    count = count + 1

    if count >= 10:
        stop()

print("Average sensors - X:", sum_x / count, ", Y:", sum_y / count, ", Z:", sum_z / count)

print("Starting turning right motion")

count = 0
sum_x = sum_y = sum_z = 0

turnRight(1)

while isMoving():
    x, y, z = getAccel()
    sum_x = sum_x + x
    sum_y = sum_y + y
    sum_z = sum_z + z
    
    print("Accel sensors - X:", x, ", Y:", y, ", Z:", z)

    wait(1)
    count = count + 1

    if count >= 10:
        stop()

print("Average sensors - X:", sum_x / count, ", Y:", sum_y / count, ", Z:", sum_z / count)

print("movement done")

count = 0
sum_x = sum_y = sum_z = 0

for seconds in timer(10):
    x, y, z = getAccel()
    sum_x = sum_x + x
    sum_y = sum_y + y
    sum_z = sum_z + z
    
    print("Accel sensors - X:", x, ", Y:", y, ", Z:", z)

    count = count + 1

    wait(1)

print("Average sensors - X:", sum_x / count, ", Y:", sum_y / count, ", Z:", sum_z / count)

print("Versions: ", getVersion())
