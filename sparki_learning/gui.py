################## Sparki Learning Library GUI Functions ##################
#
# This file contains various gui functions used by the Sparki Learning Library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# written by Jeremy Eglen
# Created: November 14, 2019
# Last Modified: November 14, 2019
from __future__ import print_function

from sparki_learning.util import printDebug

import sys
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg
    
import sparki_learning.util

def ask(message, mytitle="Question"):
    """ Gets input from the user -- prints message

        arguments:
        message - string to print to prompt the user
        mytitle - title for the window (defaults to Question)

        returns:
        string response from the user
    """
    printDebug("In ask, message={}; mytitle={}".format(message, mytitle), sparki_learning.util.DEBUG_INFO)

    try:
        result = sg.PopupGetText(message, title=mytitle)
        
    except Exception as err:
        printDebug("Error creating ask window -- gui may not be available", sparki_learning.util.DEBUG_ERROR)
        printDebug(str(err), DEBUG_DEBUG)
        result = input(message)

    return result


def messageWindow(message, mytitle="Message"):
    """ Pauses the program with a GUI message

        arguments:
        message - string to print to prompt the user
        mytitle - title for the window (defaults to Message)

        returns:
        nothing
    """
    printDebug("In messageWindow, message={}; mytitle={}".format(message, mytitle), sparki_learning.util.DEBUG_INFO)

    try:
        sg.Popup(message, title=mytitle, keep_on_top=True)
        
    except Exception as err:
        printDebug("Error creating message window -- gui may not be available", sparki_learning.util.DEBUG_ERROR)
        printDebug(str(err), sparki_learning.util.DEBUG_DEBUG)
        input(message + " (Press Enter to continue)")


def pickAFile():
    """ Gets the path to a file picked by the user

        arguments:
        none

        returns:
        string path to the file
    """
    printDebug("In pickAFile", sparki_learning.util.DEBUG_INFO)

    try:
        result = sg.PopupGetFile("Choose a file")
        
    except Exception as err:
        printDebug("Error creating pickAFile window -- gui may not be available", sparki_learning.util.DEBUG_ERROR)
        printDebug(str(err), sparki_learning.util.DEBUG_DEBUG)
        result = input("What is the path to the file? ")

    return result


def main():
    messageWindow("This will test the functions in this library.\nNormally, you include this file in your program.\nFor example:\nfrom sparki_learning.gui import *", "sparki_learning.gui test")

    # pickAFile() test
    file_test = pickAFile()
    if file_test:
        messageWindow("You picked \'" + file_test + "\' as your file")
    else:
        messageWindow("You did not pick a file")
        
    # ask test
    ask_test = ask("Type some stuff:", "ask() demo")
    if ask_test:
        messageWindow("You typed \'" + ask_test + "\'")
    else:
        messageWindow("You did not type anything (or pressed X or cancel)")
    
    messageWindow("Done with sparki_learning.gui tests", "All Done!")


if __name__ == "__main__":
    main()
