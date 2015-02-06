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

from nysa.host.driver.gpio import GPIO
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("verbose")
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
                    if n.is_device_in_platform(GPIO):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.gpio = None
            return
        n = plat[2]
        urn = n.find_device(GPIO)[0]
        self.gpio = GPIO(n, urn)
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a GPIO Device: %s" % urn)


    def test_gpio(self):
        if self.gpio is None:
            self.s.Fatal("Cannot Run Test when no device is found!")
            return
        self.s.Info ("Testing output ports (like LEDs)")

        self.s.Info ("Flashing all the outputs for one second")

        self.s.Info ("Set all the ports to outputs")
        self.gpio.set_port_direction(0xFFFFFFFF)

        self.s.Info ("Set all the values to 1s")
        self.gpio.set_port_raw(0xFFFFFFFF)
        time.sleep(1)
        self.s.Info ("Set all the values to 0s")
        self.gpio.set_port_raw(0x00000000)

        self.s.Info ("Reading inputs (Like buttons) in 2 second")
        self.gpio.set_port_direction(0x00000000)

        time.sleep(2)
        self.s.Info ("Read value: 0x%08X" % self.gpio.get_port_raw())
        self.s.Info ("Reading inputs (Like buttons) in 2 second")
        time.sleep(2)
        self.s.Info ("Read value: 0x%08X" % self.gpio.get_port_raw())

        self.s.Info ("Interrupts: 0x%08X" % self.gpio.get_interrupts())

        self.s.Info ("Testing Interrupts, setting interrupts up for positive edge detect")
        self.s.Info ("Interrupts: 0x%08X" % self.gpio.get_interrupts())
        self.gpio.set_interrupt_edge(0xFFFFFFFF)
        self.gpio.set_interrupt_enable(0xFFFFFFFF)

        self.s.Info ("Waiting for 5 seconds for the interrupts to fire")
        if self.gpio.wait_for_interrupts(5):
            self.s.Info ("Interrupt detected!\n")
            #if self.gpio.is_interrupt_for_slave():
            self.s.Info ("Interrupt for GPIO detected!")
            self.s.Info ("Interrupts: 0x%08X" % self.gpio.get_interrupts())
            self.s.Info ("Read value: 0x%08X" % self.gpio.get_port_raw())

        self.s.Info ("Interrupts: 0x%08X" % self.gpio.get_interrupts())


