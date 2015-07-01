# nRF51822 core implementation
#
# Author: Tony DiCola
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


class nRF51822(Core):
    """Nordic nRF51822 CPU."""
    # Note that the docstring will be used as the short help description.
    
    # Define the list of supported programmer types.  This should be a dict
    # with the name of a programmer (as specified in the --programmer option)
    # as the key and a tuple with the type, array of constructor positional
    # args, and dict of constructor keyword args as the value.
    programmers = {
        'jlink': (
            JLink, 
            ['Cortex-M0 r0p0, Little endian'],  # String to expect when connected.
            { 'params': '-device nrf51822_xxaa -if swd -speed 1000' }
        ),
        'stlink': (
            STLink,
            ['nrf51'],  # OpenOCD flash driver name for mass_erase.
            { 'params': '-f interface/stlink-v2.cfg -f target/nrf51.cfg' }
        )
    }
    
    def __init__(self):
        # Call base class constructor.
        super(nRF51822, self).__init__()
    
    def info(self):
        """Display info about the device."""
        # Get the HWID register value and print it.
        # Note for completeness there are also readmem32 and readmem8 functions 
        # available to use for reading memory values too.
        hwid = self.programmer.readmem16(0x1000005C)
        click.echo('Hardware ID : {0}'.format(MCU_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(self.programmer, JLink):
            hwid = self.programmer.readmem16(0x1000005C)
            hwstring = SEGGER_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID   : {0}'.format(hwstring))
        # Get the SD firmware version and print it.
        sdid = self.programmer.readmem16(0x0000300C)
        click.echo('SD Version  : {0}'.format(SD_LOOKUP.get(sdid, 'Unknown! (0x{0:04X})'.format(sdid))))
        # Get the BLE Address and print it.
        addr_high = (self.programmer.readmem32(0x100000a8) & 0x0000ffff) | 0x0000c000
        addr_low  = self.programmer.readmem32(0x100000a4)
        click.echo('Device Addr : {0:02X}:{1:02X}:{2:02X}:{3:02X}:{4:02X}:{' \
                   '5:02X}'.format((addr_high >> 8) & 0xFF,
                                   (addr_high) & 0xFF,
                                   (addr_low >> 24) & 0xFF,
                                   (addr_low >> 16) & 0xFF,
                                   (addr_low >> 8) & 0xFF,
                                   (addr_low & 0xFF)))
        # Get device ID.
        did_high = self.programmer.readmem32(0x10000060)
        did_low  = self.programmer.readmem32(0x10000064)
        click.echo('Device ID   : {0:08X}{1:08X}'.format(did_high, did_low))
