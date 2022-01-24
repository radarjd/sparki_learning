/* ***** Sparki_Myro set_name ***** */
/* created by Jeremy Eglen */
   
/* Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
   remain property of their respective owners */

/* This utility program sets the name of the Sparki */

/* initial creation - January 21, 2016 
   last modified - September 21, 2021 */

#include <Sparki.h>
#include "SparkiEEPROM.h"

int loadName(char* buf, int size);                // loads the robot's name into buffer
void printDebug(char* message, int newLine = 0);  // prints debug messages to LCD
void printDebug(char c, int newLine = 0);
void printDebug(int i, int newLine = 0);  
void setName(char* newName);                      // sets the robot's name

const int EEPROM_NAME_START = 20;          // byte location of the start of the name
const char* DEFAULT_NAME = "My Sparki";    // the default name 
const char TERMINATOR = (char)23;          // this terminates every transmission from python


// loadName(char*, int)
// load the robot's name into a buffer
// returns the number of characters read
// note that the name must be set at least once to get usable data
int loadName(char* buf, int size) {
  // zero out the buffer
  for( int j = 0; j < size; j++ ) {
    buf[j] = '\0';
  }

  int count = 0;
  printDebug("Inside loadName(), reading bytes", 1);

  char nextByte = EEPROM.read(EEPROM_NAME_START);
  
  printDebug(nextByte, 0);
  
  while( (count < size) && (nextByte != TERMINATOR) && (count < 20) ) {
    buf[count++] = nextByte;
    nextByte = EEPROM.read(EEPROM_NAME_START + count);
    printDebug(nextByte, 0);
  }
  
  printDebug(" ", 1);
  printDebug("Done reading: ", 0);
  printDebug(buf, 1);
  printDebug("Count is ", 0);
  printDebug(count, 1);
  
  return count;
} // loadName(char*, int)


// printDebug(char*,int)
// print char* on the LCD 
// prints a newLine if newLine is anything other than 0
void printDebug(char* message, int newLine) {
    if (newLine == 0) {
      sparki.print(message);
    } 
    else {
      sparki.println(message);
    }

    sparki.updateLCD();
} // printDebug(char*,int)

// printDebug(char,int)
// print char on the LCD 
// prints a newLine if newLine is anything other than 0
void printDebug(char c, int newLine) {
    if (newLine == 0) {
      sparki.print(c);
    } 
    else {
      sparki.println(c);
    }

    sparki.updateLCD();
}

// printDebug(int,int)
// print int on the LCD 
// prints a newLine if newLine is anything other than 0
void printDebug(int i, int newLine) {
    if (newLine == 0) {
      sparki.print(i);
    } 
    else {
      sparki.println(i);
    }

    sparki.updateLCD();
}


// void setName(char*)
// sets the robot's name to the argument
void setName(char* newName) {
  int name_length = strlen(newName);
  int i = 0;
  
  printDebug("Inside setName(), new name is ", 0);
  printDebug(newName, 1);
  
  printDebug("Writing... ", 1);
  while(i < name_length) {
    EEPROM.write( EEPROM_NAME_START + i, newName[i] );
    printDebug(newName[i], 0);
    i++;
  }
  
  printDebug(" ", 1);
  EEPROM.write( EEPROM_NAME_START + i, TERMINATOR );
  printDebug("Wrote ", 0);
  printDebug(i, 0);
  printDebug(" characters", 1);
} // end setName(char*)


// setup - start robot
void setup() {
  sparki.clearLCD();

  printDebug("Setting robot's name to ", 0);
  printDebug((char*)DEFAULT_NAME, 1);
  
  setName((char*)DEFAULT_NAME);
  
  delay(10000);
  
  int max_length = 20;
  char name[max_length];
  loadName(name, max_length);
  delay(10000);
  
  printDebug("Hi, my name is ", 0);
  printDebug(name, 1);
  printDebug("Done!", 1);
} // end setup()


void loop() {
  // do nothing...
  static int count = 0;
  printDebug(".");

  if (count % 3 == 0) {
    sparki.RGB( 100, 0, 0 );
  } else if (count % 3 == 1) {
    sparki.RGB( 0, 100, 0 );
  } else {
    sparki.RGB( 0, 0, 100 );
  }

  count++;
  delay(1000);
}
