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
    
    def __init__(self):
        # Call base class constructor.
        super(LPC1343, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink']
    
    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M3 r2p0, Little endian',
                         params='-device LPC1343 -if swd -speed 1000')
    
    def info(self, programmer):
        """Display info about the device."""
        # DEVICE ID = APB0 Base (0x40000000) + SYSCON Base (0x48000) + 3F4
        deviceid = programmer.readmem32(0x400483F4)
        click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:08X}'.format(deviceid))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(programmer, JLink):
            hwid = programmer.readmem32(0x400483F8)
            hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID : {0}'.format(hwstring))
