#! /usr/bin/python

import unittest
import os
import sys
from inspect import isclass
import json

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir,
                "nysa"))

from host.userland.dionysus.spi_flash import serial_flash_manager


#Mock object
class SPI(object):
    def __init__(self, jedec_id):
        self.jedec_id = 0x17

    def exchange(self, command, length = 1):
        return  0

class Test (unittest.TestCase):
    """Unit test for the gen_sim_top.py"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                           os.pardir,
                           "nysa")
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_spi_flash_manager(self):
        #jedec_id = 0x17
        #spi = SPI(jedec_id = jedec_id)
        vendor = 0x0403
        product = 0x8530
        spi_manager = serial_flash_manager.SerialFlashManager(vendor, product, debug = False)

    def test_get_devices(self):
        vendor = 0x0403
        product = 0x8530
        spi_manager = serial_flash_manager.SerialFlashManager(vendor, product, debug = False)
        spi_manager.get_flash_device(debug = True)



if __name__ == "__main__":
  unittest.main()

