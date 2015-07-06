#!/bin/bash
set -e

# First update the apt package list and install required dependencies.
echo 'Installing dependencies (enter sudo password when prompted)...'
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libusb-1.0-0 libusb-1.0-0-dev libftdi1 libftdi-dev

# Next download the source and unpack it (deleting any old version of it).
echo 'Downloading OpenOCD 0.9.0 source...'
if [ -f openocd-0.9.0.tar.gz ];
then
  rm openocd-0.9.0.tar.gz
fi
wget http://downloads.sourceforge.net/project/openocd/openocd/0.9.0/openocd-0.9.0.tar.gz
if [ -d openocd-0.9.0 ];
then
  rm -rf openocd-0.9.0
fi
tar xvfz openocd-0.9.0.tar.gz

# Finally change to openocd directory to build and install it.
echo 'Building and installing OpenOCD 0.9.0...'
cd openocd-0.9.0
./configure
make
sudo make install

echo 'Successfully installed OpenOCD 0.9.0!'
cd ..
