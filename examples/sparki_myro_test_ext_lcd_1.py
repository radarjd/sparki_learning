# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

setDebug(DEBUG_INFO)
init("COM4")

print("Drawing a string on the LCD")
LCDdrawString(30, 5, "a string")

print("Drawing a pixel on the LCD at 0,0 (upper left corner)")
LCDdrawPixel(0,0)

if LCDreadPixel(0,0):
    print("The pixel at 0,0 is black")
else:
    print("The pixel at 0,0 is white")

print("Re-drawing a pixel on the LCD at 0,0 (upper left corner)")
LCDdrawPixel(0,0)

if LCDreadPixel(0,0):
    print("The pixel at 0,0 is black")
else:
    print("The pixel at 0,0 is white")

print("Waiting 5 seconds")
wait(5)

print("Clearing the screen")
LCDclear()

if LCDreadPixel(0,0):
    print("The pixel at 0,0 is black")
else:
    print("The pixel at 0,0 is white")

print("Drawing a line from 2,2 to 8,10")
LCDdrawLine( 2, 2, 8, 10 )
