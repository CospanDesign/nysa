""" uart

Concrete interface for Nysa on the uart board
"""

__author__ = 'you@example.com'

import sys
import os
import time
import string
from array import array as Array

from nysa.cbuilder.sdb import SDBError
from nysa.host.nysa import Nysa
from nysa.host.nysa import NysaError
from nysa.host.nysa import NysaCommError

import cocotb
import threading
from cocotb.triggers import Timer
from cocotb.triggers import Join
from cocotb.triggers import RisingEdge
from cocotb.triggers import ReadOnly
from cocotb.triggers import FallingEdge
from cocotb.triggers import ReadWrite
from cocotb.triggers import Event

from cocotb.result import ReturnValue
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb import bus
import json
from collections import OrderedDict
import cocotb.monitors

#from nysa.host.nysa import Nysa
from sim.sim import FauxNysa

from nysa.ibuilder.lib.gen_scripts.gen_sdb import GenSDB
from nysa.host.nysa import NysaCommError
from nysa.common.status import Status

CLK_PERIOD = 10
RESET_PERIOD = 20



class NysaSimUart(Nysa):

    def __init__(self, dut, uart_if, sim_config, period = CLK_PERIOD, user_paths = [], status = None):
        self.dev_dict                              = json.load(open(sim_config), object_pairs_hook = OrderedDict)
        Nysa.__init__(self, Status())
        self.s.set_level('verbose')
        self.user_paths = user_paths
        self.comm_lock = cocotb.triggers.Lock('comm')
        self.dut                              = dut
        cocotb.fork(Clock(dut.clk, period).start())
        gd = GenSDB()
        self.rom = gd.gen_rom(self.dev_dict, user_paths = self.user_paths, debug = False)

        self.uart = uart_if
        self.response = Array('B')

    @cocotb.coroutine
    def wait_clocks(self, num_clks):
        for i in range(num_clks):
            yield RisingEdge(self.dut.clk)

    def read_sdb(self):
        """read_sdb

        Read the contents of the DRT

        Args:
          Nothing

        Returns (Array of bytes):
          the raw DRT data, this can be ignored for normal operation

        Raises:
          Nothing
        """
        self.s.Verbose("entered")
        gd = GenSDB()
        self.rom = gd.gen_rom(self.dev_dict, user_paths = self.user_paths, debug = False)

        return self.nsm.read_sdb(self)

    def read(self, address, length = 1, disable_auto_inc = False):
        if (address * 4) + (length * 4) <= len(self.rom):
            length *= 4
            address *= 4

            ra = Array('B')
            for count in range (0, length, 4):
                ra.extend(self.rom[address + count :address + count + 4])
            #print "ra: %s" % str(ra)
            return ra

        mem_device = False
        if self.mem_addr is None:
            self.mem_addr = self.nsm.get_address_of_memory_bus()

        if address >= self.mem_addr:
            address = address - self.mem_addr
            mem_device = True

        self._read(address, length, mem_device)
        return self.response


    @cocotb.coroutine
    def _read(self, address, length = 1, disable_auto_inc = False):

        self.dut.log.info("read response: %s" % str(read_rsp))
        read_cmd = "L%0.7X00000002%0.8X00000000"
        read_cmd = (read_cmd) % (length, address)
        yield(self.uart.read)(32 + (length * 8))
        read_rsp = self.read_data()

        self.response = Array('B')
        if len(read_rsp) > 0:
            for i in range(0, length + 1):
                value = Array('B', read_rsp[(24 + (i * 8)):(32 + (i * 8))])
                self.response.extend(value)

    def get_data(self):
        return self.response

    @cocotb.coroutine
    def write(self, address, data, disable_auto_inc = False):
        """write

        Generic write command usd to write data to a Nysa image

        Args:
            address (int): Address of the register/memory to read
            data (array of unsigned bytes): Array of raw bytes to send to the
                                           device
            disable_auto_inc (bool): if true, auto increment feature will be disabled
        Returns:
            Nothing

        Raises:
            AssertionError: This function must be overriden by a board specific
                implementation
        """
        self.dut.log.info("write value: %s" % str(read_rsp))
        if not isinstance (data, list):
            data = [data]
        length = len(data) - 1
        write_cmd = "L%0.7X00000001%0.8X"
        write_cmd = (write_cmd) % (length, address)
        yield self.uart.write(write_cmd)
        write_rsp = self.uart.read(32)

    def ping(self):
        """ping

        Pings the Nysa image

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: When a failure of communication is detected
        """
        self.uart.write("L0000000000000000000000000000000")
        ping_string = self.uart.read(32)

    @cocotb.coroutine
    def reset(self):
        """reset

        Software reset the Nysa FPGA Master, this may not actually reset the
        entire FPGA image

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: A failure of communication is detected
        """
        yield(self.comm_lock.acquire())
        #print "Reset Acquired Lock"
        yield(self.wait_clocks(RESET_PERIOD / 2))

        self.dut.rst            <= 1
        #self.dut.log.info("Sending Reset to the bus")
        self.dut.in_ready       <= 0
        self.dut.out_ready      <= 0

        self.dut.in_command     <= 0
        self.dut.in_address     <= 0
        self.dut.in_data        <= 0
        self.dut.in_data_count  <= 0
        yield(self.wait_clocks(RESET_PERIOD / 2))
        self.dut.rst            <= 0
        yield(self.wait_clocks(RESET_PERIOD / 2))
        yield( self.wait_clocks(10))
        self.comm_lock.release()
        #print "Reset Release Lock"

    def is_programmed(self):
        """
        Returns True if the FPGA is programmed

        Args:
            Nothing

        Returns (Boolean):
            True: FPGA is programmed
            False: FPGA is not programmed

        Raises:
            NysaCommError: A failure of communication is detected
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def get_sdb_base_address(self):
        """
        Return the base address of the SDB (This is platform specific)

        Args:
            Nothing

        Returns:
            32-bit unsigned integer of the address where the SDB can be read

        Raises:
            Nothing
        """
        #raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)
        #Normally with Nysa platform address is at adress 0x00 on the peripheral bus
        return 0x00

    def wait_for_interrupts(self, wait_time = 1):
        """wait_for_interrupts

        listen for interrupts for the specified amount of time

        Args:
          wait_time (int): the amount of time in seconds to wait for an
                           interrupt

        Returns:
          (boolean):
            True: Interrupts were detected
            False: No interrupts detected

        Raises:
            NysaCommError: A failure of communication is detected
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def register_interrupt_callback(self, index, callback):
        """ register_interrupt

        Setup the thread to call the callback when an interrupt is detected

        Args:
            index (Integer): bit position of the device
                if the device is 1, then set index = 1
            callback: a function to call when an interrupt is detected

        Returns:
            Nothing

        Raises:
            Nothing
        """
        temp_string = self.uart.read(32)
        if len(temp_string) == 0:
            return False
        self.interrupt_address = string.atoi(temp_string[16:24], 16)
        self.interrupts = string.atoi(temp_string[24:32], 16)
        return True

    def unregister_interrupt_callback(self, index, callback = None):
        """ unregister_interrupt_callback

        Removes an interrupt callback from the reader thread list

        Args:
            index (Integer): bit position of the associated device
                EX: if the device that will receive callbacks is 1, index = 1
            callback: a function to remove from the callback list

        Returns:
            Nothing

        Raises:
            Nothing (This function fails quietly if ther callback is not found)
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def get_board_name(self):
        return "uart"

    def upload(self, filepath):
        """
        Uploads an image to a board

        Args:
            filepath (String): path to the file to upload

        Returns:
            Nothing

        Raises:
            NysaError:
                Failed to upload data
            AssertionError:
                Not Implemented
        """

        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def program (self):
        """
        Initiate an FPGA program sequence, THIS DOES NOT UPLOAD AN IMAGE, use
        upload to upload an FPGA image

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            AssertionError:
                Not Implemented
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def ioctl(self, name, arg = None):
        """
        Platform specific functions to execute on a Nysa device implementation.

        For example a board may be capable of setting an external voltage or
        reading configuration data from an EEPROM. All these extra functions
        cannot be encompused in a generic driver

        Args:
            name (String): Name of the function to execute
            args (object): A generic object that can be used to pass an
                arbitrary or multiple arbitrary variables to the device

        Returns:
            (object) an object from the underlying function

        Raises:
            NysaError:
                An implementation specific error
        """

        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def list_ioctl(self):
        """
        Return a tuple of ioctl functions and argument types and descriptions
        in the following format:
            {
                [name, description, args_type_object],
                [name, description, args_type_object]
                ...
            }

        Args:
            Nothing

        Raises:
            AssertionError:
                Not Implemented

        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)


