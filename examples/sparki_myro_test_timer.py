# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(logging.INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

for x in timer(15):
    print("x = " + str(x))
    forward(1,1)
    backward(1,1)
