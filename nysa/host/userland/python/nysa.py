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


# -*- coding: utf-8 -*-

""" nysa

Abstract interface for working the the Nysa FPGA images

This only defines the functions required for communiction, in order to
implement a new board a user must implement all the required functions

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import time
import random
import sys
import os
import string
import json
from array import array as Array

#put nysa in the system path
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "cbuilder",
                             "drt"))
import drt as drt_controller
from drt import DRTManager


class NysaCommError(Exception):
    """NysaCommError

    Errors associated with communications
        Response Timeout
        Incorrect settings
    """
    pass


class Nysa(object):
    """Nysa

    Abstract class and must be overriden by a class that will implement
    device specific functions such as initialize, read, write, and ping
    """

    #XXX: This might be better specified as a float
    timeout  = 3
    interrupts = 0
    interrupt_address = 0

    def __init__(self, debug = False):
        self.name = "Nysa"
        self.debug = debug
        self.drt_manager = DRTManager()
        if debug:
            print "Debug Enabled"

    def __del__(self):
        print "Closing Nysa"


    """initialize

    This function will not be implemented within this abstract class and must be
    implemented within the lower concrete class that is device speific
    def initialize(self):
      AssertionError("initialize function is not implemented")
    """

    def set_timeout(self, timeout):
        """set_timeout

        Sets the timeout (in seconds) of the read

        Args:
          timeout (int): new timeout

        Returns:
          Nothing

        Raises:
          Nothing
        """
        self.timeout = timeout

    def get_timeout(self):
        """get_timeout

        Returns the read/write timeout in case of an error

        Args:
          Nothing

        Returns:
          (int): Timeout value (in seconds)

        Raises:
          Nothing
        """
        return self.timeout

    def read_register(self, device_id, address):
        """read_register

        Reads a single register from the read command and then converts it to an
        integer

        Args:
          device_id (int):  Device identification number, this number is found
                            in the DRT
          address (int):  Address of the register/memory to read

        Returns:
          (int): 32-bit unsigned register value

        Raises:
          NysaCommError: Error in communication
        """
        register_array = self.read(device_id, address, 1)
        return register_array[0] << 24 | \
               register_array[1] << 16 | \
               register_array[2] << 8  | \
               register_array[3]


    def read(self, device_id, address, length = 1, mem_device = False):
        """read

        Generic read command used to read data from a Nysa image, this will be
        overriden based on the communication method with the FPGA board

        standard methods include

        UART, FTDI Synchronous FIFO, Cypress USB 3.0 Interface,

        Args:
          length (int): Number of 32 bit words to read from the FPGA
          device_id (int):  Device identification number, this number is found
                            in the DRT
          address (int):  Address of the register/memory to read
          mem_device (int): Whether the device is on the memory bus or the
                            peripheral bus

        Returns:
          (Array of unsigned bytes): A byte array containtin the raw data
                                     returned from Nysa

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
        """
        raise AssertionError("read function is not implemented")

    def read_memory(self, address, size):
        """read_memory

        Reads a byte array of the specified size from the specified address from
        memory

        Args:
          address (int): Starting location o memory to read from
          size (int): total number of 32-bit words to read

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        return self.read(0, address, size, mem_device=True)

    def write_register(self, device_id, address, value):
        """write_register

        Writes a single register from a 32-bit unsingned integer

        Args:
          device_id (int): Device identification number, this number is found
                           in the DRT
          address (int):  Address of the register/memory to read
          value (int)  32-bit unsigned integer to be written into the register

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        register_array = Array('B', [0x00, 0x00, 0x00, 0x00])
        register_array[0]  = (value >> 24) & 0xFF
        register_array[1]  = (value >> 16) & 0xFF
        register_array[2]  = (value >> 8) & 0xFF
        register_array[3]  = (value) & 0xFF
        self.write(device_id, address, register_array)

    def enable_register_bit(self, device_id, address, bit, enable):
        """enable_register_bit

        Pass a bool value to set/clear a bit

        Args:
          device_id (int): Device identification number, this number is found
                           in the DRT
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)
          enable (bool): set or clear a bit

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if enable:
            self.set_register_bit(device_id, address, bit)
        else:
            self.clear_register_bit(device_id, address, bit)


    def set_register_bit(self, device_id, address, bit):
        """set_register_bit

        Sets an individual bit in a register

        Args:
          device_id (int): Device identification number, this number is found
                           in the DRT
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        register = self.read_register(device_id, address)
        bit_mask =  1 << bit
        register |= bit_mask
        self.write_register(device_id, address, register)

    def clear_register_bit(self, device_id, address, bit):
        """clear_register_bit

        Clear an individual bit in a register

        Args:
          device_id (int): Device identification number, this number is found
                           in the DRT
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        register = self.read_register(device_id, address)
        bit_mask =  1 << bit
        register &= ~bit_mask
        self.write_register(device_id, address, register)


    def is_register_bit_set(self, device_id, address, bit):
        """is_register_bit_set

        returns true if an individual bit is set, false if clear

        Args:
          device_id (int): Device identification number ,this number is found
                           in the DRT
          address (int): Address of the register/memory to read
          bit (int): Address of bit to check (31 - 0)

        Returns:
          (boolean):
            True: bit is set
            False: bit is not set

        Raises:
          NysaCommError
        """
        register = self.read_register(device_id, address)
        bit_mask =  1 << bit
        return ((register & bit_mask) > 0)


    def write_memory(self, address, data):
        """write_memory

        Writes the byte of array of bytes down to the memory of the bus

        Args:
          address (int): Starting location of memory to write to
          data (array of unsigned bytes): A byte array of raw values to write to
                                          the memory

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        self.write(0, address, data, mem_device = True)

    def write(self, device_id, address, data = None, mem_device = False):
        """write

        Generic write command usd to write data to a Nysa image, this will be
        overriden based on the communication method with the specific FPGA board

        Args:
          device_id (int): Device identification number, found in the DRT
          address (int): Address of the register/memory to read
          mem_device (int): True if the device is on the memory bus
          data (array of unsigned bytes): Array of raw bytes to send to the
                                          device

        Returns:
          Nothing

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
        """
        raise AssertionError("write function is not implemented")


    def read_drt(self):
        """read_drt

        Read the contents of the DRT

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: When a failure of communication is detected
        """
        data = Array('B')
        data = self.read(0, 0, 8)
        num_of_devices  = drt_controller.get_number_of_devices(data)
        len_to_read = num_of_devices * 8

        data = self.read(0, 0, len_to_read + 8)
        self.drt_manager.set_drt(data)

    def pretty_print_drt(self):
        """pretty_print_drt

        Prints out the DRT with colors and beauty

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          Nothing
        """
        self.drt_manager.pretty_print_drt()

    def get_number_of_devices(self):
        """get_number_of_devices

        Returns the number of devices found on the DRT

        Args:
          Nothing

        Returns:
          (int): The number of devices on the DRT

        Raises:
          Nothing
        """
        return self.drt_manager.get_number_of_devices()

    def get_device_id(self, device_index):
        """get_device

        From the index within the DRT return the ID of this device

        Args:
          device (int): index of the device

        Returns:
          (int): Standard device ID

        Raises:
          Nothing
        """
        return self.drt_manager.get_id_from_index(device_index)

    def get_device_address(self, device_index):
        """get_device_address

        From the index within the DRT return the address of where to find this
        device

        Args:
          device (int): index of the device

        Returns:
          (int): 32-bit address of the device

        Raises:
          Nothing
        """
        return self.drt_manager.get_address_from_index(device_index)

    def get_device_size(self, device_index):
        """get_device_size

        Gets the size of the peripheral/memory

        if peripheral gets the number of registers associated with ti
        if memory gets the size of the memory

        Args:
          device (int): index of the device

        Returns:
          (int): size

        Raises:
          Nothing
        """
        return self.drt_manager.get_size_from_index(device_index)

    def is_memory_device(self, device_index):
        """is_memory_device

        Queries the DRT to see if the device is on the memory bus or the
        peripheral bus

        Args:
          device (int): Index of the device to test

        Returns:
          (boolean):
            True: Device is on the memory bus
            False: Device is on the peripheral bus

        Raises:
          Nothing
        """
        return self.drt_manager.is_memory_device(device_index)

    def get_total_memory_size(self):
        """get_total_memory_size

        adds all the contiguous memory peripherals together and returns the
        total size

        Note: this memory must start at address 0

        Args:
          Nothing

        Returns:
          (int): Size of the total memory

        Raises:
          DRTError: DRT Not defined
        """
        return self.drt_manager.get_total_memory_size()

    def ping(self):
        """ping

        Pings the Nysa image

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          AssertionError: This function must be overriden by a board specific
          NysaCommError: When a failure of communication is detected
        """
        raise AssertionError("Ping function is not implemented")

    def reset(self):
        """reset

        Software reset the Nysa FPGA Master, this may not actually reset the
        entire FPGA image

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
          NysaCommError: A failure of communication is detected
        """
        raise AssertionError("Reset function not implemented")

    def dump_core(self):
        """dump_core

        reads the state of the wishbone master prior to a reset, useful for
        debugging

        Args:
          Nothing

        Returns:
          (Array of unsigned 32-bit values): Array of 32-bit values to be parsed
                                             by core_analyzer

        Raises:
          AssertionError: This function must be overriden by a board specific
                          implementation
          NysaCommError: A failure of communication is detected
        """
        raise AssertionError("Core Dump function not implemented")

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
          AssertionError: This function must be overriden by a board specifific
          implementation
        """
        raise AssertionError("wait_for_interrupts function i not implemented")

    def is_interrupt_for_slave(self, device_id):
        """is_interrupt_for_slave

        Test to see if the interrupt is for the specified slave

        Args:
          device_id (int):  device to test for

        Returns:
          (boolean):
            True: interrupt is for device
            False: interrupt is not for the device

        Raises:
          Nothing
        """
        #print "Device interrupts: 0x%08X" % self.interrupts
        if ( (1 << device_id) & self.interrupts) > 0:
            return True
        return False

    def find_device(self, dev_id, sub_id = None, unique_id = None):
        """
        Find a device in the DRT that has the dev_id.

        If the sub_id and or the unique_id is not specified the device returns
        the first device that is found.

        The function will attempt to match as many parameters as the user
        specifies

        XXX: Unique ID is not supported yet!

        Args:
            dev_id (int): a device identification number
            sub_id (int): sub identification number for a device
            unique_id (int): a unique integer that identifies the device

        Returns:
            None: if the device is not found
            Integer: this specifies the device index

        Raises:
            Nothing
        """
        return self.drt_manager.find_device(dev_id, sub_id, unique_id)
