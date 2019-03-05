/* ***** Sparki_Myro ping function test ***** */
/* created by Jeremy Eglen */

/* sketch to attempt to "reset" a stuck ultrasonic sensor */

/* initial creation - March 3, 2019 
   last modified -  */

#include <Arduino.h> 
#include <Sparki.h> // for the constants

/******************************* implementation of ping() from Sparki.cpp 
int SparkiClass::ping_single(){
  long duration; 
  float cm;
  digitalWrite(ULTRASONIC_TRIG, LOW); 
  delayMicroseconds(2); 
  digitalWrite(ULTRASONIC_TRIG, HIGH); 
  delayMicroseconds(10); 
  digitalWrite(ULTRASONIC_TRIG, LOW); 
  

  uint8_t bit = digitalPinToBitMask(ULTRASONIC_ECHO);
  uint8_t port = digitalPinToPort(ULTRASONIC_ECHO);
  uint8_t stateMask = (HIGH ? bit : 0);
  
  unsigned long startCount = 0;
  unsigned long endCount = 0;
  unsigned long width = 0; // keep initialization out of time critical area
  
  // convert the timeout from microseconds to a number of times through
  // the initial loop; it takes 16 clock cycles per iteration.
  unsigned long numloops = 0;
  unsigned long maxloops = 5000;
  
  // wait for any previous pulse to end
  while ((*portInputRegister(port) & bit) == stateMask)
    if (numloops++ == maxloops)
      return -1;
  
  // wait for the pulse to start
  while ((*portInputRegister(port) & bit) != stateMask)
    if (numloops++ == maxloops)
      return -1;
  
  startCount = micros();
  // wait for the pulse to stop
  while ((*portInputRegister(port) & bit) == stateMask) {
    if (numloops++ == maxloops)
      return -1;
    delayMicroseconds(10); //loop 'jams' without this
    if((micros() - startCount) > 58000 ){ // 58000 = 1000CM
      return -1;
      break;
    }
  }
  duration = micros() - startCount;
  //--------- end pulsein
  cm = (float)duration / 29.0 / 2.0; 
  return int(cm);
}

int SparkiClass::ping(){
  int attempts = 5;
  float distances [attempts];
  for(int i=0; i<attempts; i++){
    distances[i] = ping_single();
    delay(20);
  }
  
  // sort them in order
  int i, j;
  float temp;
 
  for (i = (attempts - 1); i > 0; i--)
  {
    for (j = 1; j <= i; j++)
    {
      if (distances[j-1] > distances[j])
      {
        temp = distances[j-1];
        distances[j-1] = distances[j];
        distances[j] = temp;
      }
    }
  }
  
  // return the middle entry
  return int(distances[(int)ceil((float)attempts/2.0)]); 
}
*******************************/

// getDistance function from http://therandomlab.blogspot.com/2015/05/repair-and-solve-faulty-hc-sr04.html
int getDistance() // returns the distance (cm)
{
  long duration, distance;

  digitalWrite(ULTRASONIC_TRIG, HIGH); // We send a 10us pulse
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);

  duration = pulseIn(ULTRASONIC_ECHO, HIGH, 20000); // We wait for the echo to come back, with a timeout of 20ms, which corresponds approximately to 3m

  // pulseIn will only return 0 if it timed out. (or if ULTRASONIC_ECHO was already to 1, but it should not happen)
  if (duration == 0) // If we timed out
  {
    pinMode(ULTRASONIC_ECHO, OUTPUT); // Then we set echo pin to output mode
    digitalWrite(ULTRASONIC_ECHO, LOW); // We send a LOW pulse to the echo pin
    delayMicroseconds(200);
    pinMode(ULTRASONIC_ECHO, INPUT); // And finaly we come back to input mode
  }

  distance = (duration / 2) / 29.1; // We calculate the distance (sound speed in air is aprox. 291m/s), /2 because of the pulse going and coming

  return distance; //We return the result. Here you can find a 0 if we timed out
}


void setup() {
  sparki.clearLCD();
  sparki.println("Sparki Ping Reset Util");
  sparki.println("Ping in setup()");  
  sparki.updateLCD();

  for( int i = 0; i < 5; i++ ) {
    sparki.print("Ping: ");
    sparki.println(sparki.ping());
    sparki.updateLCD();
    delay(1000);
  }
}

void loop() {
  const int loop_repeats = 4;
  
  sparki.println("Starting main loop");
  sparki.println("delaying 5 seconds...");
  sparki.updateLCD();
  delay(5000);

  for( int i = 0; i < loop_repeats; i++ ) {
    sparki.print("Ping: ");
    sparki.println(sparki.ping());
    sparki.updateLCD();
    delay(1000);
  }

  for( int i = 0; i < loop_repeats; i++ ) {
    sparki.print("getdistance(): ");
    sparki.println(getDistance());
    sparki.updateLCD();
    delay(1000);
  }
}
