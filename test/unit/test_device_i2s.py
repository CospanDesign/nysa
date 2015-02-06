#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import i2s
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

    def notest_i2s(self):
        """unit_test

        Run the unit test for the I2S
        """
        pass
        '''

        print "I2S Unit Test"
        dev_index = 0
        try:
            dev_index = n.find_device(I2S.get_core_id())
        except NysaError, e:
            print "Failed to find device on bus"
            return

        i2s = I2S(n, dev_index, debug = False)
        i2s.register_dump()
        print "Is i2s enabled: %s" % str(i2s.is_i2s_enabled())
        print "Control: 0x%08X" % i2s.read_register(CONTROL)

        print "Enabling I2S..."
        i2s.enable_i2s(True)
        print "Control: 0x%08X" % i2s.read_register(CONTROL)

        print "Is i2s enabled: %s" % str(i2s.is_i2s_enabled())
        print "Disable i2s..."
        i2s.enable_i2s(False)
        print "Is i2s enabled: %s" % str(i2s.is_i2s_enabled())

        print "Sample Rate: %d" % i2s.get_sample_rate()
        print "Set custom sample rate to 44.1Khz"
        i2s.set_custom_sample_rate(44100)
        print "Sample Rate (may not match exactly): %d" % i2s.get_sample_rate()

        i2s.enable_i2s(True)
        print "Enable post sine wave test"
        i2s.enable_post_fifo_test(True)
        time.sleep(4)
        i2s.enable_post_fifo_test(False)

        print "Enable pre sine wave test"
        #i2s.enable_pre_fifo_test(True)
        #time.sleep(4)
        #i2s.enable_pre_fifo_test(False)
        #i2s.enable_i2s(False)
        '''


