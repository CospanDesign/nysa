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

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("debug")

        self.configure_device(uart.UART)

    def configure_device(self, driver):
        self.s.Debug("type of driver: %s" % str(driver))
        plat = ["", None, None]
        pscanner = PlatformScanner()
        platform_dict = pscanner.get_platforms()
        platform_names = platform_dict.keys()

        if "sim" in platform_names:
            #If sim is in the platforms, move it to the end
            platform_names.remove("sim")
            platform_names.append("sim")
        urn = None
        for platform_name in platform_names:
            if plat[1] is not None:
                break

            self.s.Debug("Platform: %s" % str(platform_name))

            platform_instance = platform_dict[platform_name](self.s)
            #self.s.Verbose("Platform Instance: %s" % str(platform_instance))

            instances_dict = platform_instance.scan()

            for name in instances_dict:

                #s.Verbose("Found Platform Item: %s" % str(platform_item))
                n = instances_dict[name]
                plat = ["", None, None]

                if n is not None:
                    self.s.Important("Found a nysa instance: %s" % name)
                    n.read_sdb()
                    #import pdb; pdb.set_trace()
                    if n.is_device_in_platform(driver):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.d = None
            return
        n = plat[2]
        self.n = n
        urn = n.find_device(driver)[0]
        self.d = driver(n, urn)
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a driver Device: %s" % urn)

    def test_uart(self):
        """Unit test for UART
        """
        if self.d is None:
            return
        if self.n.get_board_name() == "sim":
            self.s.Warning("Unable to run UART test with simulator")
            return

        self.d.set_control(0)
        self.s.Debug ("Testing UART config")
        baudrate = self.d.get_baudrate()
        self.s.Debug ("Initial baudrate = %d" % baudrate)
        self.s.Debug ("Setting baudrate to 115200")
        self.d.set_baudrate(115200)
        '''
        self.d.set_baudrate(57600)
        if self.d.get_baudrate() > (57600 - (57600 * .01)) and self.d.get_baudrate() < (57600 + (57600 * .01)) :
            self.s.Debug ("Baudrate is within 1% of target")
        else:
            self.s.Debug ("Baudrate is not correct!")

        self.s.Debug ("Reverting back to initial baudrate")
        self.d.set_baudrate(baudrate)

        self.s.Debug ("\tXXX: Cannot test hardware flow control!")
        '''
        self.s.Debug ("\tControl: 0x%08X" % self.d.get_control())

        self.s.Debug ("Writing a string")
        self.d.write_string("STEAM ROXORS THE BIG ONE!1!!\r\n")


        self.s.Debug ("disable all interrupts")
        self.d.disable_interrupts()
        self.s.Debug ("Testing receive interrupt")
        self.d.enable_read_interrupt()
        self.s.Debug ("\tControl: 0x%08X" % self.d.get_control())

        self.s.Debug ("Read: %s " % self.d.read_string(-1))
        self.d.get_status()

        self.s.Debug ("Waiting 5 second for receive interrupts")
        if self.d.wait_for_interrupts(10) > 0:
            #if self.d.is_interrupt_for_slave():
            self.s.Debug ("Found a read interrupt")

            self.s.Debug ("Read: %s" % self.d.read_string(-1))

        self.s.Debug ("After waiting for interupt")

        self.s.Debug ("\tControl: 0x%08X" % self.d.get_control())

        #self.d.disable_read_interrupt()

        self.s.Debug ("Testing write interrupt")
        self.d.enable_write_interrupt()
        self.s.Debug ("Waiting 1 second for write interrupts")
        #if self.d.wait_for_interrupts(1) > 0:
        #    if self.d.is_interrupt_for_slave():
        #        print "Found a write interrupt!"

        #self.d.disable_write_interrupt()

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

if __name__ == "__main__":
    unittest.main()

