# adalink Main Program
#
# Allows wiping the flash and programming the bootloader, softdevice, and app
# code for a CPU using a Segger JLink device.  Note that Segger's JLink
# software MUST be installed and JLinkExe in your system path.
#
# Author: Tony DiCola
import argparse
import logging
import sys

# Import version.
from . import __version__
# MUST have * import below to cause all cores to be loaded and available to
# Core class subclasses list.
from .cores import *


def main():
    # Main program entry point.  Start by printing the version of the tool.
    print 'adalink version: {0}'.format(__version__)

    # Build map of available cores by looking at subclasses of the core type.
    # Key is the core name (in lower case) and value is the core class.
    cores = {x.__name__.lower(): x for x in core.Core.__subclasses__()}

    # Define command line argument parser and parse arguments.
    parser = argparse.ArgumentParser(description='Tool to program and erase a nRF81522 CPU using a Segger JLink device.')
    parser.add_argument('-c', '--core',
                        action='store',
                        help='use specified CPU core',
                        required=True,
                        choices=cores.keys(),
                        type=str.lower)  # Convert parameter name to lower case for case insensitivity.
    parser.add_argument('-i', '--info',
                        action='store_true',
                        help='display info about the connected CPU core like firmware version')
    parser.add_argument('-w', '--wipe',
                        action='store_true',
                        help='wipe the flash memory of the board before any programming')
    parser.add_argument('-p', '--program',
                        nargs='*',
                        help='program the specified .hex files to the board',
                        metavar='FILE')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='show verbose output including raw JLinkExe commands')
    args = parser.parse_args()

    # Enable debug logging if required.
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    # Create core instance and fail if it's not connected.
    core_instance = cores[args.core]()
    if not core_instance.is_connected():
        # Not conntected, print a warning and stop.
        print 'ERROR! Could not find {0}, is it connected?'.format(args.core)
        sys.exit(-1)

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
        print 'Programming {0} files...'.format(len(args.program))
        core_instance.program(args.program)

    if args.verbose:
        print 'Done!'
    

if __name__=='__main__':
    main()
