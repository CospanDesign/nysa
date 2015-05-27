# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)

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


# -*- coding: utf-8 -*-

"""Sata Driver

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time
import i2c
import random

from array import array as Array

import driver
from driver import NysaDMAException
from driver import DMAWriteController
from driver import DMAReadController

#Register Constants
CONTROL                     = 0x00
STATUS                      = 0x01

COSPANDEISNG_SATA_ID        = 0x01

class SATAError(Exception):
    pass

class SATADriver(driver.Driver):

    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name("storage manager")

    @staticmethod
    def get_abi_minor():
        return COSPANDESIGN_SATA_ID

    def __init__(self, nysa, urn, debug = False):
        super(SATA, self).__init__(nysa, urn, debug)

