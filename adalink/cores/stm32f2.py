# STM32f2xx core implementation
#
# Author: Kevin Townsend
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


class STM32F2(Core):
    """STMicro STM32F2 CPU."""
    # Note that the docstring will be used as the short help description.
    
    # Define the list of supported programmer types.  This should be a dict
    # with the name of a programmer (as specified in the --programmer option)
    # as the key and a tuple with the type, array of constructor positional
    # args, and dict of constructor keyword args as the value.
    programmers = {
        'jlink': (
            JLink, 
            ['Cortex-M3 r2p0, Little endian'],  # String to expect when connected.
            { 'params': '-device STM32F205RG -if swd -speed 2000' }
        ),
        # 'stlink': (
        #     STLink,
        #     [''],  # OpenOCD flash driver name for mass_erase.
        #     { 'params': '-f interface/stlink-v2.cfg -f target/???' }
        # )
    }
    
    def __init__(self):
        # Call base class constructor.
        super(STM32F2, self).__init__()
    
    def info(self):
        """Display info about the device."""
        # [0xE0042000] = CHIP_REVISION[31:16] + RESERVED[15:12] + DEVICE_ID[11:0]
        deviceid = self.programmer.readmem32(0xE0042000) & 0xFFF
        chiprev  = (self.programmer.readmem32(0xE0042000) & 0xFFFF0000) >> 16
        click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:03X}'.format(deviceid))))
        click.echo('Chip Rev  : {0}'.format(DEVICEID_CHIPREV_LOOKUP.get(chiprev,
                                                   '0x{0:04X}'.format(chiprev))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(self.programmer, JLink):
            hwid = self.programmer.readmem32(0xE0042000) & 0xFFF
            hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:03X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID : {0}'.format(hwstring))
