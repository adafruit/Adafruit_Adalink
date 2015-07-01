# Core base class
import click

from .errors import AdaLinkError

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
                                   type=click.Choice(self.programmers.keys()),
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
        super(Core, self).__init__(self.name, params=params, callback=self._callback,
                                   short_help=self.__doc__, help=self.__doc__)
    
    def _callback(self, programmer, wipe, info, program_hex):
        # Create the programmer that was specified.
        programmer = self.programmers.get(programmer)
        self.programmer = programmer[0](*programmer[1], **programmer[2])
        # Check that programmer is connected to device.
        if not self.programmer.is_connected():
            raise AdaLinkError('Could not find {0}, is it connected?'.format(self.name))
        # Display information if requested.
        if info:
            self.info()
        # Wipe flash memory if requested.
        if wipe:
            self.programmer.wipe()
        # Program the specified files.
        if len(program_hex) > 0:
            self.programmer.program(program_hex)
            
    def info(self):
        """Display information about the device."""
        # Default implementation does nothing, subclasses should override.
        pass
