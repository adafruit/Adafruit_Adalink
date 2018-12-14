# adalink.cores Module
#
# Import all python files in the directory to make them available to use.
#
# Author: Tony DiCola

# Import all python files in the cores directory manually.  This is a change
# from previous behavior which automatically imported cores, but relied on
# somewhat brittle behavior for finding the path of the current script (and
# would have problems with py2exe).  Since dynamically loading new cores
# isn't really that important, just import each one explicitly:
from . import atsamd21g18
from . import lpc824
from . import lpc1343
from . import nrf51822
from . import nrf52832
from . import nrf52840
from . import stm32f2
