# LPC1343 core implementation
#
# Author: Kevin Townsend
import click

from ..core import Core
from ..programmers import JLink, STLink


# DEVICE ID register valueto name mapping
# See 'DEVICE_ID' in: http://www.nxp.com/documents/user_manual/UM10375.pdf
DEVICEID_CHIPNAME_LOOKUP = {
    0x2C42502B: 'LPC1311FHN33',
    0x2C40102B: 'LPC1313FHN33 or LPC1313FBD48',
    0x3D01402B: 'LPC1342FHN33 or LPC1342FBD48',
    0x3D00002B: 'LPC1343FHN33 or LPC1343FBD48',
    0x1816902B: 'LPC1311FHN33/01',
    0x1830102B: 'LPC1313FHN33/01 or LPC1313FBD48/01'
}

# DEVICE ID register value to Segger '-device' name mapping
# See 'DEVICE_ID' in:
# See 'DEVICE_ID' in: http://www.nxp.com/documents/user_manual/UM10375.pdf
# Segger ID List: https://www.segger.com/jlink_supported_devices.html
DEVICEID_SEGGER_LOOKUP = {
    0x2C42502B: 'LPC1311',
    0x2C40102B: 'LPC1313',
    0x3D01402B: 'LPC1342',
    0x3D00002B: 'LPC1343',
    0x1816902B: 'LPC1311',
    0x1830102B: 'LPC1313'
}


class LPC1343(Core):
    """NXP LPC1343 CPU."""
    # Note that the docstring will be used as the short help description.
    
    # Define the list of supported programmer types.  This should be a dict
    # with the name of a programmer (as specified in the --programmer option)
    # as the key and a tuple with the type, array of constructor positional
    # args, and dict of constructor keyword args as the value.
    programmers = {
        'jlink': (
            JLink, 
            ['Cortex-M3 r2p0, Little endian'],  # String to expect when connected.
            { 'params': '-device LPC1343 -if swd -speed 1000' }
        ),
        # 'stlink': (
        #     STLink,
        #     [''],  # OpenOCD flash driver name for mass_erase.
        #     { 'params': '-f interface/stlink-v2.cfg -f target/???' }
        # )
    }
    
    def __init__(self):
        # Call base class constructor.
        super(LPC1343, self).__init__()
    
    def info(self):
        """Display info about the device."""
        # DEVICE ID = APB0 Base (0x40000000) + SYSCON Base (0x48000) + 3F4
        deviceid = self.programmer.readmem32(0x400483F4)
        click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:08X}'.format(deviceid))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(self.programmer, JLink):
            hwid = self.programmer.readmem32(0x400483F8)
            hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID : {0}'.format(hwstring))
