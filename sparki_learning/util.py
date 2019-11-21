################## Sparki Learning Library Utility Functions ##################
#
# This file contains various utility functions used by the Sparki Learning Library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# written by Jeremy Eglen
# Created: November 12, 2019 (some functions are older -- this is the original date of this file)
# Last Modified: November 18, 2019
from __future__ import division, print_function

import sys
import time


# ***** DEBUG CONSTANTS ***** #
# these are the debug levels used
DEBUG_DEBUG = 5  # reports just about everything
DEBUG_INFO = 4  # reports entering functions
DEBUG_WARN = 3  # a generally sane default; reports issues that may be mistakes, but don't interfere with operation
DEBUG_ERROR = 2  # reports something contrary to the API
DEBUG_CRITICAL = 1  # reports an error which interferes with proper or consistent operation
DEBUG_ALWAYS = 0  # should always be reported
# ***** END DEBUG CONSTANTS ***** #

GLOBAL_DEBUG = DEBUG_ERROR


def bluetoothValidate(address):
    """ Returns True if the string argument appears to be a Bluetooth address (strictly speaking, a MAC address)
    
        arguments:
        address - string MAC address
        
        returns:
        boolean - True if it appears to be a bluetooth address, otherwise false
    """
    import re

    validMAC = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

    if validMAC.match(address):
        return True
    else:
        return False


def bresenham(x0, y0, x1, y1):
    # implementation from https://github.com/encukou/bresenham/blob/master/bresenham.py; MIT License
    """Yield integer coordinates on the line from (x0, y0) to (x1, y1).
    Input coordinates should be integers.
    The result will contain both the start and the end point.
    """
    printDebug("In bresenham, x0={}; y0={}; x1={}; y1={}".format(x0, y0, x1, y1), DEBUG_INFO)

    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2*dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x*xx + y*yx, y0 + x*xy + y*yy
        if D >= 0:
            y += 1
            D -= 2*dx
        D += 2*dy


def constrain(n, min_n, max_n):
    """ Ensures n is between min_n and max_n
    
        arguments:
        n - the number
        min_n - the minimum it could be
        max_n - the maximum it could be
        
        returns:
        n, unless it's less than min_n, then min_n; or it's more than max_n, then max_n
    """
    if min_n > max_n:
        printDebug("In constrain, min was greater than max (corrected)", DEBUG_ERROR)
        min_n, max_n = max_n, min_n

    if n < min_n:
        printDebug("In constrain, n ({}) was less than min ({}) (n set to min)".format(n, min_n), DEBUG_DEBUG)
        return min_n
    elif n > max_n:
        printDebug("In constrain, n ({}) was greater than max ({}) (n set to max)".format(n,max_n), DEBUG_DEBUG)
        return max_n
    else:
        return n


def currentTime():
    """ Gets the current time in seconds from the epoch (i.e. time.time())
    
        arguments:
        none
        
        returns:
        float - time in seconds since January 1, 1970
    """
    printDebug("In currentTime", DEBUG_INFO)

    return time.time()


def flrange(start, stop, step):
    """ Generator like range() (or xrange() prior to python 3) which allows float steps
    
        arguments:
        start - the starting number for the range
        stop - the number which the range cannot go over; the last value generated will be stop - step
        step - the stepping value for the range; if step is negative, the values yielded will count down from
               start to stop, so start must be > than stop
        
        yield:
        float - the next value in the range
    """
    printDebug("In flrange, start={}; stop={}; step={}".format(start, stop, step), DEBUG_INFO)

    if step > 0:
        while start < stop:
            yield start  # yield is a special keyword which is something like return, but behaves very differently
            # more info can be found at https://docs.python.org/3.4/reference/expressions.html#yieldexpr
            start += step
    elif step < 0:
        while start > stop:
            yield start
            start += step
    else:
        printDebug("In flrange, invalid value for step", DEBUG_ERROR)
        raise StopIteration


def humanTime():
    """ Return a human readable current time (i.e. time.ctime())
        Output looks like 'Fri Apr 5 19:50:05 2016'
    
        arguments:
        none
        
        returns:
        string - time of call
    """
    printDebug("In humanTime", DEBUG_INFO)

    return time.ctime()


def printDebug(message, level=DEBUG_ERROR, myfile=sys.stderr):
    """ Prints message to stream if level is less than or equal to GLOBAL_DEBUG
    
        arguments:
        message - the message to print
        level - the level of the error (lower numbers are more severe - default DEBUG_ERROR [2])
        myfile - the stream to which we should print (default stderr)
        
        returns:
        nothing
    """
    global GLOBAL_DEBUG
    
    if level <= GLOBAL_DEBUG:
        print("[{}]/{} --- {}".format(time.ctime(), level, message), file=myfile)


def setGlobalDebug(new_level):
    """ Sets GLOBAL_DEBUG to a new level (lower numbers should be more verbose)
    
        arguments:
        new_level - the new level of GLOBAL_DEBUG
        
        returns:
        nothing
    """
    global GLOBAL_DEBUG
    
    printDebug("Changing GLOBAL_DEBUG to " + str(new_level), DEBUG_WARN)
    
    GLOBAL_DEBUG = new_level


def timer(duration):
    """ Generator which yields the time since the instantiation, and ends after start_time + duration (seconds)
    
        arguments:
        duration - the float number of seconds until the generator should end
        
        yield:
        float - number of seconds since the first call
    """
    printDebug("In timer, duration is " + str(duration), DEBUG_INFO)

    if duration > 0:
        start_time = currentTime()

        while currentTime() < start_time + duration:
            yield currentTime() - start_time
    else:
        printDebug("In timer, invalid value for duration", DEBUG_ERROR)
        raise StopIteration


def wrapAngle(angle):
    """ Ensures angle is between -360 and 360
    
        arguments:
        angle - float angle that you want to be between -360 and 360
        
        returns:
        float - angle between -360 and 360
    """
    printDebug("In wrapAngle, angle is " + str(angle), DEBUG_INFO)

    if angle >= 0:
        return angle % 360
    else:
        return angle % -360


def main():
    print("This is intended to be used as a library -- your code should call this file by importing the library, e.g.")
    print("from sparki_learning.util import *")
    print("or")
    print("import sparki_learning.util")
    print("Exiting...")


if __name__ == "__main__":
    main()
