# nRF51822 core implementation
#
# Author: Tony DiCola
import click

from ..errors import AdaLinkError
from ..main import main
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


@main.group(chain=True)  # chain = True means multiple subcommands can be sent.
@click.option('-p', '--programmer', required=True, help='Programmer type.',
              type=click.Choice(['jlink', 'stlink']))
# Note that core-specific parameters could be defined here, like a core subtype.
@click.pass_context
def nrf51822(ctx, programmer):
    """Nordic nRF51822 CPU."""
    if programmer == 'jlink':
        # Create JLink programmer and save it in the context so commands can
        # access it.
        jlink = JLink(params='-device nrf51822_xxaa -if swd -speed 1000')
        ctx.obj['programmer'] = jlink
        # Verify the CPU is connected.
        output = jlink.run_commands(['q'])
        if output.find('Info: Found Cortex-M0 r0p0, Little endian.') == -1:
            raise AdaLinkError('Could not find nRF51822 connected to JLink!')
        # Grab the Segger device ID value.
        hwid = jlink.readmem16(0x1000005C)
        hwstring = SEGGER_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))
        if '0x' not in hwstring:
            # Found a Segger device ID, save it in the context for reading later.
            ctx.obj['seggerid'] = hwstring
    elif programmer == 'stlink':
        # Create JLink programmer and save it in the context so commands can
        # access it.
        stlink = STLink('nrf51',
                        params='-f interface/stlink-v2.cfg -f target/nrf51.cfg')
        ctx.obj['programmer'] = stlink

@nrf51822.command()
@click.pass_context
def wipe(ctx):
    """Wipe the flash memory of the device."""
    programmer = ctx.obj['programmer']
    programmer.wipe()

@nrf51822.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def program(ctx, file):
    """Program the provided hex file to the device.
    
    The path to the .hex file should be provided as the only argument.
    """
    programmer = ctx.obj['programmer']
    programmer.program([file])

@nrf51822.command()
@click.pass_context
def info(ctx):
    """Display information about the device."""
    programmer = ctx.obj['programmer']
    # Get the HWID register value and print it.
    # Note for completeness there are also readmem32 and readmem8 functions 
    # available to use for reading memory values too.
    hwid = programmer.readmem16(0x1000005C)
    click.echo('Hardware ID : {0}'.format(MCU_LOOKUP.get(hwid, '0x{0:04X}'.format(hwid))))
    # Try to detect the Segger Device ID string and print it if it was set.
    seggerid = ctx.obj.get('seggerid', None)
    if seggerid is not None:
        click.echo('Segger ID   : {0}'.format(seggerid))
    # Get the SD firmware version and print it.
    sdid = programmer.readmem16(0x0000300C)
    click.echo('SD Version  : {0}'.format(SD_LOOKUP.get(sdid, 'Unknown! (0x{0:04X})'.format(sdid))))
    # Get the BLE Address and print it.
    addr_high = (programmer.readmem32(0x100000a8) & 0x0000ffff) | 0x0000c000
    addr_low  = programmer.readmem32(0x100000a4)
    click.echo('Device Addr : {0:02X}:{1:02X}:{2:02X}:{3:02X}:{4:02X}:{' \
               '5:02X}'.format((addr_high >> 8) & 0xFF,
                               (addr_high) & 0xFF,
                               (addr_low >> 24) & 0xFF,
                               (addr_low >> 16) & 0xFF,
                               (addr_low >> 8) & 0xFF,
                               (addr_low & 0xFF)))
    # Get device ID.
    did_high = programmer.readmem32(0x10000060)
    did_low  = programmer.readmem32(0x10000064)
    click.echo('Device ID   : {0:08X}{1:08X}'.format(did_high, did_low))
