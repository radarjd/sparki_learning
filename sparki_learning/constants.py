################## Sparki Learning Library Constants ##################
#
# This file contains various constants used by the Sparki Learning Library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# Previously, this was a part of sparki_myro.py -- it was broken out for flexibility
#
# written by Jeremy Eglen
# Created: November 18, 2019
# Last Modified: February 12, 2021

########### CONSTANTS ###########
# ***** VERSION NUMBER ***** #
SPARKI_MYRO_VERSION = "1.6.5"  # this may differ from the version on Sparki itself

# ***** MESSAGE TERMINATOR ***** #
TERMINATOR = chr(23)  # this character is at the end of every message to / from Sparki

# ***** SYNC ***** #
SYNC = chr(22)  # this character is sent by Sparki after every command completes so we know it's ready for the next

# ***** MISCELLANEOUS VARIABLES ***** #
SECS_PER_CM = .4  # number of seconds it takes sparki to move 1 cm; estimated from observation - may vary depending on batteries and robot
SECS_PER_DEGREE = .03  # number of seconds it takes sparki to rotate 1 degree; estimated from observation - may vary depending on batteries and robot
MAX_TRANSMISSION = 20  # maximum message length is 20 to conserve Sparki's limited RAM

LCD_BLACK = 0  # set in Sparki.h
LCD_WHITE = 1  # set in Sparki.h

# ***** COMMAND CHARACTER CODES ***** #
# Sparki Myro works by sending commands over the serial port (bluetooth) to Sparki from Python
# This is the list of possible command codes; note that it is possible for some commands to be turned off at Sparki's level (e.g. the Accel, Mag)
COMMAND_CODES = {
    'BEEP': 'b',  # requires 2 arguments: int freq and int time; returns nothing
    'COMPASS': 'c',  # no arguments; returns float heading
    'GAMEPAD': 'e',  # no arguments; returns nothing
    'GET_ACCEL': 'f',  # no arguments; returns array of 3 floats with values of x, y, and z
    #'GET_BATTERY': 'j',  # no arguments; returns float of voltage remaining
    'GET_LIGHT': 'k',  # no arguments; returns array of 3 ints with values of left, center & right light sensor
    'GET_LINE': 'm',
    # no arguments; returns array of 5 ints with values of left edge, left, center, right & right edge line sensor
    'GET_MAG': 'o',  # no arguments; returns array of 3 floats with values of x, y, and z
    'GRIPPER_CLOSE_DIS': 'v',  # requires 1 argument: float distance to close the gripper; returns nothing
    'GRIPPER_OPEN_DIS': 'x',  # requires 1 argument: float distance to open the gripper; returns nothing
    'GRIPPER_STOP': 'y',  # no arguments; returns nothing
    'INIT': 'z',  # no arguments; confirms communication between computer and robot
    'LCD_CLEAR': '0',  # no arguments; returns nothing
    ## below LCD commands removed for compacting purposes
    ##'LCD_DRAW_CIRCLE':'1',    # requires 4 arguments: int x&y, int radius, and int filled (1 is filled); returns nothing
    ##'LCD_DRAW_LINE': '2',
    # requires 4 arguments ints x&y for start point and x1&y1 for end points; returns nothing; EXT_LCD_1 must be True
    'LCD_DRAW_PIXEL': '3',  # requires 2 arguments: int x&y; returns nothing
    ##'LCD_DRAW_RECT':'4',# requires 5 arguments: int x&y for start point, ints width & height, and int filled (1 is filled); returns nothing
    'LCD_DRAW_STRING': '5',
    # requires 3 arguments: int x (column), int line_number, and char* string; returns nothing; EXT_LCD_1 must be True
    'LCD_PRINT': '6',  # requires 1 argument: char* string; returns nothing
    'LCD_PRINTLN': '7',  # requires 1 argument: char* string; returns nothing
    'LCD_READ_PIXEL': '8',
    # requires 2 arguments: int x&y; returns int color of pixel at that point; EXT_LCD_1 must be True
    'LCD_SET_COLOR': 'T',  # requires 1 argument: int color; returns nothing; EXT_LCD_1 must be True
    'LCD_UPDATE': '9',  # no arguments; returns nothing
    'MOTORS': 'A',  # requires 3 arguments: int left_speed (1-100), int right_speed (1-100), & float time
    # if time < 0, motors will begin immediately and will not stop; returns nothing
    'BACKWARD_CM': 'B',  # requires 1 argument: float cm to move backward; returns nothing
    'FORWARD_CM': 'C',  # requires 1 argument: float cm to move forward; returns nothing
    'PING': 'D',  # no arguments; returns ping at current servo position
    'RECEIVE_IR': 'E',  # no arguments; returns an int read from the IR sensor
    'SEND_IR': 'F',  # requires 1 argument: int to send on the IR sender; returns nothing
    'SERVO': 'G',  # requires 1 argument: int servo position; returns nothing
    'SET_DEBUG_LEVEL': 'H',  # requires 1 argument: int debug level (0-5); returns nothing; SPARKI_DEBUGS must be True
    'SET_RGB_LED': 'I',  # requires 3 arguments: int red, int green, int blue; returns nothing
    'SET_STATUS_LED': 'J',  # requires 1 argument: int brightness of LED; returns nothing
    'STOP': 'K',  # no arguments; returns nothing
    'TURN_BY': 'L',  # requires 1 argument: float degrees to turn - if degrees is positive, turn clockwise,
    # if degrees is negative, turn counterclockwise; returns nothing
    'GET_NAME': 'O',  # get the Sparki's name as stored in the EEPROM - USE_EEPROM must be True
    # if the name was not set previously, can give undefined behavior
    'SET_NAME': 'P',  # set the Sparki's name in the EEPROM - USE_EEPROM must be True
    'READ_EEPROM': 'Q',  # reads data as stored in the EEPROM - USE_EEPROM & EXT_LCD_1 must be True
    'WRITE_EEPROM': 'R',  # writes data to the EEPROM - USE_EEPROM & EXT_LCD_1 must be True
    'NOOP': 'Z'  # does nothing and returns nothing - NOOP must be True
}
# ***** END OF COMMAND CHARACTER CODES ***** #

# ***** DEBUG CONSTANTS ***** #
# these are the debug levels used on the sparki itself in case the SPARKI_DEBUGS capability is set to True
DEBUG_DEBUG = 5  # reports just about everything
DEBUG_INFO = 4  # reports entering functions
DEBUG_WARN = 3  # a generally sane default; reports issues that may be mistakes, but don't interfere with operation
DEBUG_ERROR = 2  # reports something contrary to the API
DEBUG_CRITICAL = 1  # reports an error which interferes with proper or consistent operation
DEBUG_ALWAYS = 0  # should always be reported

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

# ***** EEPROM STORAGE ***** #
EEPROM_BLUETOOTH_ADDRESS = 80
EEPROM_NAME_MAX_CHARS = 20
EEPROM_MAX_ADDRESS = 1023

# ***** SERVO POSITIONS ***** #
SERVO_LEFT = -80
SERVO_CENTER = 0
SERVO_RIGHT = 80

# ***** TABLE OF CAPABILITIES ***** #
# this dictionary stores the capabilities of various versions of the program running on the Sparki itself
# this is used in init to update the capabilities of the Sparki -- you could use this so that the library can
#   work with different versions of the Sparki library
# The order of the fields is NO_ACCEL, NO_MAG, SPARKI_DEBUGS, USE_EEPROM, EXT_LCD_1, reserved, NOOP
# If a version number contains a lower case r, everything after the r will be stripped when determining the capabilities
#   for example, 1.1.2r1 and 1.1.2r5 will have the same capabilities
SPARKI_CAPABILITIES = {"z": (True, True, False, False, False, False, False),
                       "DEBUG": (True, True, True, False, False, False, False),
                       "DEBUG-ACCEL": (False, True, True, False, False, False, False),
                       "DEBUG-EEPROM": (True, True, True, True, False, False, False),
                       "DEBUG-LCD": (False, False, True, False, True, False, False),
                       "DEBUG-MAG": (True, False, True, False, False, False, False),
                       "DEBUG-PING": (True, True, True, False, False, False, False),
                       "0.2 No Mag / No Accel": (True, True, False, False, False, False, False),
                       "0.8.3 Mag / Accel On": (False, False, False, False, False, False, False),
                       "0.9.6": (False, False, False, True, False, False, False),
                       "0.9.7": (False, False, False, True, False, False, False),
                       "0.9.8": (False, False, False, True, False, False, False),
                       "1.0.0": (False, False, False, True, False, False, False),
                       "1.0.1": (False, False, False, True, True, False, False),
                       "1.1.0": (False, False, False, True, True, False, False),
                       "1.1.1": (False, False, False, True, True, False, False),
                       "1.1.2": (False, False, False, True, True, False, False),
                       "1.1.3": (False, False, False, True, True, False, True),
                       "1.1.4": (False, False, False, True, True, False, True)}

########### END OF CONSTANTS ###########

