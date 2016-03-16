# adalink Raspi 2 Native Programmer (using OpenOCD).
#
# Python interface to control Raspi 2 GPIO pins as a programmer using OpenOCD.
#
# Note you MUST have OpenOCD installed.
#
# Author: Tony DiCola
import logging
import os
import platform
import re
import sys
import subprocess
import threading
import time

from .base import Programmer
from ..errors import AdaLinkError

# OSX GUI-based app does not has the same PATH as terminal-based
if platform.system() == 'Darwin':
    os.environ["PATH"] = os.environ["PATH"] + ':/usr/local/bin'

logger = logging.getLogger(__name__)


class RasPi2(Programmer):

    # Name used to identify this programmer on the command line.
    name = 'raspi2'

    def __init__(self, openocd_exe=None, openocd_path='', params=None):
        """Create a new instance of the Raspberry Pi 2 communication class.  By default
        OpenOCD should be accessible in your system path on the Raspberry Pi
	and it will be used to twiddle GPIOs.

        You can override the OpenOCD executable name by specifying a value in
        the openocd_exe parameter.  You can also manually specify the path to the
        OpenOCD executable in the openocd_path parameter.

        Optional command line arguments to OpenOCD can be provided in the
        params parameter as a string.
        """
        # If not provided, pick the appropriate OpenOCD name based on the
        # platform:
        # - Linux   = openocd
        # - Mac     = openocd
        # - Windows = openocd.exe
        if openocd_exe is None:
            system = platform.system()
            if system == 'Linux' or system == 'Darwin':
                openocd_exe = 'openocd'
            elif system == 'Windows':
                openocd_exe = 'openocd.exe'
            else:
                raise AdaLinkError('Unsupported system: {0}'.format(system))
        # Store the path to the OpenOCD tool so it can later be run.
        self._openocd_path = os.path.join(openocd_path, openocd_exe)
        logger.info('Using path to OpenOCD: {0}'.format(self._openocd_path))
        # Apply command line parameters if specified.
        self._openocd_params = []
        if params is not None:
            self._openocd_params.extend(params.split())
            logger.info('Using parameters to OpenOCD: {0}'.format(params))
        # Make sure we have OpenOCD in the system path
        self._test_openocd()

    def _test_openocd(self):
        """Checks if OpenOCD 0.9.0 is found in the system path or not."""
        # Spawn OpenOCD process with --version and capture its output.
        args = [self._openocd_path, '--version']
        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, err = process.communicate()
            # Parse out version number from response.
            match = re.search('^Open On-Chip Debugger (\S+)', output,
                              re.IGNORECASE | re.MULTILINE)
            if not match:
                return
            # Simple semantic version check to see if OpenOCD version is greater
            # or equal to 0.9.0.
            version = match.group(1).split('.')
            if int(version[0]) > 0:
                # Version 1 or greater, assume it's good (higher than 0.9.0).
                return
            if int(version[0]) == 0 and int(version[1]) >= 9:
                # Version 0.9 or greater, assume it's good.
                return
            # Otherwise assume version is too old because it's below 0.9.0.
            raise RuntimError
        except Exception as ex:
            print 'ERROR', ex
            raise AdaLinkError('Failed to find OpenOCD 0.9.0 or greater!  Make '
                               'sure OpenOCD 0.9.0 is installed and in your '
                               'system path.')

    def run_commands(self, commands, timeout_sec=60):
        """Run the provided list of commands with OpenOCD.  Commands should be
        a list of strings with with OpenOCD commands to run.  Returns the
        output of OpenOCD.  If execution takes longer than timeout_sec an
        exception will be thrown. Set timeout_sec to None to disable the timeout
        completely.
        """
        # Spawn OpenOCD process and capture its output.
        args = [self._openocd_path]
        args.extend(self._openocd_params)
        for c in commands:
            args.append('-c')
            args.append('"{0}"'.format(c))
        args = ' '.join(args)
        logger.debug('Running OpenOCD command: {0}'.format(args))
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        if timeout_sec is not None:
            # Use a timer to stop the subprocess if the timeout is exceeded.
            # This helps prevent very subtle issues with deadlocks on reading
            # subprocess output.  See: http://stackoverflow.com/a/10012262
            def timeout_exceeded(p):
                # Stop the subprocess and kill the whole program.
                p.kill()
                raise AdaLinkError('OpenOCD process exceeded timeout!')
            timeout = threading.Timer(timeout_sec, timeout_exceeded, [process])
            timeout.start()
        # Grab output of OpenOCD.
        output, err = process.communicate()
        if timeout_sec is not None:
            # Stop timeout timer when communicate call returns.
            timeout.cancel()
        logger.debug('OpenOCD response: {0}'.format(output))
        return output

    def _readmem(self, address, command):
        """Read the specified register with the provided register read command.
        """
        # Build list of commands to read register.
        address = '0x{0:08X}'.format(address)  # Convert address value to hex string.
        commands = [
            'init',
            '{0} {1}'.format(command, address),
            'exit'
        ]
        # Run command and parse output for register value.
        output = self.run_commands(commands)
        match = re.search('^{0}: (\S+)'.format(address), output,
                          re.IGNORECASE | re.MULTILINE)
        if match:
            return int(match.group(1), 16)
        else:
            raise AdaLinkError('Could not find expected memory value, is the board connected?')

    def is_connected(self):
        """Return true if the device is connected to the programmer."""
        output = self.run_commands(['init', 'exit'])
        return output.find('Error:') == -1

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # There is no general mass erase function with OpenOCD, instead only
        # chip-specific functions.  For that reason don't implement a default
        # wipe and instead force cores to subclass and provide their own
        # wipe functionality.
        raise NotImplementedError

    def program(self, hex_files=[], bin_files=[]):
        """Program chip with provided list of hex and/or bin files.  Hex_files
        is a list of paths to .hex files, and bin_files is a list of tuples with
        the first value being the path to the .bin file and the second value
        being the integer starting address for the bin file."""
        # Build list of commands to program hex files.
        commands = [
            'init',
            'reset init',
            'halt'
        ]
        # Program each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('flash write_image {0} 0 ihex'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('flash write_image {0} 0x{1:08X} bin'.format(f, addr))
        commands.append('reset run')
        commands.append('exit')
        self.run_commands(commands)

    def readmem32(self, address):
        """Read a 32-bit value from the provided memory address."""
        return self._readmem(address, 'mdw')

    def readmem16(self, address):
        """Read a 16-bit value from the provided memory address."""
        return self._readmem(address, 'mdh')

    def readmem8(self, address):
        """Read a 8-bit value from the provided memory address."""
        return self._readmem(address, 'mdb')

    def escape_path(self, path):
        """Escape the path with Tcl '{}' chars to prevent spaces,
        backslashes, etc. from being misinterpreted.
        """
        return '{{{0}}}'.format(path)
