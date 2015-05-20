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
    """Base class for adalink CPU core implementations.  The core's __init__
    function should take 1 parameter which is the argparser Namespace object
    with all the parsed command line arguments (including core-specific
    arguments).
    """

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

    @classmethod
    def add_arguments(cls, subparser):
        """Add any command line parameters that are specific to this core.  The
        passed in subparser argument is an ArgumentParser object and add_argument
        should be called on it to add arguments.  By default no extra command 
        line parameters are added to the subparser.
        """
        # Do nothing by default.  Child classes can override this function to
        # add their own arguments to the subparser.
        pass

    @classmethod
    def get_short_name(cls):
        """Return a short name to be used as the core name when selecting a core
        at the command line.  Defaults to the name of the core class.
        """
        return cls.__name__

    @classmethod
    def get_full_name(cls):
        """Return a nice human readable name for this core.  Will be shown in
        the help text for the program.  Defaults to the short name (class name),
        but should be overridden and changed to a nicer value.
        """
        return '{0} core'.format(cls.get_short_name())
