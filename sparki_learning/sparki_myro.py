################## Sparki Myro Library ##################
#
# This implements the Myro API for the Sparki robot
# The Myro API was created by the Institute for Personal Robotics in Education (IPRE)
# This library was not written by the IPRE, is not a product of the IPRE and its authors have no relationship with the IPRE.
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# Your Sparki will need the sparki_myro.ino program running on it, and you need to have paired your Sparki with your computer
# over Bluetooth.
#
# written by Jeremy Eglen
# Created: November 2, 2015
# Last Modified: March 22, 2016
# written targeting Python 3.4, but likely works with other versions; limited testing has been successful with Python 2.7

from __future__ import division, print_function    # in case this is run from Python 2.6 or greater, but less than Python 3

import datetime
import math
import os
import sys
import serial                   # developed with pyserial 2.7, but also tested with 3.1
import time

# try to import tkinter -- but make a note if we can't
try:
    import tkinter as tk        # for the senses, joystick, ask, and askQuestion functions
    root = tk.Tk().withdraw()   # hide the main window -- we're not going to use it
    USE_GUI = True
except:
    print("Unable to use tkinter; no GUI available", file = sys.stderr)
    USE_GUI = False
    

########### CONSTANTS ###########
# ***** VERSION NUMBER ***** #
SPARKI_MYRO_VERSION = "1.1.1"     # this may differ from the version on Sparki itself


# ***** MESSAGE TERMINATOR ***** #
TERMINATOR = chr(23)   # this character is at the end of every message to / from Sparki


# ***** SYNC ***** #
SYNC = chr(22)   # this character is sent by Sparki after every command completes so we know it's ready for the next


# ***** COMPILE OPTIONS ***** #
# some commands may be turned off in the version of sparki myro running on Sparki
# these will be reset during the initialization process depending on the version (see the SPARKI_CAPABILITIES variable)
NO_MAG = False
NO_ACCEL = False
SPARKI_DEBUGS = False
USE_EEPROM = True


# ***** MISCELLANEOUS VARIABLES ***** #
SECS_PER_CM = .42       # number of seconds it takes sparki to move 1 cm; estimated from observation - may vary depending on batteries and robot
SECS_PER_DEGREE = .035  # number of seconds it takes sparki to rotate 1 degree; estimated from observation - may vary depending on batteries and robot
MAX_TRANSMISSION = 30   # maximum message length is 30 - size of the buffer in getSerialBytes() on the Sparki


# ***** SERIAL TIMEOUT ***** #
CONN_TIMEOUT = 5        # in seconds


# ***** COMMAND CHARACTER CODES ***** #
# Sparki Myro works by sending commands over the serial port (bluetooth) to Sparki from Python
# This is the list of possible command codes; note that it is possible for some commands to be turned off at Sparki's level (e.g. the Accel, Mag)
COMMAND_CODES = {
                    'BEEP':'b',           # requires 2 arguments: int freq and int time; returns nothing
                    'COMPASS':'c',        # no arguments; returns float heading
                    'GAMEPAD':'e',        # no arguments; returns nothing
                    'GET_ACCEL':'f',      # no arguments; returns array of 3 floats with values of x, y, and z
                    'GET_BATTERY':'j',    # no arguments; returns float of voltage remaining
                    'GET_LIGHT':'k',      # no arguments; returns array of 3 ints with values of left, center & right light sensor
                    'GET_LINE':'m',       # no arguments; returns array of 5 ints with values of left edge, left, center, right & right edge line sensor
                    'GET_MAG':'o',        # no arguments; returns array of 3 floats with values of x, y, and z
                    'GRIPPER_CLOSE_DIS':'v',  # requires 1 argument: float distance to close the gripper; returns nothing
                    'GRIPPER_OPEN_DIS':'x',   # requires 1 argument: float distance to open the gripper; returns nothing
                    'GRIPPER_STOP':'y',   # no arguments; returns nothing
                    'INIT':'z',           # no arguments; confirms communication between computer and robot
                    'LCD_CLEAR':'0',      # no arguments; returns nothing

                    ## below LCD commands removed for compacting purposes
                    ##'LCD_DRAW_CIRCLE':'1',    # requires 4 arguments: int x&y, int radius, and int filled (1 is filled); returns nothing
                    ##'LCD_DRAW_LINE':'2',  # requires 4 arguments ints x&y for start point and x1&y1 for end points; returns nothing
                    'LCD_DRAW_PIXEL':'3',     # requires 2 arguments: int x&y; returns nothing
                    ##'LCD_DRAW_RECT':'4',  # requires 5 arguments: int x&y for start point, ints width & height, and int filled (1 is filled); returns nothing 
                    ##'LCD_DRAW_STRING':'5',    # requires 3 arguments: int x (column), int line_number, and char* string; returns nothing

                    'LCD_PRINT':'6',      # requires 1 argument: char* string; returns nothing
                    'LCD_PRINTLN':'7',    # requires 1 argument: char* string; returns nothing
                    ##'LCD_READ_PIXEL':'8',     # requires 2 arguments: int x&y; returns int color of pixel at that point - removed for compacting
                    'LCD_UPDATE':'9',     # no arguments; returns nothing
                    'MOTORS':'A',         # requires 3 arguments: int left_speed (1-100), int right_speed (1-100), & float time
                                                            # if time < 0, motors will begin immediately and will not stop; returns nothing
                    'BACKWARD_CM':'B',    # requires 1 argument: float cm to move backward; returns nothing
                    'FORWARD_CM':'C',     # requires 1 argument: float cm to move forward; returns nothing
                    'PING':'D',           # no arguments; returns ping at current servo position
                    'RECEIVE_IR':'E', 
                    'SEND_IR':'F', 
                    'SERVO':'G',          # requires 1 argument: int servo position; returns nothing
                    'SET_DEBUG_LEVEL':'H',    # requires 1 argument: int debug level (0-5); returns nothing
                    'SET_RGB_LED':'I',    # requires 3 arguments: int red, int green, int blue; returns nothing
                    'SET_STATUS_LED':'J',     # requires 1 argument: int brightness of LED; returns nothing
                    'STOP':'K',           # no arguments; returns nothing
                    'TURN_BY':'L',        # requires 1 argument: float degrees to turn - if degrees is positive, turn clockwise,
                                                            # if degrees is negative, turn counterclockwise; returns nothing
                    'GET_NAME':'O',       # get the Sparki's name as stored in the EEPROM - USE_EEPROM must be True
                                                            # if the name was not set previously, can give undefined behavior
                    'SET_NAME':'P'        # set the Sparki's name in the EEPROM - USE_EEPROM must be True
                }
#***** END OF COMMAND CHARACTER CODES ***** #


# ***** DEBUG CONSTANTS ***** #
# sparki_myro_py_debug (defined below) holds the current debug level
DEBUG_DEBUG = 5             # reports just about everything
DEBUG_INFO = 4              # reports entering functions
DEBUG_WARN = 3              # a generally sane default; reports issues that may be mistakes, but don't interfere with operation
DEBUG_ERROR = 2             # reports something contrary to the API
DEBUG_CRITICAL = 1          # reports an error which interferes with proper or consistent operation
DEBUG_ALWAYS = 0            # should always be reported


# ***** SENSOR POSITION CONSTANTS ***** #
# LINE SENSORS #
LINE_EDGE_RIGHT = 4
LINE_MID_RIGHT = 3
LINE_MID = 2
LINE_MID_LEFT = 1
LINE_EDGE_LEFT = 0


# LIGHT SENSORS #
LIGHT_SENS_RIGHT = 2
LIGHT_SENS_MID = 1
LIGHT_SENS_LEFT = 0


# ***** MAX GRIPPER DISTANCE ***** #
MAX_GRIPPER_DISTANCE = 7.0


# ***** MAX NAME LENGTH ***** #
EEPROM_NAME_MAX_CHARS = 20


# ***** SERVO POSITIONS ***** #
SERVO_LEFT = -80
SERVO_CENTER = 0
SERVO_RIGHT = 80


# ***** TABLE OF CAPABILITIES ***** #
# this dictionary stores the capabilities of various versions of the program running on the Sparki itself
# this is used in init to update the capabilities of the Sparki -- you could use this so that the library can
#   work with different versions of the Sparki library
# The order of the fields is NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, reserved, reserved, reserved
SPARKI_CAPABILTIES = { "z": [ True, True, False, False, False, False, False ],
                       "DEBUG": [ False, False, True, False, False, False, False ],
                       "0.2 No Mag / No Accel": [ True, True, False, False, False, False, False ],
                       "0.8.3 Mag / Accel On": [ False, False, False, False, False, False, False ],
                       "0.9.6": [ False, False, False, True, False, False, False ],
                       "0.9.7": [ False, False, False, True, False, False, False ],   
                       "0.9.8": [ False, False, False, True, False, False, False ],   
                       "1.0.0": [ False, False, False, True, False, False, False ] }   

########### END OF CONSTANTS ###########

########### GLOBAL VARIABLES ###########
command_queue = []              # this stores every command sent to Sparki; I don't have a use for it right now...

centimeters_moved = 0           # this stores the sum of centimeters moved forward or backward using the moveForwardcm()
                                # or moveBackwardcm() functions; forward movement is positive, and backwards movement is negative
                                # used implicitly by moveTo() and moveBy()
                                # I don't have a use for this right now either...
                                
degrees_turned = 0              # this stores the sum of degrees turned using the turnBy() function; positive is clockwise
                                # and negative is counterclockwise
                                # can be set by setAngle() or retrieved with getAngle()

init_time = -1                  # time when the robot was initialized

robot_library_version = None    # version of the code on the robot

sparki_myro_py_debug = DEBUG_WARN    # this is the default debug level
serial_port = None              # save the serial port on which we're connected
serial_conn = None              # hold the pyserial object
serial_is_connected = False     # set to true once connection is done

xpos = 0                        # for the moveBy(), moveTo(), getPosition() and setPosition() commands (the "grid commands"), these
ypos = 0                        # variables keep track of the current x,y position of the robot; each integer coordinate is 1cm, and
                                # the robot starts at 0,0
                                # note that these _only_ update with the grid commands (e.g. motors(1,1,1) will not change the xpos & ypos)
                                # making these of limited value
########### END OF GLOBAL VARIABLES ###########

########### INTERNAL FUNCTIONS ###########
# these functions are intended to be used by the library itself
def askQuestion_text(message, options, caseSensitive = True):
    """ Gets a string from the user, which must be one of the options -- prints message

        arguments:
        message - string to print to prompt the user
        options - list of options for the user to choose
        caseSensitive - boolean, if True, response must match case

        returns:
        string response from the user (if caseSentitive is False, this will always be a lower case string)
    """
    if not caseSensitive:   # if we're not caseSensitive, make the options lower case
        working_options = [ s.lower() for s in options ]
    else:
        working_options = options

    result = input(message)

    if not caseSensitive:
        result = result.lower()

    while result not in working_options:
        print("Your answer must be one of the following: " + str(options))
        result = input(message)

        if not caseSensitive:
            result = result.lower()

    return result


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
        return min_n
    elif n > max_n:
        return max_n
    else:
        return n


def disconnectSerial():
    """ Disconnects from the Sparki robot

        arguments:
        none
        
        returns:
        nothing
    """
    global init_time
    global serial_conn
    global serial_is_connected
    global serial_port

    if serial_is_connected:
        serial_is_connected = False
        serial_conn.close()
        serial_conn = None
        serial_port = None
        init_time = -1


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
    if step > 0:
        while start < stop:
            yield start    # yield is a special keyword which is something like return, but behaves very differently
                           # more info can be found at https://docs.python.org/3.4/reference/expressions.html#yieldexpr
            start += step
    elif step < 0:
        while start > stop:
            yield start
            start += step
    else:
        printDebug("In flrange, invalid value for step", DEBUG_ERROR)
        raise StopIteration


def getSerialBytes():
    """ Returns bytes from the serial port up to TERMINATOR
    
        arguments:
        none
        
        returns:
        string - created from bytes in the serial port
    """
    global serial_conn
    global serial_is_connected

    if not serial_is_connected:
        printDebug("Sparki is not connected - use init()", DEBUG_CRITICAL)
        raise RuntimeError

    result = bytearray()

    try:
        inByte = serial_conn.read()
    except serial.SerialTimeoutException:
        printDebug("Error communicating with Sparki", DEBUG_CRITICAL)
        raise
    
    printDebug("Getting Bytes... first byte is " + str(inByte), DEBUG_DEBUG)
    
    while inByte != TERMINATOR.encode(): # read until we see a TERMINATOR
        if inByte != SYNC.encode():      # ignore it - we don't care about SYNCs
            result = result + inByte

        try:
            inByte = serial_conn.read()
        except serial.SerialTimeoutException:
            printDebug("Error communicating with Sparki", DEBUG_CRITICAL)
            raise

        if inByte != SYNC.encode():    
            printDebug("Next byte is " + str(inByte), DEBUG_DEBUG)
        
    printDebug("Finished fetching bytes, result is " + str(result), DEBUG_DEBUG)    
    return result.decode()
        
        
def getSerialChar():
    """ Returns the next char (str) from the serial port
    
        arguments:
        none
        
        returns:
        char (str) - from the serial port
    """
    result = chr( int( getSerialBytes() ) )

    printDebug("In getSerialChar, returning " + result, DEBUG_DEBUG)
    return result
    
    
def getSerialFloat():
    """ Returns the next float from the serial port
    
        arguments:
        none
        
        returns:
        float - from the serial port; returns a -1 if Sparki gave "ovf" or no response
    """
    result = getSerialBytes()

    if str(result) == "ovf" or len(result) == 0:    # check for overflow
        result = -1.0   # -1.0 is not necessarily a great "error response", except that values from the Sparki should be positive
    else:
        result = float(result)

    printDebug("In getSerialFloat, returning " + str(result), DEBUG_DEBUG)
    return result

    
def getSerialInt():
    """ Returns the next int from the serial port
    
        arguments:
        none
        
        returns:
        int - from the serial port; returns a -1 if Sparki gave "ovf" or no response
    """
    result = getSerialBytes()

    if str(result) == "ovf" or len(result) == 0:    # check for overflow
        result = -1   # -1 is not necessarily a great "error response", except that values from the Sparki should be positive
    else:
        result = int(result)

    printDebug("In getSerialInt, returning " + str(result), DEBUG_DEBUG)
    return result
        
        
def getSerialString():
    """ Returns the next string from the serial port
    
        arguments:
        none
        
        returns:
        string - from the serial port
    """
    result = str( getSerialBytes() )

    printDebug("In getSerialString, returning " + result, DEBUG_DEBUG)
    return result

    
def printDebug(message, priority = DEBUG_WARN, output = sys.stderr):
    """ Print message if priorty is greater than or equal to the current sparki_myro_py_debug priority 
    
        arguments:
        message - the string message to be printed
        priority - the integer priority of the message; defaults to DEBUG_WARN
        output - the file to which the message should be printed, defaults to stderr

        returns:
        nothing
    """
    # logging could have been done via the standard library logging module
    global sparki_myro_py_debug
    
    if priority <= sparki_myro_py_debug:
        print(message, file = output);


def music_sunrise():
    # plays "Sunrise" from Also sprach Zarathustra by Strauss (aka the 2001 theme)
    beep(1000, 523)
    beep(1000, 784)
    beep(1000, 1047)
        
    
def sendSerial(command, args = None):
    """ Sends the command with the args over a serial connection
        
        arguments:
        command - a character command code as defined at the top of this file
        args - a list of arguments to be sent; optional
        
        returns:
        nothing
    """
    global command_queue
    global serial_conn
    global serial_is_connected

    if not serial_is_connected:
        printDebug("Sparki is not connected - use init()", DEBUG_ALWAYS)
        raise RuntimeError

    if command == None:
        printDebug("No command given", DEBUG_ALWAYS)
        raise RuntimeError

    command_queue.append( [ command, args ] )  # keep track of every command sent

    waitForSync()           # be sure Sparki is available before sending    
    printDebug("In sendSerial, Sending command - " + command, DEBUG_DEBUG)
         
    values = [ ]            # this will hold what we're actually sending to Sparki
   
    values.append(command)
    
    if args != None:
        if isinstance( args, str ):
            values.append(args)
            printDebug("In sendSerial, values is " + str(values), DEBUG_DEBUG)
        else:
            values = values + args
    
    for value in values:
        message = (str(value) + TERMINATOR).encode()
       
        if len(message) > MAX_TRANSMISSION:
            printDebug("Messages must be " + str(MAX_TRANSMISSION) + " characters or fewer", DEBUG_ERROR)
            raise RuntimeError
        
        printDebug("Sending bytes " + str(message) + " (" + str(value) + ")", DEBUG_DEBUG)

        try:
            serial_conn.write(message)
        except serial.SerialTimeoutException:
            printDebug("Error communicating with Sparki", DEBUG_CRITICAL)
            raise

    serial_conn.flush()     # ensure the buffer is flushed
    wait(.01)


def senses_text():
    """ Displays the senses in text
    """
    print("Left edge line sensor is " + str( getLine( LINE_EDGE_LEFT ) ) )
    print("Left line sensor is " + str( getLine( LINE_MID_LEFT ) ) )
    print("Center line sensor is " + str( getLine( LINE_MID ) ) )
    print("Right line sensor is " + str( getLine( LINE_MID_RIGHT ) ) )
    print("Right edge line sensor is " + str( getLine( LINE_EDGE_RIGHT ) ) )

    print("Left light sensor is " + str( getLight( LIGHT_SENS_LEFT ) ) )
    print("Center light sensor is " + str( getLight( LIGHT_SENS_MID ) ) )
    print("Right light sensor is " + str( getLight( LIGHT_SENS_RIGHT ) ) )

    if not NO_MAG:
        print("X mag sensor is " + str( getMagX() ) )
        print("Y mag sensor is " + str( getMagY() ) )
        print("Z mag sensor is " + str( getMagZ() ) )
        print("compass heading is " + str( compass() ) )

    if not NO_ACCEL:
        print("X accel sensor is " + str( getAccelX() ) )
        print("Y accel sensor is " + str( getAccelY() ) )
        print("Z accel sensor is " + str( getAccelZ() ) )

    print("Ping is " + str( ping() ) + " cm")

    print("Battery power is " + str( getBattery() ) )
    print("#########################################")
    

def waitForSync():
    """ Waits for the SYNC character from Sparki

        arguments:
        none

        returns:
        nothing
    """
    global serial_conn
    global serial_is_connected

    if not serial_is_connected:
        printDebug("Sparki is not connected - use init()", DEBUG_CRITICAL)
        raise RuntimeError

    serial_conn.flushInput()    # get rid of any waiting bytes

    inByte = -1
    count = 0
    loop_wait = .1              # pause this long each time through the loop

    while inByte != SYNC.encode():  # loop, doing nothing substantive, while we wait for SYNC
        try:
            inByte = serial_conn.read()
        except serial.SerialTimeoutException:
            printDebug("Unable to sync with Sparki", DEBUG_CRITICAL)
            raise
        printDebug("Waiting for sync, count = " + str(count), DEBUG_DEBUG)
        count += 1

        if count * loop_wait > CONN_TIMEOUT:
            printDebug("Unable to sync with Sparki", DEBUG_CRITICAL)
            raise serial.SerialTimeoutException

        wait(loop_wait)


def wrapAngle(angle):
    """ Ensures angle is between -360 and 360
    
        arguments:
        angle - float angle that needs to be between -360 and 360
        
        returns:
        float - angle between -360 and 360
    """
    if angle >= 0:
        return angle % 360
    else:
        return angle % -360
########### END OF INTERNAL FUNCTIONS ###########


###################### SPARKI MYRO FUNCTIONS ######################
# These functions are intended to be called by users of this library        
def ask(message, mytitle = "Question"):
    """ Gets input from the user -- prints message

        arguments:
        message - string to print to prompt the user
        mytitle - title for the window (defaults to Question)

        returns:
        string response from the user
    """
    printDebug("In ask", DEBUG_INFO)

    if USE_GUI:
        try:
            result = tk.simpledialog.askstring(mytitle, message)
        except:
            result = None
    
        return result
    else:
        return input(message)


def askQuestion(message, options, mytitle = "Question"):
    """ Gets input from the user -- prints message and displays buttons with options

        arguments:
        message - string to print to prompt the user
        options - a list of strings which could be the response
        mytitle - title for the window (defaults to Question)

        returns:
        string response from the user
    """
    printDebug("In askQuestion", DEBUG_INFO)

    if USE_GUI:
        try:
            result = tk.simpledialog(title = mytitle, text = message, buttons = options)
        except:
            result = None
    
        return result
    else:
        return askQuestion_text(message, options)


def backward(speed, time = -1):
    """ Moves backward at speed for time; time is optional
    
        arguments:
        speed - a float between -1.0 and 1.0
        time - the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """
    printDebug("In backward, speed is " + str(speed) + " and time is " + str(time), DEBUG_INFO)
    
    # adjust speed to Sparki's requirements
    if speed < 0:
        printDebug("In backward, speed < 0, calling forward", DEBUG_WARN)
        forward(-speed, time)
        return
    elif speed == 0:
        printDebug("In backward, speed == 0, doing nothing", DEBUG_WARN)
        return
    elif speed > 1.0:
        printDebug("In forward, speed > 1.0, reducing to 1", DEBUG_ERROR)
        speed = 1

    motors( -speed, -speed, time )



def beep(time = 200, freq = 2800):
    """ Plays a tone on the Sparki buzzer at freq for time; both are optional
    
        arguments:
        time - time in milliseconds to play freq (default 200ms)
        freq - integer frequency of the tone (default 2800Hz)
        
        returns:
        nothing
    """
    printDebug("In beep, freq is " + str(freq) + " and time is " + str(time), DEBUG_INFO)
    
    freq = int(freq)    # ensure we have the right type of data
    time = int(time)

    freq = constrain(freq, 0, 40000)
    time = constrain(time, 0, 10000)
    
    args = [ freq, time ]
    
    sendSerial( COMMAND_CODES["BEEP"], args )
    wait(time / 1000)


def compass():
    """ Gets the current compass heading of the Sparki - can be flakey

        arguments:
        none
        
        returns:
        float - heading
    """
    
    if NO_MAG:
        printDebug("Magnometers not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError
    
    printDebug("In compass", DEBUG_INFO)

    sendSerial( COMMAND_CODES["COMPASS"] )
    result = getSerialFloat()
    return result

    
def currentTime():
    """ Gets the current time in seconds from the epoch (i.e. time.time())
    
        arguments:
        none
        
        returns:
        float - time in seconds since January 1, 1970
    """
    
    return time.time()

    
def drawFunction(function, xvals, scale = 1):
    """ Draws the function specified on the coordinate plane using moveTo()

        The arguments are the function which calculates y as a value of x, a list of x values to calculate from,
        and an optional scale factor

        For example, a valid call to this would be drawFunction( lambda x: x**2, flrange(-5, 5.1, .1) ) which
        would draw the function y = x**2 for values of x from -2 up to 2 going .1 of a value at a time
    
        arguments:
        function - should be a lambda function; the function should calculate the value of y given x
        xvals - an iterator which holds the values of x
        scale - a multiplier for x and y to make them larger on the plane
        
        returns:
        nothing
    """
    printDebug("In drawFunction, xvals are " + str(xvals) + ", and scale is " + str(scale), DEBUG_INFO)
    
    for x in xvals:
        moveTo( x * scale, function(x) * scale )


def forward(speed, time = -1):
    """ Moves forward at speed for time; time is optional
    
        arguments:
        speed - a float between -1.0 and 1.0
        time - the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """
    printDebug("In forward, speed is " + str(speed) + " and time is " + str(time), DEBUG_INFO)
    
    # adjust speed to Sparki's requirements
    if speed < 0:
        printDebug("In forward, speed < 0, calling backward", DEBUG_WARN)
        backward(-speed, time)
        return
    elif speed == 0:
        printDebug("In forward, speed == 0, doing nothing", DEBUG_WARN)
        return
    elif speed > 1.0:
        printDebug("In forward, speed > 1.0, reducing to 1", DEBUG_ERROR)
        speed = 1
        
    motors( speed, speed, time )


def gamepad():
    """ Drives the robot using the remote control
        Do not send additional commands until gamepad() terminates
    
        arguments:
        none
        
        returns:
        nothing
    """
    printDebug("Beginning gamepad control", DEBUG_INFO)
    
    sendSerial( COMMAND_CODES["GAMEPAD"] )
    print("Sparki will not respond to other commands until remote control ends")
    print("Press - or + on the remote to stop using the gamepad")
    # we could put a waitForSync() here, but it would likely time out


def getAccel():
    """ Returns the values (X, Y, and Z) of the accelerometers
    
        arguments:
        none
        
        returns:
        list of 3 floats representing the X, Y, and Z sensors (in that order)
    """
    if NO_ACCEL:
        printDebug("Accelerometers not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getAccel", DEBUG_INFO)
        
    sendSerial( COMMAND_CODES["GET_ACCEL"] )
    result = [ getSerialFloat(), getSerialFloat(), getSerialFloat() ]
    return result
    
    
def getAccelX():
    """ Returns the values of the X accelerometer
    
        arguments:
        none
        
        returns:
        float - representing the X sensor
    """

    return getAccel()[0]

    
def getAccelY():
    """ Returns the values of the Y accelerometer
    
        arguments:
        none
        
        returns:
        float - representing the Y sensor
    """

    return getAccel()[1]
    
    
def getAccelZ():
    """ Returns the values of the Z accelerometer
    
        arguments:
        none
        
        returns:
        float - representing the Z sensor
    """

    return getAccel()[2]


def getAngle():
    """ Returns the number of degrees that the robot has turned using turnBy since it was initialized
        OR since setAngle() was called

        arguments:
        none

        returns:
        float - number of degrees that the robot has turned
    """
    global degrees_turned
    
    printDebug("In getAngle", DEBUG_INFO)

    return degrees_turned


def getBattery():
    """ Returns the voltage left in the batteries on the Sparki
    
        arguments:
        none
        
        returns:
        float - voltage level
    """
    printDebug("In getBattery", DEBUG_INFO)

    sendSerial( COMMAND_CODES["GET_BATTERY"] )
    result = getSerialFloat()
    return result


def getBright(position = LIGHT_SENS_RIGHT + 3):
    """ Returns the value of the light sensor at position; position != LINE_EDGE_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT returns all 3
        
        arguments:
        position - integer (use constants LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT)
        
        returns:
        int - value of sensor at position OR
        list of ints - values of left, middle, and right sensors (in that order)
    """
    
    return getLight(position)           # for library compatibility, this is just a synonym of getLight()


def getDistance():
    """ Synonym for ping() -- use ping()
    """
    
    return ping()           # for library compatibility, this is just a synonym of ping()


def getLight(position = LIGHT_SENS_RIGHT + 3):
    """ Returns the value of the light sensor at position; position != LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT returns all 3
        
        arguments:
        position - integer (use constants LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT)
        
        returns:
        int - value of sensor at position OR
        list of ints - values of left, middle, and right sensors (in that order)
    """
    printDebug("In getLight, position is " + str(position), DEBUG_INFO)
    
    if position == "left":
        position = LIGHT_SENS_LEFT
    elif position == "center" or position == "middle":
        position = LIGHT_SENS_MID
    elif position == "right":
        position = LIGHT_SENS_RIGHT
    
    sendSerial( COMMAND_CODES["GET_LIGHT"] )
    lights = ( getSerialInt(), getSerialInt(), getSerialInt() )
    
    if position == LIGHT_SENS_LEFT or position == LIGHT_SENS_MID or position == LIGHT_SENS_RIGHT:
        return lights[position]
    else:
        return lights


        
def getLine(position = LINE_EDGE_RIGHT + 5):
    """ Returns the value of the line sensor at position; position != LINE_EDGE_LEFT, LINE_MID_LEFT, LINE_MID, LINE_MID_RIGHT or LINE_EDGE_RIGHT returns all 5
        
        arguments:
        position - integer (use constants LINE_EDGE_LEFT, LINE_MID_LEFT, LINE_MID, LINE_MID_RIGHT or LINE_EDGE_RIGHT)
        
        returns:
        int - value of sensor at position OR
        list of ints - values of edge left, left, middle, right, and edge right sensors (in that order)
    """
    printDebug("In getLine, position is " + str(position), DEBUG_INFO)
    
    if position == "left":
        position = LINE_MID_LEFT
    elif position == "center" or position == "middle":
        position = LINE_MID
    elif position == "right":
        position = LINE_MID_RIGHT
        
    sendSerial( COMMAND_CODES["GET_LINE"] )
    lines = ( getSerialInt(), getSerialInt(), getSerialInt(), getSerialInt(), getSerialInt() )
    
    if position == LINE_EDGE_LEFT or position == LINE_MID_LEFT or position == LINE_MID or position == LINE_MID_RIGHT or position == LINE_EDGE_RIGHT:
        return lines[position]
    else:
        return lines


def getMag():
    """ Returns the values (X, Y, and Z) of the magnetometers
    
        arguments:
        none
        
        returns:
        list of 3 floats representing the X, Y, and Z sensors (in that order)
    """
    if NO_MAG:
        printDebug("Magnetometers not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getMag", DEBUG_INFO)
        
    sendSerial( COMMAND_CODES["GET_MAG"] )
    result = [ getSerialFloat(), getSerialFloat(), getSerialFloat() ]
    return result
    
    
def getMagX():
    """ Returns the values of the X magnetometer
    
        arguments:
        none
        
        returns:
        float representing the X sensor
    """

    return getMag()[0]


    
def getMagY():
    """ Returns the values of the Y magnetometer
    
        arguments:
        none
        
        returns:
        float representing the Y sensor
    """

    return getMag()[1]

    
    
def getMagZ():
    """ Returns the values of the Z magnetometer
    
        arguments:
        none
        
        returns:
        float representing the Z sensor
    """

    return getMag()[2]

    
def getName():
    """ Gets the name of this robot as set in the EEPROM

        arguments:
        None

        returns:
        string - name of robot
    """
    if not USE_EEPROM:
        printDebug("getName not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getName", DEBUG_INFO)

    sendSerial( COMMAND_CODES["GET_NAME"] )
    return getSerialString()


def getObstacle(position = "all"):
    """ Gets the obstacle sensor (the ultrasonic sensor or 'ping') at position

        arguments:
        position - can be integer between SERVO_LEFT and SERVO_RIGHT
                   can also be the strings "left", "center", "right" or "all"
                   if it is "all", this returns a list of all values
                   defaults to "all"

        returns:
        integer - value of sensor at position OR
        list of integers - value of sensor at each position
    """
    printDebug("In getObstacle, position is " + str(position), DEBUG_INFO)
    
    if position == "left":
        position = SERVO_LEFT
    elif position == "center":
        position = SERVO_CENTER
    elif position == "right":
        position = SERVO_RIGHT
    elif position == "all":
        result = [ getObstacle( SERVO_RIGHT ), getObstacle( SERVO_LEFT ), getObstacle( SERVO_CENTER ) ] # recursion
        return result

    position = int( constrain( position, SERVO_LEFT, SERVO_RIGHT ) )
    
    servo( position )
    result = ping()

    return result


def getPosition():
    """ Gets the current x,y position of Sparki - used with the grid commands (moveTo() & moveBy())
        Note that only use of the grid commands actually changes this value -- the x & y coordinates
        do not change for other move commends
        The robot begins at 0,0, and by definition is facing the positive coordinates of the Y axis

        arguments:
        none

        returns:
        list containing xpos,ypos (xpos is [0], ypos is [1])
    """
    global xpos, ypos

    printDebug("In getPosition", DEBUG_INFO)
    
    return [xpos, ypos]

    
def getUptime():
    """ Gets the amount of time since the robot was initialized - returns a -1 if the robot has not been initialized
    
        arguments:
        none
        
        returns:
        float - number of seconds since init() was called, or -1 if the robot is not connected
    """
    global init_time

    printDebug("In getUptime", DEBUG_INFO)
    
    if init_time < 0:
        return -1
    else:
        return currentTime() - init_time


def gripperClose(distance = MAX_GRIPPER_DISTANCE):
    """ Closes the gripper by distance; defaults to MAX_GRIPPER_DISTANCE

        arguments:
        distance - float distance in cm to close

        returns:
        nothing
    """
    printDebug("In gripperClose, distance is " + str(distance), DEBUG_INFO)
    
    distance = constrain(distance, 0, MAX_GRIPPER_DISTANCE)
    distance = float(distance)
    args = [ distance ]

    sendSerial( COMMAND_CODES["GRIPPER_CLOSE_DIS"], args)
    wait( distance )


def gripperOpen(distance = MAX_GRIPPER_DISTANCE):
    """ Opens the gripper by distance; defaults to MAX_GRIPPER_DISTANCE

        arguments:
        distance - float distance in cm to open

        returns:
        nothing
    """
    printDebug("In gripperOpen, distance is " + str(distance), DEBUG_INFO)
    distance = constrain(distance, 0, MAX_GRIPPER_DISTANCE)
    distance = float(distance)
    args = [ distance ]

    sendSerial( COMMAND_CODES["GRIPPER_OPEN_DIS"], args)
    wait( distance )


def gripperStop():
    """ Stops gripper movement

        arguments:
        distance - float distance in cm to open

        returns:
        nothing
    """
    printDebug("In gripperStop", DEBUG_INFO)

    sendSerial( COMMAND_CODES["GRIPPER_STOP"] )

    
def humanTime():
    """ Return a human readable current time (i.e. time.ctime())
    
        arguments:
        none
        
        returns:
        string - time of call
    """
    printDebug("In humanTime", DEBUG_INFO)
    
    return time.ctime()


def init(com_port):
    """ Connects to the Sparki robot on com_port; if it is already connected, this will disconnect and reconnect on the given port
        Note that Sparki MUST already be paired with the computer over Bluetooth
        
        arguments:
        com_port - a string designating which port Sparki is on (windows looks like "COM??"; mac and linux look like "/dev/????"
        
        returns:
        nothing
    """
    global init_time
    global robot_library_version
    global serial_conn
    global serial_port
    global serial_is_connected
    global NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM

    printDebug("In init, com_port is " + str(com_port), DEBUG_INFO)

    if serial_is_connected:
        disconnectSerial()
    
    serial_port = com_port
    
    try:
        serial_conn = serial.Serial(port = serial_port, baudrate = 9600, timeout = CONN_TIMEOUT)
    except serial.SerialException:
        printDebug("Unable to connect with Sparki", DEBUG_ALWAYS)
        printDebug("Ensure that:", DEBUG_ALWAYS)
        printDebug("    1) Sparki is turned on", DEBUG_ALWAYS)
        printDebug("    2) Sparki's Bluetooth module is inserted", DEBUG_ALWAYS)
        printDebug("    3) Your computer's Bluetooth has been paired with Sparki", DEBUG_ALWAYS)
        printDebug("    4) Sparki's batteries have some power left", DEBUG_ALWAYS)
        printDebug("If you see the Sparki logo on the LCD, turn Sparki off and back on and try to reconnect", DEBUG_ALWAYS)
        printDebug("You can also try to reset your shell", DEBUG_ALWAYS)
        raise
        
    serial_is_connected = True      # have to do this prior to sendSerial, or sendSerial will never try to send
    
    sendSerial( COMMAND_CODES["INIT"] )

    robot_library_version = getSerialString()   # Sparki sends us its library version in response
    
    if robot_library_version:
        init_time = currentTime()
    
        printDebug("Sparki connection successful", DEBUG_ALWAYS)
        printDebug("  Python library version is " + SPARKI_MYRO_VERSION, DEBUG_ALWAYS)
        printDebug("  Robot library version is " + robot_library_version, DEBUG_ALWAYS)

        # use the version number to try to figure out capabilities
        try:
            # the order is NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, reserved, reserved, reserved
            NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, reserved1, reserved2, reserved3 = SPARKI_CAPABILTIES[robot_library_version]
        except:
            printDebug("Unknown library version, using defaults -- you might need an upgrade of the Sparki Myro Python library", DEBUG_ALWAYS)
    else:
        printDebug("Sparki communication failed", DEBUG_ALWAYS)
        serial_is_connected = False
        init_time = -1


def initialize(com_port):
    """ Synonym for init(com_port)
    """
    init(com_port)


def joystick():
    """ Control Sparki using a GUI

        arguments:
        none

        returns:
        nothing
    """
    printDebug("In joystick", DEBUG_INFO)

    # grid is 4 rows by 3 columns
    #          |   forward   |    
    #   left   |     stop    |  right      
    #          |   backward  |
    #   open   |             |  close
    if USE_GUI:
        # start a new window
        control = tk.Toplevel()
        control.title("GUI Control for Sparki")

        # we'll use the grid layout manager
        # top row
        # for Buttons, we need to give a callback function -- to give a command with an argument
        #     as a callback, we create a lambda function
        tk.Button(control, text="forward", command=lambda: forward(1)).grid(row=0, column=1)

        # 2nd row
        tk.Button(control, text="left", command=lambda: turnLeft(1)).grid(row=1, column=0)
        tk.Button(control, text="stop", command=stop).grid(row=1, column=1)    # no argument needed for stop
        tk.Button(control, text="right", command=lambda: turnRight(1)).grid(row=1, column=2)

        # 3rd row
        tk.Button(control, text="backward", command=lambda: backward(1)).grid(row=2, column=1)

        # 4th row
        tk.Button(control, text="open grip", command=lambda: gripperOpen(.5)).grid(row=3, column=0)
        tk.Button(control, text="close grip", command=lambda: gripperClose(.5)).grid(row=3, column=2)

        # weights for resizing
        for i in range(3):
            control.columnconfigure(i, weight=1)

        for i in range(4):
            control.rowconfigure(i, weight=1)

        control.wait_window(control)
    else:
        printDebug("No GUI for joystick control", DEBUG_CRITICAL)
    

def LCDclear(update = True):
    """ Clears the LCD on Sparki

        arguments:
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDclear", DEBUG_INFO)

    sendSerial( COMMAND_CODES["LCD_CLEAR"] )

    if update:
        LCDupdate()
        

def LCDdrawPixel(x, y, update = True):
    """ Draws a pixel on the LCD

        arguments:
        x - int x coordinate for the pixel, must be <= 128
        y - int y coordinate for the pixel, must be <= 64
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDdrawPixel", DEBUG_INFO)

    x = int(constrain(x, 0, 128))    # the LCD is 128 x 64
    y = int(constrain(y, 0, 64))

    args = [ x, y ]

    sendSerial( COMMAND_CODES["DRAW_PIXEL"], args )

    if update:
        LCDupdate()


def LCDprint(message, update = True):
    """ Prints message on the LCD on Sparki without going to the next line

        arguments:
        message - string that you want to display
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDprint, message is " + str(message), DEBUG_INFO)

    sendSerial( COMMAND_CODES["LCD_PRINT"], message )

    if update:
        LCDupdate()


def LCDprintLn(message, update = True):
    """ Prints message on the LCD on Sparki and goes to the next line

        arguments:
        message - string that you want to display
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDprintLn, message is " + str(message), DEBUG_INFO)

    sendSerial( COMMAND_CODES["LCD_PRINTLN"], message )

    if update:
        LCDupdate()


def LCDupdate():
    """ Updates the LCD on Sparki -- you MUST update the LCD after drawing or printing

        arguments:
        none

        returns:
        nothing
    """
    printDebug("In LCDupdate", DEBUG_INFO)

    sendSerial( COMMAND_CODES["LCD_UPDATE"] )
    
    
def motors(left_speed, right_speed, time = -1):
    """ Moves wheels at left_speed and right_speed for time; time is optional
    
        arguments:
        left_speed - the left wheel speed; a float between -1.0 and 1.0
        right_speed - the right wheel speed; a float between -1.0 and 1.0
        time - the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """    
    printDebug("In motors, left speed is " + str(left_speed) + ", right speed is " + str(right_speed) + " and time is " + str(time), DEBUG_INFO)

    if left_speed == 0 and right_speed == 0:
        printDebug("In motors, both speeds == 0, doing nothing", DEBUG_WARN)
        return
        
    if left_speed < -1.0 or left_speed > 1.0:
        printDebug("In motors, left_speed is outside of the range -1.0 to 1.0", DEBUG_ERROR)
        
    if right_speed < -1.0 or right_speed > 1.0:
        printDebug("In motors, right_speed is outside of the range -1.0 to 1.0", DEBUG_ERROR)
    
    # adjust speeds to Sparki's requirements
    left_speed = constrain( left_speed, -1.0, 1.0 )
    right_speed = constrain( right_speed, -1.0, 1.0 )
        
    left_speed = int( left_speed * 100 )      # sparki expects an int between 1 and 100
    right_speed = int( right_speed * 100 )      # sparki expects an int between 1 and 100
    time = float( time )
    args = [ left_speed, right_speed, time ]
    
    sendSerial( COMMAND_CODES["MOTORS"], args )

    if time >= 0:
        wait(time)


def move(translate_speed, rotate_speed):    # NOT WELL TESTED
    """ Combines moving forward / backward while rotating -- use another command if possible

        arguments:
        translate_speed - float between -1.0 and 1.0 the forward / backward speed -- combined with rotate speed to get actual movements
        rotate_speed - float between -1.0 and 1.0 the left / right speed -- combined with translate speed to get actual movements
                       for some reason, positive is left rotation and negative is right rotation

        returns:
        nothing
    """
    printDebug("In move, translate speed is " + str(translate_speed) + ", rotate speed is " + str(rotate_speed), DEBUG_INFO)

    translate_speed = constrain(translate_speed, -1.0, 1.0)
    rotate_speed = constrain(rotate_speed, -1.0, 1.0)

    if translate_speed > 0:
        if rotate_speed > 0:
            motors( (translate_speed + rotate_speed) / 2, translate_speed + rotate_speed )
        elif rotate_speed < 0:
            motors( translate_speed + rotate_speed, (translate_speed + rotate_speed) / 2 )
        else: # rotate_speed == 0
            forward( translate_speed )
    elif translate_speed < 0:
        if rotate_speed > 0:
            motors( (translate_speed - rotate_speed) / 2, translate_speed - rotate_speed )
        elif rotate_speed < 0:
            motors( translate_speed - rotate_speed, (translate_speed - rotate_speed) / 2 )
        else: # rotate_speed == 0, so use forward() (which will actually go backward)
            forward( translate_speed )
    else: # translate_speed == 0, so turnLeft
        turnLeft( rotate_speed )


def moveBackwardcm(centimeters):
    """ Move Sparki backward by centimeters

        arguments:
        centimeters - float number of centimeters to move

        returns:
        nothing
    """
    global centimeters_moved
    
    printDebug("In moveBackwardcm, centimeters is " + str(centimeters), DEBUG_INFO)

    centimeters = float( centimeters )

    if centimeters == 0:
        printDebug("In moveBackwardcm, centimeters is 0... doing nothing", DEBUG_WARN)
        return
    elif centimeters < 0:
        printDebug("In moveBackwardcm, centimeters is negative, calling moveForwardcm", DEBUG_ERROR)
        moveForwardcm(-centimeters)
        return

    centimeters_moved = centimeters_moved - centimeters
    
    args = [ centimeters ]

    sendSerial( COMMAND_CODES["BACKWARD_CM"], args )
    wait( centimeters * SECS_PER_CM )


def moveForwardcm(centimeters):
    """ Move Sparki forward by centimeters

        arguments:
        centimeters - float number of centimeters to move

        returns:
        nothing
    """
    global centimeters_moved

    printDebug("In moveForwardcm, centimeters is " + str(centimeters), DEBUG_INFO)

    centimeters = float( centimeters )

    if centimeters == 0:
        printDebug("In moveForwardcm, centimeters is 0... doing nothing", DEBUG_WARN)
        return
    elif centimeters < 0:
        printDebug("In moveForwardcm, centimeters is negative, calling moveBackwardcm", DEBUG_ERROR)
        moveBackwardcm(-centimeters)
        return

    centimeters_moved = centimeters_moved + centimeters
    
    args = [ centimeters ]

    sendSerial( COMMAND_CODES["FORWARD_CM"], args )
    wait( centimeters * SECS_PER_CM )


def moveBy(dX, dY, turnBack = False): 
    """ Moves to the relative x,y coordinate specified (i.e. treats the current position as 0,0 and does a moveTo, but
        maintains the x,y coordinates correctly; for example, if the robot is currently at 3,4, and you give it moveBy(1,2)
        it will move to 4,5)
		
        When turned on, the robot begins at 0,0, and by definition is facing the positive coordinates of the Y axis

        The robot's heading is changed from "facing the positive coordinates of the Y axis" every time turnBy() is called
        If you want the robot to be "reset" to "facing the positive coordinates of the Y axis", call setAngle() prior to this

        Only movement commands made via moveTo() or moveBy() will update the X & Y coordinates
        Robot returns to original heading at the end of the function if turnBack is True

        arguments:
        dX - float relative X position of the robot
        dY - float relative Y position of the robot
        turnBack - boolean - True if the robot should turn back to the direction it faced prior to the command

        returns:
        none
    """
    global xpos, ypos

    printDebug("In moveBy, moving to relative position " + str(dX) + ", " + str(dY), DEBUG_INFO)    

    if (dX == 0) and (dY == 0):
        printDebug("In moveBy, already at location " + str(dX) + ", " + str(dY), DEBUG_WARN)
        return

    # determine the length (in cm) we need to move to the new position
    hypotenuse = math.hypot(dX, dY)

    # our angle is set relative to the Y axis
    # determine the angle to the new position (law of cosines, dY / hypotenuse)
    angle = math.degrees( math.acos( dY / hypotenuse ) )    # acos gives the value in radians

    if dX < 0:
        angle = -angle

    # turn & move
    oldHeading = getAngle()
    turnTo(angle)
    moveForwardcm(hypotenuse)

    xpos, ypos = xpos + dX, ypos + dY    # set the new position

    if turnBack:
        # return to the original heading
        turnTo(oldHeading)


def moveTo(newX, newY, turnBack = False): 
    """ Moves to the x,y coordinate specified 
		
        When turned on, the robot begins at 0,0, and by definition is facing the positive coordinates of the Y axis

        The robot's heading is changed from "facing the positive coordinates of the Y axis" every time turnBy() is called
        If you want the robot to be "reset" to "facing the positive coordinates of the Y axis", call setAngle()
        
        Only movement commands made via moveTo() or moveBy() will update the X & Y coordinates
        Robot returns to original heading at the end of the function if turnBack is True

        arguments:
        newX - float new X position of the robot
        newY - float new Y position of the robot
        turnBack - boolean - True if the robot should turn back to the direction it faced prior to the command

        returns:
        none
    """
    global xpos, ypos

    printDebug("In moveTo, moving to " + str(newX) + ", " + str(newY), DEBUG_INFO)

    moveBy(newX - xpos, newY - ypos, turnBack)


def pickAFile():
    """ Gets the path to a file picked by the user

        arguments:
        none

        returns:
        string path to the file
    """
    printDebug("In pickAFile", DEBUG_INFO)

    if USE_GUI:
        try:
            result = tk.filedialog.askopenfilename()
        except:
            result = None
    
        return result
    else:
        return ask("What is the path to the file? ")


def ping():
    """ Returns the reading from the ultrasonic sensor on the servo

        arguments:
        none

        returns:
        int - approximate distance in centimeters from nearest object
    """
    printDebug("In ping", DEBUG_INFO)

    sendSerial( COMMAND_CODES["PING"] )
    result = getSerialInt()
    return result


def resetPosition():
    """ Sets the number of degrees that the robot has turned to 0 and sets angle to 0 (used by the grid commands moveBy() & moveTo())
        Like reseting the Sparki to the position when it was initialized

        arguments:
        none
        
        returns:
        nothing
    """    
    printDebug("In resetPosition", DEBUG_INFO)

    setAngle(0)
    setPosition(0,0)


def rotate(speed):
    """ Synonym for turnRight -- use turnRight instead
    """
    turnRight(speed)

    
def senses():
    """ Displays readings from Sparki's sensors (lines, light, ping, mag, accel, compass, battery)

        arguments:
        none

        returns:
        nothing
    """
    printDebug("In senses", DEBUG_INFO)

    # grid is 9 rows by 6 columns
    #          |  left edge  |  left  |  center  |  right  |  right edge
    #   line   |             |        |          |         |
    #   light  |     N/A     |        |          |         |     N/A
    #          |             |        |          |         |
    #          |     N/A     |   X    |    Y     |    Z    |   compass
    #    mag   |     N/A     |        |          |         |
    #   accel  |     N/A     |        |          |         |     N/A
    #          |             |        |          |         |
    #   ping   |             |        |          | battery |
    if USE_GUI:
        # start a new window
        master = tk.Toplevel()
        master.title("Sparki Senses")

        updatePause = 2000            # time in milliseconds to update the window

        # we'll use the grid layout manager
        # top row
        tk.Label(master, text="left edge").grid(row=0, column=1)
        tk.Label(master, text="left").grid(row=0, column=2)
        tk.Label(master, text="center").grid(row=0, column=3)
        tk.Label(master, text="right").grid(row=0, column=4)
        tk.Label(master, text="right edge").grid(row=0, column=5)

        # 2nd row
        tk.Label(master, text="line").grid(row=1, column=0)
        senLinLeftEdge = tk.StringVar()
        senLinLeft = tk.StringVar()
        senLinCenter = tk.StringVar()
        senLinRight = tk.StringVar()
        senLinRightEdge = tk.StringVar()
        tk.Label(master, textvariable=senLinLeftEdge).grid(row=1, column=1)
        tk.Label(master, textvariable=senLinLeft).grid(row=1, column=2)
        tk.Label(master, textvariable=senLinCenter).grid(row=1, column=3)
        tk.Label(master, textvariable=senLinRight).grid(row=1, column=4)
        tk.Label(master, textvariable=senLinRightEdge).grid(row=1, column=5)

        # 3rd row
        tk.Label(master, text="light").grid(row=2, column=0)
        senLightLeft = tk.StringVar()
        senLightCenter = tk.StringVar()
        senLightRight = tk.StringVar()
        tk.Label(master, textvariable=senLightLeft).grid(row=2, column=2)
        tk.Label(master, textvariable=senLightCenter).grid(row=2, column=3)
        tk.Label(master, textvariable=senLightRight).grid(row=2, column=4)

        # 4th row - nada

        # 5th row
        if not NO_MAG and not NO_ACCEL:
            tk.Label(master, text="X").grid(row=4, column=2)
            tk.Label(master, text="Y").grid(row=4, column=3)
            tk.Label(master, text="Z").grid(row=4, column=4)
            tk.Label(master, text="compass").grid(row=4, column=5)
            
        # 6th row
        if not NO_MAG:
            tk.Label(master, text="mag").grid(row=5, column=0)
            senMagX = tk.StringVar()
            senMagY = tk.StringVar()
            senMagZ = tk.StringVar()
            senCompass = tk.StringVar()
            tk.Label(master, textvariable=senMagX).grid(row=5, column=2)
            tk.Label(master, textvariable=senMagY).grid(row=5, column=3)
            tk.Label(master, textvariable=senMagZ).grid(row=5, column=4)
            tk.Label(master, textvariable=senCompass).grid(row=5, column=5)

        # 7th row
        if not NO_ACCEL:
            tk.Label(master, text="accel").grid(row=6, column=0)
            senAccelX = tk.StringVar()
            senAccelY = tk.StringVar()
            senAccelZ = tk.StringVar()
            tk.Label(master, textvariable=senAccelX).grid(row=6, column=2)
            tk.Label(master, textvariable=senAccelY).grid(row=6, column=3)
            tk.Label(master, textvariable=senAccelZ).grid(row=6, column=4)

        # 8th row - nada

        # 9th row
        tk.Label(master, text="ping").grid(row=8, column=0)
        senPing = tk.StringVar()
        tk.Label(master, textvariable=senPing).grid(row=8, column=1)
        tk.Label(master, text="battery").grid(row=8, column=4)
        senBattery = tk.StringVar()
        tk.Label(master, textvariable=senBattery).grid(row=8, column=5)

        # weights for resizing
        for i in range(6):
            master.columnconfigure(i, weight=1)

        for i in range(9):
            master.rowconfigure(i, weight=1)

        # we're going to define a function inside a function, because we can!
        # more than that, this function is meaningless outside of this window -- we could create a class
        # to handle whole function, but because reusability here is limited and the code is straightforward,
        # we'll just do it like this
        def sensesUpdate():
            senUpLines = getLine()
            printDebug("In sensesUpdate, senUpLines = " + str(senUpLines), DEBUG_DEBUG)
            
            senLinLeftEdge.set( senUpLines[0] )
            senLinLeft.set( senUpLines[1] )
            senLinCenter.set( senUpLines[2] )
            senLinRight.set( senUpLines[3] )
            senLinRightEdge.set( senUpLines[4] )

            senUpLights = getLight()
            printDebug("In sensesUpdate, senUpLights = " + str(senUpLights), DEBUG_DEBUG)

            senLightLeft.set( senUpLights[0] )
            senLightCenter.set( senUpLights[1] )
            senLightRight.set( senUpLights[2] )

            if not NO_MAG:
                senUpMag = getMag()
                printDebug("In sensesUpdate, senUpMag = " + str(senUpMag), DEBUG_DEBUG)

                senMagX.set( senUpMag[0] )
                senMagY.set( senUpMag[1] )
                senMagZ.set( senUpMag[2] )
                senCompass.set( compass() )

            if not NO_ACCEL:
                senUpAccel = getAccel()
                printDebug("In sensesUpdate, senUpAccel = " + str(senUpAccel), DEBUG_DEBUG)

                senAccelX.set( senUpAccel[0] )
                senAccelY.set( senUpAccel[1] )
                senAccelZ.set( senUpAccel[2] )

            senPing.set( ping() )
            senBattery.set( getBattery() )
            master.after( updatePause, sensesUpdate )   # update the window every updatePause milliseconds

        sensesUpdate()
        master.after( updatePause, sensesUpdate )   # schedule the update of the window
        master.wait_window(master)
        # end USE_GUI
    else:
        senses_text()
## end senses() ##
        

def servo(position):
    """ Turns the servo 'head' to the position (in degrees) specified

        arguments:
        position - integer between -80 (left side) and 80 (right side) to "aim" the servo

        returns:
        nothing
    """
    printDebug("In servo, position is " + str(position), DEBUG_INFO)

    position = int( constrain( position, SERVO_LEFT, SERVO_RIGHT ) )
    args = [ position ]

    sendSerial( COMMAND_CODES["SERVO"], args )
    wait(.5)


def setAngle(newAngle = 0):
    """ Sets the number of degrees that the robot has turned (used by the grid commands moveBy() & moveTo())

        If you want the robot to be "reset" to "facing the positive coordinates of the Y axis", call setAngle()

        arguments:
        newAngle - float new number of degrees the robot has turned (defaults to 0); cannot be greater than 360

        returns:
        nothing
    """
    global degrees_turned
    
    printDebug("In setAngle, newAngle is " + str(newAngle), DEBUG_INFO)
        
    newAngle = float( wrapAngle( newAngle ) )  # ensure we're getting a float between -360 and 360
    
    degrees_turned = newAngle


def setDebug(level):
    """ Sets the debug (in Python) to level

        arguments:
        level - int between 0 and 5; greater numbers produce more output

        returns:
        none
    """
    global sparki_myro_py_debug
    
    printDebug("Changing debug level from " + str(sparki_myro_py_debug) + " to " + str(level), DEBUG_INFO)
    level = int( constrain( level, DEBUG_ALWAYS, DEBUG_DEBUG ) )
    
    sparki_myro_py_debug = level


def setPosition(newX, newY):
    """ Sets the current x,y position of Sparki - used with the grid commands (moveTo() & moveBy())
        Note that this does not move the robot, but merely tells it that it is at another location
        Also note that only use of the grid commands actually changes this value -- the x & y coordinates
        do not change for other move commends
        The robot begins at 0,0, and by definition is facing the positive coordinates of the Y axis

        arguments:
        newX - float new X position of the robot
        newY - float new Y position of the robot

        returns:
        none
    """
    global xpos, ypos   # also can be set in moveBy()

    printDebug("In setPosition, new position will be " + str(newX) + ", " + str(newY), DEBUG_INFO)
    
    xpos = float(newX)
    ypos = float(newY)


def setSparkiDebug(level):
    """ Sets the debug (in Sparki) to level

        arguments:
        level - int between 0 and 5; greater numbers produce more output (many of Sparki's debug statements are turned off)

        returns:
        none
    """
    if SPARKI_DEBUGS:
        printDebug("Changing Sparki debug level to " + str(level), DEBUG_INFO)
        level = int( constrain( level, DEBUG_ALWAYS, DEBUG_DEBUG ) )
    
        sendSerial( COMMAND_CODES["SET_DEBUG_LEVEL"], level )
    else:
        printDebug("Setting sparki debug level is not available", DEBUG_ERROR)
    

def setLEDBack(brightness):
    """ Sets the RGB LED to the brightness given -- should be a number between 0 and 100, which is a percentage

        arguments:
        brightness - int between 0 and 100 which is a percentage of brightness

        returns:
        nothing
    """

    setRGBLED( brightness, brightness, brightness )


def setLEDFront(brightness):
    """ Sets the status LED to the brightness given -- should be a number between 0 and 100, which is a percentage

        arguments:
        brightness - int between 0 and 100 which is a percentage of brightness

        returns:
        nothing
    """

    setStatusLED( brightness )

    
def setName(newName):
    """ Sets the name of this robot as set in the EEPROM

        arguments:
        newName - string - must be less than EEPROM_NAME_MAX_CHARS

        returns:
        string - name of robot
    """
    if not USE_EEPROM:
        printDebug("setName not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In setName, newName is " + str(newName), DEBUG_INFO)

    if len(newName) > EEPROM_NAME_MAX_CHARS - 1:
        printDebug("In setName(), the name " + str(newName) + " is too long. It must be fewer than " + str(EEPROM_NAME_MAX_CHARS - 1) + " letters and numbers. Truncating...", DEBUG_WARN)
        newName = newName[:EEPROM_NAME_MAX_CHARS - 1]

    args = [ newName ]
    sendSerial( COMMAND_CODES["SET_NAME"], args )


def setRGBLED(red, green, blue):
    """ Sets the RGB LED to the color given -- colors should be a value between 0 and 100, which is a percentage of that color

        arguments:
        red - int between 0 and 100 which is an amount of brightness for that LED
        green - int between 0 and 100 which is an amount of brightness for that LED
        blue - int between 0 and 100 which is an amount of brightness for that LED

        returns:
        nothing
    """
    printDebug("In setRGBLED, red is " + str(red) + ", green is " + str(green) + ", blue is " + str(blue), DEBUG_INFO)
    
    red = int(constrain(red, 0, 100))
    green = int(constrain(green, 0, 100))
    blue = int(constrain(blue, 0, 100))
    args = [ red, green, blue ]

    sendSerial( COMMAND_CODES["SET_RGB_LED"], args )


def setStatusLED(brightness):
    """ Sets the status LED to the brightness given -- should be a number between 0 and 100, which is a percentage
        Note that the internal Sparki code makes use of the status LED to show when it is executing a command

        arguments:
        brightness - int between 0 and 100 which is a percentage of brightness; can also be string "on" or "off"

        returns:
        nothing
    """
    printDebug("In setStatusLED, brightness is " + str(brightness), DEBUG_INFO)

    if brightness == "on":
        brightness = 100
    elif brightness == "off":
        brightness = 0

    brightness = int( constrain( brightness, 0, 100 ) )
    args = [ brightness ]

    sendSerial( COMMAND_CODES["SET_STATUS_LED"], args )


def stop():
    """ Stops the robot and the gripper
    
        arguments:
        none
        
        returns:
        nothing
    """
    printDebug("In stop", DEBUG_INFO)

    sendSerial( COMMAND_CODES["STOP"] )


def translate(speed):
    """ Synonym for forward() -- use forward instead
    """
    forward(speed)


def turnBy(degrees):
    """ Turn Sparki by degrees; positive numbers turn clockwise & negative numbers turn counter clockwise

        arguments:
        degrees - float number of degrees to turn; positive is clockwise and negative is counter clockwise; should
                  be greater than -360 and less than 360

        returns:
        nothing
    """
    global degrees_turned
    
    printDebug("In turnBy, degrees is " + str(degrees), DEBUG_INFO)

    degrees = wrapAngle( degrees )

    if abs(degrees) >= 360:     # >= -- the greater than is in case there's a rounding error
        degrees = 0

    if degrees == 0:
        printDebug("In turnBy, degrees is 0... doing nothing", DEBUG_WARN)
        return

    degrees_turned += degrees

    # keep degrees_turned greater than -360 and less than 360
    degrees_turned = wrapAngle( degrees_turned )
    
    printDebug("In turnBy, degrees_turned is now " + str(degrees_turned), DEBUG_DEBUG)
    
    args = [ degrees ]

    sendSerial( COMMAND_CODES["TURN_BY"], args )
    wait( abs(degrees) * SECS_PER_DEGREE )


def turnTo(newHeading):
    """ Turns Sparki to the heading specified, where 0 is the heading the Sparki was at when initialized
        Note that the heading only changes from turnBy() or turnTo() commands and not turnLeft(), turnRight(), or motors()

        Note that the functionality of this command changed between library versions 1.0.0 and 1.1.0

        arguments:
        newHeading - float heading in degrees to turn to
        
        returns:
        nothing
    """
    printDebug("In turnTo, newHeading is " + str(newHeading), DEBUG_INFO)

    # ensure newHeading is less than 360 and greater than or equal to 0
    newHeading = wrapAngle( newHeading )
    
    currentHeading = getAngle()

    printDebug("In turnTo turning from " + str(currentHeading) + " to " + str(newHeading), DEBUG_DEBUG)       
    turnBy(newHeading - currentHeading)


def turnLeft(speed, time = -1):
    """ Turns left (counter clockwise) at speed for time; time is optional
    
        arguments:
        speed - a float between -1.0 and 1.0
        time - the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """
    printDebug("In turnLeft, speed is " + str(speed) + " and time is " + str(time), DEBUG_INFO)
    
    # adjust speed to Sparki's requirements
    if speed < 0:
        printDebug("In turnLeft, speed < 0, calling turnRight", DEBUG_WARN)
        turnRight(-speed, time)
        return
    elif speed == 0:
        printDebug("In turnLeft, speed == 0, doing nothing", DEBUG_WARN)
        return
    elif speed > 1.0:
        printDebug("In turnLeft, speed > 1.0, reducing to 1", DEBUG_ERROR)
        speed = 1
        
    motors( -speed, speed, time )


def turnRight(speed, time = -1):
    """ Turns right (clockwise) at speed for time; time is optional
    
        arguments:
        speed - a float between -1.0 and 1.0
        time - the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """
    printDebug("In turnRight, speed is " + str(speed) + " and time is " + str(time), DEBUG_INFO)
    
    # adjust speed to Sparki's requirements
    if speed < 0:
        printDebug("In turnRight, speed < 0, calling turnLeft", DEBUG_WARN)
        turnLeft(-speed, time)
        return
    elif speed == 0:
        printDebug("In turnRight, speed == 0, doing nothing", DEBUG_WARN)
        return
    elif speed > 1.0:
        printDebug("In turnRight, speed > 1.0, reducing to 1", DEBUG_ERROR)
        speed = 1
        
    motors( speed, -speed, time)


def wait(wait_time):
    """ Wait for wait_time seconds; actual time will vary somewhat due to factors outside of program control
    
        arguments:
        wait_time - float number of seconds to wait
        
        returns:
        nothing
    """
    printDebug("In wait, wait_time is " + str(wait_time), DEBUG_INFO)

    if wait_time > 120:
        printDebug("Wait time is greater than 2 minutes", DEBUG_WARN)
    
    wait_time = constrain(wait_time, 0, 600)    # don't wait longer than ten minutes
    
    time.sleep(wait_time)    # in Python > 3.5, it will wait at least wait_time seconds; prior to that it could be less


def yesorno(message):
    """ Gets the string 'yes' or 'no' from the user -- prints message

        arguments:
        message - string to print to prompt the user

        returns:
        string response from the user
    """
    printDebug("In yesorno", DEBUG_INFO)

    if USE_GUI:
        try:
            result = askQuestion(message, ["yes", "no"], "Yes or No?")
        except:
            result = None
    
        return result
    else:
        return askQuestion_text(message, ["yes", "no", "y", "n" ], False)
###################### END OF SPARKI MYRO FUNCTIONS ######################

    
### functions which cannot be or are not implemented ###
def arcBy(args = None):
    printDebug("arcBy not implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError

def arcTo(args = None):
    printDebug("arcTo not implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError

def getIR(args = None):
    printDebug("getIR cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError

def getMicrophone():
    printDebug("getMicrophone cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError
    
def getStall():
    printDebug("getStall cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError

def takePicture(args = None):
    printDebug("takePicture cannot be implemented on Sparki (because there's no camera)", DEBUG_CRITICAL)
    raise NotImplementedError
    
def speak(message, async = False):
    printDebug("speak cannot be implemented on Sparki; printing instead", DEBUG_WARN)
    print(message)
    
def show(args = None):
    printDebug("show cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError
### end junk functions ###    


def main():
    print("Sparki Myro version " + SPARKI_MYRO_VERSION)
    print("This is intended to be used as a library -- your code should call this program by importing the library, e.g.")
    print("from sparki_myro import *")
    print("Exiting...")

if __name__ == "__main__":
    main()