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
import atsamd21g18
import lpc824
import lpc1343
import nrf51822
import stm32f2
