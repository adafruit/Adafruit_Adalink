# Adalink ARM CPU Tool

Tool to automate flashing ARM CPUs with new program code using a Segger J-link
or STMicro STLink V2 device.

Currently supported cores:
*   atsamd21g18
*   lpc824
*   lpc1343
*   nrf51822
*   nrf52832
*   nrf52840
*   stm32f2

## Installation

There are three options for installing and using adalink:

*   Use a pre-built standalone binary distribution.  See the releases tab for
    the current release for each platform (Windows, OSX).  You don't need
    Python installed for this option to work, but you will need [JLink](#install-j-link-tools) and/or
    [OpenOCD](#install-openocd) tools installed.  You will also need to manually add the downloaded
    adalink executable to your system path so the command is available from any
    terminal.

*   Download the source and run it directly with Python.  This is a good option
    if the binary distribution doesn't work and you don't want to install the
    code globally.  You will also need [JLink](#install-j-link-tools) and/or
    [OpenOCD](#install-openocd) tools installed.  Jump to the [Running Without Installation](#running-without-installation)
    section to learn more about this option.

*   Install from source using the setup.py script.  This is useful if you're
    developing or modifying adalink code.  You will need [JLink](#install-j-link-tools) and/or
    [OpenOCD](#install-openocd) tools installed.  Jump to the [Install from Source](#install-from-source)
    section to learn more about this option.

Once you've installed or downloaded a release of adalink see the [Usage](#usage)
section for information on how to use it.

### Running Without Installation

To run the tool without having to install it simply clone the repository, navigate
to the repository's folder in a terminal (i.e. the directory with the setup.py file)
and run:

    python -m adalink.main

This will invoke the program as if you ran the adalink command.  All the command
line parameters, etc. are the same and specified after the `-m adalink.main` part of
the command.

Note that you will still need JLink and/or OpenOCD executables in your path--see
the Install JLink and Install OpenOCD sections above.

In addition you might need to manually install the [click](http://click.pocoo.org/5/)
module.  Using pip run `sudo pip install click` (omit sudo on Windows) to install this
module, then try running adalink as describe above.

### Install from Source

On Linux and MacOS run:

    sudo python setup.py develop

On Windows run:

    python setup.py develop

**Note that currently the setuptools 'develop' mode is used because of an issue/bug under investigation.**

### Install J-Link Tools

To use the Segger J-Link programmer you must [install Segger's J-Link tools](https://www.segger.com/jlink-software.html).  Note that there is currently
no version of Segger's tools which will work on a Raspberry Pi--check out the
STLink V2 programmer if using the Pi.

Once the tools are installed you must make sure they are in your system path.
On Windows the tools are by default installed to C:\Program Files
(x86)\SEGGER\JLink_V496h so add that to your path.  On Linux and MacOSX the path
is the location of download.

To check if JLink's tools are in your path, on Linux/MacOSX try running `JLinkExe`
or on Windows try running `JLink` in a command Window.  If you receive a command
not found error then carefully check you have the JLink tools installed and in
your system path.

### Install OpenOCD

To use the STLink V2 programmer you must install OpenOCD version 0.9.0.  Below
are the easiest options for installing OpenOCD on your platform:

#### Debian, Ubuntu, and Raspbian (Raspberry Pi)

Run the included install_openocd_debian.sh script to download, compile, and
install OpenOCD 0.9.0 automatically.  After cloning this repository navigate to
it in a terminal and run:

    chmod +x install_openocd_debian.sh
    ./install_openocd_debian.sh

The script will download, compile, and install OpenOCD.  When if finishes you
should see a message such as:

    =====================================
    Successfully installed OpenOCD 0.9.0!
    =====================================

Note that on a Raspberry Pi that installation will take around 30 minutes to an hour
as the code is compiled.

#### Mac OSX

On Mac OSX the easiest way to install OpenOCD 0.9.0 is with the
[homebrew](http://brew.sh/) software installation tool.  After installing homebrew
open a terminal and execute:

    brew install openocd

If you already have homebrew installed make sure it has up to date formulas for
building software by first running:

    brew update

Then run the brew install command above to install openocd.  This will ensure you
get the latest 0.9.0 version of OpenOCD.

#### Windows

On Windows the easiest way to install OpenOCD is with an unofficial pre-built
binary package.  Download the [OpenOCD 0.9.0 package from here](http://www.freddiechopin.info/en/download/category/4-openocd),
open the archive (using [7zip](http://www.7-zip.org/)).  Then add the extracted
openocd-0.9.0\bin or \bin-x64 (if on a 64-bit operating system) path to your
system path.

When using the STLink V2 programmer with OpenOCD on Windows you will also need to
use [Zadig tool](http://zadig.akeo.ie/) to force Windows to use a libusb driver
for the STLink device.  Follow the [basic usage here](https://github.com/pbatard/libwdi/wiki/Zadig),
but look for an STLink device and install the libusbK driver for the device.  This
driver installation only needs to be done once for the STLink device.

### Uninstall

If you installed adalink using its setup.py you can uninstall it using the pip
package manager.  Note that if you are running adalink from a stand-alone binary
or directly from its source then you just need to delete the files to remove it.

You can install pip by downloading and executing the [get-pip.py script here](https://bootstrap.pypa.io/get-pip.py).

Then run the following to uninstall adalink:

    sudo pip uninstall adalink

Note on Windows the sudo part of the command should be omitted.

## Usage

Once installed run the following command to see the usage information:

    adalink --help

There are two command line parameters which are required when using adalink.  The
first is a positional argument that specifies the CPU core to program.  You can
see a full list of supported cores by running the `--help` command above.

The second required parameter is the `--programmer` option which chooses the
programming hardware to use to communicate with the chip.  Once you've chosen
a CPU core you can see the supported programmers for it by running the `--help`
option again, for example to see the supported programmers for the nRF51822 run:

    adalink nrf51822 --help

The --programmer option shows both the jlink and stlink options are available:

    -p, --programmer [jlink|stlink]
                                    Programmer type.  [required]

You can also see other options for the core which represent available actions
to perform, such as listing information or programming a hex file:

    -w, --wipe                      Wipe flash memory before programming.
    -i, --info                      Display information about the core.
    -h, --program-hex PATH          Program the specified .hex file. Can be
                                    specified multiple times.
    -b, --program-bin PATH ADDRESS  Program the specified .bin file at the
                                    provided address. Address can be specified
                                    in hex, like 0x00FF.  Can be specified
                                    multiple times.


To perform one of the actions invoke adalink with the core parameter, programmer
option, and the desired action option.  For example to wipe a nRF51822 board and
program it using a JLink with a bootloader, soft device, app, and app signature
hex file you can run:

    adalink nrf51822 --programmer jlink --wipe --program-hex bootloader.hex --program-hex soft_device.hex --program-hex app.hex --program-hex app_signature.hex

You can also issue the `--info` command to try to retrieve basic info about the
connected nRF51822 device, which can be done with the following command (again
assuming the JLink programmer):

    adalink nrf51822 --programmer jlink --info

Which should give you a response like the following (depending on the device
  connected to the J-Link):

    Hardware ID : QFACA10 (32KB)
    SD Version  : S110 8.0.0
    Device Addr : C1:99:FC:D9:8A:D1
    Device ID   : ****************

**Note:** Make sure the JLink device and board are connected and powered before running the command!

## Common Problems

### Windows Path Errors

If you get an error on Windows trying to run adalink (ex. `adalink nRF51822 --info`), you likely need to **add the Python Scripts folder** (ex `C:\PythonXX\Scripts`) to your system path so that Windows knows where to find the `adalink.exe` file generated by setup.py.

The exact path is displayed in the output when running setup.py, for example:

    Installing adalink-script.py script to C:\Python27\Scripts
    Installing adalink.exe script to C:\Python27\Scripts

If it isn't already present, you may also need to **add the J-Link binary folder** to your system path so that adalink can run JLink.exe, which is used to communicate with the J-Link via generated script files.

Depending on the version of the J-Link drivers you installed, the folder to add to your system path should resemble the following:

    C:\Program Files (x86)\SEGGER\JLink_V494f

### Can't find CPU core when using STLink programmer on Windows

If you receive an error that adalink can't find the desired CPU core when using
an STLink programmer on Windows you might not have the programmer setup with libusb
correctly.  Follow the steps in the OpenOCD Windows install section above to use
Zadig tool to install a libusb driver for the STLink device.

## Extending AdaLink

adalink is built with a modular structure in mind and can be extended to support
new CPUs and programmer types without much effort.  

### Adding new CPU cores

Look in the adalink/core.py file to see the abstract base class that each core
needs to inherit from and implement.  Each core implementation should be inside
the adalink/cores folder and the core should be imported explicitly inside the
adalink/cores/__init__.py file.

Each core needs to at a minimum implement these functions:

-   list_programmers - This function should return a list of strings that define
    the available programmers for the core.

-   create_programmer - This function will be called with the chosen programmer
    type (a string provided by list_programmers) and expects a programmer instance
    to be created and returned.  For example if a user chooses the jlink programmer
    option then create_programmer is called with 'jlink' as the parameter and the
    function should return a programmer instance that uses the JLink to program
    the core.

-   info - This function is called if the user runs the `--info` option.  The
    selected programmer instance is passed to the function and it can be used to
    read parts of the core memory and display them.  It is entirely up to each
    core to choose what information it reads and displays with the info function.
    The default info implementation will do nothing.

The logic to program and wipe the memory of a core is defined by the core's
programmers.  There are generic JLink and STLink programmer implementations available
and they can be subclassed by a core to provide a custom programmer that performs
core-specific commands to program or wipe a core.  See the nRF51822 core for an
example of building a STLink-specific core to program and wipe the nRF51822.

### Adding new Programmers

Look in the adalink/programmers/base.py file to see the abstract base class that
a programmer needs to implement.  You can also see the provided concrete programmer
implementations in the adalink/programmers directory, like jlink.py and stlink.py.

Each programmer needs to implement the following functions:

-   is_connected - This returns True if the programmers is connected to a CPU and
    False if not connected.

-   program - This function takes a list of hex file paths and will program them
    to the CPU.

-   wipe - This function will wipe the flash memory of the CPU.

-   readmem32, readmem16, readmem8 - This function takes an address and returns
    the 32, 16, or 8 bit value at that address.

To add support for a programmer to a core make sure the core's list_programmers
function returns a string that identifies the programmer, and the core's create_programmer
function builds an instance of that programmer when requested.

### Producing Binary releases

To build a standalone binary release for Windows, OSX, etc. you can use the
[PyInstaller](http://www.pyinstaller.org/) tool.  This tool will package up the
adalink source into an executable that can run without python or other dependencies
being installed.

To produce the binary first install PyInstaller (typically using pip).  Then
download this source repository for adalink, open a terminal, navigate to the
root of the source and run:

    pyinstaller --onefile adalink.py

This will point PyInstaller at simple adalink bootstrap script which helps it
find all the dependencies and package up a standalone executable.  When PyInstaller
finishes it will output the executable in the `dist` directory.
