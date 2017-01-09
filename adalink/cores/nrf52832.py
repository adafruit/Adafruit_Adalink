# nRF52832 core implementation
#
# Author: Kevin Townsend
import os

import click

from ..core import Core
from ..programmers import JLink


# CONFIGID register HW ID value to name mapping.
# List of HWID can be found at https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.nrf52832.ps.v1.1%2Fficr.html&resultof=%22FICR%22%20%22ficr%22%20
MCU_LOOKUP = {
    0x41414141: 'AAAA',
    0x41414142: 'AAAB',
    0x41414241: 'AABA',
    0x41414242: 'AABB',
    0xFFFFFFFF: 'Unspecified'
}

# SD ID value to name mapping.
SD_LOOKUP = {
    0xFFFF: 'None'
}

# CONFIGID register HW ID to Segger '-device' name mapping.
# Segger ID List: https://www.segger.com/jlink_supported_devices.html
SEGGER_LOOKUP = {
    0x0000: 'nRF52832_xxaa'
}

class nRF52832_JLink(JLink):
    # nRF52832-specific JLink programmer, required to add custom wipe command
    # for the chip.

    def __init__(self):
        # Call base STLink initializer and set it up to program the nRF52832.
        super(nRF52832_JLink, self).__init__('Cortex-M4 r0p1, Little endian',
            params='-device nrf52832_xxaa -if swd -speed 1000 -autoconnect 1')

    def wipe(self):
        # Run JLink commands to wipe nRF52832 memory.
        commands = [
            'erase',          # Erase all
            'sleep 100',      # Wait again
            'r',              # Reset
            'q'               # Quit
        ]
        self.run_commands(commands)


class nRF52832(Core):
    """Nordic nRF52832 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(nRF52832, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink']

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return nRF52832_JLink()

    def info(self, programmer):
        """Display info about the device."""
        # Get the HWID register value and print it.
        # Note for completeness there are also readmem32 and readmem8 functions
        # available to use for reading memory values too.
        hwid = programmer.readmem16(0x10000100)
        click.echo('Hardware ID : {0}'.format(MCU_LOOKUP.get(hwid, '0x{0:05X}'.format(hwid))))
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
