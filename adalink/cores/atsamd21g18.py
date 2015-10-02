# Atmel ATSAMD21G18 core implementation.
# See chip summary at:
#   http://www.atmel.com/Images/Atmel-42181-SAM-D21_Summary.pdf
#
# Author: Tony DiCola
import os

import click

from ..core import Core
from ..programmers import JLink


class ATSAMD21G18(Core):
    """Atmel ATSAMD21G18 CPU."""
    # Note that the docstring will be used as the short help description.

    def __init__(self):
        # Call base class constructor--MUST be done!
        super(ATSAMD21G18, self).__init__()

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU."""
        return ['jlink']

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!
        """
        if programmer == 'jlink':
            return JLink('Cortex-M0 r0p1, Little endian',
                         params='-device ATSAMD21G18 -if swd -speed 1000')

    def info(self, programmer):
        """Display info about the device."""
        click.echo('Not implemented!')
