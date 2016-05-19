"""
    This library implements the Python part of a system for using Python with
    the Sparki robot (<http://arcbotics.com/products/sparki/>).

    For this system to be of any use, you will need to install the other half
    of the library onto your Sparki. Directions can be found at the homepage
    at <https://github.com/radarjd/sparki_learning>

    The Python part of the library implements much of the IPRE (Institute for
    Personal Robotics in Education <http://www.roboteducation.org/>) Myro API
    (API reference at <http://calicoproject.org/Calico_Myro>). This API was
    originally chosen because the original author of this project taught (or
    teaches, depending on when you read this) a class making use of that
    program. A free textbook exists to teach that program may be found at
    <http://calicoproject.org/Learning_Computing_With_Robots_Using_Calico_Python>.
    The Python library here does not implement all of that library -- in
    particular, anything having to do with the camera cannot be implemented
    on Sparki because Sparki does not have that hardware.    
"""

from sparki_learning.sparki_myro import *
from sparki_learning.sync_lib import start_sync_server,start_sync_client
from sparki_learning.speak import speak

import sparki_learning.sparki_myro
