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
    def is_connected(self):
        """Return true if the device is connected to the programmer."""
        raise NotImplementedError

    @abc.abstractmethod
    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def program(self, hex_files=[], bin_files=[]):
        """Program chip with provided list of hex and/or bin files.  Hex_files
        is a list of paths to .hex files, and bin_files is a list of tuples with
        the first value being the path to the .bin file and the second value
        being the integer starting address for the bin file."""
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
