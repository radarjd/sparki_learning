# Sparki_Myro testing
from __future__ import print_function

from sparki_myro import *

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
