# Sparki_Myro drawFunction testing
from __future__ import print_function

from sparki_learning import *

import math

com_port = None     # replace with your COM port or /dev/

setDebug(logging.INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

print("Drawing y = x ** 2")

setPosition( -5, 25 )

drawFunction( lambda x: x**2, flrange(-5, 5.1, .1) )

print("Drawing y = sin(x)")

setPosition( 3.1, 0 )

drawFunction( lambda x: math.sin(x), flrange(3.1, -3.1, -.1), 5 ) 
