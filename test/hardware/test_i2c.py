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

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("debug")

        self.configure_device(i2c.I2C)

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


    def test_device(self):
        if self.d is None:
            return
        if self.n.get_board_name() == "sim":
            self.s.Warning("Unable to run Device test with simulator")
            return


        self.d.reset_i2c_core()

        '''
        print "Check if core is enabled"
        print "enabled: " + str(self.d.is_i2c_enabled())


        print "Disable core"
        self.d.enable_i2c(False)

        print "Check if core is enabled"
        print "enabled: " + str(self.d.is_i2c_enabled())
        print "Check if core is enabled"
        print "enabled: " + str(self.d.is_i2c_enabled())

        print "Check if interrupt is enabled"
        print "enabled: " + str(self.d.is_interrupt_enabled())

        print "Enable interrupt"
        self.d.enable_interrupt(True)
        print "Check if interrupt is enabled"
        print "enabled: " + str(self.d.is_interrupt_enabled())

        clock_rate = self.d.get_clock_rate()
        print "Clock Rate: %d" % clock_rate

        print "Get clock divider"
        clock_divider = self.d.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set clock divider to generate 100kHz clock"
        self.d.set_speed_to_100khz()

        print "Get clock divider"
        clock_divider = self.d.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set clock divider to generate 400kHz clock"
        self.d.set_speed_to_400khz()

        print "Get clock divider"
        clock_divider = self.d.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Set a custom clock divider to get 1MHz I2C clock"
        self.d.set_custom_speed(1000000)

        print "Get clock divider"
        clock_divider = self.d.get_clock_divider()
        print "Clock Divider: %d" % clock_divider

        print "Setting clock rate back to 100kHz"
        '''
        print "Enable core"
        self.d.enable_i2c(True)
        self.d.enable_interrupt(True)
        self.d.get_status()
        self.d.set_speed_to_100khz()

        print "Check if core is enabled"
        print "enabled: " + str(self.d.is_i2c_enabled())

        print "Check if interrupt is enabled"
        print "enabled: " + str(self.d.is_interrupt_enabled())



        #PMOD AD2 (this is used on PMODA with config file:
        #dionysus_i2c_pmod.json file
        #The following reads ADC Channel 0
        i2c_id = 0x28
        data   = Array('B', [0x15])

        self.d.write_to_i2c(i2c_id, data)

        #reading from I2C device
        #print "Reading from register"
        #data  = Array('B', [0x02])
        read_data = self.d.read_from_i2c(i2c_id, None, 2)
        print "Read Data: %s" % str(read_data)

if __name__ == "__main__":
    unittest.main()



