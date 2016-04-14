/* ***** Sparki_Myro draw_pixel_test ***** */
/* created by Jeremy Eglen */
   
/* Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
   remain property of their respective owners */

/* This utility program tests different functions drawing on the LCD of the Sparki */

/* initial creation - April 14, 2016 
   last modified - April 14, 2016 */

#include <Sparki.h>

/* most recent version developed in Sparkiduino 1.6.8.2 -- there do appear to be differences in compiled progam size 
 * among different versions of Sparkiduino
*/

// for simplicity of installation, we're keeping the constants and prototypes in the cpp file
#ifndef Sparki_Myro_h
#define Sparki_Myro_h

#include <Sparki.h>

/* ########### CONSTANTS ########### */
/* ***** VERSION NUMBER ***** */
const char* SPARKI_MYRO_VERSION = "DEBUG-LCD"; 

/* ***** MESSAGE TERMINATOR ***** */
const char TERMINATOR = (char)23;      // this terminates every transmission from python

/* ***** ACTION TERMINATOR ***** */
const char SYNC = (char)22;            // send this when in the command loop waiting for instructions


/* ***** LOW BATTERY VOLTAGE ***** */
const float LOW_BATTERY = 4.0;         // 6.0 should be a full power battery


/* ***** COMMAND CHARACTER CODES ***** */
/* Sparki Myro works by listening on the serial port for a command from the computer in the loop() function
 * The loop() function is primarily a massive switch statement that gets a COMMAND code and executes the proper
 * funtion on Sparki. This is the list of COMMAND codes -- the Python library calling Sparki will need this list
 * to be identical.
 */
const char COMMAND_INIT = 'z';          // no arguments; confirms communication between computer and robot
const char COMMAND_LCD_CLEAR = '0';     // no arguments; returns nothing

#ifndef COMPACT_2
const char COMMAND_LCD_DRAW_CIRCLE = '1';   // requires 4 arguments: int x&y, int radius, and int filled (1 is filled); returns nothing
const char COMMAND_LCD_DRAW_RECT = '4'; // requires 5 arguments: int x&y for start point, ints width & height, and int filled (1 is filled); returns nothing 
#endif // COMPACT_2

const char COMMAND_LCD_DRAW_LINE = '2'; // requires 4 arguments ints x&y for start point and x1&y1 for end points; returns nothing
const char COMMAND_LCD_DRAW_PIXEL = '3';    // requires 2 arguments: int x&y; returns nothing
const char COMMAND_LCD_DRAW_STRING = '5';   // requires 3 arguments: int x (column), int line_number, and char* string; returns nothing
const char COMMAND_LCD_PRINT = '6';     // requires 1 argument: char* string; returns nothing
const char COMMAND_LCD_PRINTLN = '7';   // requires 1 argument: char* string; returns nothing
const char COMMAND_LCD_READ_PIXEL = '8';    // requires 2 arguments: int x&y; returns int color of pixel at that point
const char COMMAND_LCD_SET_COLOR = 'T'; // requires 1 argument: int color; returns nothing
const char COMMAND_LCD_UPDATE = '9';    // no arguments; returns nothing

#ifndef NO_DEBUGS
const char COMMAND_SET_DEBUG_LEVEL = 'H';   // requires 1 argument: int debug level (0-5); returns nothing
#endif // NO_DEBUGS
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

void sendSerial(char c);
void sendSerial(char* message);
void sendSerial(float f);
void sendSerial(float* floats, int size);
void sendSerial(int i);
void sendSerial(int* ints, int size);


/* ***** SPARKI COMMANDS ***** */
/* These functions can be called by the computer */
void initSparki();  // confirms communication with Python

// LCD functions are generally handled via direct calls
#ifndef COMPACT_2
void LCDdrawCircle(int center_x, int center_y, int radius, int filled);
void LCDdrawRect(int corner_x, int corner_y, int width, int height, int filled);
#endif // COMPACT_2

void LCDdrawString(int x, int y);
void LCDprint();
void LCDsetColor(int color);
void setDebugLevel(int level);
void setStatusLED(int brightness);
/* ########## END OF FUNCTION PROTOTYPES ########### */
#endif // Sparki_Myro_h

/* ########### GLOBALS ########### */
#ifndef NO_DEBUGS
int debug_level = DEBUG_INFO;
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


// setup - start robot
void setup() {
  setStatusLED(50);
  sparki.clearLCD();
  sparki.print("Version ");
  sparki.println((char*)SPARKI_MYRO_VERSION);
//  sparki.println("Prepare for motion");
  sparki.updateLCD();

  sparki.servo(SERVO_CENTER); // rotate the servo to its 0 degree postion (forward)  

  printDebug("Drawing pixels at 5,10 - 5,11 - 6,10, then erasing", DEBUG_INFO, 1);

  delay(5000);
  
  sparki.clearLCD();
  sparki.updateLCD();
  
  sparki.drawPixel( 5, 10 );
  sparki.updateLCD();
  delay(500);
  sparki.drawPixel( 5, 11 );
  sparki.updateLCD();
  delay(500);
  sparki.drawPixel( 6, 10 );
  sparki.updateLCD();

  delay(5000);

  LCDsetColor( 1 );
  sparki.drawPixel( 5, 10 );
  sparki.updateLCD();
  delay(500);
  sparki.drawPixel( 5, 11 );
  sparki.updateLCD();
  delay(500);
  sparki.drawPixel( 6, 10 );
  sparki.updateLCD();
  
  delay(5000);

  LCDsetColor(0);
  printDebug("Drawing many pixels at 20,20, then erasing", DEBUG_INFO, 1);

  delay(5000);
  
  sparki.clearLCD();
  sparki.updateLCD();
  
  for( int i = 0; i < 20; i++ ) {
    sparki.drawPixel( 20, 20 );
    sparki.updateLCD();
    delay(500);
  }

  delay(5000);
  
  LCDsetColor(1);
  
  for( int i = 20; i > 0; i-- ) {
    sparki.drawPixel( 20, 20 );
    sparki.updateLCD();
    delay(500);
  }

  delay(5000);

  LCDsetColor(0);

  serial.begin(9600);

  sparki.println("Ready");
  sparki.updateLCD();
} // end setup()


// main loop()
void loop() {
  setStatusLED(0);                      // turn off the LED
  if (serial.available()) {
    char inByte = getSerialChar();
    setStatusLED(100);                  // turn on the LED while we're processing a command

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
    case COMMAND_LCD_DRAW_LINE:       // int, int, int, int; returns nothing
      {
      int x1 = getSerialInt();
      int y1 = getSerialInt();
      int x2 = getSerialInt();
      int y2 = getSerialInt();
      sparki.drawLine( x1, y1, x2, y2 );
      break;
      }
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
#ifndef NO_DEBUGS
    case COMMAND_SET_DEBUG_LEVEL:     // int; returns nothing
      setDebugLevel( getSerialInt() );
      break;
#endif // NO_DEBUGS

    default:
      sparki.print("Bad input");
      sparki.updateLCD();
      sparki.beep();
      serial.print(TERMINATOR); 
      break;
    } // end switch ((char)inByte)
  } // end if (serial.available())
  
  sendSync();    // we send the sync every time rather than a more complex handshake to save space in the program
} // end loop()
/* ########### END OF FUNCTIONS ########### */

