This project implements libraries for the Sparki robot <http://arcbotics.com/products/sparki/> to work through Python over a Bluetooth connection. It is intended to help educators who are teaching using the Sparki and/or Python.

Conceptually, the library which is loaded on the robot is simply an interpreter for commands the Sparki receives over its Serial1 (Bluetooth) port. You could implement a complementary library on any platform that you like to send the commands. In this case, I have implemented a library in Python which makes use of the pyserial library to send those commands. The library on the Sparki does not implement all the commands available on the Sparki. Specifically, there are several LCD commands which I have been unable to fit into the Sparki's memory. As of version 1.0.0 of the Sparki library, it consumes 28,650 bytes of the 28,672 bytes available on the little robot. Perhaps programmers more skilled than I can fit more on there. 

The Python part of the library implements much of the IPRE (Institute for Personal Robotics in Education <http://www.roboteducation.org/>) Myro API (API reference at <http://calicoproject.org/Calico_Myro>). This API was originally chosen because the original author of this project taught (or teaches, depending on when you read this) a class making use of that program. A free textbook exists to teach that program may be found at <http://calicoproject.org/Learning_Computing_With_Robots_Using_Calico_Python>. The Python library here does not implement all of that library -- in particular, anything having to do with the camera cannot be implemented on Sparki because Sparki does not have that hardware. 

To make use of this library with your Sparki:
1. Download the latest version of Sparkiduino from Arcbotics: <http://arcbotics.com/products/sparki/start/>
2. Make a copy (through git clone or otherwise) on your computer of the sparki_myro.ino file -- it has to be in its own directory called sparki_myro
3. Load the sparki_myro.ino file in Sparkiduino and upload it to your Sparki
4. You're done! At least, you're done with the part that concerns your Sparki. The library on its own won't do much unless you've got a way to talk to it.

To talk to the library using Python:
1. Download a version of Python 3 -- this was developed on Python 3.4, but the author believes any version of Python 3 will work <https://www.python.org/downloads/>. The author has also successfully used Python 2.7, though it is not as thoroughly tested.
2. Use pypi or easy_install to install the library. It should download everything for you automagically. 
3. Use the sparki_myro.py library to control your Sparki!

All of the software in this project is provided under the Apache version 2 license available at <http://www.apache.org/licenses/LICENSE-2.0> and is WITHOUT WARRANTY, including implied warranties. I have also included a couple of sample / test programs for you to look at in python to get a feel for how to use the library. 

Both libraries were written with the intention of being helpful to students and educators, and are fairly well commented. I have tested them some, but they may not work on all platforms for all people. There may be bugs. There may be problems that cause the destruction of your Sparki (though I don't think there are). You assume all risk in your use of this software.

Finally, I have included an increasingly long "Quick Reference" sheet that documents the libraries. 

Sparki is an excellent little robot, and I hope this proves useful to you in exploring the world. Good luck!