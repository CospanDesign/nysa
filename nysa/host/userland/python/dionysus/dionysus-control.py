#! /usr/bin/python

# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

""" Dionysus Controller

Module to perform low level communication with Dionysus

Features:
    -Sets the mode of port B from Aync to FT245 to SPI and back
    -Programs SPI PROM
    -Asserts/Deasserts GPIOs to do various FPGA controls
        -Initiate a program of the FPGA
        -Resets the internal state machine
    -Change the mode of the pinsto synchronous FT245 mode to acheive 25MBytes throughput
    -Geve the kernel control of the driver or take control away
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

""" Changelog:
02/04/2012
    added the feature to change to FIFO mode '-c'
    added the feature to change to config mode '-x'
05/16/2012
    added the "alt" command line feature that allows
    users to specify vendor and product ID
10/18/2013
    -Pep8ing the module and some cleanup
"""

import sys
import os
import string
import time
import argparse
from array import array as Array
from pyftdi.pyftdi.ftdi import Ftdi
from fifo.fifo import FifoController
from spi_flash import serial_flash_manager
from bitbang.bitbang import BitBangController

sys.path.append(os.path.join(os.path.dirname(__file__), "spi_flash"))
sys.path.append(os.path.join(os.path.dirname(__file__), "bitbang"))
sys.path.append(os.path.join(os.path.dirname(__file__), "fifo"))

DESCRIPTION= "\n" \
" \n"
"\n"\
"usage: dionysus-control.py [options] <filename>\n"\
"\n"\
"filename: bin file to program the FPGA\n"\
"\n"\


EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tupload the bin file and program the FPGA\n"\
"\t\tdionysus-control.py bitfile.bin\n"\
"\n"\
"\treset the FPGA and program without loading a new bin file\n"\
"\t\tdionysus-control.py -p\n"\
"\n"\
"\treset the FPGA and program without loading a new bin file on an alternate FTDI VID:PID\n"\
"\t\tdionysus-control.py --alt=0403:6010 -p\n"\
"\n"\
"\treset the internal state machine of the FPGA\n"\
"\t\tdionysus-control.py -r\n"\
"\n"\
"\tread back the .bin file, all files will be 2MB\n"\
"\t\tdionysus-control.py -z outfile.txt\n"\
"\n"\
"Author: Dave McCoy (dave.mccoy@cospandesign.com)\n"\
"\n"\


class DionysusController():

    def __init__(self, vendor_id = 0x0403, product_id = 0x8530, debug = False):
        self.vendor = vendor_id
        self.product = product_id
        self.debug = debug
        self.fifo = FifoController(vendor_id, product_id)

    def write_bin_file(self, filename):
        """ write_bin_file

        Write a binary file to the the SPI Prom

        Args:
            filename (String): Path to FPGA Binary (bin) image

        Returns (boolean):
            True: Successfully programmed
            False: Failed to program

        Raises:
            IOError:
                Failed to open binary file      
        """
        binf = ""

        f = open(filename, "r")
        binf = f.read()
        f.close()
        #Allow the users to handle File Errors

        #Open the SPI Flash Device
        manager = serial_flash_manager.SerialFlashManager(self.vendor, self.product, 2)
        flash = manager.get_flash_device()

        #Print out the device was found
        print "Found: %s" % str(flash)

        #Erase the flash
        print "Erasing the SPI Flash device, this can take a minute or two..."
        flash.bulk_erase()
        #Write the binary file
        print "Flash erased, writing binary image to PROM"
        flash.write(0x00, binf)

        #Verify the data was read
        binf_rb = flash.read(0x00, len(binf))
        binf_str = binf_rb.tostring()

        del flash
        del manager

        if binf_str != binf:
            return False
        return True

    def read_bin_file(self, filename):
        """
        Read the binary image from the SPI Flash

        Args:
            filename (String): Path to the filename where the SPI image will
                be written to

        Returns:
            Nothing

        Raises:
            IOError:
                Problem openning file to write to
        """
        manager = serial_flash_manager.SerialFlashManager(self.vendor, self.product, 2)
        flash = manager.get_flash_device()

        #Don't know how long the binary file is so we need to read the entire
        #Image

        binf_rb = flash.read(0x00, len(flash))
        f = open(filename, "w")
        binf_rb.tofile(f)
        f.close()


    def program(self, debug = False):
        """
        Send a program signal to the board, the FPGA will attempt to read the
        binary image file from the SPI prom. If successful the 'done' LED will
        illuminate

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """
        bbc = BitBangController(self.vendor, self.product, 2)
        if debug:
            print "Set signals to input"
        bbc.set_pins_to_input()
        bbc.set_pins_to_output()
        bbc.program_high()
        time.sleep(.5)
        bbc.program_low()
        time.sleep(.2)
        bbc.program_high()
        bbc.pins_on()
        bbc.set_pins_to_input()

    def reset(self):
        """
        Send a reset signal to the board, this is the same as pressing the
        'reset' button

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """
        bbc = BitBangController(self.vendor, self.product, 2)
        bbc.set_soft_reset_to_output()
        bbc.soft_reset_high()
        time.sleep(.2)
        bbc.soft_reset_low()
        time.sleep(.2)
        bbc.soft_reset_high()
        bbc.pins_on()
        bbc.set_pins_to_input()


    def set_sync_fifo_mode(self):
        """
        Change the mode of the FIFO to a synchronous FIFO

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing

        """
        self.fifo.set_sync_fifo()

    def set_debug_mode(self):
        """
        Change the mode of the FIFO to a asynchronous FIFO

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """

        self.fifo.set_async_fifo()


    def open_dev(self):
        """_open_dev

        Open an FTDI Communication Channel

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Exception
        """
        self.dev = Ftdi()
        frequency = 30.0E6
        latency  = 4
        self.dev.open(self.vendor, self.product, 0)

        #Drain the input buffer
        self.dev.purge_buffers()

        #Reset
        #Enable MPSSE Mode
        self.dev.set_bitmode(0x00, Ftdi.BITMODE_SYNCFF)


        #Configure Clock
        frequency = self.dev._set_frequency(frequency)

        #Set Latency Timer
        self.dev.set_latency_timer(latency)

        #Set Chunk Size
        self.dev.write_data_set_chunksize(0x10000)
        self.dev.read_data_set_chunksize(0x10000)

        #Set the hardware flow control
        self.dev.set_flowctrl('hw')
        self.dev.purge_buffers()

    def ping (self):
        """ping

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        data = Array('B')
        data.extend([0xCD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        if self.debug:
            print "Sending ping...",
        self.dev.write_data(data)

        #Set up a response
        rsp = Array('B')
        temp = Array('B')

        timeout = time.time() + 1

        while time.time() < timeout:
            response = self.dev.read_data(5)
            if self.debug:
                print ".",
            rsp = Array ('B')
            rsp.fromstring(response)
            temp.extend(rsp)
            if 0xDC in rsp:
                if self.debug:
                    print "Response to Ping"
                    print "Resposne: %s" % str(temp)
                break

        if not 0xDC in rsp:
            if self.debug:
                print "ID byte not found in response"

        index = rsp.index (0xDC) + 1
        read_data = Array('B')
        read_data.extend(rsp[index:])

        num = 3 - index
        read_data.fromstring(self.dev.read_data(num))
        if self.debug:
            print "Success"

        return

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = DESCRIPTION,
        epilog = EPILOG
    )

    debug = False
    vendor_id = 0x0403
    product_id = 0x8530
    dc = None

    #Add the supported commands
    parser.add_argument("-a", "--alt",
                        type = str, nargs=1,
                        default="0x0403:0x8530",
                        help="Alternate Vendor and Product ID (in hex)")
    parser.add_argument("-d", "--debug",
                        action='store_true',
                        help="Output test debug information")
    parser.add_argument("-r", "--reset",
                        action='store_true',
                        help="Reset the FPGA image (this is the same as pressing the reset button)")
    parser.add_argument("-p", "--program",
                        action='store_true',
                        help="Program the FPGA image (this is the same as pressing the program button)")
    parser.add_argument("-c", "--comm",
                        action='store_true',
                        help="Change the comm mode to use the high speed FIFO")
    parser.add_argument("-x", "--config",
                        action='store_true',
                        help="Change the comm mode to configuration mode (programming and button control)")
    parser.add_argument("--ping",
                        action='store_true',
                        help="Send a ping command to Dionysus and wait for a response")
    #parser.add_argument("-z", "--read_back",
    #                    type = str, 
    #                    nargs=1,
    #                    default="0x0403:0x8530",
    #                    help="Readback the .bin image to the filename given")
    parser.add_argument("bin",
                        type = str, 
                        nargs='?', 
                        default="nothing", 
                        help = "Binary file to load into the SPI Prom")
   
    #Parse out the arguments
    args = parser.parse_args()

    if args.debug:
        print "Debug Enabled"
        debug = True

    #different vendor and or product ID
    if args.alt:
        vendor_id = string.atoi(args.alt.partition(":")[0], 16)
        product_id = string.atoi(args.alt.partition(":")[2], 16)

    dc = DionysusController(vendor_id, product_id)

    #Program the FPGA
    if args.program:
        print "Send program signal to FPGA"
        dc.program(debug)
        sys.exit()

    #Resetting the board
    if args.reset:
        print "Sending Reset to FPGA Image"
        dc.reset()
        sys.exit()

    #Change to Synchronous FIFO Mode
    if args.comm:
        print "Change to High Speed Communication mode"
        dc.set_sync_fifo_mode()
        sys.exit()

    #Change to Configuration Mode
    if args.config:
        print "Change to configuration mode"
        dc.set_debug_mode()
        sys.exit()

    if args.ping:
        print "Sending a ping request to Dionysus"
        dc.open_dev()
        dc.reset()
        dc.ping()
        sys.exit()

    #Read back the FPGA image
    #if args.read_back:
    #    print "Read back the bin file from the flash"
    #    dc.read_bin_file(args.read_back)
    #    sys.exit()

    #Go into configuration mode to program the FPGA
    dc.set_debug_mode() 
    print "Uploading FPGA Binary File"
    if args.bin[0] == "nothing":
        print "No binary file to upload"
        sys.exit()

    if not dc.write_bin_file(args.bin):
        print "Failed"
        sys.exit(2)

    print "Success!"
    print "Sending Program Signal"
    dc.program()
    time.sleep(1)
    print "Send a reset signal to reset the internal state machine"
    dc.reset()

    dc.set_sync_fifo_mode()
    #Attempt to read once to flush outthe communication channel
    dc.open_dev()
    dc.reset()
    #This will probably Fail but this will flush out the controllers problem
    dc.ping()
    dc.reset()

if __name__ == "__main__":
    main(sys.argv)

