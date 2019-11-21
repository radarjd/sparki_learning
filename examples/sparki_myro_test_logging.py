# Sparki_Myro testing
from __future__ import print_function

from sparki_learning import *

# for version 1.6.0.0 and above of the library

print("This program tests out logging in the sparki library -- must be using version > 1.6.0.0")
print("Your current version is {}".format(getVersion()[0]))
printDebug("Check to see if printDebug works with the default level")

print("The logging levels are:")
print("{} is DEBUG_DEBUG".format(DEBUG_DEBUG))
print("{} is DEBUG_INFO".format(DEBUG_INFO))
print("{} is DEBUG_WARN".format(DEBUG_WARN))
print("{} is DEBUG_ERROR".format(DEBUG_ERROR))
print("{} is DEBUG_CRITICAL".format(DEBUG_CRITICAL))

for logging_level in (DEBUG_DEBUG, DEBUG_INFO, DEBUG_WARN, DEBUG_ERROR, DEBUG_CRITICAL):
    setDebug(logging_level)

    for message_level in (DEBUG_DEBUG, DEBUG_INFO, DEBUG_WARN, DEBUG_ERROR, DEBUG_CRITICAL):
        printDebug("Checking logging level {} with message level {}".format(logging_level, message_level), message_level)

print("That was increasing levels of severity -- now do decreasing")

for logging_level in (DEBUG_CRITICAL, DEBUG_ERROR, DEBUG_WARN, DEBUG_INFO, DEBUG_DEBUG):
    setDebug(logging_level)

    for message_level in (DEBUG_CRITICAL, DEBUG_ERROR, DEBUG_WARN, DEBUG_INFO, DEBUG_DEBUG):
        printDebug("Checking logging level {} with message level {}".format(logging_level, message_level), message_level)