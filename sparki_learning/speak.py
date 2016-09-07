# speak input over the computer
#
# Created: May 18, 2016 by Jeremy Eglen with assistance from Kelly Schmidt for the Mac function
# Last Modified: September 7, 2016
#
# included with the sparki_learning library, though that is not required
#

from __future__ import print_function

import os
import platform
import sys

def speak( *message ):  # the * syntax allows multiple arguments to be passed, which will be stored in the list message
    """ Speaks the message over the computer speaker; relies on underlying operating system services

        arguments:
        message - data to speak; can be multiple arguments (like print) but all must be able to be converted to a string or this throws an error
                  for example, speak("Hello", 2, "day") should be a valid call

        returns:
        nothing
    """
    currentOS = platform.system()
    message = ' '.join([str(arg) for arg in message])   # concatenate all the arguments into one string
    
    if currentOS == "Darwin":
        speak_mac( message )
    elif currentOS == "Windows":
        speak_windows( message )
    elif "CYGWIN" in currentOS:
        speak_cygwin( message )
    elif currentOS == "Linux":
        speak_linux( message )
    else:
        speak_alt( message )


def speak_alt( message ):
    """ Prints the message to standard out

        arguments:
        message - string to print

        returns:
        nothing
    """
    print( message )


def speak_cygwin( message ):
    """ Prints the message to standard out (cygwin does not support speech at this time)

        arguments:
        message - string to print

        returns:
        nothing
    """
    print("Cygwin does not support speech (use print instead)", file=sys.stderr)
    speak_alt( message )


def speak_linux( message ):
    """ Prints the message to standard out (linux does not support speech at this time)

        arguments:
        message - string to print

        returns:
        nothing
    """
    print("Linux does not support speech (use print instead)", file=sys.stderr)
    speak_alt( message )


def speak_mac( message ):
    """ Speaks the message over the computer speaker

        arguments:
        message - string to speak

        returns:
        nothing
    """
    try:
        os.system("say " + message)     # uses the Mac command line program "say"
    except:
        print("There was a problem using the builtin say command", file=sys.stderr)
        speak_alt( message )


def speak_windows( message ):
    """ Prints the message to standard out (windows does not support speech at this time)

        arguments:
        message - string to print

        returns:
        nothing
    """
    # the code here attempts to create a vb script file to use the OS to speak
    # the given text; it's a horrid way to do this, but the best I could come
    # up with to speak using windows without relying on external programs

    # the idea for the code was taken from http://superuser.com/questions/223913/os-x-say-command-for-windows
    # as answered by Alessandro Mascolo
    try:
        temp_file = "tempspeech.vbs"
        with open( temp_file, mode='w' ) as f:
            f.write('Dim speech\n')
            f.write('Set speech=CreateObject("SAPI.spvoice")\n')
            f.write('speech.Speak "' + message + '"\n')
        os.system(temp_file)
        os.remove(temp_file)
    except:
        print("There was a problem creating the external vbs", file=sys.stderr)
        speak_alt( message )


def main():
    if len(sys.argv) > 1:               # this if statement looks for a command line argument to the program
        data = ' '.join(sys.argv[1:])   # if there's an argument, treat that thing to be spoken
    else:                               # otherwise, let the user enter the thing to say
        data = input("What do you want me to say? ")

    speak( data )
    

if __name__ == "__main__":
    main()
