# Sparki_Myro testing
from sparki_myro import *
import sparki_myro

result = ask("What is your name? ")
print("The user said " + result)

result = yesorno("Click yes or no")
print("The user said " + result)

result = askQuestion_text("Type a shape ", [ 'square', 'circle' ], False)
print("The user said " + result)

result = pickAFile()
print("The user said " + result)

init("COM4")        # change for your COM port (or /dev/)
senses()

senses_text()

joystick()
