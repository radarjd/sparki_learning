################## Sparki Learning Library GUI Functions ##################
#
# This file contains various gui functions used by the Sparki Learning Library
#
# Sparki is a mark of Arcbotics, LLC; no claim is made to the name Sparki and all rights in the name Sparki
# remain property of their respective owners
#
# written by Jeremy Eglen
# Created: November 14, 2019
# Last Modified: November 18, 2019
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


def askQuestion(message, options, mytitle="Question"):
    """ Gets input from the user -- prints message and displays buttons with options

        arguments:
        message - string to print to prompt the user
        options - a list of strings which could be the response
        mytitle - title for the window (defaults to Question)

        returns:
        string response from the user
    """
    printDebug("In askQuestion, message={}; options={}; mytitle={}".format(message, options, mytitle), sparki_learning.util.DEBUG_INFO)
    radio_group = "options"

    try:
        radio = [[sg.Radio(text, radio_group, key=text),] for text in options]
        layout = [[sg.Text(message)]] + radio + [[sg.OK(), sg.Cancel()]]
        window = sg.Window(mytitle, layout)

        while True:             # Event Loop
            event, values = window.Read()
            if event in (None, "OK", "Cancel"):
                break

        printDebug("In askQuestion, event = {}; values = {}".format(event,values), sparki_learning.util.DEBUG_DEBUG)
        window.close()

        result = False
        for text in options:
            if window[text].get():
                result = text

    except Exception as err:
        printDebug("Error creating askQuestion window -- gui may not be available", sparki_learning.util.DEBUG_ERROR)
        printDebug(str(err), sparki_learning.util.DEBUG_DEBUG)
        result = askQuestion_text(message, options, False)

    return result


def askQuestion_text(message, options, caseSensitive=True):
    """ Gets a string from the user, which must be one of the options -- prints message
        (this is called if askQuestion fails)

        arguments:
        message - string to print to prompt the user
        options - list of options for the user to choose
        caseSensitive - boolean, if True, response must match case

        returns:
        string response from the user (if caseSentitive is False, this will always be a lower case string)
    """
    printDebug("In askQuestion_text, message={}; options={}; caseSensitive={}".format(message, options, caseSensitive), sparki_learning.util.DEBUG_INFO)
    if not caseSensitive:  # if we're not caseSensitive, make the options lower case
        working_options = [s.lower() for s in options]
    else:
        working_options = options

    result = input(message)

    if not caseSensitive:
        result = result.lower()

    while result not in working_options:
        print("Your answer must be one of the following: " + str(options))
        result = input(message)

        if not caseSensitive:
            result = result.lower()

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
        input(message + " (Press Enter to continue) ")


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


def yesorno(message):
    """ Gets the string 'yes' or 'no' from the user -- prints message

        arguments:
        message - string to print to prompt the user

        returns:
        string response from the user
    """
    printDebug("In yesorno", sparki_learning.util.DEBUG_INFO)

    return askQuestion(message, ["yes", "no"], "Yes or No?")


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
        
    # askQuestion test
    askQuestion_test = askQuestion("Choose wisely:", ["yes", "no", "maybe so"], "askQuestion() demo")
    if askQuestion_test:
        messageWindow("You chose \'" + askQuestion_test + "\'")
    else:
        messageWindow("You did not choose anything (or pressed X or cancel)")
    
    messageWindow("Done with sparki_learning.gui tests", "All Done!")


if __name__ == "__main__":
    main()
