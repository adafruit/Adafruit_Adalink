# LPC824 core implementation
#
# Author: Kevin Townsend
from adalink.jlink import JLink
from adalink.cores.core import Core
import os

# DEVICE ID register valueto name mapping
# See 'DEVICE_ID' in:
# LPC81x Series --> http://www.nxp.com/documents/user_manual/UM10601.pdf
# LPC82x Series --> http://www.nxp.com/documents/user_manual/UM10800.pdf
DEVICEID_LOOKUP = {
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


class LPC824(Core):
    """LPC824 core implementation."""

    def __init__(self):
        """Create instance of LPC824 core."""
        # Initialize communication with the JLink device using LPC824-specific
        # device type, SWD, and speed.
        # For a list of known devices for the J-Link see the following URI:
        # https://www.segger.com/jlink_supported_devices.html
        self._jlink = JLink(params='-device LPC824M201 -if swd -speed 1000')

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # Build list of commands to wipe memory.
        commands = []
        commands.append('erase')          # NVIC erase enabled
        commands.append('r')              # Reset
        commands.append('q')              # Quit
        # Run commands.
        self._jlink.run_commands(commands)

    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        # Build list of commands to program hex files.
        commands = []
        commands.append('erase')          # NVIC erase enabled
        # Program each hex file.
        for f in hex_files:
            f = os.path.abspath(f)
            commands.append('loadfile "{0}"'.format(f))
        commands.append('r')              # Reset
        commands.append('g')              # Run the MCU
        commands.append('q')              # Quit
        # Run commands.
        self._jlink.run_commands(commands)

    def info(self):
        """Print information about the connected nRF51822."""
        # DEVICE ID = APB0 Base (0x40000000) + SYSCON Base (0x48000) + 3F4
        deviceid = self._jlink.readreg32(0x400483F8)
        print 'Device ID :', DEVICEID_LOOKUP.get(deviceid, '0x{0:08X}'.format(
            deviceid))

    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        # Run JLink and verify output has expected CPU type found.  Only a 'q'
        # command is sent to ensure J-Link runs and immediately quits (after
        # printing some debug output).
        output = self._jlink.run_commands(['q'])
        return output.find('Info: Found Cortex-M0 r0p0, Little endian.') != -1
