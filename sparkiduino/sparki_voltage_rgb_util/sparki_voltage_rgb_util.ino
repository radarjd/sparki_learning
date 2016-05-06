/* ****** sparki voltage & RGB test ****** */

#include <Sparki.h>

void setup() {
  sparki.clearLCD();
  sparki.updateLCD();
  sparki.servo(SERVO_CENTER); // rotate the servo to its 0 degree postion (forward)  

  float battery_level = sparki.systemVoltage();
  sparki.print("Starting voltage: ");
  sparki.println(battery_level);
  sparki.updateLCD();
  
  sparki.RGB( 0, 0, 0 );
}

void loop() {
  float battery_level = sparki.systemVoltage();
  sparki.print("Current voltage: ");
  sparki.println(battery_level);
  sparki.updateLCD();

  for( int b = 1; b <= 100; b++ ) {
    sparki.RGB( b, b, b );
    delay(100);
  }

  delay(2000);
}
