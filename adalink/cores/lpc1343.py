# LPC1343 core implementation
#
# Author: Kevin Townsend
import click

from ..errors import AdaLinkError
from ..main import main
from ..programmers.jlink import JLink


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


@main.group(chain=True)  # chain = True means multiple subcommands can be sent.
@click.option('-p', '--programmer', required=True, help='Programmer type.',
              type=click.Choice(['jlink', 'stlink']))
# Note that core-specific parameters could be defined here, like a core subtype.
@click.pass_context
def lpc1343(ctx, programmer):
    """NXP LPC1343 CPU."""
    # Save the selected programmer in the context so commands can access it.
    if programmer == 'jlink':
        jlink = JLink(params='-device LPC1343 -if swd -speed 1000')
        ctx.obj['programmer'] = jlink
        # Verify the CPU is connected.
        output = jlink.run_commands(['q'])
        if output.find('Info: Found Cortex-M3 r2p0, Little endian.') == -1:
            raise AdaLinkError('Could not find LPC1343 connected to JLink!')
        # Grab the Segger device ID value.
        hwid = jlink.readmem32(0x400483F8)
        hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
        if '0x' not in hwstring:
            # Found a Segger device ID, save it in the context for reading later.
            ctx.obj['seggerid'] = hwstring
    elif programmer == 'stlink':
        raise NotImplementedError('Not implemented!')

@lpc1343.command()
@click.pass_context
def wipe(ctx):
    """Wipe the flash memory of the device."""
    programmer = ctx.obj['programmer']
    programmer.wipe()

@lpc1343.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def program(ctx, file):
    """Program the provided hex file to the device.
    
    The path to the .hex file should be provided as the only argument.
    """
    programmer = ctx.obj['programmer']
    programmer.program([file])

@lpc1343.command()
@click.pass_context
def info(ctx):
    """Display information about the device."""
    programmer = ctx.obj['programmer']
    # DEVICE ID = APB0 Base (0x40000000) + SYSCON Base (0x48000) + 3F4
    deviceid = programmer.readmem32(0x400483F4)
    click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                               '0x{0:08X}'.format(deviceid))))
    # Try to detect the Segger Device ID string and print it if it was set.
    seggerid = ctx.obj.get('seggerid', None)
    if seggerid is not None:
        click.echo('Segger ID : {0}'.format(seggerid))
