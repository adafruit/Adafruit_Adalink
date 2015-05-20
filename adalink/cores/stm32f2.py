# STM32f2xx core implementation
#
# Author: Kevin Townsend
from ..jlink import JLink
from .core import Core
import os

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
    """STM32f2xx core implementation."""

    def __init__(self):
        """Create instance of STM32f2xx core."""
        # Initialize communication with the JLink device using STM32f2xx-specific
        # device type, SWD, and speed.
        # For a list of known devices for the J-Link see the following URI:
        # https://www.segger.com/jlink_supported_devices.html
        self._jlink = JLink(params='-device STM32F205RG -if swd -speed 2000')

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # Build list of commands to wipe memory.
        commands = []
        commands.append('r')              # Reset
        commands.append('erase')          # NVIC erase enabled
        commands.append('r')              # Reset
        commands.append('q')              # Quit
        # Run commands.
        self._jlink.run_commands(commands)

    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        # Build list of commands to program hex files.
        commands = []
        commands.append('r')              # Reset

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
        hwid = self._jlink.readreg32(0xE0042000) & 0xFFF
        hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:03X}'.format(hwid))
        if "0x" not in hwstring:
            return hwstring
        else:
            return "Unknown!"

    def info(self):
        """Print information about the connected STM32f2xx."""
        # [0xE0042000] = CHIP_REVISION[31:16] + RESERVED[15:12] + DEVICE_ID[11:0]
        deviceid = self._jlink.readreg32(0xE0042000) & 0xFFF
        chiprev  = (self._jlink.readreg32(0xE0042000) & 0xFFFF0000) >> 16
        print 'Device ID :', DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                                   '0x{0:03X}'.format(deviceid))
        print 'Chip Rev  :', DEVICEID_CHIPREV_LOOKUP.get(chiprev,
                                                   '0x{0:04X}'.format(chiprev))
        print 'Segger ID :', self.detect_segger_device_id()

    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        # Run JLink and verify output has expected CPU type found.  Only a 'q'
        # command is sent to ensure J-Link runs and immediately quits (after
        # printing some debug output).
        output = self._jlink.run_commands(['q'])
        return output.find('Info: Found Cortex-M3 r2p0, Little endian.') != -1
