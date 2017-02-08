# Sparki_Myro testing
# requires version 1.4.0 or greater of the Python library
from __future__ import print_function
from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

address_written = False

while not address_written:
    bt = ask("What is your robot's bluetooth address? ")
    try:
        bluetoothWrite(bt)
        address_written = True
    except:
        print("That does not appear to be a valid bluetooth address")
        print("Bluetooth addresses contain six pairs of the numbers 0-9")
        print("and the letters A-F. The pairs are separated by - or :")
        print("If you have a Butler sparki, the bluetooth address is on a ")
        print("sticker on the bottom of your robot, and on your box")

bt = bluetoothRead()

if bt == None:
    print("Your bluetooth address is not properly stored")
else:
    print("Your bluetooth address is stored as " + bt)
