# nRF51822 core implementation
#
# Author: Tony DiCola
from ..jlink import JLink
from .core import Core
import os

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


class NRF51822(Core):
    """nRF51822 core implementation."""

    def __init__(self):
        """Create instance of nRF51822 core."""
        # Initialize communication with the JLink device using nRF51822-specific
        # device type, SWD, and speed.
        self._jlink = JLink(params='-device nrf51822_xxaa -if swd -speed 1000')

    def wipe(self):
        """Wipe clean the flash memory of the device.  Will happen before any
        programming if requested.
        """
        # Build list of commands to wipe memory.
        commands = []
        commands.append('r')              # Reset
        commands.append('sleep 500')      # Delay 500ms
        commands.append('w4 4001e504 2')  # NVIC erase enabled
        commands.append('w4 4001e50c 1')  # NVIC erase all
        commands.append('sleep 1000')     # Delay 1000ms
        commands.append('r')              # Reset
        commands.append('q')              # Quit
        # Run commands.
        self._jlink.run_commands(commands)

    def program(self, hex_files):
        """Program chip with provided list of hex files."""
        # Build list of commands to program hex files.
        commands = []
        commands.append('r')              # Reset
        commands.append('w4 4001e504 1')  # NVIC write enabled
        commands.append('r')              # Reset
        commands.append('sleep 1000')     # Delay 1000ms
        # Program each hex file.
        for f in hex_files:
            f = os.path.abspath(f)
            commands.append('loadfile "{0}"'.format(f))
        commands.append('sleep 1000')     # Delay 1000ms
        commands.append('r')              # Reset
        commands.append('q')              # Quit
        # Run commands.
        self._jlink.run_commands(commands)

    def detect_segger_device_id(self):
        """Attempts to detect the Segger device ID string for the chip."""
        hwid = self._jlink.readreg16(0x1000005C)
        hwstring = SEGGER_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))
        if "0x" not in hwstring:
            return hwstring
        else:
            return "Unknown!"

    def info(self):
        """Print information about the connected nRF51822."""
        # Get the HWID register value and print it.
        # Note for completeness there are also readreg32 and readreg8 functions 
        # available to use for reading register values too.
        hwid = self._jlink.readreg16(0x1000005C)
        print 'Hardware ID :', MCU_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))
        # Try to detect the Segger Device ID string
        seggerid = self.detect_segger_device_id()
        print 'Segger ID   :', seggerid
        # Get the SD firmware version and print it.
        sdid = self._jlink.readreg16(0x0000300C)
        print 'SD Version  :', SD_LOOKUP.get(sdid, 'Unknown! (0x{0:04X})'.format(sdid))
        # Get the BLE Address and print it.
        addr_high = (self._jlink.readreg32(0x100000a8) & 0x0000ffff) | 0x0000c000
        addr_low  = self._jlink.readreg32(0x100000a4)
        print 'Device Addr : {0:02X}:{1:02X}:{2:02X}:{3:02X}:{4:02X}:{' \
              '5:02X}'.format((addr_high >> 8) & 0xFF,
                              (addr_high) & 0xFF,
                              (addr_low >> 24) & 0xFF,
                              (addr_low >> 16) & 0xFF,
                              (addr_low >> 8) & 0xFF,
                              (addr_low & 0xFF))
        # Get device ID.
        did_high = self._jlink.readreg32(0x10000060)
        did_low  = self._jlink.readreg32(0x10000064)
        print 'Device ID   : {0:08X}{1:08X}'.format(did_high, did_low)

    def is_connected(self):
        """Return True if the CPU is connected, otherwise returns False."""
        # Run JLink and verify output has expected CPU type found.  Only a 'q'
        # command is sent to ensure J-Link runs and immediately quits (after
        # printing some debug output).
        output = self._jlink.run_commands(['q'])
        return output.find('Info: Found Cortex-M0 r0p0, Little endian.') != -1
