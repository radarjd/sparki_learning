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
# Last Modified: November 18, 2019
# Originally developed on Python 3.4 and 3.5; this version modified to work with 3.6; should work on any version >3; limited testing has been successful with Python 2.7
# working with Python 3.7

from __future__ import division, \
    print_function  # in case this is run from Python 2.7 or greater, but less than Python 3

import logging
import math
import platform
import sys
import serial  # developed with pyserial 2.7, but also works with later versions
import time

from sparki_learning.constants import *
from sparki_learning.util import *


########### GLOBAL VARIABLES ###########
# ***** SERIAL TIMEOUT ***** #
if platform.system() == "Darwin":  # Macs seem to be extremely likely to timeout -- so this is a lower value
    CONN_TIMEOUT = 2  # in seconds
else:
    CONN_TIMEOUT = 5  # in seconds
    
# ***** COMPILE OPTIONS ***** #
# these may change upon initialization, but should not change thereafter
# some commands may be turned off in the version of sparki myro running on Sparki
# these will be reset during the initialization process depending on the version (see the SPARKI_CAPABILITIES variable)
NO_MAG = False  # compass(), getMag(), getMagX(), getMagY(), getMagZ()
NO_ACCEL = False  # getAccel(), getAccelX(), getAccelY(), getAccelZ()
SPARKI_DEBUGS = False  # setSparkiDebug()
USE_EEPROM = False  # EEPROMread(), EEPROMwrite(), getName(), setName()
EXT_LCD_1 = False  # EEPROMread(), EEPROMwrite(), LCDdrawLine(), LCDdrawString(), LCDreadPixel()
NOOP = False  # noop() -- if False, noop is simulated with setStatusLED

# ***** RUNTIME OPTIONS ***** #
command_queue = []  # this stores every command sent to Sparki

centimeters_moved = 0  # this stores the sum of centimeters moved forward or backward using the moveForwardcm()
# or moveBackwardcm() functions; used implicitly by moveTo() and moveBy(); use directly
# by getCentimetersMover(); this only increases in value

current_lcd_color = LCD_BLACK  # this is the color that an LCDdraw command will draw in -- can be LCD_BLACK or LCD_WHITE

degrees_turned = 0  # this stores the sum of degrees turned using the turnBy() function; positive is clockwise
# and negative is counterclockwise
# can be set by setAngle() or retrieved with getAngle()

in_motion = False  # set to True when moving -- note this is a guess set in motors(), stop() & turnBy()
# this library is not multi-thread safe (for many reasons), so this doesn't need to be
# set whenever the robot is actually moving -- only when the user can do something after it
# starts moving

init_time = -1  # time when the robot was initialized

robot_library_version = None  # version of the code on the robot

logging.basicConfig(level=logging.DEBUG)  # we want to catch all DEBUG messages
sparki_logger = logging.getLogger("sparki_learning")
sparki_logger.setLevel(logging.WARN)
sparki_std_handler = logging.StreamHandler(sys.stderr)
sparki_std_handler.setLevel(logging.WARN)
sparki_logger.addHandler(sparki_std_handler)

serial_port = None  # save the serial port on which we're connected
serial_conn = None  # hold the pyserial object
serial_is_connected = False  # set to true once connection is done
robot_name = None # cache the robot's name

xpos = 0  # for the moveBy(), moveTo(), getPosition() and setPosition() commands (the "grid commands"), these
ypos = 0  # variables keep track of the current x,y position of the robot; each integer coordinate is 1cm, and
# the robot starts at 0,0
# note that these _only_ update with the grid commands (e.g. motors(1,1,1) will not change the xpos & ypos)
# making these of limited value
########### END OF GLOBAL VARIABLES ###########

########### INTERNAL FUNCTIONS ###########
# these functions are intended to be used by the library itself
def bluetoothRead():
    """ Returns the bluetooth address of the robot (if it has been previously stored)
    
        arguments:
        none
        
        returns:
        string - the bluetooth address of the robot, if it has been previously stored; None otherwise
    """
    global EEPROM_BLUETOOTH_ADDRESS

    bt = EEPROMread(EEPROM_BLUETOOTH_ADDRESS, 17)

    if bluetoothValidate(bt):
        return bt
    else:
        return None


def bluetoothWrite(bt):
    """ Writes the bluetooth address of the robot and stores it in EEPROM
    
        arguments:
        bt - string bluetooth address of the format 00-00-00-00-00-00 or ff:ff:ff:ff:ff:ff
        
        returns:
        none
    """
    global EEPROM_BLUETOOTH_ADDRESS

    if bluetoothValidate(bt):
        EEPROMwrite(EEPROM_BLUETOOTH_ADDRESS, bt)
    else:
        raise TypeError(str(bt) + " does not appear to be a valid bluetooth address")


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

    while inByte != TERMINATOR.encode():  # read until we see a TERMINATOR
        if inByte != SYNC.encode():  # ignore it - we don't care about SYNCs
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
    result = chr(int(getSerialBytes()))

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

    if str(result) == "ovf" or len(result) == 0:  # check for overflow
        result = -1.0  # -1.0 is not necessarily a great "error response", except that values from the Sparki should be positive
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

    if str(result) == "ovf" or len(result) == 0:  # check for overflow
        result = -1  # -1 is not necessarily a great "error response", except that values from the Sparki should be positive
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
    result = str(getSerialBytes())

    printDebug("In getSerialString, returning " + result, DEBUG_DEBUG)
    return result


def music_sunrise():
    # plays "Sunrise" from Also sprach Zarathustra by Strauss (aka the 2001 theme)
    beep(1000, 523)
    beep(1000, 784)
    beep(1000, 1047)


def printUnableToConnect():
    """ Prints a troubleshooting message

        arguments:
        none

        returns:
        nothing
    """
    print("Unable to connect with Sparki", file=sys.stderr)
    print("Ensure that:", file=sys.stderr)
    print("    1) Sparki is turned on", file=sys.stderr)
    print("    2) Sparki's Bluetooth module is inserted correctly", file=sys.stderr)
    print("    3) Your computer's Bluetooth has been paired with Sparki", file=sys.stderr)
    print("    4) Sparki's batteries have some power left", file=sys.stderr)
    print("If you see the Sparki logo on the LCD, press reset on the Sparki and try to reconnect -- you may have to do this many times.", file=sys.stderr)
    print("Windows 10 and MacOS will shut down the Bluetooth to save power (I think). Sometimes immediately rerunning the program will fix it.", file=sys.stderr)
    print("You can also try to reset your shell", file=sys.stderr)


def sendSerial(command, args=None):
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
    global serial_port

    if not serial_is_connected:
        printDebug("In sendSerial, Sparki is not connected - use init()", DEBUG_ALWAYS)
        raise RuntimeError("Attempt to send message to Sparki without initialization")

    if command is None:
        printDebug("In sendSerial, no command given", DEBUG_ALWAYS)
        raise RuntimeError("Attempt to send message to Sparki without command")

    command_queue.append((command, args))  # keep track of every command sent

    try:
        waitForSync()  # be sure Sparki is available before sending
    except serial.SerialTimeoutException:  # Macs seem to be sensitive to disconnecting, so we try to reconnect if we have a problem
        # if there's a failure, try to reconnect unless we're init'ing
        if command != COMMAND_CODES["INIT"]:
            init(serial_port, False)
            try:
                waitForSync()
            except:
                printDebug("In sendSerial, retry failed", DEBUG_CRITICAL)
                printUnableToConnect()
                raise
        else:
            printDebug("In sendSerial, serial timeout on init", DEBUG_CRITICAL)
            printUnableToConnect()
            raise

    printDebug("In sendSerial, Sending command - " + command, DEBUG_DEBUG)

    values = []  # this will hold what we're actually sending to Sparki

    values.append(command)

    if args is not None:
        if isinstance(args, str):
            values.append(args)
            printDebug("In sendSerial, values is " + str(values), DEBUG_DEBUG)
        else:
            values = values + args

    for value in values:
        message = (str(value) + TERMINATOR).encode()

        if len(message) > MAX_TRANSMISSION:
            printDebug("In sendSerial, messages must be " + str(MAX_TRANSMISSION) + " characters or fewer", DEBUG_ERROR)
            stop()  # done for safety -- in case robot is in motion
            raise RuntimeError("Messages sent to Sparki must be {} or fewer characters".format(str(MAX_TRANSMISSION)))

        printDebug("Sending bytes " + str(message) + " (" + str(value) + ")", DEBUG_DEBUG)

        try:
            serial_conn.write(message)
        except serial.SerialTimeoutException:
            printDebug("In sendSerial, error communicating with Sparki", DEBUG_CRITICAL)
            printUnableToConnect()
            raise

    serial_conn.flush()  # ensure the buffer is flushed
    wait(.01)


def senses_text():
    """ Displays the senses in text
    """
    print("Left edge line sensor is " + str(getLine(LINE_EDGE_LEFT)))
    print("Left line sensor is " + str(getLine(LINE_MID_LEFT)))
    print("Center line sensor is " + str(getLine(LINE_MID)))
    print("Right line sensor is " + str(getLine(LINE_MID_RIGHT)))
    print("Right edge line sensor is " + str(getLine(LINE_EDGE_RIGHT)))

    print("Left light sensor is " + str(getLight(LIGHT_SENS_LEFT)))
    print("Center light sensor is " + str(getLight(LIGHT_SENS_MID)))
    print("Right light sensor is " + str(getLight(LIGHT_SENS_RIGHT)))

    if not NO_MAG:
        print("X mag sensor is " + str(getMagX()))
        print("Y mag sensor is " + str(getMagY()))
        print("Z mag sensor is " + str(getMagZ()))
        print("compass heading is " + str(compass()))

    if not NO_ACCEL:
        print("X accel sensor is " + str(getAccelX()))
        print("Y accel sensor is " + str(getAccelY()))
        print("Z accel sensor is " + str(getAccelZ()))
        
    if isMoving():
        print("I think the robot is moving")
    else:
        print("I do not think the robot is moving")

    print("Ping is " + str(ping()) + " cm")
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
        raise RuntimeError("Attempt to listen for message from Sparki without initialization")

    serial_conn.flushInput()  # get rid of any waiting bytes

    start_time = currentTime()

    inByte = -1

    if platform.system() == "Darwin":  # Macs seem to be extremely likely to timeout -- this is attempting to deal with that quickly
        retries = 1  # the number of times to retry connecting in the case of a timeout
        loop_wait = 0  # pause this long each time through the loop
    else:
        retries = 5  # the number of times to retry connecting in the case of a timeout
        loop_wait = .01  # pause this long each time through the loop

    while inByte != SYNC.encode():  # loop, doing nothing substantive, while we wait for SYNC
        if currentTime() > start_time + (CONN_TIMEOUT * retries):
            if platform.system() == "Darwin":  # Macs seem to be extremely likely to timeout -- so we report at a different debug level
                printDebug(
                    "In waitForSync, unable to sync with Sparki (this may not be due to power saving settings)",
                    DEBUG_INFO)
            else:
                printDebug("In waitForSync, unable to sync with Sparki", DEBUG_ERROR)
            raise serial.SerialTimeoutException("Unable to sync with Sparki -- may be temporary error due to power saving")

        try:
            inByte = serial_conn.read()
        except serial.SerialTimeoutException:
            printDebug("SerialTimeoutException caught in waitForSync, unable to sync with Sparki", DEBUG_ERROR)
            raise

        wait(loop_wait)


########### END OF INTERNAL FUNCTIONS ###########


###################### SPARKI MYRO FUNCTIONS ######################
# These functions are intended to be called by users of this library        
def backward(speed, time=-1):
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

    motors(-speed, -speed, time)


def beep(time=200, freq=2800):
    """ Plays a tone on the Sparki buzzer at freq for time; both are optional
    
        arguments:
        time - time in milliseconds to play freq (default 200ms)
        freq - integer frequency of the tone (default 2800Hz)
        
        returns:
        nothing
    """
    printDebug("In beep, freq is " + str(freq) + " and time is " + str(time), DEBUG_INFO)

    freq = int(freq)  # ensure we have the right type of data
    time = int(time)

    freq = constrain(freq, 0, 40000)
    time = constrain(time, 0, 10000)

    args = [freq, time]

    sendSerial(COMMAND_CODES["BEEP"], args)
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

    sendSerial(COMMAND_CODES["COMPASS"])
    result = getSerialFloat()
    return result


def drawFunction(function, xvals, scale=1):
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
        moveTo(x * scale, function(x) * scale)


def EEPROMread(location, amount):
    """ Reads amount of data from location in the EEPROM on Sparki

        arguments:
        location - int - must be a valid location (0 through 1023)
        amount - int - the number of bytes you want to read

        returns:
        bytes - bytes from the EEPROM
    """
    if not (USE_EEPROM and EXT_LCD_1):
        printDebug("EEPROMread not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In EEPROMread, location is " + str(location) + " and amount is " + str(amount), DEBUG_INFO)

    if location > EEPROM_MAX_ADDRESS:
        printDebug(
            "In EEPROMread, location greater than maximum valid address (" + str(EEPROM_MAX_ADDRESS) + ") fixing...",
            DEBUG_WARN)

    if amount > EEPROM_MAX_ADDRESS:
        printDebug(
            "In EEPROMread, amount greater than maximum valid address (" + str(EEPROM_MAX_ADDRESS) + ") fixing...",
            DEBUG_WARN)

    location = int(constrain(location, 0, EEPROM_MAX_ADDRESS))
    amount = int(constrain(amount, 0, EEPROM_MAX_ADDRESS))

    if amount == 0:
        printDebug("In EEPROMread, asked to read 0 bytes, returning...", DEBUG_WARN)

    if location + amount > EEPROM_MAX_ADDRESS:
        printDebug("In EEPROMread, amount greater than EEPROM space", DEBUG_CRITICAL)
        raise IndexError

    args = [location, amount]
    sendSerial(COMMAND_CODES["READ_EEPROM"], args)

    return getSerialBytes()


def EEPROMwrite(location, data):
    """ Writes data to location in the EEPROM on Sparki

        arguments:
        location - int - must be a valid location (0 through 1023)
        data - string - data to be written; must fit in EEPROM (len(data) + location <= 1023

        returns:
        nothing
    """
    if not (USE_EEPROM and EXT_LCD_1):
        printDebug("EEPROMwrite not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In EEPROMwrite, location is " + str(location) + " and data is " + str(data), DEBUG_INFO)

    if location > EEPROM_MAX_ADDRESS:
        printDebug(
            "In EEPROMwrite, location greater than maximum valid address (" + str(EEPROM_MAX_ADDRESS) + ") fixing...",
            DEBUG_WARN)

    location = int(constrain(location, 0, EEPROM_MAX_ADDRESS))

    if location + len(data) > EEPROM_MAX_ADDRESS:
        printDebug("In EEPROMwrite, too much data to store", DEBUG_CRITICAL)
        raise IndexError

    args = [location, data]
    sendSerial(COMMAND_CODES["WRITE_EEPROM"], args)


def forward(speed, time=-1):
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

    motors(speed, speed, time)


def gamepad():
    """ Drives the robot using the remote control
        Do not send additional commands until gamepad() terminates
    
        arguments:
        none
        
        returns:
        nothing
    """
    printDebug("Beginning gamepad control", DEBUG_INFO)

    sendSerial(COMMAND_CODES["GAMEPAD"])
    print("Sparki will not respond to other commands until remote control ends")
    print("Press - or + on the remote to stop using the gamepad")
    # we could put a waitForSync() here, but it would likely time out


def getAccel():
    """ Returns the values (X, Y, and Z) of the accelerometers
    
        arguments:
        none
        
        returns:
        tuple of 3 floats representing the X, Y, and Z sensors (in that order)
    """
    if NO_ACCEL:
        printDebug("Accelerometers not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getAccel", DEBUG_INFO)

    sendSerial(COMMAND_CODES["GET_ACCEL"])
    result = (getSerialFloat(), getSerialFloat(), getSerialFloat())
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
    """ DEPRICATED due to inaccuracy of library
        Returns the voltage left in the batteries on the Sparki (not very accurate)
    
        arguments:
        none
        
        returns:
        -1
    """
    # the underlying sparki library causes this function not to be accurate, or to be inconsistent at the very least

    printDebug("In getBattery - function is DEPRICATED and will always return -1", DEBUG_WARN)

    return -1


def getBright(position=LIGHT_SENS_RIGHT + 3):
    """ Returns the value of the light sensor at position; position != LINE_EDGE_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT returns all 3
        
        arguments:
        position - integer (use constants LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT)
        
        returns:
        int - value of sensor at position OR
        tuple of ints - values of left, middle, and right sensors (in that order)
    """

    return getLight(position)  # for library compatibility, this is just a synonym of getLight()


def getCentimetersMoved():
    """ Returns a float containing the number of centimeters Sparki has moved since the library was first imported
        Only movement using the grid commands is counted in this number
        
        arguments:
        none
        
        returns:
        float - number of cm moved since beginning of program
    """
    global centimeters_moved

    printDebug("In getCentimetersMoved", DEBUG_INFO)

    return centimeters_moved


def getCommandQueue():
    """ Returns a tuple containing all commands sent to sparki since the library was first imported
        
        arguments:
        none
        
        returns:
        tuple of tuples - each inner tuple is a command code plus arguments
    """
    global command_queue

    printDebug("In getCommandQueue", DEBUG_INFO)

    return tuple(command_queue)


def getDistance():
    """ Synonym for ping() -- use ping()
    """

    return ping()  # for library compatibility, this is just a synonym of ping()


def getLight(position=LIGHT_SENS_RIGHT + 3):
    """ Returns the value of the light sensor at position; position != LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT returns all 3
        
        arguments:
        position - integer (use constants LIGHT_SENS_LEFT, LIGHT_SENS_MID or LIGHT_SENS_RIGHT)
        
        returns:
        int - value of sensor at position OR
        tuple of ints - values of left, middle, and right sensors (in that order)
    """
    printDebug("In getLight, position is " + str(position), DEBUG_INFO)

    if position == "left":
        position = LIGHT_SENS_LEFT
    elif position == "center" or position == "middle":
        position = LIGHT_SENS_MID
    elif position == "right":
        position = LIGHT_SENS_RIGHT

    sendSerial(COMMAND_CODES["GET_LIGHT"])
    lights = (getSerialInt(), getSerialInt(), getSerialInt())

    if position == LIGHT_SENS_LEFT or position == LIGHT_SENS_MID or position == LIGHT_SENS_RIGHT:
        return lights[position]
    else:
        return lights


def getLine(position=LINE_EDGE_RIGHT + 5):
    """ Returns the value of the line sensor at position; position != LINE_EDGE_LEFT, LINE_MID_LEFT, LINE_MID, LINE_MID_RIGHT or LINE_EDGE_RIGHT returns all 5
        
        arguments:
        position - integer (use constants LINE_EDGE_LEFT, LINE_MID_LEFT, LINE_MID, LINE_MID_RIGHT or LINE_EDGE_RIGHT)
        
        returns:
        int - value of sensor at position OR
        tuple of ints - values of edge left, left, middle, right, and edge right sensors (in that order)
    """
    printDebug("In getLine, position is " + str(position), DEBUG_INFO)

    if position == "left":
        position = LINE_MID_LEFT
    elif position == "center" or position == "middle":
        position = LINE_MID
    elif position == "right":
        position = LINE_MID_RIGHT

    sendSerial(COMMAND_CODES["GET_LINE"])
    lines = (getSerialInt(), getSerialInt(), getSerialInt(), getSerialInt(), getSerialInt())

    if position == LINE_EDGE_LEFT or position == LINE_MID_LEFT or position == LINE_MID or position == LINE_MID_RIGHT or position == LINE_EDGE_RIGHT:
        return lines[position]
    else:
        return lines


def getMag():
    """ Returns the values (X, Y, and Z) of the magnetometers
    
        arguments:
        none
        
        returns:
        tuple of 3 floats representing the X, Y, and Z sensors (in that order)
    """
    if NO_MAG:
        printDebug("Magnetometers not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getMag", DEBUG_INFO)

    sendSerial(COMMAND_CODES["GET_MAG"])
    result = (getSerialFloat(), getSerialFloat(), getSerialFloat())
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
    global robot_name
    
    if not USE_EEPROM:
        printDebug("getName not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In getName", DEBUG_INFO)
    
    if robot_name:
        return robot_name
    else:
        sendSerial(COMMAND_CODES["GET_NAME"])
        robot_name = getSerialString()
        return robot_name


def getObstacle(position="all"):
    """ Gets the obstacle sensor (the ultrasonic sensor or 'ping') at position

        arguments:
        position - can be integer between SERVO_LEFT and SERVO_RIGHT
                   can also be the strings "left", "center", "right" or "all"
                   if it is "all", this returns a list of all values
                   defaults to "all"

        returns:
        integer - value of sensor at position OR
        tuple of integers - value of sensor at each position [left, center, right]

        a value of -1 in the return indicates that nothing was found
    """
    printDebug("In getObstacle, position is " + str(position), DEBUG_INFO)

    if position == "left":
        position = SERVO_LEFT
    elif position == "center" or position == "middle":
        position = SERVO_CENTER
    elif position == "right":
        position = SERVO_RIGHT
    elif position == "all":
        result = (getObstacle(SERVO_LEFT), getObstacle(SERVO_CENTER), getObstacle(SERVO_RIGHT))  # recursion
        return result

    position = int(constrain(position, SERVO_LEFT, SERVO_RIGHT))

    servo(position)
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
        tuple containing xpos,ypos (xpos is [0], ypos is [1])
    """
    global xpos, ypos

    printDebug("In getPosition", DEBUG_INFO)

    return (xpos, ypos)


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


def getVersion():
    """ Gets versions of the Python library and the software running on the Sparki
    
        arguments:
        none
        
        returns:
        tuple - [0] is string version of Python library; [1] is string version of robot software (None if not initialized)
    """
    global robot_library_version, SPARKI_MYRO_VERSION

    printDebug("In getVersion", DEBUG_INFO)

    return (SPARKI_MYRO_VERSION, robot_library_version)


def gripperClose(distance=MAX_GRIPPER_DISTANCE):
    """ Closes the gripper by distance; defaults to MAX_GRIPPER_DISTANCE

        arguments:
        distance - float distance in cm to close

        returns:
        nothing
    """
    printDebug("In gripperClose, distance is " + str(distance), DEBUG_INFO)

    distance = constrain(distance, 0, MAX_GRIPPER_DISTANCE)
    distance = float(distance)
    args = [distance]

    sendSerial(COMMAND_CODES["GRIPPER_CLOSE_DIS"], args)
    wait(distance)


def gripperOpen(distance=MAX_GRIPPER_DISTANCE):
    """ Opens the gripper by distance; defaults to MAX_GRIPPER_DISTANCE

        arguments:
        distance - float distance in cm to open

        returns:
        nothing
    """
    printDebug("In gripperOpen, distance is " + str(distance), DEBUG_INFO)
    distance = constrain(distance, 0, MAX_GRIPPER_DISTANCE)
    distance = float(distance)
    args = [distance]

    sendSerial(COMMAND_CODES["GRIPPER_OPEN_DIS"], args)
    wait(distance)


def gripperStop():
    """ Stops gripper movement

        arguments:
        distance - float distance in cm to open

        returns:
        nothing
    """
    printDebug("In gripperStop", DEBUG_INFO)

    sendSerial(COMMAND_CODES["GRIPPER_STOP"])


def init(com_port, print_versions=True):
    """ Connects to the Sparki robot on com_port; if it is already connected, this will disconnect and reconnect on the given port
        Note that Sparki MUST already be paired with the computer over Bluetooth
        
        arguments:
        com_port - a string designating which port Sparki is on (windows looks like "COM??"; mac and linux look like "/dev/????"
                   if com_port is the string "mac", this will assume the standard mac port ("/dev/tty.ArcBotics-DevB")
                   if com_port is the string "hc06", this will assume the standard HC-06 port ("tty.HC-06-DevB")
        print_versions - boolean whether or not to print connection message
        
        returns:
        nothing
    """
    global init_time
    global robot_library_version, SPARKI_MYRO_VERSION
    global serial_conn
    global serial_port
    global serial_is_connected
    global robot_name
    global NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, EXT_LCD_1, NOOP

    printDebug("In init, com_port is " + str(com_port), DEBUG_INFO)

    if serial_is_connected:
        disconnectSerial()

    if com_port == "mac":
        com_port = "/dev/tty.ArcBotics-DevB"
    elif com_port == "hc06":
        com_port = "/dev/tty.HC-06-DevB"

    robot_name = None
    serial_port = com_port

    try:
        serial_conn = serial.Serial(port=serial_port, baudrate=9600, timeout=CONN_TIMEOUT)
    except serial.SerialException:
        printUnableToConnect()
        raise

    serial_is_connected = True  # have to do this prior to sendSerial, or sendSerial will never try to send

    sendSerial(COMMAND_CODES["INIT"])

    robot_library_version = getSerialString()  # Sparki sends us its library version in response

    if robot_library_version:
        init_time = currentTime()

        if print_versions:  # done this way to avoid reprinting it for Mac connection issues
            printDebug("Sparki connection successful", DEBUG_ALWAYS)
            printDebug("  Python library version is " + SPARKI_MYRO_VERSION, DEBUG_ALWAYS)
            printDebug("  Robot library version is " + robot_library_version, DEBUG_ALWAYS)

        # use the version number to try to figure out capabilities
        # if the version has a lower case r, strip off the r and anything to the right of it (that's what .partition() does below)
        try:
            # the order is NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, EXT_LCD_1, reserved, NOOP
            NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, EXT_LCD_1, reserved2, NOOP = SPARKI_CAPABILITIES[
                robot_library_version.partition('r')[0]]
            printDebug("Sparki Capabilities:", DEBUG_INFO)
            printDebug("\tNO_ACCEL:\tNO_MAG:\tSPARKI_DEBUGS:\tUSE_EEPROM:\tEXT_LCD_1:", DEBUG_INFO)
            printDebug("\t" + str(NO_ACCEL) + "\t\t" + str(NO_MAG) + "\t" + str(SPARKI_DEBUGS) + "\t\t" + str(
                USE_EEPROM) + "\t\t" + str(EXT_LCD_1), DEBUG_INFO)
        except KeyError:
            printDebug(
                "Unknown library version, using defaults -- you might need an upgrade of the Sparki Learning Python library",
                DEBUG_ALWAYS)
            printDebug("(to upgrade the library type: pip sparki-learning --upgrade)", DEBUG_ALWAYS)
            printDebug("Sparki Capabilities will be limited", DEBUG_ALWAYS)
        
        if USE_EEPROM and print_versions:
            robot_name = getName()
            printDebug(robot_name + " is ready", DEBUG_ALWAYS)
    else:
        printDebug("Sparki communication failed", DEBUG_ALWAYS)
        serial_is_connected = False
        init_time = -1


initialize = init # Synonym for init(com_port)


def isMoving():
    """ Returns True if the robot is in motion
        Note that this can be unreliable - there's no way to "ask" the robot if it is moving

        arguments:
        None
        
        returns:
        boolean - True if robot is in motion; otherwise False
    """
    global in_motion

    printDebug("In isMoving", DEBUG_INFO)

    return in_motion


def joystick():
    """ Control Sparki using a GUI

        arguments:
        none

        returns:
        nothing
    """
    printDebug("In joystick", DEBUG_INFO)

    #          |   forward   |    
    #   left   |     stop    |  right      
    #          |   backward  |
    #   open   |             |  close
    #   left   |   center    |  right     (these are for the "head" servo)
    #     current action:
    #     in motion?
    #               Exit
    try:
        if sys.version_info[0] >= 3:
            import PySimpleGUI as sg
        else:
            import PySimpleGUI27 as sg
        
        robot_name = getName()

        moving_message = "{} is moving".format(robot_name)
        not_moving_message = "{} is not moving".format(robot_name)
        
        print("{} will not respond to other commands until the joystick window is closed".format(robot_name))
        
        layout = [[sg.Button('Forward')],
                  [sg.Button('Left'), sg.Button('Stop'), sg.Button('Right')],
                  [sg.Button('Backward')],
                  [sg.Button('Open'), sg.Button('Close')],
                  [sg.Button('Head Left'), sg.Button('Head Center'), sg.Button('Head Right')],
                  [sg.Text('Last Click:'), sg.Text('', key='_ACTION_', size=(18,1))],
                  [sg.Text(not_moving_message, key='_MOTION_')],
                  [sg.Button('Exit')],
                  [sg.Text('You must close this window to give other commands to {}'.format(robot_name))]]

        window = sg.Window('Joystick - Drive your Sparki', layout, auto_size_text = True,
                           auto_size_buttons = True, resizable = True,
                           element_justification = "center")

        while True:  # Event Loop
            event, values = window.read()       # can also be written as event, values = window()
            
            if event is None or event == 'Exit':
                break
            elif event == 'Forward':
                # change the action to be forward
                window['_ACTION_'].update("Forward")
                window['_MOTION_'].update(moving_message)
                forward(1)
            elif event == 'Left':
                # change the action to be left
                window['_ACTION_'].update("Left")
                window['_MOTION_'].update(moving_message)
                turnLeft(1)
            elif event == 'Stop':
                # change the action to be stop
                window['_ACTION_'].update("Stop")
                window['_MOTION_'].update(not_moving_message)
                stop()
            elif event == 'Right':
                # change the action to be right
                window['_ACTION_'].update("Right")
                window['_MOTION_'].update(moving_message)
                turnRight(1)
            elif event == 'Backward':
                # change the action to be backward
                window['_ACTION_'].update("Backward")
                window['_MOTION_'].update(moving_message)
                backward(1)
            elif event == 'Open':
                # change the action to be open gripper
                window['_ACTION_'].update("Open Gripper 1cm")
                gripperOpen(1)
            elif event == 'Close':
                # change the action to be close gripper
                window['_ACTION_'].update("Close Gripper 1cm")
                gripperClose(1)
            elif event == 'Head Left':
                # change the action to turn head left
                window['_ACTION_'].update("Head Left")
                servo(SERVO_LEFT)
            elif event == 'Head Center':
                # change the action to turn head center
                window['_ACTION_'].update("Head Center")
                servo(SERVO_CENTER)
            elif event == 'Head Right':
                # change the action to turn head right
                window['_ACTION_'].update("Head Right")
                servo(SERVO_RIGHT)
            else:
                window['_ACTION_'].update("** BAD EVENT **")
                printDebug("Bad event in joystick() -- this should never happen", DEBUG_CRITICAL)

        window.close()
        
    except Exception as err:
        printDebug("No gui for joystick() or other error in joystick()", DEBUG_CRITICAL)
        printDebug(str(err), DEBUG_DEBUG)

    stop()
    print("joystick() ended")


def LCDclear(update=True):
    """ Clears the LCD on Sparki

        arguments:
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDclear", DEBUG_INFO)

    sendSerial(COMMAND_CODES["LCD_CLEAR"])

    if update:
        LCDupdate()


def LCDdrawPixel(x, y, update=True, outofbounds = False):
    """ Draws a pixel on the LCD (which is 128x64; 0,0 is upper left; 127,63 is lower right)

        arguments:
        x - int x coordinate for the pixel, must be >= 0 and <= 127
        y - int y coordinate for the pixel, must be >=0 and <= 63
        update - True (default) if you want Sparki to update the display
        outofbounds - False (default) if you want to constrain x,y to the dimensions of
                      the LCD; if True, the function will silently ignore pixels out
                      of bounds (i.e. x < 0 or x > 127; y < 0 or y > 63)

        returns:
        nothing
    """
    # in the Sparkiduino library of 1.6.8.2 or earlier, this will function not work reliably due to a bug in the underlying library
    printDebug("In LCDdrawPixel, x is " + str(x) + ", y is " + str(y), DEBUG_INFO)

    if outofbounds:
        if x < 0 or x > 127 or y < 0 or y > 63:
            return
    else:
        x = int(constrain(x, 0, 127))  # the LCD is 128 x 64
        y = int(constrain(y, 0, 63))

    args = [x, y]

    sendSerial(COMMAND_CODES["LCD_DRAW_PIXEL"], args)

    if update:
        LCDupdate()


def LCDdrawLine(x1, y1, x2, y2, update=True):
    """ Draws a line on the LCD

        arguments:
        x1 - int first x coordinate for the line, must be <= 127
        y1 - int first y coordinate for the line, must be <= 63
        x2 - int second x coordinate for the line, must be <= 127
        y2 - int second y coordinate for the line, must be <= 63
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    # this has been reimplemented due to bugs in the underlying Sparki library
    printDebug("In LCDdrawLine, x1 is " + str(x1) + ", y1 is " + str(y1) + ", x2 is " + str(x2) + ", y2 is " + str(y2),
               DEBUG_INFO)

    x1 = int(constrain(x1, 0, 127))  # the LCD is 128 x 64
    y1 = int(constrain(y1, 0, 63))
    x2 = int(constrain(x2, 0, 127))
    y2 = int(constrain(y2, 0, 63))

    for x,y in bresenham(x1, y1, x2, y2):
        LCDdrawPixel(x,y,False)    

    if update:
        LCDupdate()


def LCDdrawRect(x1, y1, x2, y2, update=True):
    """ Draws a rectangle on the LCD with opposite corners at x1,y1 and x2,y2

        arguments:
        x1 - int x coordinate for the upper left corner, must be <= 127
        y1 - int y coordinate for the upper left corner, must be <= 63
        x2 - int x coordinate for the lower right corner, must be <= 127
        y2 - int y coordinate for the lower right corner, must be <= 63
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    # this has been reimplemented due to bugs in the underlying Sparki library
    printDebug("In LCDdrawRect, x1 is " + str(x1) + ", y1 is " + str(y1) + ", x2 is " + str(x2) + ", y2 is " + str(y2),
               DEBUG_INFO)

    x1 = int(constrain(x1, 0, 127))  # the LCD is 128 x 64
    y1 = int(constrain(y1, 0, 63))
    x2 = int(constrain(x2, 0, 127))
    y2 = int(constrain(y2, 0, 63))

    if x1 == x2:
        printDebug("In LCDdrawRect, x1 == x2 ({})".format(x1), DEBUG_WARN)
    if y1 == y2:
        printDebug("In LCDdrawRect, y1 == y2 ({})".format(y1), DEBUG_WARN)

    LCDdrawLine(x1,y1,x1,y2,False)    
    LCDdrawLine(x1,y1,x2,y1,False)    
    LCDdrawLine(x2,y2,x1,y2,False)    
    LCDdrawLine(x2,y2,x2,y1,False)    

    if update:
        LCDupdate()


def LCDdrawString(x, y, message, update=True):
    """ Prints message on the LCD on Sparki at the given x,y coordinate

        arguments:
        x - int x coordinate (the location where the text starts) -- can be from 0 to 121 (inclusive)
        y - int y coordinate (the line number where the text states) -- can be from 0 to 7 (inclusive)
        message - string that you want to display
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    if not EXT_LCD_1:
        printDebug("LCDdrawString not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In LCDdrawString, x is " + str(x) + ", y is " + str(y) + ", message is " + str(message), DEBUG_INFO)

    x = int(constrain(x, 0, 121))  # 128 (0 to 127) pixels on the LCD, and a character is 6 pixels wide
    y = int(constrain(y, 0, 7))  # 8 (0 to 7) lines on the LCD

    args = [x, y, message]

    sendSerial(COMMAND_CODES["LCD_DRAW_STRING"], args)

    if update:
        LCDupdate()


def LCDerasePixel(x, y, update=True):
    """ Erases (makes blank) a pixel on the LCD

        arguments:
        x - int x coordinate for the pixel, must be <= 127
        y - int y coordinate for the pixel, must be <= 63
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    # in the Sparkiduino library of 1.6.8.2 or earlier, this will function not work reliably due to a bug in the underlying library
    if not EXT_LCD_1:
        printDebug("LCDerasePixel not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In LCDerasePixel, x is " + str(x) + ", y is " + str(y), DEBUG_INFO)

    LCDsetColor(LCD_WHITE)
    LCDdrawPixel(x, y, update)
    LCDsetColor(LCD_BLACK)


def LCDprint(message, update=True):
    """ Prints message on the LCD on Sparki without going to the next line

        arguments:
        message - string that you want to display
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDprint, message is " + str(message), DEBUG_INFO)

    message = str(message)

    sendSerial(COMMAND_CODES["LCD_PRINT"], message)

    if update:
        LCDupdate()


def LCDprintLn(message, update=True):
    """ Prints message on the LCD on Sparki and goes to the next line

        arguments:
        message - string that you want to display
        update - True (default) if you want Sparki to update the display

        returns:
        nothing
    """
    printDebug("In LCDprintLn, message is " + str(message), DEBUG_INFO)

    message = str(message)

    sendSerial(COMMAND_CODES["LCD_PRINTLN"], message)

    if update:
        LCDupdate()


def LCDreadPixel(x, y):
    """ Returns True if the pixel at the x,y coordinate given is black (colored in)
    
        arguments:
        x - int x coordinate for the pixel, must be <= 127
        y - int y coordinate for the pixel, must be <= 63

        returns:
        bool - True if the pixel is black
    """
    if not EXT_LCD_1:
        printDebug("LCDreadPixel not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In LCDredPixel, x is " + str(x) + ", y is " + str(y), DEBUG_INFO)

    x = int(constrain(x, 0, 127))  # the LCD is 128 x 64
    y = int(constrain(y, 0, 63))

    args = [x, y]

    sendSerial(COMMAND_CODES["LCD_READ_PIXEL"], args)
    result = getSerialInt()

    if result == 1:
        return True
    else:
        return False


def LCDsetColor(color=LCD_BLACK):
    """ Sets the color that LCDdraw commands will draw with; LCD_BLACK will be normal drawing, LCD_WHITE will erase

        arguments:
        color - int color value; should be LCD_BLACK or LCD_WHITE

        returns:
        nothing
    """
    global current_lcd_color

    # in the Sparkiduino library of 1.6.8.2 or earlier, this will function not work reliably due to a bug in the underlying library

    if not EXT_LCD_1:
        printDebug("LCDsetColor not implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In LCDsetColor, color is " + str(color), DEBUG_INFO)

    args = [color]

    sendSerial(COMMAND_CODES["LCD_SET_COLOR"], args)

    current_lcd_color = color


def LCDupdate():
    """ Updates the LCD on Sparki -- you MUST update the LCD after drawing or printing

        arguments:
        none

        returns:
        nothing
    """
    printDebug("In LCDupdate", DEBUG_INFO)

    sendSerial(COMMAND_CODES["LCD_UPDATE"])


def motors(left_speed, right_speed, time=-1):
    """ Moves wheels at left_speed and right_speed for time; time is optional
    
        arguments:
        left_speed - the left wheel speed; a float between -1.0 and 1.0
        right_speed - the right wheel speed; a float between -1.0 and 1.0
        time - float the number of seconds to move; negative numbers will cause the robot to move without stopping
        
        returns:
        nothing
    """
    global in_motion

    printDebug(
        "In motors, left speed is " + str(left_speed) + ", right speed is " + str(right_speed) + " and time is " + str(
            time), DEBUG_INFO)

    if left_speed == 0 and right_speed == 0:
        printDebug("In motors, both speeds == 0, stopping (but please use stop())", DEBUG_WARN)
        stop()
        return

    if left_speed < -1.0 or left_speed > 1.0:
        printDebug("In motors, left_speed is outside of the range -1.0 to 1.0", DEBUG_ERROR)

    if right_speed < -1.0 or right_speed > 1.0:
        printDebug("In motors, right_speed is outside of the range -1.0 to 1.0", DEBUG_ERROR)

    # adjust speeds to Sparki's requirements
    left_speed = constrain(left_speed, -1.0, 1.0)
    right_speed = constrain(right_speed, -1.0, 1.0)

    left_speed = int(left_speed * 100)  # sparki expects an int between 1 and 100
    right_speed = int(right_speed * 100)  # sparki expects an int between 1 and 100
    time = float(time)
    args = [left_speed, right_speed, time]

    in_motion = True
    try:
        sendSerial(COMMAND_CODES["MOTORS"], args)
        if time >= 0:
            wait(time)
    finally:
        if time >= 0:
            in_motion = False


def move(translate_speed, rotate_speed):  # NOT WELL TESTED
    """ Combines moving forward / backward while rotating -- use another command if possible

        arguments:
        translate_speed - float between -1.0 and 1.0 the forward / backward speed -- combined with rotate speed to get actual movements
        rotate_speed - float between -1.0 and 1.0 the left / right speed -- combined with translate speed to get actual movements
                       for some reason, positive is left rotation and negative is right rotation

        returns:
        nothing
    """
    printDebug("In move, translate speed is " + str(translate_speed) + ", rotate speed is " + str(rotate_speed),
               DEBUG_INFO)
    printDebug("The move() function is not well tested", DEBUG_WARN)

    translate_speed = constrain(translate_speed, -1.0, 1.0)
    rotate_speed = constrain(rotate_speed, -1.0, 1.0)

    if translate_speed > 0:
        if rotate_speed > 0:
            motors((translate_speed + rotate_speed) / 2, translate_speed + rotate_speed)
        elif rotate_speed < 0:
            motors(translate_speed + rotate_speed, (translate_speed + rotate_speed) / 2)
        else:  # rotate_speed == 0
            forward(translate_speed)
    elif translate_speed < 0:
        if rotate_speed > 0:
            motors((translate_speed - rotate_speed) / 2, translate_speed - rotate_speed)
        elif rotate_speed < 0:
            motors(translate_speed - rotate_speed, (translate_speed - rotate_speed) / 2)
        else:  # rotate_speed == 0, so use forward() (which will actually go backward)
            forward(translate_speed)
    else:  # translate_speed == 0, so turnLeft
        turnLeft(rotate_speed)


def moveBackwardcm(centimeters):
    """ Move Sparki backward by centimeters

        arguments:
        centimeters - float number of centimeters to move

        returns:
        nothing
    """
    global centimeters_moved
    global in_motion

    printDebug("In moveBackwardcm, centimeters is " + str(centimeters), DEBUG_INFO)

    centimeters = float(centimeters)

    if centimeters == 0:
        printDebug("In moveBackwardcm, centimeters is 0... doing nothing", DEBUG_WARN)
        return
    elif centimeters < 0:
        printDebug("In moveBackwardcm, centimeters is negative, calling moveForwardcm", DEBUG_ERROR)
        moveForwardcm(-centimeters)
        return

    centimeters_moved += centimeters

    args = [centimeters]

    in_motion = True
    sendSerial(COMMAND_CODES["BACKWARD_CM"], args)
    wait(centimeters * SECS_PER_CM)
    in_motion = False


def moveForwardcm(centimeters):
    """ Move Sparki forward by centimeters

        arguments:
        centimeters - float number of centimeters to move

        returns:
        nothing
    """
    global centimeters_moved
    global in_motion

    printDebug("In moveForwardcm, centimeters is " + str(centimeters), DEBUG_INFO)

    centimeters = float(centimeters)

    if centimeters == 0:
        printDebug("In moveForwardcm, centimeters is 0... doing nothing", DEBUG_WARN)
        return
    elif centimeters < 0:
        printDebug("In moveForwardcm, centimeters is negative, calling moveBackwardcm", DEBUG_ERROR)
        moveBackwardcm(-centimeters)
        return

    centimeters_moved += centimeters

    args = [centimeters]

    in_motion = True
    sendSerial(COMMAND_CODES["FORWARD_CM"], args)
    wait(centimeters * SECS_PER_CM)
    in_motion = False


def moveBy(dX, dY, turnBack=False):
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
    angle = math.degrees(math.acos(dY / hypotenuse))  # acos gives the value in radians

    if dX < 0:
        angle = -angle

    # turn & move
    oldHeading = getAngle()
    turnTo(angle)
    moveForwardcm(hypotenuse)

    xpos, ypos = xpos + dX, ypos + dY  # set the new position

    if turnBack:
        # return to the original heading
        turnTo(oldHeading)


def moveTo(newX, newY, turnBack=False):
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


def noop():
    """ Sends a command to the Sparki which should do nothing

        Intended as a way to prevent serial timeouts

        arguments:
        none

        returns:
        none
    """
    printDebug("In noop", DEBUG_INFO)

    if NOOP:
        sendSerial(COMMAND_CODES["NOOP"])
    else:
        printDebug("no op is not available on sparki; simulating", DEBUG_WARN)
        setStatusLED("on")
        setStatusLED("off")


def ping():
    """ Returns the reading from the ultrasonic sensor on the servo

        arguments:
        none

        returns:
        int - approximate distance in centimeters from nearest object (-1 means nothing was found)
    """
    printDebug("In ping", DEBUG_INFO)

    sendSerial(COMMAND_CODES["PING"])
    result = getSerialInt()
    return result


def receiveIR():
    """ Returns the reading from the IR sensor on front of the Sparki (presumably sent from another Sparki using sendIR)
    
        arguments:
        none
        
        returns:
        int - reading (-1 indicates no data is available)
        note that the TERMINATOR and SYNC characters would never be received if sent
    """
    printDebug("In receiveIR", DEBUG_INFO)

    sendSerial(COMMAND_CODES["RECEIVE_IR"])
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
    setPosition(0, 0)


def rotate(speed):
    """ Synonym for turnRight -- use turnRight instead
    """
    turnRight(speed)


def sendIR(sendMe):
    """ Sends an integer via the IR emitter on the front of the Sparki; intended to be received by another Sparki
        via receiveIR

        arguments:
        sendMe - int to transmit using the IR emitter 

        returns:
        nothing
    """
    printDebug("In sendIR, sendMe is " + str(sendMe), DEBUG_INFO)
    sendMe = int(sendMe)
    args = [sendMe]

    sendSerial(COMMAND_CODES["SEND_IR"], args)


def senses():
    """ Displays readings from Sparki's sensors (lines, light, ping, mag, accel, compass)

        arguments:
        none

        returns:
        nothing
    """
    global NO_MAG, NO_ACCEL
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
    #   ping   |             |        |          | moving  |
    try:
        if sys.version_info[0] >= 3:
            import PySimpleGUI as sg
        else:
            import PySimpleGUI27 as sg
        
        robot_name = getName()
        
        print("{} will not respond to other commands until the senses window is closed".format(robot_name))
        
        # 1st column: space, line, light, space, space, mag, accel, space, ping
        col1 = [
                   [ sg.Text('') ],
                   [ sg.Text('line') ],
                   [ sg.Text('light') ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('mag') ],
                   [ sg.Text('accel') ],
                   [ sg.Text('') ],
                   [ sg.Text('ping') ]
               ]

        # 2nd column: left edge, le value, space, space, space, space, space, space, ping value
        col2 = [
                   [ sg.Text('left edge') ],
                   [ sg.Text('   ', key='_LEDGE_VALUE_', size=(3,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('   ', key='_PING_VALUE_', size=(3,1)) ]
               ]

        # 3rd column: left, l line value, l light value, space, X, X mag, X accel, space, space
        col3 = [
                   [ sg.Text('left') ],
                   [ sg.Text('   ', key='_LLINE_VALUE_', size=(3,1)) ],
                   [ sg.Text('   ', key='_LLIGHT_VALUE_', size=(3,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('X') ],
                   [ sg.Text('   ', key='_XMAG_VALUE_', size=(5,1)) ],
                   [ sg.Text('   ', key='_XACCEL_VALUE_', size=(5,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('') ]
               ]
 
        # 4th column: center, c line value, c light value, space, Y, Y mag, Y accel, space, space
        col4 = [
                   [ sg.Text('center') ],
                   [ sg.Text('   ', key='_CLINE_VALUE_', size=(3,1)) ],
                   [ sg.Text('   ', key='_CLIGHT_VALUE_', size=(3,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('Y') ],
                   [ sg.Text('   ', key='_YMAG_VALUE_', size=(5,1)) ],
                   [ sg.Text('   ', key='_YACCEL_VALUE_', size=(5,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('') ]
               ]
 
        # 5th column: right, r line value, r light value, space, Z, Z mag, Z accel, space, moving
        col5 = [
                   [ sg.Text('right') ],
                   [ sg.Text('   ', key='_RLINE_VALUE_', size=(3,1)) ],
                   [ sg.Text('   ', key='_RLIGHT_VALUE_', size=(3,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('Z') ],
                   [ sg.Text('   ', key='_ZMAG_VALUE_', size=(5,1)) ],
                   [ sg.Text('   ', key='_ZACCEL_VALUE_', size=(5,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('moving?') ]
               ]
 
        # 6th column: right edge, re value, space, space, compass, compass value, space, space, moving value
        col6 = [
                   [ sg.Text('right edge') ],
                   [ sg.Text('   ', key='_REDGE_VALUE_', size=(3,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('compass') ],
                   [ sg.Text('   ', key='_COMPASS_VALUE_', size=(5,1)) ],
                   [ sg.Text('') ],
                   [ sg.Text('') ],
                   [ sg.Text('   ', key='_MOVING_VALUE_', size=(3,1)) ]
               ]
        
        layout = [ [ sg.Text("{}'s senses".format(robot_name)) ],
                   [ sg.Column(col1, element_justification = "center"), sg.Column(col2, element_justification = "center"),
                     sg.Column(col3, element_justification = "center"), sg.Column(col4, element_justification = "center"),
                     sg.Column(col5, element_justification = "center"), sg.Column(col6, element_justification = "center") ],
                   [ sg.Button('Exit') ],
                   [ sg.Text("You must close this window to give other commands to {}".format(robot_name))] ]
        
        window = sg.Window("Sparki senses", layout, auto_size_text = True, keep_on_top = True,
                           grab_anywhere = True, auto_size_buttons = True, resizable = True,
                           element_justification = "center")
        
        pause = 2000 # length of time to timeout window in milliseconds
        
        while True:
            event, values = window.Read(timeout = pause)
            
            if event is None or event == 'Exit':
                break # user closed the window
            else:
                # update the values
                ledge, lline, cline, rline, redge = getLine()
                llight, clight, rlight = getLight()
                
                window['_LEDGE_VALUE_'].update(ledge)
                window['_LLINE_VALUE_'].update(lline)
                window['_CLINE_VALUE_'].update(cline)
                window['_RLINE_VALUE_'].update(rline)
                window['_REDGE_VALUE_'].update(redge)

                window['_LLIGHT_VALUE_'].update(llight)
                window['_CLIGHT_VALUE_'].update(clight)
                window['_RLIGHT_VALUE_'].update(rlight)

                if not NO_MAG:
                    xmag, ymag, zmag = getMag()
                    window['_XMAG_VALUE_'].update(xmag)
                    window['_YMAG_VALUE_'].update(ymag)
                    window['_ZMAG_VALUE_'].update(zmag)
                    window['_COMPASS_VALUE_'].update(compass())

                if not NO_ACCEL:
                    xaccel, yaccel, zaccel = getAccel()
                    window['_XACCEL_VALUE_'].update(xaccel)
                    window['_YACCEL_VALUE_'].update(yaccel)
                    window['_ZACCEL_VALUE_'].update(zaccel)

                window['_PING_VALUE_'].update(ping())

                if isMoving():
                    window['_MOVING_VALUE_'].update("Yes")
                else:
                    window['_MOVING_VALUE_'].update("No")
            # end update else
        window.close()
        
    except Exception as err:
        printDebug("No gui for senses() or other error in senses()", DEBUG_CRITICAL)
        printDebug(str(err), DEBUG_DEBUG)
        senses_text()

    print("senses() ended")
## end senses() ##


def servo(position):
    """ Turns the servo 'head' to the position (in degrees) specified

        arguments:
        position - integer between -80 (left side) and 80 (right side) to "aim" the servo

        returns:
        nothing
    """
    printDebug("In servo, position is " + str(position), DEBUG_INFO)

    position = int(constrain(position, SERVO_LEFT, SERVO_RIGHT))
    args = [position]

    sendSerial(COMMAND_CODES["SERVO"], args)
    wait(.2)


def setAngle(newAngle=0):
    """ Sets the number of degrees that the robot has turned (used by the grid commands moveBy() & moveTo())

        If you want the robot to be "reset" to "facing the positive coordinates of the Y axis", call setAngle()

        arguments:
        newAngle - float new number of degrees the robot has turned (defaults to 0); cannot be greater than 360

        returns:
        nothing
    """
    global degrees_turned

    printDebug("In setAngle, newAngle is " + str(newAngle), DEBUG_INFO)

    newAngle = float(wrapAngle(newAngle))  # ensure we're getting a float between -360 and 360

    degrees_turned = newAngle


setDebug = setGlobalDebug


def setLEDBack(brightness):
    """ Sets the RGB LED to white light at the brightness given -- should be a number between 0 and 100, which is a percentage

        arguments:
        brightness - int between 0 and 100 which is a percentage of brightness

        returns:
        nothing
    """
    # the RGB LED is limited in terms of what it can display -- red takes the most voltage, green second, and blue third
    # a single resistor works on all lights, and they cannot be turned on to the same brightness; Arcbotics recommends
    # that to turn on the LED to white color, that we use 60, 100, 90 for the values

    setRGBLED((brightness / 100) * 60, brightness, (brightness / 100) * 90)


def setLEDFront(brightness):
    """ Sets the status LED to the brightness given -- should be a number between 0 and 100, which is a percentage

        arguments:
        brightness - int between 0 and 100 which is a percentage of brightness

        returns:
        nothing
    """

    setStatusLED(brightness)


def setName(newName):
    """ Sets the name of this robot as set in the EEPROM

        arguments:
        newName - string - must be less than EEPROM_NAME_MAX_CHARS

        returns:
        string - name of robot
    """
    global robot_name
    
    if not USE_EEPROM:
        printDebug("setName not be implemented on Sparki", DEBUG_CRITICAL)
        raise NotImplementedError

    printDebug("In setName, newName is " + str(newName), DEBUG_INFO)

    if len(newName) > EEPROM_NAME_MAX_CHARS - 1:
        printDebug("In setName(), the name " + str(newName) + " is too long. It must be fewer than " + str(
            EEPROM_NAME_MAX_CHARS - 1) + " letters and numbers. Truncating...", DEBUG_WARN)
        newName = newName[:EEPROM_NAME_MAX_CHARS - 1]

    args = [newName]
    sendSerial(COMMAND_CODES["SET_NAME"], args)
    
    robot_name = newName


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
    global xpos, ypos  # also can be set in moveBy()

    printDebug("In setPosition, new position will be " + str(newX) + ", " + str(newY), DEBUG_INFO)

    xpos = float(newX)
    ypos = float(newY)


def setRGBLED(red, green, blue):
    """ Sets the RGB LED to the color given -- colors should be a value between 0 and 100, which is a percentage of that color

        arguments:
        red - int between 0 and 100 which is an amount of brightness for that LED
        green - int between 0 and 100 which is an amount of brightness for that LED
        blue - int between 0 and 100 which is an amount of brightness for that LED

        arcbotics recommends the following values for the specified colors:
        blue   0,   0,   100
        green  0,   100, 0
        indigo 20,  0,   100
        orange 90,  100, 0
        pink   90,  0,   100
        red    100, 0,   0
        violet 60,  0,   100
        white  60,  100, 90
        yellow 60,  100, 0
        off    0,   0,   0

        returns:
        nothing
    """
    printDebug("In setRGBLED, red is " + str(red) + ", green is " + str(green) + ", blue is " + str(blue), DEBUG_INFO)

    if red == green and red == blue and red != 0:
        printDebug(
            "In setRGBLED, red, green and blue are the same - hardware limitations will cause this to be fully red",
            DEBUG_WARN)

    red = int(constrain(red, 0, 100))
    green = int(constrain(green, 0, 100))
    blue = int(constrain(blue, 0, 100))
    args = [red, green, blue]

    sendSerial(COMMAND_CODES["SET_RGB_LED"], args)


def setSparkiDebug(level):
    """ Sets the debug (in Sparki) to level

        arguments:
        level - int between 0 and 5; greater numbers produce more output (many of Sparki's debug statements are turned off)

        returns:
        none
    """
    if SPARKI_DEBUGS:
        printDebug("Changing Sparki debug level to " + str(level), DEBUG_INFO)
        level = int(constrain(level, DEBUG_ALWAYS, DEBUG_DEBUG))

        args = [level]

        sendSerial(COMMAND_CODES["SET_DEBUG_LEVEL"], args)
    else:
        printDebug("Setting sparki debug level is not available", DEBUG_ERROR)


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

    brightness = int(constrain(brightness, 0, 100))
    args = [brightness]

    sendSerial(COMMAND_CODES["SET_STATUS_LED"], args)


def stop():
    """ Stops the robot and the gripper
    
        arguments:
        none
        
        returns:
        nothing
    """
    global in_motion

    printDebug("In stop", DEBUG_INFO)

    sendSerial(COMMAND_CODES["STOP"])
    in_motion = False


def syncWait(server_ip=None, server_port=32216):
    """ Wait for a time specified by a sync server over a network

        This function attempts to synchronize multiple computers controlling Sparkis using the sparki_learning.sync_lib library
        One computer is designated by the programmers as the server. It can, but does not have to, control a sparki itself.
        The others are designated by the programmers as clients. On the server, you specify an amount of time from now (e.g. 30 seconds)
        for all clients (and the server) to wait. Each of the clients connects to the server to find out the amount of time to wait.
        Once the countdown is complete, all the computers stop waiting and execute the rest of the program.
    
        arguments:
        server_ip - string IPv4 address for the program running the server
                    if none is given to the function, will ask for input
        server_port - int port to which to connect
                      if none is given to the function, defaults to 32216
        
        returns:
        nothing
    """
    printDebug("In waitForSync, server_ip is " + str(server_ip) + "; server_port is " + str(server_port), DEBUG_INFO)

    from sparki_learning.sync_lib import get_client_start
    wait_time = get_client_start(server_ip, server_port)

    waitNoop(wait_time)


def translate(speed):
    """ Synonym for forward() -- use forward instead
    """
    forward(speed)


def turnBy(degrees):
    """ Turn Sparki by degrees; positive numbers turn clockwise & negative numbers turn counter clockwise

        arguments:
        degrees - float number of degrees to turn; positive is clockwise and negative is counter clockwise; should
                  be greater than -360 and less than 360 (Note that the clockwise direction is different than the
                  Myro library)

        returns:
        nothing
    """
    global degrees_turned, in_motion

    printDebug("In turnBy, degrees is " + str(degrees), DEBUG_INFO)

    degrees = wrapAngle(degrees)

    if abs(degrees) >= 360:  # >= in case there's a rounding error
        degrees = 0

    if degrees == 0:
        printDebug("In turnBy, degrees is 0... doing nothing", DEBUG_WARN)
        return

    degrees_turned += degrees

    # keep degrees_turned greater than -360 and less than 360
    degrees_turned = wrapAngle(degrees_turned)

    printDebug("In turnBy, degrees_turned is now " + str(degrees_turned), DEBUG_DEBUG)

    args = [degrees]

    in_motion = True
    sendSerial(COMMAND_CODES["TURN_BY"], args)
    wait(abs(degrees) * SECS_PER_DEGREE)
    in_motion = False


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
    newHeading = wrapAngle(newHeading)

    currentHeading = getAngle()

    printDebug("In turnTo turning from " + str(currentHeading) + " to " + str(newHeading), DEBUG_DEBUG)
    turnBy(newHeading - currentHeading)


def turnLeft(speed, time=-1):
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

    motors(-speed, speed, time)


def turnRight(speed, time=-1):
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

    motors(speed, -speed, time)


def wait(wait_time):
    """ Wait for wait_time seconds; actual time will vary somewhat due to factors outside of program control
    
        arguments:
        wait_time - float number of seconds to wait
        
        returns:
        nothing
    """
    printDebug("In wait, wait_time is " + str(wait_time), DEBUG_INFO)
    maxWait = 600

    if wait_time >= maxWait:
        printDebug("Wait time is " + str(maxWait) + " seconds or greater -- reducing to " + str(maxWait) + " seconds",
                   DEBUG_ERROR)
    elif wait_time > 120:
        printDebug("Wait time is greater than 2 minutes", DEBUG_WARN)

    wait_time = float(constrain(wait_time, 0, maxWait))  # don't wait longer than ten minutes

    time.sleep(wait_time)  # in Python >= 3.5, it will wait at least wait_time seconds; prior to that it could be less


def waitNoop(wait_time):
    """ Wait for wait_time seconds while sending noops to sparki; actual time will vary somewhat due to factors outside of program control
        less accurate for timing than wait, but may maintain a serial connection better
    
        arguments:
        wait_time - float number of seconds to wait
        
        returns:
        nothing
    """
    printDebug("In waitNoop, wait_time is " + str(wait_time), DEBUG_INFO)
    maxWait = 1200
    sleepTime = 1

    if wait_time >= maxWait:
        printDebug("Wait time is " + str(maxWait) + " seconds or greater -- reducing to " + str(maxWait) + " seconds",
                   DEBUG_ERROR)

    wait_time = float(constrain(wait_time, 0, maxWait))  # don't wait longer than maxWait seconds

    for s in timer(wait_time):
        noop()
        time_remaining = wait_time - s

        if time_remaining <= sleepTime:
            time.sleep(
                time_remaining)  # in Python >= 3.5, it will wait at least wait_time seconds; prior to that it could be less
        else:
            time.sleep(sleepTime)


###################### END OF SPARKI MYRO FUNCTIONS ######################


### functions which cannot be or are not implemented ###
def arcBy(args=None):
    printDebug("arcBy not implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


def arcTo(args=None):
    printDebug("arcTo not implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


def getIR(args=None):
    printDebug("getIR cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


def getMicrophone():
    printDebug("getMicrophone cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


def getStall():
    printDebug("getStall cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


def takePicture(args=None):
    printDebug("takePicture cannot be implemented on Sparki (because there's no camera)", DEBUG_CRITICAL)
    raise NotImplementedError


## speak is implemented in sparki_leaning.speak

def show(args=None):
    printDebug("show cannot be implemented on Sparki", DEBUG_CRITICAL)
    raise NotImplementedError


### end junk functions ###


def main():
    print("sparki_learning version " + SPARKI_MYRO_VERSION)
    print(
        "This is intended to be used as a library -- your code should call this program by importing the library, e.g.")
    print("from sparki_learning import *")
    print("Exiting...")


if __name__ == "__main__":
    main()
