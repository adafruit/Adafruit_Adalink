# Adalink main entry point for PyInstaller.
#
# This is necessary because pointing PyInstaller at the adalink.main module
# directly will produce an executable that doesn't work (it fails to resolve
# the relative imports).  Instead this module serves as a simple 'bootstrap'
# that imports adalink and calls its main without any relative imports.
#
# You don't need or want to call this script directly, it's only for pointing
# PyInstaller at to produce a standalone executable!
#
# Author: Tony DiCola
import adalink.main


if __name__ == '__main__':
    adalink.main.main()
