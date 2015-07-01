# LPC824 core implementation
#
# Author: Kevin Townsend
import click

from ..core import Core
from ..programmers import JLink, STLink


# DEVICE ID register value to name mapping
# See 'DEVICE_ID' in:
# LPC81x Series --> http://www.nxp.com/documents/user_manual/UM10601.pdf
# LPC82x Series --> http://www.nxp.com/documents/user_manual/UM10800.pdf
DEVICEID_CHIPNAME_LOOKUP = {
    0x00008100: 'LPC810M021FN8',
    0x00008110: 'LPC811M001JDH16',
    0x00008120: 'LPC812M101JDH16',
    0x00008121: 'LPC812M101JD20',
    0x00008122: 'LPC812M101JDH20 or LPC812M101JTB16',
    0x00008241: 'LPC824M201JHI33',
    0x00008221: 'LPC822M101JHI33',
    0x00008242: 'LPC824M201JDH20',
    0x00008222: 'LPC822M101JDH20'
}

# DEVICE ID register value to Segger '-device' name mapping
# See 'DEVICE_ID' in:
# LPC81x Series --> http://www.nxp.com/documents/user_manual/UM10601.pdf
# LPC82x Series --> http://www.nxp.com/documents/user_manual/UM10800.pdf
# Segger ID List: https://www.segger.com/jlink_supported_devices.html
DEVICEID_SEGGER_LOOKUP = {
    0x00008100: 'LPC810M021',
    0x00008110: 'LPC811M001',
    0x00008120: 'LPC812M101',
    0x00008121: 'LPC812M101',
    0x00008122: 'LPC812M101',
    0x00008241: 'LPC824M201',
    0x00008221: 'LPC822M101',
    0x00008242: 'LPC824M201',
    0x00008222: 'LPC822M101'
}


class LPC824(Core):
    """NXP LPC824 CPU."""
    # Note that the docstring will be used as the short help description.
    
    # Define the list of supported programmer types.  This should be a dict
    # with the name of a programmer (as specified in the --programmer option)
    # as the key and a tuple with the type, array of constructor positional
    # args, and dict of constructor keyword args as the value.
    programmers = {
        'jlink': (
            JLink, 
            ['Cortex-M0 r0p0, Little endian'],  # String to expect when connected.
            { 'params': '-device LPC824M201 -if swd -speed 1000' }
        ),
        # 'stlink': (
        #     STLink,
        #     [''],  # OpenOCD flash driver name for mass_erase.
        #     { 'params': '-f interface/stlink-v2.cfg -f target/???' }
        # )
    }
    
    def __init__(self):
        # Call base class constructor.
        super(LPC824, self).__init__()
    
    def info(self):
        """Display info about the device."""
        deviceid = self.programmer.readmem32(0x400483F8)
        click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:08X}'.format(deviceid))))
        # Try to detect the Segger Device ID string and print it if using JLink
        if isinstance(self.programmer, JLink):
            hwid = self.programmer.readmem32(0x400483F8)
            hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
            if '0x' not in hwstring:
                click.echo('Segger ID : {0}'.format(hwstring))
