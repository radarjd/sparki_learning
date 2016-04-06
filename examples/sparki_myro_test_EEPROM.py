# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

com_port = None     # replace with your COM port or /dev/

setDebug(DEBUG_INFO)

while com_port == None:
    com_port = input("What is your com port or /dev/? ")

setDebug(DEBUG_INFO)

init(com_port)

EEPROM_store_location = 80
message = "testing"

EEPROMwrite(EEPROM_store_location, message)

read_back = str(EEPROMread(EEPROM_store_location, len(message)))
print(read_back)

if read_back == message:
    print("EEPROM write/read successful!")
else:
    print("Error in EEPROM test")

print("Overwriting testing with garbage")
EEPROMwrite(EEPROM_store_location, "garbage")

print("Overflow test time")

try:
    EEPROMwrite(1023, "supercalifragilisticexpialidocious")
    print("Uh, oh, you should not see this")
except IndexError:
    print("Correctly threw IndexError")

print("done")
