# draw regular polygons with the sparki
# 
# written by Jeremy Eglen
# Created: September 13, 2012
# Last Modified: April 12, 2016

from __future__ import division,print_function

from sparki_learning import *

def getInteriorAngle(numSides):
    """ Calculates the interior angle of an equilateral polygon

    argument:
    numSides -- integer number of sides

    returns:
    float -- number of degrees in each interior angle """

    numSides = int(numSides)                # ensure that numSides is an integer
    return ( (numSides - 2.0) * 180.0 / numSides )  


def getExteriorAngle(numSides):
    """ Calculates the exterior angle of an equilateral polygon

    argument:
    numSides -- integer number of sides

    returns:
    float -- number of degrees in each exterior angle """

    numSides = int(numSides)                # ensure that numSides is an integer
    return ( 180 - getInteriorAngle(numSides) )


def drawFigure(numSides, sideLength=1):
    """ Draws an equilateral polygon of numSides

    arguments:
    numSides -- integer number of sides
    sideLength -- float number of seconds to spend drawing each side (defaults to 1)

    returns:
    nothing """

    angle = getExteriorAngle(numSides)

    for x in range(0, numSides):
        forward( 1, sideLength )
        wait(.1)
        turnBy(angle)


def main():
    myCom = None

    while not myCom:
        myCom = ask("What COM port is the Sparki on? ")
    
    init(myCom)

    numSides = int( ask("How many sides does the figure have? ") )
    sideLength = float( ask("How long should I make each side? ") )

    while numSides > 2 and sideLength > 0:
        print("I am going to draw a figure with " + str(numSides) + " sides")
        print("If you'd like to draw, please insert a pen or marker")
        ask("Press okay once you have placed a pen or marker in me")
        
        drawFigure(numSides, sideLength)

        print("Please remove the marker")
        ask("Press okay once you have removed the marker from me")

        # move a little so that figures don't overlap
        turnBy( -90 )
        wait(1)
        forward( 1, 2 )
        turnBy( 90 )
        
        numSides = int( ask("How many sides does the figure have? (<=2 to quit) ") )
        sideLength = float( ask("How long should I make each side? (<= 0 to quit) ") )
        

if __name__ == "__main__":
    main()
