#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import gpio
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

        print "Unit test!"

    def notest_gpio(self):
        '''
        urns = n.find_device(GPIO)
        if len(urns) == 0:
            print "Failed to find GPIO Device!\n"
            return
        gpio = GPIO(n, urns[0])

        print "Testing output ports (like LEDs)"

        print "Flashing all the outputs for one second"

        print "Set all the ports to outputs"
        gpio.set_port_direction(0xFFFFFFFF)

        print "Set all the values to 1s"
        gpio.set_port_raw(0xFFFFFFFF)
        time.sleep(1)
        print "Set all the values to 0s"
        gpio.set_port_raw(0x00000000)

        print "Reading inputs (Like buttons) in 2 second"
        gpio.set_port_direction(0x00000000)

        time.sleep(2)
        print "Read value: 0x%08X" % gpio.get_port_raw()
        print "Reading inputs (Like buttons) in 2 second"
        time.sleep(2)
        print "Read value: 0x%08X" % gpio.get_port_raw()

        print "Interrupts: 0x%08X" % gpio.get_interrupts()

        print "Testing Interrupts, setting interrupts up for positive edge detect"
        print "Interrupts: 0x%08X" % gpio.get_interrupts()
        gpio.set_interrupt_edge(0xFFFFFFFF)
        gpio.set_interrupt_enable(0xFFFFFFFF)

        print "Waiting for 5 seconds for the interrupts to fire"
        if gpio.wait_for_interrupts(5):
            print "Interrupt detected!\n"
            #if gpio.is_interrupt_for_slave():
            print "Interrupt for GPIO detected!"
            print "Interrupts: 0x%08X" % gpio.get_interrupts()
            print "Read value: 0x%08X" % gpio.get_port_raw()

        print "Interrupts: 0x%08X" % gpio.get_interrupts()
        '''
        pass


