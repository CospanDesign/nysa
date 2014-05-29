#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


"""
Script to probe
"""
__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import argparse
import sys
import os
import time
from array import array as Array


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))
import nysa

from dionysus.dionysus import Dionysus
from driver import gpio
from driver import i2c
from driver import i2s
from driver import spi
from driver import uart


devices = {
        "GPIO":gpio,
        "I2C":i2c,
        "I2S":i2s,
        "SPI":spi,
        "UART":uart
        }


DESCRIPTION = "\n" \
"\n"\
"usage: test_dionysus.py [options]\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tTest all cores available\n" \
"\t\ttest_dionysus.py\n"\
"\n"\
"\tTest only the slave specified\n" \
"\t\ttest_dionysus.py -t <name>\n" \
"\n"\
"\tList all cores that can be tested\n" \
"\t\ttest_dionysus.py -l\n" \
"\n"


debug = False

def test_memory(dyn, dev_index):
    print "Testing memory @ %d" % dev_index
    num = 0
    data_out = Array('B')
    size = dyn.get_device_size(dev_index)
    print "Size: 0x%08X" % size

    for i in range(0, ((size / 4) - 1)):
        num = 0x00
        data_out.append(num)

    print "Length of data out: 0x%08X" % len(data_out)
    print "Word Size: 0x%08X" % (size / 4)
    print "Clearing Memory"
    dyn.write_memory(0, data_out)

    print "Testing short write at the beginning of the memory"
    data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
    dyn.write_memory(0, data_out)

    print "Testing short read at the beginning of the memory"
    data_in = dyn.read_memory(0, 2)
    for i in range (len(data_out)):
        if data_in[i] != data_out[i]:
            print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))

    print "Testing short write at the end of memory"
    print "Writing to memory location: 0x%08X" % (size - 16)
    dyn.write_memory((size - 16), data_out)
    print "Reading from location: 0x%08X" % (size - 16)
    data_in = dyn.read_memory((size - 16), 2)

    for i in range (len(data_out)):
        if data_in[i] != data_out[i]:
            print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))


    data_out = Array('B')
    for i in range (0, size):
        data_out.append((i % 255))

    print "Writing 0x%08X bytes of data" % (len(data_out))
    start = time.time()
    dyn.write_memory(0, data_out)
    end = time.time()
    print "Write Time: %f" % (end - start)
    print "Reading 0x%08X bytes of data" % (len(data_out))
    start = time.time()
    data_in = dyn.read_memory(0, len(data_out) / 4)
    end = time.time()
    print "Read Time: %f" % (end - start)

    print "Comparing Values"
    fail = False
    fail_count = 0
    if len(data_out) != len(data_in):
        print "Data in lenght not equal to data_out length"
        print "\toutgoing: %d" % len(data_out)
        print "\tincomming: %d" % len(data_in)

    for i in range(len(data_out)):
        if int(data_out[i]) != int(data_in[i]):
            fail = True
            print "Mismatch at: {0:>8}: WRITE (Hex):[{0:>8}] Read (Hex): [{0:>8}]".format(
                        hex(i),
                        hex(data_out[i]),
                        hex(data_in[i]))
            if fail_count >= 16:
                break
            fail_count += 1

    if not fail:
        print "Memory Test Passed!"
    elif (fail_count == 0):
        print "Data length of data in and data out do not match"
    else:
        print "Failed: %d or more mismatched" % fail_count

def perform_unit_tests(dyn, core = None):
    """
    Perform unit tests on specified cores

    Args:
        dyn: dionysus object used to interface with the FPGA
        core: Core name specified as a string, if this is left blank or None
            then all the devices found on the bus will be tested (as long as
            there is a unit test specified)

    Returns:
        Nothing

    Raises:
        NysaCommError
    """
    pass

def list_cores(dyn):
    from nysa.host.userland.python import driver
    #Get a list of the devices from the DRT
    #Get a of devices found in Dionysus from the DRT
    #Go through the driver directory and find all the drivers available
    print "drivers: %s" % str(driver)
    pass

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = DESCRIPTION,
        epilog = EPILOG
    )
    debug = False
    parser.add_argument("-d", "--debug",
                        action='store_true',
                        help="Enable Debug messages")
    parser.add_argument("-m", "--memory",
                        action='store_true',
                        help="Test Memory")
    parser.add_argument("-l", "--list_devices",
                        action='store_true',
                        help="List the cores that can be tested")
    parser.add_argument("-t", "--test",
                        type = str,
                        nargs = 1,
                        default = "nothing",
                        help = "Test an individual core")

    args = parser.parse_args()

    if args.debug:
        print "Debug Enabled"
        debug = True

    dyn = None
    try:
        dyn = Dionysus(debug = debug)
    except IOError, ex:
        #print "PyFtdi IOError while openning: %s" % str(ex)
        print "Dionysus not found!"
        return
    except AttributeError, ex:
        #print "PyFtdi Attribute Error while openning: %s" % str(ex)
        print "Dionysus not found!"
        return

    #Open up Dionysus and read the DRT
    if dyn is None:
        print "Dionysus not found!"
        return

    dyn.ping()
    print "Reading DRT"
    dyn.read_drt()
    print "Printing DRT"
    dyn.pretty_print_drt()

    if args.memory:
        print "Test Memory"
        for i in range(dyn.get_number_of_devices()):
            if dyn.is_memory_device(i):
                test_memory(dyn, i)

    if args.list_devices:
        print "List the cores that can be tested"
        list_cores(dyn)
        sys.exit(0)

    if args.test[0].upper() in devices:
        dev_id = dyn.get_id_from_name(args.test[0].upper())
        #print "%s: Device id: %d" % (args.test[0].upper(), dev_id)
        dev_index = dyn.find_device(dev_id)
        devices[args.test[0].upper()].unit_test(dyn, dev_index)
    else:
        print "Nothing to test"

if __name__ == "__main__":
    main(sys.argv)


