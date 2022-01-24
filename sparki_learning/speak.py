# speak input over the computer
#
# Created: May 18, 2016 by Jeremy Eglen with assistance from Kelly Schmidt for the Mac function
# Last Modified: January 18, 2022
#
# included with the sparki_learning library, though that is not required
#
import os
import platform
import re
import sys

clean_regex = re.compile('[^A-Za-z0-9., ]+')

def speak(*message, alsoprint=False):  # the * syntax allows multiple arguments to be passed, which will be stored in the list message
    """ Speaks the message over the computer speaker; relies on underlying operating system services

        arguments:
        message - data to speak; can be multiple arguments (like print) but all must be able to be converted to a string or this throws an error
                  for example, speak("Hello", 2, "day") should be a valid call
        alsoprint - keyword only argument which will cause the message to be printed in addition to spoken;
                    if you want to use this, you must do something like speak("Hello my name is Sparki", alsoprint=True)

        returns:
        nothing
    """
    currentOS = platform.system()
    message = ' '.join([str(arg) for arg in message])  # concatenate all the arguments into one string

    if currentOS == "Darwin":
        if alsoprint:
            print(message)
        speak_mac(message)
    elif currentOS == "Windows":
        if alsoprint:
            print(message)
        speak_windows(message)
    elif "CYGWIN" in currentOS:
        speak_cygwin(message)
    elif currentOS == "Linux":
        speak_linux(message)
    else:
        speak_alt(message)


def speak_alt(message):
    """ Prints the message to standard out

        arguments:
        message - string to print

        returns:
        nothing
    """
    print(message)


def speak_cygwin(message):
    """ Prints the message to standard out (cygwin does not support speech at this time)

        arguments:
        message - string to print

        returns:
        nothing
    """
    print("Cygwin does not support speech (use print instead)", file=sys.stderr)
    speak_alt(message)


def speak_linux(message):
    """ Prints the message to standard out (linux does not support speech at this time)

        arguments:
        message - string to print

        returns:
        nothing
    """
    print("Linux does not support speech (use print instead)", file=sys.stderr)
    speak_alt(message)


def speak_mac(message):
    """ Speaks the message over the computer speaker

        arguments:
        message - string to speak

        returns:
        nothing
    """
    global clean_regex
    try:
        message = clean_regex.sub(' ', message)
        os.system("say " + message)  # uses the Mac command line program "say"
    except:
        print("There was a problem using the builtin say command", file=sys.stderr)
        speak_alt(message)


def speak_windows(message):
    """ Speaks the message over the computer speaker (windows uses vb script and windows text-to-speech)
        It's an ugly hack

        arguments:
        message - string to speak

        returns:
        nothing
    """
    global clean_regex
    # the code here attempts to create a vb script file to use the OS to speak
    # the given text; it's a horrid way to do this, but the best I could come
    # up with to speak using windows without relying on external programs

    # the idea for the code was taken from http://superuser.com/questions/223913/os-x-say-command-for-windows
    # as answered by Alessandro Mascolo
    
    try:
        message = clean_regex.sub(' ', message)
        temp_file_dir = os.path.expanduser('~')
        temp_file = temp_file_dir + "/tempspeech.vbs"
        with open(temp_file, mode='w') as f:
            f.write('Dim speech\n')
            f.write('Set speech=CreateObject("SAPI.spvoice")\n')
            f.write('speech.Speak "' + message + '"\n')
        os.system(temp_file)
        os.remove(temp_file)
    except:
        print("There was a problem creating the external vbs", file=sys.stderr)
        speak_alt(message)


def main():
    alsoprint = "undefined"
    
    while alsoprint.lower() not in ["yes", "no", "y", "n"]:
        alsoprint = input("Should I also print the message? [y/n] ")
        
        if not alsoprint:
            alsoprint = "undefined"
            
    if alsoprint.lower() in ["yes","y"]:
        alsoprint = True
    else:
        alsoprint = False
    
    if len(sys.argv) > 1:  # this if statement looks for a command line argument to the program
        data = ' '.join(sys.argv[1:])  # if there's an argument, treat that thing to be spoken
    else:  # otherwise, let the user enter the thing to say
        data = input("What do you want me to say? ")

    speak(data, alsoprint=alsoprint)


if __name__ == "__main__":
    main()
