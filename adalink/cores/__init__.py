# adalink.cores Module
#
# Import all python files in the directory to simplify adding a new core.
# Just drop a new core .py file in the directory and it will be picked up 
# automatically.
#
# Author: Tony DiCola
import os


# Import all python files in the cores directory by setting them to the __all__
# global which tells python the modules to load.  Grabs a list of all files in
# the directory and filters down to just the names (without .py extensions) of
# python files that don't start with '__' (which are module metadata that should
# be ignored.
__all__ = map(lambda x: x[:-3],
              filter(lambda x: not x.startswith('__') and x.lower().endswith('.py'),
                     os.listdir(__path__[0])))
