# adalink Programmer Base Class
#
# Base class for an adalink CPU programmer.  Concrete implementations of
# programmers should inherit from this class and provide implementations of 
# functions below.
#
# Author: Tony DiCola
import abc


class Programmer(object):
    __metaclass__ = abc.ABCMeta
    """Base class for adalink CPU programmer implementations."""

    @abc.abstractmethod
    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        raise NotImplementedError

    @abc.abstractmethod
    def readmem32(self, address):
        """Read a 32-bit value from the provided memory address."""
        raise NotImplementedError

    @abc.abstractmethod
    def readmem16(self, address):
        """Read a 16-bit value from the provided memory address."""
        raise NotImplementedError

    @abc.abstractmethod
    def readmem8(self, address):
        """Read a 8-bit value from the provided memory address."""
        raise NotImplementedError
