#! /usr/bin/python

# Copyright (c) 2014 name (dave.mccoy@cospandesign.com)

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


"""
I2C Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys

class I2CException(Exception):
    pass

class I2CToken(object):

    def __init__(self, token_type):
        super (I2CToken, self).__init__()
        self.token_type = "Unknown"
        self.write_data = 0x00
        self.read_data = 0x00
        self.require_ack = True
        self.address = 0x00
        self.reading = False
        self.set_type(token_type)

    def set_type(self, token_type):
        self.token_type = token_type
        if self.token_type == "Start":
            pass
        if self.token_type == "Stop":
            pass
        if self.token_type == "Repeat Start":
            pass
        if self.token_type == "Write":
            pass
        if self.token_type == "Read":
            pass

    def get_type(self):
        return self.token_type

    def set_write_data(self, data):
        if type(data) is not int:
            raise I2CException("Token data is not an integer, only integers can be set")
        self.write_data = data

    def set_read_data(self, data):
        if type(data) is not int:
            raise I2CException("Token data is not an integer, only integers can be set")
        self.read_data = data

    def get_write_data(self):
        return self.write_data

    def get_read_data(self):
        return self.read_data

    def data_require_ack(self, enable = True):
        #print "Require Ack: %s" % str(enable)
        self.require_ack = enable

    def is_ack_required(self):
        return self.require_ack

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def set_reading(self):
        self.reading = True

    def set_writing(self):
        self.reading = False

    def is_reading(self):
        return self.reading

