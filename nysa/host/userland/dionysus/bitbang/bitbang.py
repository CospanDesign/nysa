# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from array import array as Array
from pyftdi.pyftdi.ftdi import Ftdi

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

class BitBangController(object):
    PROGRAM_PIN     = 0x20
    SOFT_RESET_PIN    = 0x40

    def __init__(self, vendor_id, product_id, interface, debug = False):
        self.vendor = vendor_id
        self.product = product_id
        self.interface = interface
        self.f = Ftdi()
        self.debug = True
        self.f.open_bitbang(vendor_id, product_id, interface)


    def hiz(self):
        pass

    def is_in_bitbang(self):
        return self.f.bitbang_enabled()

    def read_pins(self):
        return self.f.read_pins()

    def read_program_pin(self):
        return (self.PROGAM_PIN & self.f.read_pins() > 0)

    def read_soft_reset_pin(self):
        return (self.SOFT_RESET_PIN & self.f.read_pins() > 0)

    def soft_reset_high(self):
        pins = self.f.read_pins()
        pins |= self.SOFT_RESET_PIN
        self.f.write_data(Array('B', [0x01, pins]))

    def soft_reset_low(self):
        pins = self.f.read_pins()
        pins &= ~(self.SOFT_RESET_PIN)
        self.f.write_data(Array('B', [0x01, pins]))

    def program_high(self):
        pins = self.f.read_pins()
        pins |= self.PROGRAM_PIN
        self.f.write_data(Array('B', [0x01, pins]))

    def program_low(self):
        pins = self.f.read_pins()
        pins &= ~(self.PROGRAM_PIN)
        self.f.write_data(Array('B', [0x01, pins]))

    def set_soft_reset_to_output(self):
        pin_dir = self.SOFT_RESET_PIN
        self.f.open_bitbang(self.vendor,
                            self.product,
                            self.interface,
                            direction = pin_dir)

    def set_program_pin_to_output(self):
        pin_dir = self.PROGRAM_PIN
        self.f.open_bitbang(self.vendor,
                            self.product,
                            self.interface,
                            direction = pin_dir)

    def set_pins_to_input(self):
        self.f.open_bitbang(self.vendor,
                            self.product,
                            self.interface,
                            direction = 0x00)

    def set_pins_to_output(self):
        self.f.open_bitbang(self.vendor,
                            self.product,
                            self.interface,
                            direction = 0xFF)

    def pins_on(self):
        """
        Set all pins high
        """
        self.f.write_data(Array('B', [0x01, 0xFF]))

    def pins_off(self):
        """
        Set all pins low
        """
        self.f.write_data(Array('B', [0x01, 0x00]))

