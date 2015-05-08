# adalink Core Base Class
#
# Base class for an adalink CPU core.  Concrete implementations of cores should
# inherit from this class and provide implementations of functions below.  Note
# that the class name of the core will be used to identify and choose the core
# using the adalink tool, so make it short and descriptive.
#
# Author: Tony DiCola
import abc


class Core(object):
    __metaclass__ = abc.ABCMeta
    """Base class for adalink CPU core implementations."""

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
    def detect_segger_device_id(self):
        """Attempts to detect the Segger device ID string for the chip."""
        raise NotImplementedError

    @abc.abstractmethod
    def info(self):
        """Print diagnostic information about the CPU."""
        raise NotImplementedError

    @abc.abstractmethod
    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        raise NotImplementedError
