/* ***** Sparki_Myro ***** */
/* created by Jeremy Eglen */

/* implements an API compatible with the Myro command set by the Institute for Personal Robotics in Education
   This implementation is not associated in any way with the IPRE */
   
/* Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
   remain property of their respective owners */

/* initial creation - October 27, 2015 
   last modified - March 6, 2019 */

/* conceptually, the Sparki recieves commands over the Bluetooth module from another computer 
 * a minimal command set is implemented on the Sparki itself -- just sufficient to expose the major functions
 * timing (i.e. when a command has a set duration) should be done on the Sparki when possible for accuracy 
 */

/* the library is written to be simple and straightforward -- when there's a choice between clarity and 
 * optimization, always choose clarity, and assume a student learning the language and the hardware will
 * be reviewing and maintaining the code
 */

/* most recent version developed in Sparkiduino 1.6.8.2 -- there do appear to be differences in compiled progam size 
 * among different versions of Sparkiduino; verified to work with 1.6.9.1; verified to work with 1.6.9.4
*/

// for simplicity of installation, we're keeping the constants and prototypes in the cpp file
#ifndef Sparki_Myro_h
#define Sparki_Myro_h

// these defines make the code ugly in a lot of places, but have been put in to save space (in Sparki's memory) when possible
//#define NO_ACCEL  // disables the Accelerometer, be sure to also set in Sparki.h
//#define NO_MAG    // disables the Magnetometer, be sure to also set in Sparki.h
#define NO_DEBUGS	// save more memory by excluding any DEBUG_DEBUG lines
#define COMPACT_2  // remove certain LCD functions (there was once a COMPACT)
#define USE_EEPROM // use EEPROM to store certain values
#define STATUS_ACK // if this is defined, the status light will be lit when the Sparki is processing a command

#include <Sparki.h>

#ifdef USE_EEPROM
#include "SparkiEEPROM.h"
#endif // USE_EEPROM

/* ########### CONSTANTS ########### */
/* ***** VERSION NUMBER ***** */
const char* SPARKI_MYRO_VERSION = "1.1.4r2";    // debugs off; mag on, accel on, EEPROM on; compact 2 on
												// versions having the same number (before the lower case r)
												// should always have the same capabilities

/* ***** MESSAGE TERMINATOR ***** */
const char TERMINATOR = (char)23;      // this terminates every transmission from python

/* ***** ACTION TERMINATOR ***** */
const char SYNC = (char)22;            // send this when in the command loop waiting for instructions


/* ***** COMMAND CHARACTER CODES ***** */
/* Sparki Myro works by listening on the serial port for a command from the computer in the loop() function
 * The loop() function is primarily a massive switch statement that gets a COMMAND code and executes the proper
 * funtion on Sparki. This is the list of COMMAND codes -- the Python library calling Sparki will need this list
 * to be identical.
 */
const char COMMAND_BEEP = 'b';          // requires 2 arguments: int freq and int time; returns nothing
const char COMMAND_COMPASS = 'c';       // no arguments; returns float heading
const char COMMAND_GAMEPAD = 'e';       // no arguments; returns nothing

#ifndef NO_ACCEL
const char COMMAND_GET_ACCEL = 'f';     // no arguments; returns array of 3 floats with values of x, y, and z
#endif // NO_ACCEL

// GET_BATTERY removed because results were unreliable
//const char COMMAND_GET_BATTERY = 'j';   // no arguments; returns float of voltage remaining; per arcbotics, the systemVoltage() function should not be relied upon
const char COMMAND_GET_LIGHT = 'k';     // no arguments; returns array of 3 ints with values of left, center & right light sensor                                    
const char COMMAND_GET_LINE = 'm';      // no arguments; returns array of 5 ints with values of left edge, left, center, right & right edge line sensor

#ifndef NO_MAG
const char COMMAND_GET_MAG = 'o';       // no arguments; returns array of 3 floats with values of x, y, and z
#endif // NO_MAG

const char COMMAND_GRIPPER_CLOSE_DIS = 'v'; // requires 1 argument: float distance to close the gripper; returns nothing
const char COMMAND_GRIPPER_OPEN_DIS = 'x';  // requires 1 argument: float distance to open the gripper; returns nothing
const char COMMAND_GRIPPER_STOP = 'y';  // no arguments; returns nothing
const char COMMAND_INIT = 'z';          // no arguments; confirms communication between computer and robot
const char COMMAND_LCD_CLEAR = '0';     // no arguments; returns nothing

#ifndef COMPACT_2
const char COMMAND_LCD_DRAW_CIRCLE = '1';   // requires 4 arguments: int x&y, int radius, and int filled (1 is filled); returns nothing
const char COMMAND_LCD_DRAW_RECT = '4'; // requires 5 arguments: int x&y for start point, ints width & height, and int filled (1 is filled); returns nothing 
#endif // COMPACT_2

// LCD_DRAW_LINE removed due to errors in the underlying library -- reimplemented in python
//const char COMMAND_LCD_DRAW_LINE = '2'; // requires 4 arguments ints x&y for start point and x1&y1 for end points; returns nothing
const char COMMAND_LCD_DRAW_PIXEL = '3';    // requires 2 arguments: int x&y; returns nothing
const char COMMAND_LCD_DRAW_STRING = '5';   // requires 3 arguments: int x (column), int line_number, and char* string; returns nothing
const char COMMAND_LCD_PRINT = '6';     // requires 1 argument: char* string; returns nothing
const char COMMAND_LCD_PRINTLN = '7';   // requires 1 argument: char* string; returns nothing
const char COMMAND_LCD_READ_PIXEL = '8';    // requires 2 arguments: int x&y; returns int color of pixel at that point
const char COMMAND_LCD_SET_COLOR = 'T'; // requires 1 argument: int color; returns nothing
const char COMMAND_LCD_UPDATE = '9';    // no arguments; returns nothing
const char COMMAND_MOTORS = 'A';        // requires 3 arguments: int left_speed (-100 to 100), int right_speed (-100 to 100), & float time
                                        // if time < 0, motors will begin immediately and will not stop; returns nothing
const char COMMAND_BACKWARD_CM = 'B';   // requires 1 argument: int cm to move backward; returns nothing
const char COMMAND_FORWARD_CM = 'C';    // requires 1 argument: int cm to move forward; returns nothing
const char COMMAND_PING = 'D';          // no arguments; returns ping at current servo position
const char COMMAND_RECEIVE_IR = 'E';    // no arguments; returns int IR receiver value (-1 indicates no data available)
const char COMMAND_SEND_IR = 'F';       // requires 1 argument: int data; returns nothing
const char COMMAND_SERVO = 'G';         // requires 1 argument: int servo position; returns nothing

#ifndef NO_DEBUGS
const char COMMAND_SET_DEBUG_LEVEL = 'H';   // requires 1 argument: int debug level (0-5); returns nothing
#endif // NO_DEBUGS

const char COMMAND_SET_RGB_LED = 'I';   // requires 3 arguments: int red, int green, int blue; returns nothing; note hardware limitations 
                                        // will prevent some values of red, green, and blue from showing up
const char COMMAND_SET_STATUS_LED = 'J';    // requires 1 argument: int brightness of LED; returns nothing
const char COMMAND_STOP = 'K';          // no arguments; returns nothing
const char COMMAND_TURN_BY = 'L';       // requires 1 argument: float degrees to turn - if degrees is positive, turn clockwise,
                                        // if degrees is negative, turn counterclockwise; returns nothing

#ifdef USE_EEPROM
const char COMMAND_GET_NAME = 'O';      // get Sparki's name from the EEPROM
const char COMMAND_SET_NAME = 'P';      // set Sparki's name in the EEPROM
const char COMMAND_EEPROM_READ = 'Q';   // reads data from the EEPROM
const char COMMAND_EEPROM_WRITE = 'R';  // writes data to the EEPROM
#endif // USE_EEPROM

#ifndef COMPACT_2
const char COMMAND_VERSION = 'V';   // no arguments; returns version
#endif // COMPACT_2

const char COMMAND_NOOP = 'Z';  // no arguments; returns nothing; does nothing; added 1.1.3; can be used to prevent a timeout in communication with the robot
/* ***** END OF COMMAND CHARACTER CODES ***** */


/* ***** DEBUG CONSTANTS ***** */
#ifndef NO_DEBUGS
const int DEBUG_DEBUG = 5;
const int DEBUG_INFO = 4;
const int DEBUG_WARN = 3;
const int DEBUG_ERROR = 2;
const int DEBUG_CRITICAL = 1;
const int DEBUG_ALWAYS = 0;
#endif

/* ***** EEPROM LOCATIONS ***** */
#ifdef USE_EEPROM
const int EEPROM_NAME_START = 20;          // byte location of the start of the name
const int EEPROM_NAME_MAX_CHARS = 20;      // the max number of bytes in the name
#endif // USE_EEPROM


/* ***** SENSOR POSITION CONSTANTS ***** */
/* LINE SENSORS */
const int LINE_EDGE_RIGHT = 4;
const int LINE_MID_RIGHT = 3;
const int LINE_MID = 2;
const int LINE_MID_LEFT = 1;
const int LINE_EDGE_LEFT = 0;

/* LIGHT SENSORS */
const int LIGHT_SENS_RIGHT = 2;
const int LIGHT_SENS_MID = 1;
const int LIGHT_SENS_LEFT = 0;


/* ***** SERIAL PORT FOR BLUETOOTH ***** */
#define serial Serial1

/* ########### END OF CONSTANTS ########### */



/* ########## FUNCTION PROTOTYPES ########### */
/* ***** SPARKI UTILITY FUNCTIONS ***** */
/* These functions are used internally, and are not called by the computer */
char getSerialChar();  // gets a char from the serial port; BLOCKING
float getSerialFloat();  // gets a float from the serial port; BLOCKING
int getSerialInt();  // gets an int from the serial port; BLOCKING

int getSerialBytes(char* buf, int size); // gets bytes from the serial port; BLOCKING

void motors(int left_speed, int right_speed);  // starts the motors at the speed indicated

#ifndef NO_DEBUGS
void printDebug(char* message, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(char c, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(float f, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(float* floats, int importance, int size, int newLine = 0);  // prints debug messages to LCD
void printDebug(int i, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(int* ints, int importance, int size, int newLine = 0);  // prints debug messages to LCD
#endif // NO_DEBUGS

#ifdef USE_EEPROM
int loadFromEEPROM(char* buf, int size, int start);  // loads data from EEPROM into buffer
#endif // USE_EEPROM

void sendSerial(char c);
void sendSerial(char* message);
void sendSerial(float f);
void sendSerial(float* floats, int size);
void sendSerial(int i);
void sendSerial(int* ints, int size);


/* ***** SPARKI COMMANDS ***** */
/* These functions can be called by the computer */
// void backward(int speed, float time); now handled in Python as call to motors()
// beep is handled via a direct call
// compass is handled via a direct call
// void forward(int speed, float time);  now handled in Python as call to motors()
void gamepad();

#ifndef NO_ACCEL
void getAccel();
#endif // NO_ACCEL

float getBattery();
void getLight();
void getLine();

#ifndef NO_MAG
void getMag();
#endif

#ifdef USE_EEPROM
void getName();
void setName();
void readFromEEPROM(int start, int amount);  // reads data from EEPROM at location start and sends over serial port
void writeToEEPROM(int start);  // writes data to EEPROM at location start
#endif // USE_EEPROM

void initSparki();  // confirms communication with Python

// LCD functions are generally handled via direct calls
#ifndef COMPACT_2
void LCDdrawCircle(int center_x, int center_y, int radius, int filled);
void LCDdrawRect(int corner_x, int corner_y, int width, int height, int filled);
#endif // COMPACT_2

void LCDdrawString(int x, int y);
void LCDprint();
void LCDsetColor(int color);
void motors(int left_speed, int right_speed, float time);
void setDebugLevel(int level);
void setStatusLED(int brightness);
void stop();
void turnBy(float deg);
/* ########## END OF FUNCTION PROTOTYPES ########### */
#endif // Sparki_Myro_h

/* ########### GLOBALS ########### */
#ifndef NO_DEBUGS
int debug_level = DEBUG_WARN;
#endif //NO_DEBUGS
/* ########### END OF GLOBALS ########### */



/* ########### FUNCTIONS ########### */
/* ***** SERIAL FUNCTIONS ***** */
// gets a char from the serial port
// blocks until one is available
char getSerialChar() {
  int size = 5;
  char buf[size];
  int result = getSerialBytes(buf, size);
  return buf[0];
}

// gets a float from the serial port
// blocks until one is available
// floats are sent to Sparki as char* in order to eliminate conversion issues
// we then convert the string to a float and return that
// there is likely to be some loss of precision
float getSerialFloat() {
  int size = 20;
  char buf[size];
  int result = getSerialBytes(buf, size);
  return atof( buf );
}

// gets an int from the serial port
// blocks until one is available
// ints are sent to Sparki as char* in order to eliminate conversion issues
// we then convert the string to an int and return that
int getSerialInt() {
  int size = 20;
  char buf[size];
  int result = getSerialBytes(buf, size);
  return atoi( buf );
}

// gets bytes from the serial port
// the byte stream should be terminated by TERMINATOR
// buf will be overwritten entirely
// way too much work went into getting this function right - it probably could be more efficient
// returns the number of bytes read
int getSerialBytes(char* buf, int size) {
  char inByte = -1;
  int maxChars = size; 
  int count = 0;
  
  // zero out the buffer
  for( int i = 0; i < maxChars; i++ ) {
    buf[i] = '\0';
  }

  while ((inByte != TERMINATOR) && (count < maxChars)) {
    if(serial.available()) {
      inByte = serial.read();

#ifndef NO_DEBUGS
      printDebug(inByte, DEBUG_DEBUG);
      printDebug(' ', DEBUG_DEBUG);
#endif
   
      if ((inByte != TERMINATOR) && (inByte >= 0)) {
        buf[count++] = (char)inByte;
      }
    }
  }
  
  // flush extra characters
  while ((inByte != TERMINATOR) && (serial.available())) {
      inByte = serial.read();
  }

  return count;
}


/* These functions send data from Sparki to the computer over Bluetooth */
void sendSerial(char c) {
#ifndef NO_DEBUGS
  printDebug("Sending char over Bluetooth: ", DEBUG_DEBUG);
  printDebug(c, DEBUG_DEBUG, 1);
#endif

  serial.print(c); 
  serial.print(TERMINATOR); 
}

void sendSerial(char* message) {
#ifndef NO_DEBUGS
  printDebug("Sending message over Bluetooth: ", DEBUG_DEBUG);
  printDebug(message, DEBUG_DEBUG, 1);
#endif
  
  serial.print(message); 
  serial.print(TERMINATOR); 
}

void sendSerial(float f) {
#ifndef NO_DEBUGS
  printDebug("Sending float over Bluetooth: ", DEBUG_DEBUG);
  printDebug(f, DEBUG_DEBUG, 1);
#endif
  
  serial.print(f); 
  serial.print(TERMINATOR); 
}

void sendSerial(float* floats, int size) {
  for(int j = 0; j < size; j++) {  
    sendSerial(floats[j]);
  }
}

void sendSerial(int i) {
#ifndef NO_DEBUGS
  printDebug("Sending int over Bluetooth: ", DEBUG_DEBUG);
  printDebug(i, DEBUG_DEBUG, 1);
#endif
  
  serial.print(i); 
  serial.print(TERMINATOR); 
}

void sendSerial(int* ints, int size) {
  for(int j = 0; j < size; j++) {  
    sendSerial(ints[j]);
  }
}

void sendSync() {
//  printDebug(".", DEBUG_DEBUG);
  serial.print(SYNC);
  serial.flush();
}
/* ***** END OF SERIAL FUNCTIONS ***** */

/* ***** PRINT DEBUG FUNCTIONS ***** */
#ifndef NO_DEBUGS
// printDebug(char*,int,int)
// print char* on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(char* message, int importance, int newLine) {
  if (importance <= debug_level) {
    if (newLine == 0) {
      sparki.print(message);
    } 
    else {
      sparki.println(message);
    }

    sparki.updateLCD();
  }
}

// printDebug(char,int,int)
// print char on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(char c, int importance, int newLine) {
  if (importance <= debug_level) {
    if (newLine == 0) {
      sparki.print(c);
    } 
    else {
      sparki.println(c);
    }

    sparki.updateLCD();
  }
}

// printDebug(float,int,int)
// print int on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(float f, int importance, int newLine) {
  if (importance <= debug_level) {
    if (newLine == 0) {
      sparki.print(f);
    } 
    else {
      sparki.println(f);
    }

    sparki.updateLCD();
  }
}

// printDebug(float*,int,int,int)
// print float* on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(float* floats, int importance, int size, int newLine) {
  if (importance <= debug_level) {
    for(int j = 0; j < size; j++) {
      printDebug(floats[j], importance, newLine);

      if (newLine == 0) { // space out multiple figures
        printDebug(', ', importance); 
      }
    }
  }
}

// printDebug(int,int,int)
// print int on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(int i, int importance, int newLine) {
  if (importance <= debug_level) {
    if (newLine == 0) {
      sparki.print(i);
    } 
    else {
      sparki.println(i);
    }

    sparki.updateLCD();
  }
}

// printDebug(int*,int,int,int)
// print int* on the LCD if the importance is less than or equal to debug_level
// prints a newLine if newLine is anything other than 0
void printDebug(int* ints, int importance, int size, int newLine) {
  if (importance <= debug_level) {
    for(int j = 0; j < size; j++) {
      printDebug(ints[j], importance, newLine);

      if (newLine == 0) { // space out multiple figures
        printDebug(', ', importance); 
      }
    }
  }
}
#endif // NO_DEBUGS
/* ***** END OF PRINT DEBUG FUNCTIONS ***** */


/* ***** SPARKI FUNCTIONS ***** */
// gamepad()
// command the robot using the remote
// will run until the robot gets a command over the serial port
void gamepad() { 
#ifndef NO_DEBUGS
  printDebug("In gamepad, ready for input", DEBUG_INFO, 1);
#endif // NO_DEBUGS
  bool keep_going = true;
  
  while (keep_going) {
    int code = sparki.readIR();

#ifndef NO_DEBUGS
    if (code != -1) {
      printDebug("Received code: ", DEBUG_INFO);
      printDebug(code, DEBUG_INFO, 1);
    }
#endif // NO_DEBUGS

// /------^-----\
// |            |
// | 69  70  71 |
// | 68  64  67 |
// |  7  21   9 |
// | 22  25  13 |
// | 12  24  94 |
// |  8  28  90 |
// | 66  82  74 |
// \____________/

// 66 and 82 (7 & 8 buttons) are unused

    switch(code) {
      // Movement buttons
    case 70: // forward button
      motors(100,100); 
#ifndef NO_DEBUGS
      printDebug("Moving forward", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 21: // backward button
      motors(-100,-100); 
#ifndef NO_DEBUGS
      printDebug("Moving backward", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 67: // right button
    case 71: // clockwise button
      motors(100,-100); 
#ifndef NO_DEBUGS
      printDebug("Moving right", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 68: // left button
    case 69: // counter-clockwise button
      motors(-100,100); 
#ifndef NO_DEBUGS
      printDebug("Moving left", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 64: // stop button
      stop();
#ifndef NO_DEBUGS
      printDebug("Stopping", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;

      // Gripper Buttons
    case 9: // <- -> button 
      sparki.gripperOpen(); 
#ifndef NO_DEBUGS
      printDebug("Opening gripper", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 7: // -> <- button 
      sparki.gripperClose(); 
#ifndef NO_DEBUGS
      printDebug("Closing gripper", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;

      // buzzer
    case 74: // 9 button
      sparki.beep(); 
      break;

      // Servo
    case 90: // 6 button
      sparki.servo(SERVO_LEFT); 
#ifndef NO_DEBUGS
      printDebug("Servo left", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 28: // 5 button
      sparki.servo(SERVO_CENTER); 
#ifndef NO_DEBUGS
      printDebug("Servo center", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 8: // 4 button 
      sparki.servo(SERVO_RIGHT); 
#ifndef NO_DEBUGS
      printDebug("Servo right", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;

      // - or +
    case 22: // - button
    case 13: // + button
      keep_going = false;
#ifndef NO_DEBUGS
      printDebug("Ending gamepad", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;

      // RGB LED
    case 25: // 0 button
      sparki.RGB(RGB_OFF); 
#ifndef NO_DEBUGS
      printDebug("RGB off", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 12: // 1 button
      sparki.RGB(RGB_RED); 
#ifndef NO_DEBUGS
      printDebug("RGB red", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 24: // 2 button
      sparki.RGB(RGB_GREEN); 
#ifndef NO_DEBUGS
      printDebug("RGB green", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;
    case 94: // 3 button
      sparki.RGB(RGB_BLUE); 
#ifndef NO_DEBUGS
      printDebug("RGB blue", DEBUG_INFO, 1);
#endif // NO_DEBUGS
      break;

    default:
      break;
    } // end switch
  } // end while
  
  sparki.println("End remote");
  sparki.updateLCD();
} // end gamepad()


#ifndef NO_ACCEL
// void getAccel()
// sends an array with the values of the X, Y, and Z accelerometers
void getAccel() { 
#ifndef NO_DEBUGS
  printDebug("In getAccel, values: ", DEBUG_INFO, 1);
#endif

  sparki.readAccelData(); // it's faster to get the values this way than call them individually
  float values[3] = { 
    -sparki.xAxisAccel*9.8, 
    -sparki.yAxisAccel*9.8, 
    -sparki.zAxisAccel*9.8   };

#ifndef NO_DEBUGS
  printDebug(values, DEBUG_INFO, 3, 0);
  printDebug(' ', DEBUG_INFO, 1);
#endif // NO_DEBUGS
  
  sendSerial( values, 3 );
} // end getAccel()
#endif // NO_ACCEL


// void getLight()
// sends an array with the values of the left, center and right light sensors
void getLight() { 
  int values[3] = { 
    sparki.lightLeft(),
    sparki.lightCenter(),
    sparki.lightRight()   };

#ifndef NO_DEBUGS
  printDebug("In getLight, values are ", DEBUG_INFO, 0);
  printDebug(values, DEBUG_INFO, 3, 0);
  printDebug(' ', DEBUG_INFO, 1);
#endif // NO_DEBUGS
  
  sendSerial( values, 3 );
} // end getLight()


// void getLine()
// sends an array with the values of the left edge, left, center, right, and right edge line sensors
void getLine() { 
  int values[5] = { 
    sparki.edgeLeft(),
    sparki.lineLeft(),
    sparki.lineCenter(),
    sparki.lineRight(),
    sparki.edgeRight()   };

#ifndef NO_DEBUGS
  printDebug("In getLine, values are ", DEBUG_INFO, 0);
  printDebug(values, DEBUG_INFO, 5, 0);
  printDebug(' ', DEBUG_INFO, 1);
#endif // NO_DEBUGS
  
  sendSerial( values, 5 );
} // end getLine()


#ifndef NO_MAG
// void getMag()
// sends an array with the values of the X, Y, and Z magnometers
void getMag() { 
  sparki.readMag(); // it's faster to get the values this way than call them individually
  float values[3] = { 
    sparki.xAxisMag, 
    sparki.yAxisMag, 
    sparki.zAxisMag   };

#ifndef NO_DEBUGS	
  printDebug("In getMag", DEBUG_INFO, 1);
  printDebug(values, DEBUG_INFO, 3, 0);
  printDebug(' ', DEBUG_INFO, 1);
#endif // NO_DEBUGS

  sendSerial( values, 3 );
} // end getMag()
#endif // NO_MAG


// return version to prove communication
void initSparki() {
  sparki.clearLCD();
//  sparki.println("Connected");
  sparki.updateLCD();
	
  sendSerial( (char*)SPARKI_MYRO_VERSION );
} 


#ifndef COMPACT_2
// LCDdrawCircle(int, int, int, int)
// draw a circle with a center at center_x, center_y
// with a radius of radius
// if filled > 0, fill it in
void LCDdrawCircle(int center_x, int center_y, int radius, int filled) {
#ifndef NO_DEBUGS
  printDebug("In LCDdrawCircle, args are: ", DEBUG_DEBUG);
  printDebug(center_x, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(center_y, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(radius, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(filled, DEBUG_DEBUG, 1); 
#endif // NO_DEBUGS

  if (filled > 0) {
    sparki.drawCircleFilled(center_x, center_y, radius);
  } else {
    sparki.drawCircle(center_x, center_y, radius);
  }
} // end LCDdrawCircle(int, int, int, int)


// LCDdrawRect(int, int, int, int, int)
// draw a circle with a corner at corner_x, corner_y
// with a width of width and a height of height
// if filled > 0, fill it in
void LCDdrawRect(int corner_x, int corner_y, int width, int height, int filled) {
#ifndef NO_DEBUGS
  printDebug("In LCDdrawCircle, args are: ", DEBUG_DEBUG);
  printDebug(corner_x, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(corner_y, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(width, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(height, DEBUG_DEBUG); 
  printDebug(", ", DEBUG_DEBUG); 
  printDebug(filled, DEBUG_DEBUG, 1); 
#endif // NO_DEBUGS

  if (filled > 0) {
    sparki.drawRectFilled(corner_x, corner_y, width, height);
  } else {
    sparki.drawRect(corner_x, corner_y, width, height);
  }
} // end LCDdrawRect(int, int, int, int, int)
#endif // COMPACT_2


// LCDdrawString(int, int)
// gets a line number and position, then gets a string from the serial port and prints it
void LCDdrawString(int x, int y) {
  int maxChars = 20;
  char buf[maxChars];
 
  getSerialBytes( buf, maxChars );

  sparki.drawString( x, y, buf);  
} // end LCDdrawString(int, int)


// LCDprint()
// gets data from the serial port and prints it
void LCDprint() {
  int maxChars = 20;
  char buf[maxChars];
  
  getSerialBytes( buf, maxChars );

  sparki.print(buf);  
} // end LCDprint()


// LCDsetColor(int)
// sets the drawing color where the color is a constant defined in Sparki.h
void LCDsetColor(int color) {
  sparki.setPixelColor( color );  // WHITE is defined in Sparki.h
} // end LCDsetColor(int)


#ifdef USE_EEPROM
// void getName()
// sends the robot's name over the serial port
void getName() {
  int buf_size = EEPROM_NAME_MAX_CHARS;
  char buf[buf_size];

  int count = loadFromEEPROM( buf, buf_size, EEPROM_NAME_START );
  
  sendSerial( buf );
}


// loadFromEEPROM(char*, int, int)
// loads data from EEPROM into a buffer (buffer will be overwritten)
// returns the number of characters read
int loadFromEEPROM(char* buf, int size, int start) {
  int count = 0;

  // zero out the buffer
  for( int i = 0; i < size; i++ ) {
    buf[i] = '\0';
  }

  char nextByte = EEPROM.read(start);
  
  while( (count < size - 1) && (nextByte != TERMINATOR)  ) {
    buf[count++] = nextByte;
    nextByte = EEPROM.read(start + count);
  }
  
  return count;
} // loadFromEEPROM(char*, int, int)


// void readFromEEPROM(int, int)
// sends arbitrary data from the EEPROM over the serial port
void readFromEEPROM(int start, int amount) {
  int buf_size = amount + 1;
  char buf[buf_size];

  loadFromEEPROM( buf, buf_size, start );
   
  sendSerial( buf );
}


// void setName()
// sets the robot's name from the argument on the serial port
void setName() {
  writeToEEPROM(EEPROM_NAME_START);
} // end setName()


// writeToEEPROM(int)
// writes data from the serial port to EEPROM beginning at start location
void writeToEEPROM(int start) {
  int buf_size = EEPROM_NAME_MAX_CHARS;
  char buf[buf_size];
  int i = 0;
  int count = getSerialBytes( buf, buf_size );
  
  while(i < count) {
    EEPROM.write( start + i, buf[i] );
    i++;
  }
  
  EEPROM.write( start + i, TERMINATOR );
}
#endif // USE_EEPROM


// motors(int,int,float)
// moves Sparki's left wheel at left_speed and right wheel at right_speed for time
// speed should be a number from 1 to 100 indicating the percentage of power used
// time should be in seconds; if time < 0, move immediately and without stopping
void motors(int left_speed, int right_speed, float time) { 
#ifndef NO_DEBUGS
  printDebug("In motors, time is ", DEBUG_INFO);
  printDebug(time, DEBUG_INFO, 1); // speeds will be printed when motors(int,int) is called
#endif // NO_DEBUGS

  if (time < 0) {
    motors(left_speed, right_speed);
  } 
  else {
    motors(left_speed, right_speed);
    delay(time * 1000);
    stop();
  }
} // end motors(int, int, float)


// motors(int,int)
// moves Sparki's left wheel at left_speed and right wheel at right_speed
// speed should be a number from -100 to 100 indicating the percentage of power used
// if the speed is positive, that indicates forward motion on that wheel
void motors(int left_speed, int right_speed) { 
#ifndef NO_DEBUGS
  printDebug("In motors, moving at left speed ", DEBUG_INFO);
  printDebug(left_speed, DEBUG_INFO);
  printDebug(" and right speed ", DEBUG_INFO);
  printDebug(right_speed, DEBUG_INFO, 1);
#endif // NO_DEBUGS

  if (left_speed >= 0) {
    sparki.motorRotate(MOTOR_LEFT, DIR_CCW, left_speed);
//    sparki.println("left_speed is positive");
  } 
  else if (left_speed < 0) {
    sparki.motorRotate(MOTOR_LEFT, DIR_CW, -left_speed);
//    sparki.println("left_speed is negative");
  }

  if (right_speed >= 0) {
    sparki.motorRotate(MOTOR_RIGHT, DIR_CW, right_speed);
//    sparki.println("right_speed is positive");
  } 
  else if (right_speed < 0) {
    sparki.motorRotate(MOTOR_RIGHT, DIR_CCW, -right_speed);
//    sparki.println("right_speed is negative");
  }
//  sparki.updateLCD();
} // end motors(int,int)


#ifndef NO_DEBUGS
// setDebugLevel(int)
// sets the debug level -- higher numbers result in more verbose output
// -1 will turn off all debugging messages
void setDebugLevel(int level) {
  printDebug("Changing debug level from ", DEBUG_DEBUG);
  printDebug(debug_level, DEBUG_DEBUG);
  printDebug(" to ", DEBUG_DEBUG);
  printDebug(level, DEBUG_DEBUG, 1);

  debug_level = level;
} //setDebugLevel(int)
#endif // NO_DEBUGS


// setStatusLED(int)
// sets the status LED to brightness -- brightness should be between 0 and 100 (as a percentage)
void setStatusLED(int brightness) {
#ifndef NO_DEBUGS
  printDebug("In setStatusLED, brightness is ", DEBUG_DEBUG);
  printDebug(brightness, DEBUG_DEBUG, 1);
#endif // NO_DEBUGS
 
  // if brightness is 0 or 100, we'll use the digital write
  if (brightness <= 0) {
    digitalWrite(STATUS_LED, LOW); // will turn the LED off
    delay(5);
  } else if (brightness >= 100) {
    digitalWrite(STATUS_LED, HIGH); // will turn the LED on
    delay(5);
  } else { // otherwise, we'll use the analog write
    analogWrite(STATUS_LED, brightness * 2.55); // the maximum brightness is 255, so we convert the percentage to that absolute
    delay(5);
  }
} // end setStatusLED(int)


// stop()
// stop the gripper and the movement motor
void stop() {
  sparki.gripperStop();
  sparki.moveStop();
} // end stop()


// turnBy(float)
// turn the robot by deg degress -- positive will turn right and negative will turn left
void turnBy(float deg) {
#ifndef NO_DEBUGS 
  printDebug("In turnBy, deg is ", DEBUG_INFO);
  printDebug(deg, DEBUG_INFO, 1);
#endif // NO_DEBUGS
//  const float SECS_PER_DEGREE = .04;  // estimated from observation - may vary based on battery strength and other factors
  
  if (deg < 0) {
    sparki.moveLeft(-deg);
  } else if (deg > 0) {
    sparki.moveRight(deg);
  } else {
#ifndef NO_DEBUGS
    printDebug("In turnBy, deg is 0", DEBUG_WARN, 1);
#endif // NO_DEBUGS
  }

//  delay(deg * SECS_PER_DEGREE); // delay happens in moveLeft / moveRight
} // end turnBy(int)


// setup - start robot
void setup() {
  setStatusLED(50);
  sparki.clearLCD();
  sparki.print("Version ");
  sparki.println((char*)SPARKI_MYRO_VERSION);
//  sparki.println("Prepare for motion");
  sparki.updateLCD();

  sparki.servo(SERVO_CENTER); // rotate the servo to its 0 degree postion (forward)  


//  sparki.println("Connecting to Bluetooth");
//  sparki.updateLCD();
  serial.begin(9600);
 
  sparki.RGB( 0, 0, 0 );

#ifdef USE_EEPROM
  char name[EEPROM_NAME_MAX_CHARS];
  sparki.print("Hi, I'm ");
  loadFromEEPROM(name, EEPROM_NAME_MAX_CHARS, EEPROM_NAME_START);
  sparki.println(name);
#endif

  sparki.println("Ready");
  sparki.updateLCD();
} // end setup()


// main loop()
void loop() {
#ifdef STATUS_ACK
  setStatusLED(0);                      // turn off the LED
#endif // STATUS_ACK

  if (serial.available()) {
    char inByte = getSerialChar();

#ifdef STATUS_ACK
    setStatusLED(100);                  // turn on the LED while we're processing a command
#endif  // STATUS_ACK

#ifndef NO_DEBUGS
    if (debug_level >= DEBUG_DEBUG) {
      sparki.print("Received character: ");
      sparki.println(inByte);
      sparki.updateLCD();
    }
#endif // NO_DEBUGS

    /* For any and all commands which have multiple arguments, we must first
     * get those arguments and then pass them to the function. It appears that
     * the compiler does not do the getSerial___()'s in the order that they're
     * written, but the reverse of that -- it's unclear if that's this particular
     * version of the compiler, or if it's simply that you're not guaranteed
     * as to the order of calls
     */

    switch (inByte) {
    case COMMAND_BEEP:                // int, int; returns nothing
      {
      int freq = getSerialInt();
      int duration = getSerialInt();
      sparki.beep( freq, duration );
      break;
      }
#ifndef NO_MAG
    case COMMAND_COMPASS:             // no args; returns float
      sendSerial( sparki.compass() );
      break;
#endif // NO_MAG

    case COMMAND_GAMEPAD:             // no args; returns nothing
      gamepad();
      break;

#ifndef NO_ACCEL
    case COMMAND_GET_ACCEL:           // no args; returns array of 3 floats
      getAccel();                     // sendSerial is done in the function
      break;
#endif // NO_ACCEL

/*  removed because it does not produce a reliable result   
	case COMMAND_GET_BATTERY:         // no args; returns float
      // per arcbotics, the systemVoltage() function should not be relied upon
      sendSerial( sparki.systemVoltage() );
      break;
 */
	case COMMAND_GET_LIGHT:           // no args; returns array of 3 ints
      getLight();                     // sendSerial is done in the function
      break;
    case COMMAND_GET_LINE:            // no args; returns array of 5 ints
      getLine();                      // sendSerial is done in the function
      break;

#ifndef NO_MAG
    case COMMAND_GET_MAG:             // no args; returns array of 3 floats
      getMag();                       // sendSerial is done in the function
      break;
#endif // NO_MAG

    case COMMAND_GRIPPER_CLOSE_DIS:   // float; returns nothing
      sparki.gripperClose( getSerialFloat() );
      break;
    case COMMAND_GRIPPER_OPEN_DIS:    // float; returns nothing
      sparki.gripperOpen( getSerialFloat() );
      break;
    case COMMAND_GRIPPER_STOP:        // no args; returns nothing
      sparki.gripperStop();
      break;
    case COMMAND_INIT:                // no args; returns a char
      initSparki();                   // sendSerial is done in the function
      break;
    case COMMAND_LCD_CLEAR:           // no args; returns nothing
      sparki.clearLCD();
      break;

#ifndef COMPACT_2
    case COMMAND_LCD_DRAW_CIRCLE:     // int, int, int, int; returns nothing
      {
      int center_x = getSerialInt();
      int center_y = getSerialInt();
      int radius = getSerialInt();
      int filled = getSerialInt();
      LCDdrawCircle( center_x, center_y, radius, filled );
      break;
      }
    case COMMAND_LCD_DRAW_RECT:       // int, int, int, int, int; returns nothing
      {
      int corner_x = getSerialInt();
      int corner_y = getSerialInt();
      int width = getSerialInt();
      int height = getSerialInt();
      int filled = getSerialInt();
      LCDdrawRect( corner_x, corner_y, width, height, filled );
      break;
      }
#endif // COMPACT_2

    case COMMAND_LCD_DRAW_PIXEL:      // int, int; returns nothing
      {
      int x = getSerialInt();
      int y = getSerialInt();
      sparki.drawPixel( x, y );
      break;
      }
/*  LCD_DRAW_LINE removed due to errors in the underlying command  
	case COMMAND_LCD_DRAW_LINE:       // int, int, int, int; returns nothing
      {
      int x1 = getSerialInt();
      int y1 = getSerialInt();
      int x2 = getSerialInt();
      int y2 = getSerialInt();
      sparki.drawLine( x1, y1, x2, y2 );
      break;
      }
 */    
	case COMMAND_LCD_DRAW_STRING:     // int, int, char*; returns nothing
      {
      int x = getSerialInt();
      int y = getSerialInt();
      LCDdrawString( x, y );
      break;
      }
    case COMMAND_LCD_SET_COLOR:      // int; returns nothing
      LCDsetColor( getSerialInt() );
      break;
    case COMMAND_LCD_PRINT:           // char*; returns nothing
      LCDprint();					  // gets char* in function
      break;
    case COMMAND_LCD_PRINTLN:         // char*; returns nothing
      LCDprint();					  // gets char* in function
      sparki.println(' ');
      break;
    case COMMAND_LCD_READ_PIXEL:      // int, int; returns nothing
      {
      int x = getSerialInt();
      int y = getSerialInt();
      sendSerial( sparki.readPixel( x, y ) );
      break;
      }
    case COMMAND_LCD_UPDATE:          // no args; returns nothing
      sparki.updateLCD();
      break;
    case COMMAND_MOTORS:              // int, int, float; returns nothing
      { 
      int left_speed = getSerialInt();
      int right_speed = getSerialInt();
      float time_length = getSerialFloat();     
      motors( left_speed, right_speed, time_length );
      break;
      } // end COMMAND_MOTORS
    case COMMAND_BACKWARD_CM:         // float; returns nothing
      sparki.moveBackward( getSerialFloat() );
      break;
    case COMMAND_FORWARD_CM:          // float; returns nothing
      sparki.moveForward( getSerialFloat() );
      break;
    case COMMAND_PING:                // no args; returns int
      sendSerial( sparki.ping() );
      break;
    case COMMAND_RECEIVE_IR:          // no args; returns int
      sendSerial( sparki.readIR() );
      break;
    case COMMAND_SEND_IR:             // int; returns nothing
      sparki.sendIR( getSerialInt() );
      break;
    case COMMAND_SERVO:               // int; returns nothing
      sparki.servo( getSerialInt() );
      break;
      
#ifndef NO_DEBUGS
    case COMMAND_SET_DEBUG_LEVEL:     // int; returns nothing
      setDebugLevel( getSerialInt() );
      break;
#endif // NO_DEBUGS

    case COMMAND_SET_RGB_LED:         // int, int, int; returns nothing
      {
	    /* arcbotics states that underlying hardware limitations can cause colors not to appear as intended
	       specifically, the LEDs draw different voltages, red more than green and green more than blue
	       as a side effect, if you have a situation where red == green == blue, only red will show */
		 
	    /* arcbotics recommends the following values for the specified colors:
         blue   0,   0,   100
         green  0,   100, 0
         indigo 20,  0,   100
         orange 90,  100, 0
         pink   90,  0,   100
         red    100, 0,   0
         violet 60,  0,   100
         white  60,  100, 90
         yellow 60,  100, 0
         off    0,   0,   0 */

      int red = getSerialInt();
      int green = getSerialInt();
      int blue = getSerialInt();
      sparki.RGB( red, green, blue );
      break;
      }
    case COMMAND_SET_STATUS_LED:      // int; returns nothing
      setStatusLED( getSerialInt() );
      break;
    case COMMAND_STOP:                // no args; returns nothing
      stop();
      break;
    case COMMAND_TURN_BY:             // float; returns nothing
      turnBy( getSerialFloat() );
      break;

#ifdef USE_EEPROM
    case COMMAND_GET_NAME:            // no args; returns char*
      getName();                      // sendSerial is done in the function
      break;
    case COMMAND_SET_NAME:            // char*; returns nothing
      setName();					  // gets char* in function
      break;
    case COMMAND_EEPROM_READ:         // int, int; returns char*
      {
      int location = getSerialInt();
      int size = getSerialInt();
      readFromEEPROM( location, size ); // sendSerial is done in the function
      break;
      }
    case COMMAND_EEPROM_WRITE:        // int, char*; returns nothing
      writeToEEPROM( getSerialInt() );// gets char* in function
      break;
#endif // USE_EEPROM

#ifndef COMPACT_2
    case COMMAND_VERSION:             // no args; returns char*
      sendSerial( (char*)SPARKI_MYRO_VERSION );
      break;
#endif // COMPACT_2

    case COMMAND_NOOP:             // no args; returns nothing; does nothing
      // can be used to prevent a timeout in communication with the robot
      break;

    default:
      sparki.print("Bad input");
      sparki.updateLCD();
      stop();
      sparki.beep();
      serial.print(TERMINATOR); 
      break;
    } // end switch ((char)inByte)
  } // end if (serial.available())
  
  sendSync();    // we send the sync every time rather than a more complex handshake to save space in the program
} // end loop()
/* ########### END OF FUNCTIONS ########### */

