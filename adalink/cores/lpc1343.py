# LPC1343 core implementation
#
# Author: Kevin Townsend
from ..jlink import JLink
from .core import Core
import os

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
    """LPC1343 core implementation."""

    def __init__(self):
        """Create instance of LPC1343 core."""
        # Initialize communication with the JLink device using LPC1343-specific
        # device type, SWD, and speed.
        # For a list of known devices for the J-Link see the following URI:
        # https://www.segger.com/jlink_supported_devices.html
        self._jlink = JLink(params='-device LPC1343 -if swd -speed 1000')

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

    def detect_segger_device_id(self):
        """Attempts to detect the Segger device ID string for the chip."""
        hwid = self._jlink.readreg32(0x400483F8)
        hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
        if "0x" not in hwstring:
            return hwstring
        else:
            return "Unknown!"

    def info(self):
        """Print information about the connected nRF51822."""
        # DEVICE ID = APB0 Base (0x40000000) + SYSCON Base (0x48000) + 3F4
        deviceid = self._jlink.readreg32(0x400483F4)
        print 'Device ID :', DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:08X}'.format(deviceid))
        print 'Segger ID :', self.detect_segger_device_id()

    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        # Run JLink and verify output has expected CPU type found.  Only a 'q'
        # command is sent to ensure J-Link runs and immediately quits (after
        # printing some debug output).
        output = self._jlink.run_commands(['q'])
        return output.find('Info: Found Cortex-M3 r2p0, Little endian.') != -1
