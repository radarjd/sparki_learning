# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *
import logging

com_port = None     # replace with your COM port or /dev/

setDebug(logging.INFO)

while not com_port:
    com_port = input("What is your com port or /dev/? ")

init(com_port)

LCDprint("Beginning ping()")
LCDprintLn(" test")

count = 1

for _ in timer(120):
    LCDprint("Ping: ")
    LCDprintLn(str(ping()))
    wait(1)
    
    if count % 5 == 0:
        LCDprintLn("------------")
    
    count += 1
