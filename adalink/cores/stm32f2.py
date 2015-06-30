# STM32f2xx core implementation
#
# Author: Kevin Townsend
import click

from ..errors import AdaLinkError
from ..main import main
from ..programmers.jlink import JLink


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


@main.group(chain=True)  # chain = True means multiple subcommands can be sent.
@click.option('-p', '--programmer', required=True, help='Programmer type.',
              type=click.Choice(['jlink', 'stlink']))
# Note that core-specific parameters could be defined here, like a core subtype.
@click.pass_context
def stm32f2(ctx, programmer):
    """STMicro STM32F2 CPU."""
    # Save the selected programmer in the context so commands can access it.
    if programmer == 'jlink':
        jlink = JLink(params='-device STM32F205RG -if swd -speed 2000')
        ctx.obj['programmer'] = jlink
        # Verify the CPU is connected.
        output = jlink.run_commands(['q'])
        if output.find('Info: Found Cortex-M3 r2p0, Little endian.') == -1:
            raise AdaLinkError('Could not find STM32F2 connected to JLink!')
        # Grab the Segger device ID value.
        hwid = jlink.readmem32(0xE0042000) & 0xFFF
        hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:03X}'.format(hwid))
        if '0x' not in hwstring:
            # Found a Segger device ID, save it in the context for reading later.
            ctx.obj['seggerid'] = hwstring
    elif programmer == 'stlink':
        raise NotImplementedError('Not implemented!')

@stm32f2.command()
@click.pass_context
def wipe(ctx):
    """Wipe the flash memory of the device."""
    programmer = ctx.obj['programmer']
    programmer.wipe()

@stm32f2.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def program(ctx, file):
    """Program the provided hex file to the device.
    
    The path to the .hex file should be provided as the only argument.
    """
    programmer = ctx.obj['programmer']
    programmer.program([file])

@stm32f2.command()
@click.pass_context
def info(ctx):
    """Display information about the device."""
    programmer = ctx.obj['programmer']
    # [0xE0042000] = CHIP_REVISION[31:16] + RESERVED[15:12] + DEVICE_ID[11:0]
    deviceid = programmer.readmem32(0xE0042000) & 0xFFF
    chiprev  = (programmer.readmem32(0xE0042000) & 0xFFFF0000) >> 16
    click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                               '0x{0:03X}'.format(deviceid))))
    click.echo('Chip Rev  : {0}'.format(DEVICEID_CHIPREV_LOOKUP.get(chiprev,
                                               '0x{0:04X}'.format(chiprev))))
    # Try to detect the Segger Device ID string and print it if it was set.
    seggerid = ctx.obj.get('seggerid', None)
    if seggerid is not None:
        click.echo('Segger ID : {0}'.format(seggerid))
