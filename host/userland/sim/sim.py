# -*- coding: utf-8 -*-
#
# This file is part of Nysa (http://ninja-ide.org).
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

from userland import nysa
import cocotb
import threading
from cocotb.triggers import Timer, Join, RisingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
from cocotb.result import ReturnValue, TestFailure
from cocotb.binary import BinaryValue


class NysaSim (nysa.Nysa):

    def __init__(self, dut, debug = False):
        self.dut = dut
        super (NysaSim, self).__init__(debug)
    def read(self, device_id, address, length = 1, mem_device = False):
        pass
    def write(self, device_id, address, data = None, mem_device = False):
        pass
    def wait_for_interrupts(self, wait_time = 1):
        pass
    def dump_core(self):
        pass
    def reset(self):
        pass
    def ping(self):
        pass

