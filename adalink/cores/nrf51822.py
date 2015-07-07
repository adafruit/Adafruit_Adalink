# nRF51822 core implementation
#
# Author: Tony DiCola
import os

import click

from ..core import Core
from ..programmers import JLink, STLink


# CONFIGID register HW ID value to name mapping.
# List of HWID can be found at https://www.nordicsemi.com/eng/nordic/Products/nRF51822/ATTN-51/41917
MCU_LOOKUP = {
    0x003c: 'QFAAG00 (16KB)',
    0x0044: 'QFAAGC0 (16KB)',
    0x0083: 'QFACA00 (32KB)',
    0x0084: 'QFACA10 (32KB)'
}

# SD ID value to name mapping.
SD_LOOKUP = {
    0x005a: 'S110 7.1.0',
    0x005e: 'S130 0.9alpha',
    0x0060: 'S120 2.0.0',
    0x0064: 'S110 8.0.0',
    0xFFFF: 'None'
}

# CONFIGID register HW ID to Segger '-device' name mapping.
# Segger ID List: https://www.segger.com/jlink_supported_devices.html
SEGGER_LOOKUP = {
    0x003c: 'nRF51822_xxAA',
    0x0044: 'nRF51822_xxAA',
    0x0083: 'nRF51822_xxAC',
    0x0084: 'nRF51822_xxAC'
}


class STLink_nRF51822(STLink):
    # nRF51822-specific STLink-based programmer.  Required to add custom
    # wipe and erase before programming needed for the nRF51822 & OpenOCD.

    def __init__(self):
        # Call base STLink initializer and set it up to program the nRF51822.
        super(STLink_nRF51822, self).__init__(params='-f interface/stlink-v2.cfg -f target/nrf51.cfg')

    def wipe(self):
        # Run OpenOCD commands to wipe nRF51822 memory.
        commands = [
            'init',
            'reset init',
            'halt',
            'nrf51 mass_erase',
            'exit'
        ]
        self.run_commands(commands)

    def program(self, hex_files=[], bin_files=[]):
        # Program the nRF51822 with the provided hex files.  Note that programming
        # the soft device and bootloader requires erasing the memory so it will
        # always be done.
        click.echo('WARNING: Flash memory will be erased before programming nRF51822 with the STLink!')
        commands = [
            'init',
            'reset init',
            'halt',
            'nrf51 mass_erase'
        ]
        # Program each hex file.
        for f in hex_files:
            f = os.path.abspath(f)
            commands.append('flash write_image {0} 0 ihex'.format(f))
        # Program each bin file.
        for f, addr in bin_files:
            f = os.path.abspath(f)
            commands.append('flash write_image {0} 0x{1:08X} bin'.format(f, addr))
        commands.append('reset run')
        commands.append('exit')
        self.run_commands(commands)


class nRF51822(Core):
    """Nordic nRF51822 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(nRF51822, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink', 'stlink']

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M0 r0p0, Little endian',
                         params='-device nrf51822_xxaa -if swd -speed 1000')
        elif programmer == 'stlink':
            return STLink_nRF51822()

    def info(self, programmer):
        """Display info about the device."""
        # Get the HWID register value and print it.
        # Note for completeness there are also readmem32 and readmem8 functions
        # available to use for reading memory values too.
        hwid = programmer.readmem16(0x1000005C)
        click.echo('Hardware ID : {0}'.format(MCU_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(programmer, JLink):
            hwid = programmer.readmem16(0x1000005C)
            hwstring = SEGGER_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID   : {0}'.format(hwstring))
        # Get the SD firmware version and print it.
        sdid = programmer.readmem16(0x0000300C)
        click.echo('SD Version  : {0}'.format(SD_LOOKUP.get(sdid, 'Unknown! (0x{0:04X})'.format(sdid))))
        # Get the BLE Address and print it.
        addr_high = (programmer.readmem32(0x100000a8) & 0x0000ffff) | 0x0000c000
        addr_low  = programmer.readmem32(0x100000a4)
        click.echo('Device Addr : {0:02X}:{1:02X}:{2:02X}:{3:02X}:{4:02X}:{' \
                   '5:02X}'.format((addr_high >> 8) & 0xFF,
                                   (addr_high) & 0xFF,
                                   (addr_low >> 24) & 0xFF,
                                   (addr_low >> 16) & 0xFF,
                                   (addr_low >> 8) & 0xFF,
                                   (addr_low & 0xFF)))
        # Get device ID.
        did_high = programmer.readmem32(0x10000060)
        did_low  = programmer.readmem32(0x10000064)
        click.echo('Device ID   : {0:08X}{1:08X}'.format(did_high, did_low))
