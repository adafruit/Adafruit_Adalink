# Atmel ATSAMD21G18 core implementation.
# See chip summary at:
#   http://www.atmel.com/Images/Atmel-42181-SAM-D21_Summary.pdf
#
# Author: Tony DiCola
import os

import click

from ..core import Core
from ..errors import AdaLinkError
from ..programmers import JLink, STLink


class STLink_ATSAMD21G18(STLink):
    # ATSAMD21G18-specific STLink-based programmer.  Required to add custom
    # wipe function, and to use the load_image command for programming (the
    # flash write_image function doesn't seem to work because of OpenOCD bugs).

    def __init__(self):
        # Call base STLink initializer and set it up to program the ATSAMD21G18.
        super(STLink_ATSAMD21G18, self).__init__(params='-f interface/stlink-v2.cfg ' \
            '-c "set CHIPNAME at91samd21g18; set ENDIAN little; set CPUTAPID 0x0bc11477; source [find target/at91samdXX.cfg]"')

    def wipe(self):
        # Run OpenOCD command to wipe ATSAMD21G18 memory.
        commands = [
            'init',
            'reset init',
            'at91samd chip-erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the ATSAMD21G18 with the provided hex/bin files.
        click.echo('WARNING: Make sure the provided hex/bin files are padded with ' \
            'at least 64 bytes of blank (0xFF) data!  This will work around a cache bug with OpenOCD 0.9.0.')
        commands = [
            'init',
            'reset init'
        ]
        # Program each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0 ihex'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('load_image {0} 0x{1:08X} bin'.format(f, addr))
        # Verify each hex file.
        for f in hex_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0 ihex'.format(f))
        # Verify each bin file.
        for f, addr in bin_files:
            f = self.escape_path(os.path.abspath(f))
            commands.append('verify_image {0} 0x{1:08X} bin'.format(f, addr))
        commands.append('reset run')
        commands.append('exit')
        # Run commands.
        output = self.run_commands(commands)
        # Check that expected number of files were verified.  Look for output lines
        # that start with 'verified ' to signal OpenOCD output that the verification
        # succeeded.  Count up these lines and expect they match the number of
        # programmed files.
        verified = len(filter(lambda x: x.startswith('verified '), output.splitlines()))
        if verified != (len(hex_files) + len(bin_files)):
            raise AdaLinkError('Failed to verify all files were programmed!')


class ATSAMD21G18(Core):
    """Atmel ATSAMD21G18 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(ATSAMD21G18, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink', 'stlink']

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M0 r0p1, Little endian',
                         params='-device ATSAMD21G18 -if swd -speed 1000')
        elif programmer == 'stlink':
            return STLink_ATSAMD21G18()

    def info(self, programmer):
        """Display info about the device."""
        click.echo('Not implemented!')
