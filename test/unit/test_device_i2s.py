#!/usr/bin/python

import unittest
import json
import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import i2s
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("debug")

        self.configure_device(i2s.I2S)

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
        '''
        if self.n.get_board_name() == "sim":
            self.s.Warning("Unable to run Device test with simulator")
            return
        '''


        self.d.register_dump()
        self.s.Debug("Is self.d enabled: %s" % str(self.d.is_i2s_enabled()))
        self.s.Debug("Control: 0x%08X" % self.d.get_control())

        self.s.Debug("Enabling I2S...")
        self.d.enable_i2s(True)
        self.s.Debug("Control: 0x%08X" % self.d.get_control())

        self.s.Debug("Is self.d enabled: %s" % str(self.d.is_i2s_enabled()))
        self.s.Debug("Disable self.d...")
        self.d.enable_i2s(False)
        self.s.Debug("Is self.d enabled: %s" % str(self.d.is_i2s_enabled()))

        self.s.Debug("Sample Rate: %d" % self.d.get_sample_rate())
        self.s.Debug("Set custom sample rate to 44.1Khz")
        self.d.set_custom_sample_rate(44100)
        self.s.Debug("Sample Rate (may not match exactly): %d" % self.d.get_sample_rate())

        self.d.enable_i2s(True)
        self.s.Debug("Enable post sine wave test")
        self.d.enable_post_fifo_test(True)
        time.sleep(4)
        self.d.enable_post_fifo_test(False)

        self.s.Debug("Enable pre sine wave test")
        #self.d.enable_pre_fifo_test(True)
        #time.sleep(4)
        #self.d.enable_pre_fifo_test(False)
        #self.d.enable_i2s(False)


