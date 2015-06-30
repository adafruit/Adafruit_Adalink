import logging

import click

from . import __version__


@click.group(subcommand_metavar='CORE')
@click.option('-v', '--verbose', is_flag=True,
              help='Display verbose output like raw programmer commands.')
@click.version_option(version=__version__)
@click.pass_context
def main(ctx, verbose):
    """AdaLink ARM CPU Programmer.
    
    AdaLink can program different ARM CPUs using programming hardware such as
    the Segger JLink or STLink v2 (using OpenOCD).
    
    To use the JLink programmer you MUST have Segger's JLink tools installed
    and in the system path.
    
    To use the STLink programmer you MUST have OpenOCD 0.9.0+ installed.
    """
    # Initialize context as empty dict to store data sent from core to commands.
    ctx.obj = {}
    # Enable verbose debug output if required.
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

# Import all the cores.  Must be done after the main function above or else
# there will be a circular reference.  Also MUST be a * reference to ensure all
# the cores are dynamically loaded.
from .cores import *


if __name__ == '__main__':
    main()
