#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import i2c
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

    def notest_i2c(self):
        dev_i2c = i2c.I2C(nysa, dev_id)

        dev_i2c.reset_i2c_core()

        '''
        print "Check if core is enabled"
        print "enabled: " + str(dev_i2c.is_i2c_enabled())


        print "Disable core"
        dev_i2c.enable_i2c(False)

        print "Check if core is enabled"
        print "enabled: " + str(dev_i2c.is_i2c_enabled())
        print "Check if core is enabled"
        print "enabled: " + str(dev_i2c.is_i2c_enabled())

        print "Check if interrupt is enabled"
        print "enabled: " + str(dev_i2c.is_interrupt_enabled())

        print "Enable interrupt"
        dev_i2c.enable_interrupt(True)
        print "Check if interrupt is enabled"
        print "enabled: " + str(dev_i2c.is_interrupt_enabled())

        clock_rate = dev_i2c.get_clock_rate()
        print "Clock Rate: %d" % clock_rate

        print "Get clock divider"
        clock_divider = dev_i2c.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set clock divider to generate 100kHz clock"
        dev_i2c.set_speed_to_100khz()

        print "Get clock divider"
        clock_divider = dev_i2c.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set clock divider to generate 400kHz clock"
        dev_i2c.set_speed_to_400khz()

        print "Get clock divider"
        clock_divider = dev_i2c.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set a custom clock divider to get 1MHz I2C clock"
        dev_i2c.set_custom_speed(1000000)

        print "Get clock divider"
        clock_divider = dev_i2c.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Setting clock rate back to 100kHz"
        '''
        print "Enable core"
        dev_i2c.enable_i2c(True)
        dev_i2c.enable_interrupt(True)
        dev_i2c.get_status()
        dev_i2c.set_speed_to_100khz()

        print "Check if core is enabled"
        print "enabled: " + str(dev_i2c.is_i2c_enabled())

        print "Check if interrupt is enabled"
        print "enabled: " + str(dev_i2c.is_interrupt_enabled())



        #PMOD AD2 (this is used on PMODA with config file:
        #dionysus_i2c_pmod.json file
        #The following reads ADC Channel 0
        i2c_id = 0x28
        data   = Array('B', [0x15])

        dev_i2c.write_to_i2c(i2c_id, data)

        #reading from I2C device
        #print "Reading from register"
        #data  = Array('B', [0x02])
        read_data = dev_i2c.read_from_i2c(i2c_id, None, 2)
        print "Read Data: %s" % str(read_data)


