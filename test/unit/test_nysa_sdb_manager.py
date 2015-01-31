#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


class Test (unittest.TestCase):
    """Unit test for Nysa SDB Manager"""

    def setUp(self):
        self.dbg = False

    #SOM Functions
    def test_enumerate_device(self):
        """
        Go through all the devices and return a URN that will allow users
        to obtain a unique reference to a device

        """
        self.fail()

    def test_get_number_of_devices(self):
        self.fail()

    def test_find_device_from_ids(self, vendor_id = None, product_id = None):
        self.fail()

    def test_find_device_from_address(self, address):
        self.fail()

    def find_device_from_abi(self, abi_class = None, abi_major = None, abi_minor = None):
        self.fail()

    def test_read_sdb(self, n):
        self.fail()

    def test_is_wishbone_bus(self):
        self.fail()

    def test_is_axi_bus(self):
        self.fail()

    def test_is_storage_bus(self):
        self.fail()

    def test_get_total_memory_size(self):
        self.fail()

    #Device Functions
    def test_get_device_address(self, urn):
        self.fail()

    def test_get_device_size(self, urn):
        self.fail()

    def test_get_device_vendor_id(self, urn):
        self.fail()

    def test_get_device_product_id(self, urn):
        self.fail()

    def test_get_device_size(self, urn):
        self.fail()

    def test_get_device_abi_class(self, urn):
        self.fail()

    def test_get_device_abi_major(self, urn):
        self.fail()

    def test_get_device_abi_minor(self, urn):
        self.fail()

    #Board Function
    def test_get_board_name(self):
        self.fail()


