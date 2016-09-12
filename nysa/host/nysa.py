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

from nysa_sdb_manager import NysaSDBManager

class NysaCommError(Exception):
    """NysaCommError

    Errors associated with communications
        Response Timeout
        Incorrect settings
    """
    pass

class NysaError(Exception):
    """NysaError

    Errors associated with Nysa
        Device not found in SDB
    """
    pass


#FLAGS
class NYSA_FLAGS(object):
    DISABLE_AUTO_INC    = 0
    MASTER_ADDRESS      = 1

class Nysa(object):
    """Nysa

    Abstract class and must be overriden by a class that will implement
    device specific functions such as initialize, read, write, and ping
    """

    @staticmethod
    def get_id_from_name(name):
        """Gets the device ID number from it's name,

        Example: GPIO return 0x01 (this is defined within sdb database

        Args:
            name (String): Name of the device to identify

        Returns:
            (Integer):
            Integer device identification number

        Raises:
            NysaError:
                Name not found in sdb database
        """
        try:
            return sdb_controller.get_device_id_from_name(name)
        except SDBError, e:
            raise NysaError(e)

    #XXX: This might be better specified as a float
    timeout  = 3
    interrupts = 0
    interrupt_address = 0

    def __init__(self, status = None):
        self.name = "Nysa"
        self.s = status
        self.nsm = NysaSDBManager(self, self.s)
        self.mem_addr = None
        if status: status.Debug("nysa started")

    def __del__(self):
        #print "Closing Nysa"
        pass

    #Control Functions
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

    def read(self, address, length = 1, flags = []):
        """read

        Generic read command used to read data from a Nysa image, this will be
        overriden based on the communication method with the FPGA board

        standard methods include

        UART, FTDI Synchronous FIFO, Cypress USB 3.0 Interface,

        Args:
          length (int): Number of 32 bit words to read from the FPGA
          address (int):  Address of the register/memory to read
          flags (list of flags): [flag1, flag2, flag3]
            NYSA_FLAG.DISABLE_AUTO_INC    = 0
            NYSA_FLAG.MASTER_ADDRESS      = 1

        Returns:
          (Array of unsigned bytes): A byte array containtin the raw data
                                     returned from Nysa

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def write(self, address, data, flags = []):
        """write

        Generic write command usd to write data to a Nysa image, this will be
        overriden based on the communication method with the specific FPGA board

        Args:
            address (int): Address of the register/memory to read
            data (array of unsigned bytes): Array of raw bytes to send to the
                                           device
            flags (list of flags): [flag1, flag2, flag3]
                NYSA_FLAG.DISABLE_AUTO_INC    = 0
                NYSA_FLAG.MASTER_ADDRESS      = 1

        Returns:
            Nothing

        Raises:
            AssertionError: This function must be overriden by a board specific
                implementation
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)
        if len(data) == 0:
            raise NysaCommError("Data length cannot be 0")

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
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

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
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def is_programmed(self):
        """
        Returns True if the FPGA is programmed

        Args:
          Nothing

        Returns (Boolean):
          True: FPGA is programmed
          False: FPGA is not programmed

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
          NysaCommError: A failure of communication is detected
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

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
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

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
        AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

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

    #Helpful Control Functions
    def read_register(self, address):
        """read_register

        Reads a single register from the read command and then converts it to an
        integer

        Args:
          address (int):  Address of the register/memory to read

        Returns:
          (int): 32-bit unsigned register value

        Raises:
          NysaCommError: Error in communication
        """
        register_array = self.read(address, 1)
        return register_array[0] << 24 | \
               register_array[1] << 16 | \
               register_array[2] << 8  | \
               register_array[3]

    def write_register(self, address, value):
        """write_register

        Writes a single register from a 32-bit unsingned integer

        Args:
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
        self.write(address, register_array)

    def enable_register_bit(self, address, bit, enable):
        """enable_register_bit

        Pass a bool value to set/clear a bit

        Args:
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)
          enable (bool): set or clear a bit

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if enable:
            self.set_register_bit(address, bit)
        else:
            self.clear_register_bit(address, bit)

    def set_register_bit(self, address, bit):
        """set_register_bit

        Sets an individual bit in a register

        Args:
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        register = self.read_register(address)
        bit_mask =  1 << bit
        register |= bit_mask
        self.write_register(address, register)

    def clear_register_bit(self, address, bit):
        """clear_register_bit

        Clear an individual bit in a register

        Args:
          address (int): Address of the register/memory to modify
          bit (int): Address of bit to set (31 - 0)

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        register = self.read_register(address)
        bit_mask =  1 << bit
        register &= ~bit_mask
        self.write_register(address, register)

    def is_register_bit_set(self, address, bit):
        """is_register_bit_set

        returns true if an individual bit is set, false if clear

        Args:
          address (int): Address of the register/memory to read
          bit (int): Address of bit to check (31 - 0)

        Returns:
          (boolean):
            True: bit is set
            False: bit is not set

        Raises:
          NysaCommError
        """
        register = self.read_register(address)
        bit_mask =  1 << bit
        return ((register & bit_mask) > 0)

    def write_master_register(self, address, value):
        """write_register

        Writes a single register from a 32-bit unsingned integer

        Args:
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
        self.write(address, register_array)

    def read_master_register(self, address, value):
        """read_register

        Reads a single register from the read command and then converts it to an
        integer

        Args:
          address (int):  Address of the register/memory to read

        Returns:
          (int): 32-bit unsigned register value

        Raises:
          NysaCommError: Error in communication
        """
        register_array = self.read(address, 1)
        return register_array[0] << 24 | \
               register_array[1] << 16 | \
               register_array[2] << 8  | \
               register_array[3]

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
        if self.mem_addr is None:
            self.mem_addr = self.nsm.get_address_of_memory_bus()

        address = self.mem_addr + address
        self.write(address, data)

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
        if self.mem_addr is None:
            self.mem_addr = self.nsm.get_address_of_memory_bus()
        address += self.mem_addr

        return self.read(address = address,
                         length = size)

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
            AssertionError:
                Not Implemented
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

    def write_register_bit_range(self, address, high_bit, low_bit, value):
        """
        Write data to a range of bits within a register

        Register = [XXXXXXXXXXXXXXXXXXXXXXXH---LXXXX]

        Write to a range of bits within ia register

        Args:
            address (unsigned long): Address or the register/memory to write
            high_bit (int): the high bit of the bit range to edit
            low_bit (int): the low bit of the bit range to edit
            value (int): the value to write in the range

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        reg = self.read_register(address)
        bitmask = (((1 << (high_bit + 1))) - (1 << low_bit))
        reg &= ~(bitmask)
        reg |= value << low_bit
        self.write_register(address, reg)

    def read_register_bit_range(self, address, high_bit, low_bit):
        """
        Read a range of bits within a register at address 'address'

        Register = [XXXXXXXXXXXXXXXXXXXXXXXH---LXXXX]

        Read the value within a register, the top bit is H and bottom is L

        Args:
            address (unsigned long): Address or the register/memory to read
            high_bit (int): the high bit of the bit range to read
            low_bit (int): the low bit of the bit range to read

        Returns (unsigned integer):
            Value within the bitfield

        Raises:
            NysaCommError
            
        """

        value = self.read_register(address)
        bitmask = (((1 << (high_bit + 1))) - (1 << low_bit))
        value = value & bitmask
        value = value >> low_bit
        return value

    #SDB Related
    def sdb_read_callback(self):
        """
        Called when SDB has been read and parsed, this should be overridden by
        the interface designer and is used when the interface designer will
        initialize values when the SDB has been successfully parsed

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """
        pass

    def get_sdb_base_address(self):
        """
        Return the base address of the SDB (This is platform specific)

        Args:
            Nothing

        Returns:
            (Tuple (Integer, Integer))
                Address of the SDB Component

        Raises:
            AssertionError: This function must be overriden by a board specific
            implementation
        """
        raise AssertionError("%s not implemented" % sys._getframe().f_code.co_name)

    def read_sdb(self):
        """read_sdb

        Read the contents of the SDB

        Args:
            Nothing

        Returns:
            Array of bytes of the SDB

        Raises:
            NysaCommError: When a failure of communication is detected
        """
        s = self.nsm.read_sdb(self)
        self.sdb_read_callback()
        return s

    def pretty_print_sdb(self):
        """pretty_print_sdb

        Prints out the SDB with colors and beauty

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          Nothing
        """
        self.nsm.pretty_print_sdb()

    def get_number_of_components(self):
        """get_number_of_components

        Returns the number of components found on the SDB

        Args:
          Nothing

        Returns:
          (int): The number of components on the SDB

        Raises:
          Nothing
        """
        return self.nsm.get_number_of_components()

    def get_number_of_devices(self):
        """get_number_of_devices

        Returns the number of devices found on the SDB

        Args:
          Nothing

        Returns:
          (int): The number of devices on the SDB

        Raises:
          Nothing
        """
        return self.nsm.get_number_of_devices()

    def get_device_name(self, urn):
        """
        From the URN get the name of the device

        Args:
          device (int): index of the device

        Returns:
          (string): name of the device

        Raises:
          Nothing
        """
        return self.nsm.get_device_name(urn)

    def get_device_address(self, urn):
        """
        From the URN get the base address of the device

        Args:
          device (int): index of the device

        Returns:
          (long): 64-bit address value

        Raises:
          Nothing
        """
        return self.nsm.get_device_address(urn)

    def get_device_size(self, urn):
        """get_device_size

        Gets the size of the peripheral/memory

        if peripheral gets the number of registers associated with ti
        if memory gets the size of the memory

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (long): size

        Raises:
          SDBError: User attempted to get the size of a component that doesn't
            have a size
        """
        return self.nsm.get_device_size(urn)

    def get_device_vendor_id(self, urn):
        """get_device_vendor_id

        Gets the vendor ID of the peripheral or memory device

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (long): Vendor ID

        Raises:
          SDBError: User attempted to get the vendor_id of a component that
            doesn't have a vendor_id
        """

        return self.nsm.get_device_vendor_id(urn)

    def get_device_product_id(self, urn):
        """get_device_product_id

        Gets the product ID of the peripheral or memory device

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (int): Product ID

        Raises:
          SDBError: User attempted to get the product_id of a component that
            doesn't have a product ID
        """
        return self.nsm.get_device_product_id(urn)

    def get_device_abi_class(self, urn):
        """
        Gets the ABI class of the peripheral or memory device

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (int): ABI Class

        Raises:
          SDBError: User attempted to get the abi_class of a component that
            doesn't have a ABI class
        """
        return self.nsm.get_device_abi_class(urn)

    def get_device_abi_major(self, urn):
        """
        Gets the ABI major of the peripheral or memory device

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (int): ABI major

        Raises:
          SDBError: User attempted to get the abi_major of a component that
            doesn't have a ABI major
        """
        return self.nsm.get_device_abi_major(urn)

    def get_device_abi_minor(self, urn):
        """
        Gets the ABI minor of the peripheral or memory device

        Args:
          urn (string): urn of the device, example
            "/top/peripheral/gpio1"

        Returns:
          (int): ABI minor

        Raises:
          SDBError: User attempted to get the abi_minor of a component that
            doesn't have a ABI minor
        """
        return self.nsm.get_device_abi_minor(urn)

    def is_device_in_platform(self, device):
        """
        Returns true if a platform has the device

        Args:
            device(Driver): a Driver object

        Returns:
            True: device exists in the platform
            False: device does not exist in the platform

        Returns:
            Nothing
        """
        return len(self.find_device(device)) > 0

    def find_device(self, driver):
        """
        Returns a list of URNs that can be used to instantiate a driver

        Args:
            device (Driver object)

        Returns: (List of URNs)
            a list of URNs that can be used to instantiate a device

        Raises:
            Nothing
        """
        return self.nsm.find_device_from_driver(driver)

    def find_device_from_name(self, device_name, abi_minor = None, abi_class = 0):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            device_name (String or Integer, Driver Object): Type of device to
                find, 'gpio' or 'uart'  can be searched for
            device_abi_minor (None, Integer): a number to identify one version
                of the device and another
            abi_class (None, Integer): A number identifying the class

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        return self.nsm.find_urn_from_device_type(device_name, abi_minor, abi_class)

    def find_urn_from_abi(self, abi_class = 0, abi_major = None, abi_minor = None):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            abi_class (None, Integer): Application Binary Interface Class,
                currently most components use '0' as the class is not defined
            abi_major (None, Integer): Application Binary Interface Major Number
                the current list of abi_major numbers can be found using the
                nysa command line tool ('nysa devices')
            abi_minor (None, Integer): Applicatoin Binary Interface Minor Number
                this is an identification within the major number, used to
                distinguish one version of a device from another

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        return self.nsm.find_urn_from_abi(abi_class, abi_major, abi_minor)

    def find_urn_from_ids(self, vendor_id = None, product_id = None):
        """
        Returns a list of SDB components that reference all the criteria the
        user specified

        Args:
            vendor_id (None, Integer): Vendor Identification number
            product_id(None, Integer): Product Identification number

        Returns (List of Strings):
            a list of sdb components URNs

        Raises:
            None
        """
        return self.nsm.find_urn_from_ids(vendor_id, product_id)

    def get_peripheral_device_index(self, urn):
        """
        Return the index of the device in the peripheral

        Args:
            urn (string): Unique Reference Name identifying the device

        Returns: (Integer)
            index of the device in the peripheral in the bus

        Raises:
            Nothing
        """

        return self.nsm.get_device_index_in_bus(urn)

    def is_memory_device(self, urn):
        """is_memory_device

        Queries the SDB to see if the device is on the memory bus or the
        peripheral bus

        Args:
          urn (String): universal resource name of device

        Returns:
          (boolean):
            True: Device is on the memory bus
            False: Device is on the peripheral bus

        Raises:
          Nothing
        """
        return self.nsm.is_memory_device(urn)

    def get_total_memory_size(self):
        """get_total_memory_size

        adds all the contiguous memory peripherals together and returns the
        total size

        Note: this memory must start at address 0

        Args:
          Nothing

        Returns:
          (long): Size of the total memory

        Raises:
          SDBError: SDB Not defined
        """
        return self.nsm.get_total_memory_size()

    def is_wishbone_bus(self):
        """is_wishbone_bus

        Returns true if the FPGA image is using a wishbone bus

        Returns:
            (Boolean):
                True: Image uses wishbone bus
                False: Image doesn't use wishbone bus

        Raises:
            SDBError: SDB not defines
        """
        return self.nsm.is_wishbone_bus()

    def is_axi_bus(self):
        """is_axi_bus
        Returns true if the FPGA image is using a axi bus

        Returns:
            (Boolean):
                True: Image uses axi bus
                False: Image doesn't use axi bus

        Raises:
            SDBError: SDB not defines

        """
        return self.nsm.is_axi_bus()

    def get_board_name(self):
        """
        Returns the board name

        Args:
            Nothing

        Returns:
            (String): Name of the board

        Raises:
            SDBError if SDB is not defined
        """
        #return self.sdb_manager.get_board_name(int(self.sdb_lines[3]))
        raise AssertionError("This function should be overridden")

    def get_integration_references(self, urn):
        """
        Given a URN return a list of URNs that the integration record is
        pointing to

        Args:
            urn (String): Universal Reference Name pointing to a particular
            device

        Return (List of URNs):
            An empty list if there is no reference to the URN

        Raises:
            Nothing
        """
        return self.nsm.get_integration_references(urn)

    def get_all_urns(self):
        """
        Returns all the components as a list of URNS

        Args:
            Nothing

        Returns:
            (List of strings)

        Raises:
            Nothing
        """
        return self.nsm.get_all_components_as_urns()

    def get_peripheral_devices_as_urns(self):
        """
        Returns a list of all the peirpheral devices as URNs

        Args:
            Nothing

        Returns:
            (List of URNs)

        Raises:
            Nothing
        """
        urns = self.nsm.get_all_devices_as_urns()
        peripheral_urns = []
        for urn in urns:
            if self.nsm.is_memory_device(urn):
                continue
            peripheral_urns.append(urn)
        return peripheral_urns

    def get_memory_devices_as_urns(self):
        """
        Returns a list of all the peirpheral devices as URNs

        Args:
            Nothing

        Returns:
            (List of URNs)

        Raises:
            Nothing
        """
        urns = self.nsm.get_all_devices_as_urns()
        memory_urns = []
        for urn in urns:
            if not self.nsm.is_memory_device(urn):
                continue
            memory_urns.append(urn)
        return memory_urns

    #Programming
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


