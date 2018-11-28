# adalink Segger JLink Programmer
#
# Python interface to communicate with a JLink device using the native JLinkExe
# tool provided by Segger.  Note that you must have installed Segger JLink
# software from:
#   https://www.segger.com/jlink-software.html
#
# Additionally the JLinkExe should be in your system path (or explicitly
# provided to the JLink class initializer).
#
# Author: Tony DiCola
import logging
import os
import platform
import re
import sys
import subprocess
import tempfile
import threading
import time

from .base import Programmer
from ..errors import AdaLinkError

# OSX GUI-based app does not has the same PATH as terminal-based
if platform.system() == 'Darwin':
    os.environ["PATH"] = os.environ["PATH"] + ':/usr/local/bin'


logger = logging.getLogger(__name__)


class JLink(Programmer):

    # Name used to identify this programmer on the command line.
    name = 'jlink'

    def __init__(self, connected, jlink_exe=None, jlink_path='', params=None):
        """Create a new instance of the JLink communication class.  By default
        JLinkExe should be accessible in your system path and it will be used
        to communicate with a connected JLink device.

        You can override the JLinkExe executable name by specifying a value in
        the jlink_exe parameter.  You can also manually specify the path to the
        JLinkExe executable in the jlink_path parameter.

        Optional command line arguments to JLinkExe can be provided in the
        params parameter as a string.
        """
        self._connected = connected
        # If not provided, pick the appropriate JLinkExe name based on the
        # platform:
        # - Linux   = JLinkExe
        # - Mac     = JLinkExe
        # - Windows = JLink.exe
        if jlink_exe is None:
            system = platform.system()
            if system == 'Linux':
                jlink_exe = 'JLinkExe'
            elif system == 'Windows':
                jlink_exe = 'JLink.exe'
            elif system == 'Darwin':
                jlink_exe = 'JLinkExe'
            else:
                raise AdaLinkError('Unsupported system: {0}'.format(system))
        # Store the path to the JLinkExe tool so it can later be run.
        self._jlink_path = os.path.join(jlink_path, jlink_exe)
        logger.info('Using path to JLinkExe: {0}'.format(self._jlink_path))
        # Apply command line parameters if specified.
        self._jlink_params = []
        if params is not None:
            self._jlink_params.extend(params.split())
            logger.info('Using parameters to JLinkExe: {0}'.format(params))
        # Make sure we have the J-Link executable in the system path
        self._test_jlinkexe()

    def _test_jlinkexe(self):
        """Checks if JLinkExe is found in the system path or not."""
        # Spawn JLinkExe process and capture its output.
        args = [self._jlink_path]
        args.append('?')
        try:
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            process.wait()
        except OSError:
            raise AdaLinkError("'{0}' missing. Is the J-Link folder in your system "
                               "path?".format(self._jlink_path))

    def run_filename(self, filename, timeout_sec=60):
        """Run the provided script with JLinkExe.  Filename should be a path to
        a script file with JLinkExe commands to run.  Returns the output of
        JLinkExe.  If execution takes longer than timeout_sec an exception will
        be thrown.  Set timeout_sec to None to disable the timeout completely.
        """
        # Spawn JLinkExe process and capture its output.
        args = [self._jlink_path]
        args.extend(self._jlink_params)
        args.append(filename)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if timeout_sec is not None:
            # Use a timer to stop the subprocess if the timeout is exceeded.
            # This helps prevent very subtle issues with deadlocks on reading
            # subprocess output.  See: http://stackoverflow.com/a/10012262
            def timeout_exceeded(p):
                # Stop the subprocess and kill the whole program.
                p.kill()
                raise AdaLinkError('JLink process exceeded timeout!')
            timeout = threading.Timer(timeout_sec, timeout_exceeded, [process])
            timeout.start()
        # Grab output of JLink.
        output, err = process.communicate()
        if timeout_sec is not None:
            # Stop timeout timer when communicate call returns.
            timeout.cancel()
        logger.debug('JLink response: {0}'.format(output))
        return output

    def run_commands(self, commands, timeout_sec=60):
        """Run the provided list of commands with JLinkExe.  Commands should be
        a list of strings with with JLinkExe commands to run.  Returns the
        output of JLinkExe.  If execution takes longer than timeout_sec an
        exception will be thrown. Set timeout_sec to None to disable the timeout
        completely.
        """
        # Create temporary file to hold script.
        script_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        # commands.insert(0, 'connect\n')
        commands = '\n'.join(commands)
        script_file.write(commands)
        script_file.close()
        logger.debug('Using script file name: {0}'.format(script_file.name))
        logger.debug('Running JLink commands: {0}'.format(commands))
        return self.run_filename(script_file.name, timeout_sec)

    def _readmem(self, address, command):
        """Read the specified register with the provided register read command.
        """
        # Build list of commands to read register.
        address = '{0:08X}'.format(address)  # Convert address value to hex string.
        commands = [
            '{0} {1} 1'.format(command, address),
            'q'
        ]
        # Run command and parse output for register value.
        output = self.run_commands(commands)
        match = re.search('^{0} = (\S+)'.format(address), output,
                          re.IGNORECASE | re.MULTILINE)
        if match:
            return int(match.group(1), 16)
        else:
            raise AdaLinkError('Could not find expected memory value, are the JLink and board connected?')

    def is_connected(self):
        """Return true if the device is connected to the programmer."""
        output = self.run_commands(['connect', 'q'])
        return output.find('Found {0}'.format(self._connected)) != -1

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # Build list of commands to wipe memory.
        commands = [
            'r',      # Reset
            'erase',  # Erase
            'r',      # Reset
            'q'       # Quit
        ]
        # Run commands.
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        """Program chip with provided list of hex and/or bin files.  Hex_files
        is a list of paths to .hex files, and bin_files is a list of tuples with
        the first value being the path to the .bin file and the second value
        being the integer starting address for the bin file."""
        # Build list of commands to program hex files.
        commands = ['r']   # Reset
        # Program each hex file.
        for f in hex_files:
            f = os.path.abspath(f)
            commands.append('loadfile "{0}"'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = os.path.abspath(f)
            commands.append('loadbin "{0}" 0x{1:08X}'.format(f, addr))
        commands.extend([
            'r',  # Reset
            'g',  # Run the MCU
            'q'   # Quit
        ])
        # Run commands.
        self.run_commands(commands)

    def readmem32(self, address):
        """Read a 32-bit value from the provided memory address."""
        return self._readmem(address, 'mem32')

    def readmem16(self, address):
        """Read a 16-bit value from the provided memory address."""
        return self._readmem(address, 'mem16')

    def readmem8(self, address):
        """Read a 8-bit value from the provided memory address."""
        return self._readmem(address, 'mem8')
