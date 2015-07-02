# adalink STLink V2 Programmer (using OpenOCD).
#
# Python interface to control the STLink V2 programmer using OpenOCD.
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


logger = logging.getLogger(__name__)


class STLink(Programmer):
    
    # Name used to identify this programmer on the command line.
    name = 'stlink'
    
    def __init__(self, flash_driver, openocd_exe=None, openocd_path='', 
                 params=None):
        """Create a new instance of the STLink communication class.  By default
        OpenOCD should be accessible in your system path and it will be used
        to communicate with a connected STLink device.
        
        Flash_driver must specify the name of the OpenOCD flash driver for
        running the mass_erase command (see http://openocd.org/doc/html/Flash-Commands.html,
        for example 'nrf51' is the flash driver name for the nRF51 series chips).

        You can override the OpenOCD executable name by specifying a value in
        the openocd_exe parameter.  You can also manually specify the path to the
        OpenOCD executable in the openocd_path parameter.

        Optional command line arguments to OpenOCD can be provided in the
        params parameter as a string.
        """
        self._flash_driver = flash_driver
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
        """Checks if OpenOCD is found in the system path or not."""
        # Spawn OpenOCD process and capture its output.
        args = [self._openocd_path, '--help']
        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
        except OSError:
            raise AdaLinkError("'{0}' missing. Is OpenOCD in your system "
                               "path?".format(self._openocd_path))

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
            args.append(c)
        logger.debug('Running OpenOCD command: {0}'.format(' '.join(args)))
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        # Grab output of STLink.
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
        commands = []
        commands.append('init')
        commands.append('{0} {1}'.format(command, address))
        commands.append('exit')
        # Run command and parse output for register value.
        output = self.run_commands(commands)
        match = re.search('^{0}: (\S+)'.format(address), output,
                          re.IGNORECASE | re.MULTILINE)
        if match:
            return int(match.group(1), 16)
        else:
            raise AdaLinkError('Could not find expected memory value, are the STLink and board connected?')
    
    def is_connected(self):
        """Return true if the device is connected to the programmer."""
        output = self.run_commands(['init', 'exit'])
        return output.find('Error:') == -1
    
    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # Build list of commands to wipe memory.
        commands = []
        commands.append('init')
        commands.append('reset init')
        commands.append('halt')
        commands.append('{0} mass_erase'.format(self._flash_driver))
        commands.append('exit')
        # Run commands.
        self.run_commands(commands)

    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        # Build list of commands to program hex files.
        commands = []
        commands.append('init')
        commands.append('reset init')
        commands.append('halt')
        # On the nRF51822 it MUST run a mass_erase before programming the
        # bootloader and softdevice areas of memory.
        commands.append('{0} mass_erase'.format(self._flash_driver))
        click.echo('WARNING: STLink programmer requires wiping flash memory before programming.  Flash memory will be wiped!')
        # Program each hex file.  First program all the file up to the last one
        # and mark them only to verify.
        for f in hex_files[:-1]:
            f = os.path.abspath(f)
            commands.append('program {0} verify'.format(f))
        # Program the last hex file and be careful to reset and exit at the end.
        commands.append('program {0} verify reset'.format(hex_files[-1]))
        # Run commands.
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
