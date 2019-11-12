from sparki_learning import *
init("com3")

print("---- This is a test of the new utility library ----")

print("* Move in an arc for 5 seconds *")
for _ in timer(5):
    motors(1, -.5)
stop()

print("* Draw two lines on the LCD *")
LCDdrawLine(5, 5, 6, 15)
LCDdrawLine(6, 15, 20, 5)

print("* Read the bluetooth address and rewrite it *")
bluetooth_address = bluetoothRead()
print("The bluetooth_address is {}".format(bluetooth_address))
if bluetoothValidate(bluetooth_address):
    print("It is a valid address")
else:
    print("It is not a valid address")

print("* Test angle wrapping and flrange *")
for a in flrange(350, 370, .5):
    print("{} wrapped is {}".format(a, wrapAngle(a)))
    
for a in flrange(-350, -370, -.5):
    print("{} wrapped is {}".format(a, wrapAngle(a)))
