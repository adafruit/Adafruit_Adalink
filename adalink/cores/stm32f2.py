# STM32f2xx core implementation
#
# Author: Kevin Townsend
import os

import click

from ..core import Core
from ..programmers import JLink, STLink


# DEVICE ID register valueto name mapping
DEVICEID_CHIPNAME_LOOKUP = {
    0x411: 'STM32F2xx'
}

# DEVICE ID register value to Segger '-device' name mapping
# Segger ID List: https://www.segger.com/jlink_supported_devices.html
DEVICEID_SEGGER_LOOKUP = {
    0x411: 'STM32F205RG'
}

# REV_D name mapping
# See Section 32.6.1 of the STM32F205 Reference Manual (DBGMDU_IDCODE)
DEVICEID_CHIPREV_LOOKUP = {
    0x1000: 'A (0x1000)',
    0x1001: 'Z (0x1001)',
    0x2000: 'B (0x2000)',
    0x2001: 'Y (0x2001)',
    0x2003: 'X (0x2003)',
    0x2007: '1 (0x2007)',
    0x200F: 'V (0x200F)',
    0x201F: '2 (0x201F)'
}


class STLink_STM32F2(STLink):
    # STM32F2-specific STLink-based programmer.  Required to add custom mass
    # erase command logic to wiping.

    def __init__(self):
        # Call base STLink initializer and set it up to program the STM32F2.
        super(STLink_STM32F2, self).__init__(params='-f interface/stlink-v2.cfg -f target/stm32f2x.cfg')

    def wipe(self):
        # Run OpenOCD commands to wipe STM32F2 memory.
        commands = [
            'init',
            'reset init',
            'halt',
            'stm32f2x mass_erase 0',
            'exit'
        ]
        self.run_commands(commands)


class STM32F2(Core):
    """STMicro STM32F2 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor.
        super(STM32F2, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink','stlink']

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M3 r2p0, Little endian',
                         params='-device STM32F205RG -if swd -speed 2000')
        elif programmer == 'stlink':
            return STLink_STM32F2()

    def info(self, programmer):
        """Display info about the device."""
        # [0xE0042000] = CHIP_REVISION[31:16] + RESERVED[15:12] + DEVICE_ID[11:0]
        deviceid = programmer.readmem32(0xE0042000) & 0xFFF
        chiprev  = (programmer.readmem32(0xE0042000) & 0xFFFF0000) >> 16
        click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:03X}'.format(deviceid))))
        click.echo('Chip Rev  : {0}'.format(DEVICEID_CHIPREV_LOOKUP.get(chiprev,
                                                   '0x{0:04X}'.format(chiprev))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(programmer, JLink):
            hwid = programmer.readmem32(0xE0042000) & 0xFFF
            hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:03X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID : {0}'.format(hwstring))
