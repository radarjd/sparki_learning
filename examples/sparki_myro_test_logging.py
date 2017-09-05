# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

import logging

# for version 1.5.0.0 and above of the library

print("This program tests out logging in the sparki library -- must be using version > 1.5.0.0")
print("Your current version is {}".format(getVersion()[0]))
printDebug("Check to see if printDebug works with the default level")

print("The logging levels are:")
print("{} is logging.DEBUG".format(logging.DEBUG))
print("{} is logging.INFO".format(logging.INFO))
print("{} is logging.WARN".format(logging.WARN))
print("{} is logging.ERROR".format(logging.ERROR))
print("{} is logging.CRITICAL".format(logging.CRITICAL))

for logging_level in (logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR, logging.CRITICAL):
    setDebug(logging_level)

    for message_level in (logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR, logging.CRITICAL):
        printDebug("Checking logging level {} with message level {}".format(logging_level, message_level), message_level)

print("That was increasing levels of severity -- now do decreasing")

for logging_level in (logging.CRITICAL, logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG):
    setDebug(logging_level)

    for message_level in (logging.CRITICAL, logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG):
        printDebug("Checking logging level {} with message level {}".format(logging_level, message_level), message_level)

