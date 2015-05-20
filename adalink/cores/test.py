# Test core implementation.  Good for demonstrating and testing out core
# functionality.
#
# Author: Tony DiCola
from ..core import Core

class TestCore(Core):
    """Test core implementation."""

    # A core can override the get_full_name class method below to specify a nice
    # name and description that will be printed in the help text.  By default
    # the short name of the core (see below) will be used: "(short name) core".
    @classmethod
    def get_full_name(cls):
        return "Test Core (does nothing, only for testing)"

    # Can also override the get_short_name class method to change the short
    # name of the core (used in the command line arguments to select the core).
    # By default the class name will be used so it's not recommended to change
    # this value.
    # @classmethod
    # def get_short_name(cls):
    #     return "custom_short_name"

    # Add any core-specific command line parameters by defining the add_arguments
    # function below.  The function will receive an ArgumentParser object which
    # add_argument calls can be made against to add command line arguments.  See
    # the argparse documentation for details on the add_argument syntax:
    #   https://docs.python.org/2.7/library/argparse.html#the-add-argument-method
    @classmethod
    def add_arguments(cls, subparser):
        # Add a couple parameters as an example.
        # Add a --device <device_type> parameter that is required.
        subparser.add_argument('-d', '--device',
                               action='store',
                               required=True,
                               help='specify device type',
                               choices=['one','two'],  # List of allowed values (optional).
                               metavar='TYPE')  # Metavar is what's printed in 
                                                # help messages for the argument
                                                # value.
        # Add an optional --foo parameter that is just a boolean value (i.e. it's
        # true if provided and false if not provided).
        subparser.add_argument('--foo',
                               action='store_true',
                               help='enable foo mode')

    def __init__(self, args):
        """Create instance of test core."""
        # Do any initialization of the core here.  The args parameter is the
        # parsed command line parameter object (an argparser Namespace object).
        # Grab the devie type parameter value and print it out.
        print 'Test core using device type: {0}'.format(args.device)
        # Print out a message if foo parameter was specified.
        if args.foo:
            print 'Test core foo mode enabled!'

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        print 'Wiping test core memory!'

    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        for f in hex_files:
            print 'Programming test core with {0}!'.format(f)

    def detect_segger_device_id(self):
        """Attempts to detect the Segger device ID string for the chip."""
        return "TestCoreDeviceId"

    def info(self):
        """Print information about the connected core."""
        print 'Test core information!'

    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        return True
