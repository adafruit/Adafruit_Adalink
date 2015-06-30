# LPC824 core implementation
#
# Author: Kevin Townsend
import click

from ..errors import AdaLinkError
from ..main import main
from ..programmers.jlink import JLink


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


@main.group(chain=True)  # chain = True means multiple subcommands can be sent.
@click.option('-p', '--programmer', required=True, help='Programmer type.',
              type=click.Choice(['jlink', 'stlink']))
# Note that core-specific parameters could be defined here, like a core subtype.
@click.pass_context
def lpc824(ctx, programmer):
    """NXP LPC824 CPU."""
    # Save the selected programmer in the context so commands can access it.
    if programmer == 'jlink':
        jlink = JLink(params='-device LPC824M201 -if swd -speed 1000')
        ctx.obj['programmer'] = jlink
        # Verify the CPU is connected.
        output = jlink.run_commands(['q'])
        if output.find('Info: Found Cortex-M0 r0p0, Little endian.') == -1:
            raise AdaLinkError('Could not find LPC824 connected to JLink!')
        # Grab the Segger device ID value.
        hwid = jlink.readmem32(0x400483F8)
        hwstring = DEVICEID_SEGGER_LOOKUP.get(hwid, '0x{0:08X}'.format(hwid))
        if '0x' not in hwstring:
            # Found a Segger device ID, save it in the context for reading later.
            ctx.obj['seggerid'] = hwstring
    elif programmer == 'stlink':
        raise NotImplementedError('Not implemented!')

@lpc824.command()
@click.pass_context
def wipe(ctx):
    """Wipe the flash memory of the device."""
    programmer = ctx.obj['programmer']
    programmer.wipe()

@lpc824.command()
@click.argument('file', type=click.Path(exists=True))
@click.pass_context
def program(ctx, file):
    """Program the provided hex file to the device.
    
    The path to the .hex file should be provided as the only argument.
    """
    programmer = ctx.obj['programmer']
    programmer.program([file])

@lpc824.command()
@click.pass_context
def info(ctx):
    """Display information about the device."""
    programmer = ctx.obj['programmer']
    deviceid = programmer.readmem32(0x400483F8)
    click.echo('Device ID : {0}'.format(DEVICEID_CHIPNAME_LOOKUP.get(deviceid,
                                               '0x{0:08X}'.format(deviceid))))
    # Try to detect the Segger Device ID string and print it if it was set.
    seggerid = ctx.obj.get('seggerid', None)
    if seggerid is not None:
        click.echo('Segger ID : {0}'.format(seggerid))
