/* ***** Sparki_Myro motor function test ***** */
/* created by Jeremy Eglen */

/* Test for the motors() command on Sparki and with python */

/* includes a minimal implementation of the Sparki Myro library */

/* initial creation - January 24, 2016 
   last modified - April 5, 2016 */

#include <Sparki.h>

/* ########### CONSTANTS ########### */
/* ***** VERSION NUMBER ***** */
const char* SPARKI_MYRO_VERSION = "DEBUG";    // debugs on; mag off, accel off, EEPROM off; compact 2 off

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
const char COMMAND_INIT = 'z';          // no arguments; confirms communication between computer and robot
const char COMMAND_MOTORS = 'A';        // requires 3 arguments: int left_speed (1-100), int right_speed (1-100), & float time
                                        // if time < 0, motors will begin immediately and will not stop; returns nothing
const char COMMAND_SET_DEBUG_LEVEL = 'H';   // requires 1 argument: int debug level (0-5); returns nothing
const char COMMAND_STOP = 'K';          // no arguments; returns nothing


/* ***** DEBUG CONSTANTS ***** */
const int DEBUG_DEBUG = 5;
const int DEBUG_INFO = 4;
const int DEBUG_WARN = 3;
const int DEBUG_ERROR = 2;
const int DEBUG_CRITICAL = 1;
const int DEBUG_ALWAYS = 0;


/* ***** SERIAL PORT FOR BLUETOOTH ***** */
#define serial Serial1


/* ########## FUNCTION PROTOTYPES ########### */
/* ***** SPARKI UTILITY FUNCTIONS ***** */
/* These functions are used internally, and are not called by the computer */
char getSerialChar();  // gets a char from the serial port; BLOCKING
float getSerialFloat();  // gets a float from the serial port; BLOCKING
int getSerialInt();  // gets an int from the serial port; BLOCKING

int getSerialBytes(char* buf, int size); // gets bytes from the serial port; BLOCKING

void motors(int left_speed, int right_speed);  // starts the motors at the speed indicated

void printDebug(char* message, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(char c, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(float f, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(float* floats, int importance, int size, int newLine = 0);  // prints debug messages to LCD
void printDebug(int i, int importance, int newLine = 0);  // prints debug messages to LCD
void printDebug(int* ints, int importance, int size, int newLine = 0);  // prints debug messages to LCD


/* ***** SPARKI COMMANDS ***** */
/* These functions can be called by the computer */
void initSparki();  // confirms communication with Python
void motors(int left_speed, int right_speed, float time);
void setDebugLevel(int level);
void setStatusLED(int brightness);
void stop();

int debug_level = DEBUG_INFO;

/* ########### FUNCTIONS ########### */
/* ***** SERIAL FUNCTIONS ***** */
// gets a char from the serial port
// blocks until one is available
char getSerialChar() {
  int size = 30;
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
  int size = 30;
  char buf[size];
  int result = getSerialBytes(buf, size);
  return atof( buf );
}

// gets an int from the serial port
// blocks until one is available
// ints are sent to Sparki as char* in order to eliminate conversion issues
// we then convert the string to an int and return that
int getSerialInt() {
  int size = 30;
  char buf[size];
  int result = getSerialBytes(buf, size);
  return atoi( buf );
}

// gets bytes from the serial port
// the byte stream should be terminated by TERMINATOR
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

      printDebug(inByte, DEBUG_DEBUG);
      printDebug(' ', DEBUG_DEBUG);
   
      if ((inByte != TERMINATOR) && (inByte >= 0)) {
        buf[count++] = (char)inByte;
      }
    }
  }

  return count;
}


/* These functions send data from Sparki to the computer over Bluetooth */
void sendSerial(char c) {
  printDebug("Sending char over Bluetooth: ", DEBUG_DEBUG);
  printDebug(c, DEBUG_DEBUG, 1);

  serial.print(c); 
  serial.print(TERMINATOR); 
}

void sendSerial(char* message) {
  printDebug("Sending message over Bluetooth: ", DEBUG_DEBUG);
  printDebug(message, DEBUG_DEBUG, 1);
  
  serial.print(message); 
  serial.print(TERMINATOR); 
}

void sendSerial(float f) {
  printDebug("Sending float over Bluetooth: ", DEBUG_DEBUG);
  printDebug(f, DEBUG_DEBUG, 1);
  
  serial.print(f); 
  serial.print(TERMINATOR); 
}

void sendSerial(float* floats, int size) {
  for(int j = 0; j < size; j++) {  
    sendSerial(floats[j]);
  }
}

void sendSerial(int i) {
  printDebug("Sending int over Bluetooth: ", DEBUG_DEBUG);
  printDebug(i, DEBUG_DEBUG, 1);
  
  serial.print(i); 
  serial.print(TERMINATOR); 
}

void sendSerial(int* ints, int size) {
  for(int j = 0; j < size; j++) {  
    sendSerial(ints[j]);
  }
}

void sendSync() {
//  printDebug("Sending SYNC", DEBUG_DEBUG);
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


// return version to prove communication
void initSparki() {
  sparki.clearLCD();
  sparki.println("Connected");
  sparki.updateLCD();
	
  sendSerial( (char*)SPARKI_MYRO_VERSION );
} 

// motors(int,int,float)
// moves Sparki's left wheel at left_speed and right wheel at right_speed for time
// speed should be a number from 1 to 100 indicating the percentage of power used
// time should be in seconds; if time < 0, move immediately and without stopping
void motors(int left_speed, int right_speed, float time) { 
  printDebug("In motors, time is ", DEBUG_INFO);
  printDebug(time, DEBUG_INFO, 1); // speeds will be printed when motors(int,int) is called

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
// speed should be a number from 1 to 100 indicating the percentage of power used
// if the speed is positive, that indicates forward motion on that wheel
void motors(int left_speed, int right_speed) { 
  printDebug("In motors, left speed ", DEBUG_INFO);
  printDebug(left_speed, DEBUG_INFO);
  printDebug(" and right speed ", DEBUG_INFO);
  printDebug(right_speed, DEBUG_INFO, 1);

  if (left_speed > 0) {
    sparki.motorRotate(MOTOR_LEFT, DIR_CCW, left_speed);
//    sparki.println("left_speed is positive");
  } 
  else if (left_speed < 0) {
    sparki.motorRotate(MOTOR_LEFT, DIR_CW, -left_speed);
//    sparki.println("left_speed is negative");
  }

  if (right_speed > 0) {
    sparki.motorRotate(MOTOR_RIGHT, DIR_CW, right_speed);
//    sparki.println("right_speed is positive");
  } 
  else if (right_speed < 0) {
    sparki.motorRotate(MOTOR_RIGHT, DIR_CCW, -right_speed);
//    sparki.println("right_speed is negative");
  }
//  sparki.updateLCD();
} // end motors(int,int)


// setDebugLevel(int)
// sets the debug level -- higher numbers result in more verbose output
// -1 will turn off all debugging messages
void setDebugLevel(int level) {
  printDebug("Changing debug level", DEBUG_INFO);

  debug_level = level;
} //setDebugLevel(int)


// setStatusLED(int)
// sets the status LED to brightness -- brightness should be between 0 and 100 (as a percentage)
void setStatusLED(int brightness) {
//  printDebug("In setStatusLED, brightness is ", DEBUG_DEBUG);
//  printDebug(brightness, DEBUG_DEBUG, 1);
 
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


// setup - start robot
void setup() {
  sparki.clearLCD();
  sparki.print("Sparki Myro Version ");
  sparki.println((char*)SPARKI_MYRO_VERSION);
  sparki.updateLCD();

//  sparki.println("Connecting to Bluetooth");
  sparki.updateLCD();
  serial.begin(9600);

//  sparki.println("Robot initialization successful");
  sparki.updateLCD();
  
//  printDebug("Using motors to move forward for 1 second", DEBUG_INFO, 1);
//  delay(2000);
  motors(100, 100, 1.0);

//  printDebug("Using motors to move backward for 1 second", DEBUG_INFO, 1);
//  delay(2000);
  motors(-100, -100, 1.0);
 
//  printDebug("Using motors to turn right for 1 second", DEBUG_INFO, 1);
//  delay(2000);
  motors(100, -100, 1.0);

//  printDebug("Using motors to turn left for 1 second", DEBUG_INFO, 1);
//  delay(2000);
  motors(-100, 100, 1.0);
 
  printDebug("Now try giving commands over Bluetooth", DEBUG_INFO, 1);
} // end setup()


// main loop()
void loop() {
  setStatusLED(0);                      // turn off the LED
  if (serial.available()) {
    char inByte = getSerialChar();
    setStatusLED(100);                  // turn on the LED while we're processing a command

    if (debug_level >= DEBUG_DEBUG) {
      sparki.print("Received character: ");
      sparki.println(inByte);
      sparki.updateLCD();
    }

    switch (inByte) {
    case COMMAND_INIT:                // no args; returns a char
      initSparki();                   // sendSerial is done in the function
      break;

    case COMMAND_MOTORS:              // int, int, int; returns nothing
      motors( getSerialInt(), getSerialInt(), getSerialInt() );
      break;
      
    case COMMAND_SET_DEBUG_LEVEL:     // int; returns nothing
      setDebugLevel( getSerialInt() );
      break;

    case COMMAND_STOP:                // no args; returns nothing
      stop();
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

