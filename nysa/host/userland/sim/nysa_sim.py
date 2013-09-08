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

import cocotb
import threading
from cocotb.triggers import Timer, Join, RisingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
from cocotb.result import ReturnValue, TestFailure
from cocotb.binary import BinaryValue

import nysa

class NysaSim (nysa.Nysa):

    def __init__(self, dut, debug = False):
        period = 10
        self.rest_length = 40

        self.dut    = dut
        super (NysaSim, self).__init__(debug)
        self.clk    = Clock(self.dut.clk, period)
        self.rst    = self.dut.rst

        self.rst    <=  0

        self.master_ready   = self.dut.sim_master_ready
        self.in_reset       = self.dut.sim_in_reset

        self.in_ready       = self.dut.sim_in_ready
        self.in_command     = self.dut.sim_in_command
        self.in_address     = self.dut.sim_in_address
        self.in_data        = self.dut.sim_in_data
        self.in_data_count  = self.dut.sim_in_data_count

        self.out_en         = self.dut.sim_out_en
        self.out_ready      = self.dut.sim_out_ready
        self.out_status     = self.dut.sim_out_status
        self.out_address    = self.dut.sim_out_address
        self.out_data       = self.dut.sim_out_data

        self.in_ready       <= 0
        self.in_reset       <= 0
        self.out_ready      <= 0

        self.in_command     <= 0
        self.in_address     <= 0
        self.in_data        <= 0
        self.in_data_count  <= 0

        self.clk.start()
        yield Timer(0)
        self.reset()

    @cocotb.coroutine
    def read(self, device_id, address, length = 1, mem_device = False):
        pass

    @cocotb.coroutine
    def write(self, device_id, address, data = None, mem_device = False):
        pass

    @cocotb.coroutine
    def wait_for_interrupts(self, wait_time = 1):
        pass

    @cocotb.coroutine
    def dump_core(self):
        pass

    @cocotb.coroutine
    def reset(self):
        self.rst            <=  0
        yield ClockCycles(self.clk, self.reset_length)
        self.rst            <= 1
        self.in_ready       <= 0
        self.in_reset       <= 0
        self.out_ready      <= 0

        self.in_command     <= 0
        self.in_address     <= 0
        self.in_data        <= 0
        self.in_data_count  <= 0
        yield ClockCycles(self.clk, self.reset_length)


        self.rst            <= 0
        yield ClockCycles(self.clk, self.reset_length)

    @cocotb.coroutine
    def ping(self):
        self.in_ready       <=  1

