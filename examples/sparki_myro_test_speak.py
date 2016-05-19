# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

sayme = None

print("The speak function relies on services provided by your operating system")
print("Check the sparki_learning.speak module to see what platforms have been implemented")

while sayme != "exit":
    sayme = str( input("What should I say? (type exit to stop) ") )
    speak( sayme )
