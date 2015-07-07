# Core base class
import click

from .errors import AdaLinkError


class HexInt(click.ParamType):
    """Custom click parameter type for an integer which can be specified as a
    hex value (starts with 0x...), octal (starts with 0), or decimal value.
    """
    name = 'integer (supports hex with 0x)'

    def convert(self, value, param, ctx):
        try:
            return int(value, 0)
        except ValueError:
            self.fail('%s is not a valid integer' % value, param, ctx)

    def __repr__(self):
        return 'INT'


class Core(click.Command):

    def __init__(self, name=None):
        # Default to the name of the class if one isn't specified.
        if name is None:
            name = self.__class__.__name__.lower()
        self.name = name
        # Build the standard list of parameters that a core can take.
        params = []
        params.append(click.Option(param_decls=['-p', '--programmer'],
                                   required=True,
                                   type=click.Choice(self.list_programmers()),
                                   help='Programmer type.'))
        params.append(click.Option(param_decls=['-w', '--wipe'],
                                   is_flag=True,
                                   help='Wipe flash memory before programming.'))
        params.append(click.Option(param_decls=['-i', '--info'],
                                   is_flag=True,
                                   help='Display information about the core.'))
        params.append(click.Option(param_decls=['-h', '--program-hex'],
                                   multiple=True,
                                   type=click.Path(exists=True),
                                   help='Program the specified .hex file. Can be specified multiple times.'))
        params.append(click.Option(param_decls=['-b', '--program-bin'],
                                   multiple=True,
                                   nargs=2,
                                   type=(click.Path(exists=True), HexInt()),
                                   metavar='PATH ADDRESS',
                                   help='Program the specified .bin file at the provided address. Address can be specified in hex, like 0x00FF.  Can be specified multiple times.'))
        super(Core, self).__init__(self.name, params=params, callback=self._callback,
                                   short_help=self.__doc__, help=self.__doc__)

    def _callback(self, programmer, wipe, info, program_hex, program_bin):
        # Create the programmer that was specified.
        programmer = self.create_programmer(programmer)
        # Check that programmer is connected to device.
        if not programmer.is_connected():
            raise AdaLinkError('Could not find {0}, is it connected?'.format(self.name))
        # Wipe flash memory if requested.
        if wipe:
            programmer.wipe()
        # Program the specified files.
        if len(program_bin) > 0:
            print 'Bangos'
            for f, addr in program_bin:
                print 'Talk', f, addr
        if len(program_hex) > 0:
            programmer.program(program_hex)
        # Display information if requested.
        if info:
            self.info(programmer)

    def list_programmers(self):
        """Return a list of the programmer names supported by this CPU.  These
        names will be exposed by the --programmer option values, and the chosen
        one will be passed to create_programmer."""
        raise NotImplementedError

    def create_programmer(self, programmer):
        """Create and return a programmer instance that will be used to program
        the core.  Must be implemented by subclasses!  The p
        """
        raise NotImplementedError

    def info(self, programmer):
        """Display information about the device.  Will be passed an instance
        of the programmer created by create_programmer.  The programmer can be
        used to read memory and use it to display information."""
        # Default implementation does nothing, subclasses should override.
        pass
