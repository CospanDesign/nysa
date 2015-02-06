#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import uart
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

        print "Unit test!"
        pass
        '''
        for name in get_platforms():
            try:
                self.n = find_board(name, status = s)
            except PlatformScannerException as ex:
                pass
        self.n.read_sdb()
        urns = self.n.find_device(I2C)
        self.simple_dev = MockGPIODriver(self.n, urns[0], False)
        s.set_level("error")
        '''

    def notest_uart(self):
        """Unit test for UART
        """
        """
        uart = UART(nysa, urn, debug = debug)
        #uart.reset()
        uart.set_control(0)
        print "Testing UART config"
        baudrate = uart.get_baudrate()
        print "Initial baudrate = %d" % baudrate
        print "Setting baudrate to 115200"
        uart.set_baudrate(115200)
        '''
        uart.set_baudrate(57600)
        if uart.get_baudrate() > (57600 - (57600 * .01)) and uart.get_baudrate() < (57600 + (57600 * .01)) :
            print "Baudrate is within 1% of target"
        else:
            print "Baudrate is not correct!"

        print "Reverting back to initial baudrate"
        uart.set_baudrate(baudrate)

        print "\tXXX: Cannot test hardware flow control!"
        '''
        print "\tControl: 0x%08X" % uart.get_control()

        print "Writing a string"
        uart.write_string("STEAM ROXORS THE BIG ONE!1!!\r\n")


        print "disable all interrupts"
        uart.disable_interrupts()
        print "Testing receive interrupt"
        uart.enable_read_interrupt()
        print "\tControl: 0x%08X" % uart.get_control()

        print "Read: %s " % uart.read_string(-1)
        uart.get_status()

        print "Waiting 5 second for receive interrupts"
        if uart.wait_for_interrupts(10) > 0:
            #if uart.is_interrupt_for_slave():
            print "Found a read interrupt"

            print "Read: %s" % uart.read_string(-1)

        print "After waiting for interupt"

        print "\tControl: 0x%08X" % uart.get_control()

        #uart.disable_read_interrupt()

        print "Testing write interrupt"
        uart.enable_write_interrupt()
        print "Waiting 1 second for write interrupts"
        #if uart.wait_for_interrupts(1) > 0:
        #    if uart.is_interrupt_for_slave():
        #        print "Found a write interrupt!"

        #uart.disable_write_interrupt()

        #print "Testing write"

        '''
        print "Writing the maximum amount of data possible"
        write_max = uart.get_write_available() - 2
        print "Max: %d" % write_max
        data_out = Array('B')
        num = 0
        try:
            for i in range (0, write_max):
                num = (i) % 256
                if (i / 256) % 2 == 1:
                    data_out.append( 255 - (num))
                else:
                    data_out.append(num)


        except OverflowError as err:
            print "Overflow Error: %d >= 256" % num
            sys.exit(1)
        uart.write_raw(data_out)

        print "Testing read: Type something"


        time.sleep(3)

        fail = False
        fail_count = 0
        data = uart.read_all_data()

        if len(data_out) != len(data):
            print "data_in length not equal to data_out length:"
            print "\totugoing: %d incomming: %d" % (len(data_out), len(data))
            fail = True

        else:
            for i in range (0, len(data_out)):
                if data[i] != data_out[i]:
                    fail = True
                    print "Mismatch at %d: READ DATA %d != WRITE DATA %d" % (i, data[i], data_out[i])
                    fail_count += 1


        if len(data) > 0:
            print "Read some data from the UART"
            print "data (raw): %s" % str(data)
            print "data (string): %s" % str(data.tostring())


        if not fail:
            print "UART test passed!"
        elif (fail_count == 0):
            print "Data length of data_in and data_out do not match"
        else:
            print "Failed: %d mismatches" % fail_count


        uart.write_raw(data_out)
        print "look for the status conditions"
        print "Status: " + hex(uart.get_status())

        if uart.is_read_overflow():
            print "Read overflow"

        '''
        """
        pass
