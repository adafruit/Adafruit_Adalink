# adalink Main Program
#
# Allows wiping the flash and programming the bootloader, softdevice, and app
# code for a CPU using a Segger JLink device.  Note that Segger's JLink
# software MUST be installed and JLinkExe in your system path.
#
# Author: Tony DiCola
import argparse
import logging
import os.path
import sys

from . import __version__
from . import core
# MUST have * import below to cause all cores to be loaded and available to
# Core class subclasses list.
from .cores import *
from .errors import AdaLinkError


def main():
    try:
        # Main program entry point.  Start by printing the version of the tool.
        print 'adalink version: {0}'.format(__version__)

        # Build map of available cores by looking at subclasses of the core type.
        # Key is the lower case core short name and value is the core class.
        cores = {x.get_short_name().lower(): x for x in core.Core.__subclasses__()}

        # Define command line argument parser.
        parser = argparse.ArgumentParser(description='Tool to program and erase a nRF81522 CPU using a Segger JLink device.')
        # Add common command line arguments for actions that can be taken on any
        # core. Create this as a separate argument parser that will be aparent 
        # to all the core subparsers.
        common_parser = argparse.ArgumentParser(add_help=False)
        common_parser.add_argument('-i', '--info',
                                   action='store_true',
                                   help='display info about the connected CPU core like firmware version')
        common_parser.add_argument('-w', '--wipe',
                                   action='store_true',
                                   help='wipe the flash memory of the board before any programming')
        common_parser.add_argument('-p', '--program',
                                   nargs='*',
                                   help='program the specified .hex files to the board',
                                   metavar='FILE')
        common_parser.add_argument('-v', '--verbose',
                                   action='store_true',
                                   help='show verbose output including raw JLinkExe commands')
        # Create subparser for the core type.
        core_parsers = parser.add_subparsers(title='core',
                                             description='use specified CPU core',
                                             dest='core')
        for core_name, core_class in iter(cores.items()):
            subparser = core_parsers.add_parser(core_name,
                                                help=core_class.get_full_name(),
                                                parents=[common_parser])
            # Let the core add any of its parameters.
            core_class.add_arguments(subparser)
        # Parse command line arguments.
        args = parser.parse_args()

        # Enable debug logging if required.
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)

        # Create core instance and fail if it's not connected.
        core_instance = cores[args.core](args)
        if not core_instance.is_connected():
            # Not conntected, print a warning and stop.
            raise AdaLinkError('Could not find {0}, is it connected?'.format(args.core))

        # Perform requested actions.
        if args.info:
            # Print information about the chip.
            core_instance.info()
        if args.wipe:
            # Wipe flash memory of the chip.
            print 'Wiping flash memory...'
            core_instance.wipe()
        if args.program is not None:
            # Program files to the board.
            print 'Programming {0} file{1}...'.format(len(args.program),
                                                      's' if len(args.program) > 1 else '')
            # First check all of the files exist.
            for f in args.program:
                if not os.path.isfile(f):
                    raise AdaLinkError('{0} is not a file!'.format(f))
            # Tell core to program the hex files.
            core_instance.program(args.program)

        # Finished!
        if args.verbose:
            print 'Done!'

    except AdaLinkError as ex:
        print 'ERROR! {0}'.format(ex.message)
        sys.exit(-1)


if __name__ == '__main__':
    main()
