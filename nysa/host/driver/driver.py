#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import sys
import os
import time

from array import array as Array

import Queue
import threading
from threading import Lock

from nysa.cbuilder.device_manager import get_device_id_from_name

class Driver(object):
    def __init__(self,
                 n,
                 urn,
                 debug):
        self.n = n
        self.urn = urn
        if debug: print "Dev ID: %s" % self.urn
        self.debug = debug
        self.interrupt_detected = False
        #print "interrupts: 0x%08X" % self.n.interrupts
        self.peripheral_index = self.n.get_peripheral_device_index(self.urn)
        self.n.interrupts = (self.n.interrupts & ~(1 << self.peripheral_index))
        self.base_addr = self.n.get_device_address(self.urn)
        #print "interrupts: 0x%08X" % self.n.interrupts

    def __del__(self):
        self.unregister_interrupt_callback()

    @staticmethod
    def get_abi_class():
        """
        Returns the identification number of the ABI Class that this device
        uses

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Integer):
            By default this number returns 0, which is the experimental
            version, this function should be overriden by subclasses if
            a newer version of the abi class is used
        """
        return None

    @staticmethod
    def get_abi_major():
        """
        Returns the identification number of the device this module controls

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Integer):
            Number corresponding to the device in the online sdb repository
            file

        Raises:
            SDBError: Device ID Not found in online sdb repositor
        """
        return None

    @staticmethod
    def get_abi_minor():
        """Returns the identification of the specific implementation of this
        controller

        If not used return None or let the base class return None for you

        Example: Cospan Design wrote the HDL GPIO core with sub_id = 0x01
            this module was designed to interface and exploit features that
            are specific to the Cospan Design version of the GPIO controller.

            Some controllers may add extra functionalities that others do not
            sub_ids are used to differentiate them and select the right python
            controller for those HDL modules

        Args:
            Nothing

        Returns (Integer):
            Number ID for the HDL Module that this controls
            (Note: 0 = generic control or baseline funtionality of the module)

        Raises:
            Nothing
        """
        return None

    @staticmethod
    def get_vendor_id():
        """Returns the vendor identification of the device

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Long):
            Vendor ID of the HDL Module

        Raises:
            Nothing
        """
        return None

    @staticmethod
    def get_device_id():
        """Returns the device identification of the device

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Integer):
            Device ID of the HDL Module

        Raises:
            Nothing
        """
        return None

    @staticmethod
    def get_version():
        """Returns the version of the device

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Integer):
            Version ID of the HDL Module

        Raises:
            Nothing
        """
        return None

    @staticmethod
    def get_date():
        """Returns the date of the device

        If not used return None or let the base class return None for you

        Args:
            Nothing

        Returns (Integer):
            Date ID of the HDL Module

        Raises:
            Nothing
        """
        return None

    def register_interrupt_callback(self, callback = None):
        """register_interrupt_callback

        Register a function to be called when an interrupt occurs

        if left no callback is supplied then a local function will be called.

        This local function will set a flag to indicate that a register has
        occured

        Args:
            callback (Callable): this is the function to call when an
                interrupt occurs. If left blank this will set a local variable
                that can be polled with 'wait_for_interrupt'

        Returns:
            Nothing

        Raises:
            Nothing
        """
        if callback is None:
            callback = self.interrupt_callback

        self.n.register_interrupt_callback(self.peripheral_index, callback)

    def unregister_interrupt_callback(self, callback = None):
        """unregister_interrupt_callback

        Unregister a function from the interrupt callable list

        if no callback is supplied then a the local function will be removed

        Args:
            callback (Callable): This is the function to call when an interrupt
                occurs. If left blank all the callbacks will be removed

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.n.unregister_interrupt_callback(self.peripheral_index, callback = callback)

    def set_timeout(self, timeout):
        """set_timeout

        Sets the timeout (in seconds) of the read

        Args:
          timeout: new timeout

        Returns:
          Nothing

        Raises:
          Nothing
        """
        self.n.set_timeout(timeout)

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
        return self.n.get_timeout()

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
        address = long(self.base_addr + address)
        return self.n.read_register(address)

    def read(self, address, length = 1, disable_auto_inc = False):
        """read

        Args:
          length (int): Number of 32 bit words to read from the FPGA
          address (int):  Address of the register/memory to read
          disable_auto_inc (boolean): Disable the auto increment behavior

        Returns:
          (Array of unsigned bytes): A byte array containtin the raw data
                                     returned from Nysa

        Raises:
          NysaCommError: Error in communication
        """
        address = long(self.base_addr + address)
        return self.n.read(address, length, disable_auto_inc = disable_auto_inc)

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
        return self.n.read_memory(address, size)

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
        address = long(self.base_addr + address)
        self.n.write_register(address, value)

    def write(self, address, data, disable_auto_inc = False):
        """write

        Generic write command usd to write data to an Nysa image, this will be
        overriden based on the communication method with the specific FPGA board

        Args:
          address (int): Address of the register/memory to read
          data (array of unsigned bytes): Array of raw bytes to send to the
                                          device
          disable_auto_inc (boolean): Disable the auto increment behavior

        Returns:
          Nothing

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
        """
        address = long(self.base_addr + address)
        self.n.write(address, data, disable_auto_inc = disable_auto_inc)

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
        self.n.write_memory(address, data)

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
        address = long(self.base_addr + address)
        self.n.enable_register_bit(address, bit, enable)

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
        address = long(self.base_addr + address)
        self.n.set_register_bit(address, bit)

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
        address = long(self.base_addr + address)
        self.n.clear_register_bit(address, bit)

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
        address = long(self.base_addr + address)
        return self.n.is_register_bit_set(address, bit)

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
        """
        if self.interrupt_detected:
            self.interrupt_detected = False
            return True
        retval = self.n.wait_for_interrupts(wait_time)
        self.n.interrupts &= ~(1 << self.peripheral_index)
        return retval

    def interrupt_callback(self):
        self.interrupt_detected = True

    def register_dump(self):
        """
        Display All the Register Values

        Reads the size number of registers from the SDB and
        prints them all out
        """
        count = self.n.get_device_size(self.urn)
        print "Register Dump"
        for i in range(count):
            print "Register [0x%02X]: 0x%08X" % (i, self.read_register(i))

        print ""

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
        return self.n.get_integration_references(urn)

class NysaDMAException(Exception):
    '''
    DMA has incorrectly been setup
    DMA setup for write is read from
    DMA setup for read has ben written to
    '''
    pass


class DMAReaderData(object):
    data = None
    ready = None
    callback = None
    next = 0

class DMAReadWorker(threading.Thread):
    """
    Start an worker thread that will read data from the dma device when an
    Interrupt occurs. The main thread will receive the interrupt that will
    enqueue an event into the dma_write_queue.

    A queue is used to notify the worker instead of an event so that
    if an interrupt is detected while the data is being processed for the
    first interrupt it can be executed immediately

    Using the DMAReaderData object to pass the data so I don't need to pass
    a large structure into the queue and it doesn't need to be copied more
    than is required

    Use the AttributeError to notify the thread when the main thread has
    exited
    """
    def __init__(   self,
                    dev,
                    dmar,
                    dma_write_queue,
                    dma_rdata,
                    data_locks):

        super(DMAReadWorker, self).__init__()
        self.dev = dev
        self.dmar = dmar
        self.dwq = dma_write_queue
        self.drd = dma_rdata
        self.locks = data_locks
        #print "setup worker thread"

    def run(self):
        #print "Running worker thread"
        rdata = None
        dmar = self.dmar
        dev = self.dev
        fs = [False, False]
        bs = [False, False]
        read_channel = 0
        next = 0
        enable = False
        size = dmar.size

        while (1):
            if not fs[0] and not fs[1]:
                #print "DMA Reader: No finished flag"
                #There is no finished status from previous reads
                status = dev.read_register(dmar.reg_status)
                fs[0] = ((status & dmar.finished[0]) > 0)
                fs[1] = ((status & dmar.finished[1]) > 0)
                bs[0] = ((status & dmar.empty[0]) == 0)
                bs[1] = ((status & dmar.empty[1]) == 0)
                #print "DMA Reader: fs flags: %s %s, bs flags: %s %s" % (fs[1], fs[0], bs[1], bs[0])
                if not fs[0] and not fs[1]:
                    if enable:
                        #print "DMA Reader: Start reading!"
                        #We are enabled
                        #Nothing is ready, we need to wait for an interrupt

                        #Check if there is anything working
                        if not bs[0]:
                            #side 0 is not busy, intiate a transaction
                            #print "DMA Reader 0 thread wakeup!: Size 0x%08X" % size
                            dev.write_register(dmar.reg_size0, size)

                        if not bs[1]:
                            #print "DMA Reader 1 thread wakeup!: Size 0x%08X" % size
                            #side 1 is not busy, intiate a transaction
                            dev.write_register(dmar.reg_size1, size)

                    try:
                        #wait for an interrupt condeciton
                        #print "DMA Reader 0 Size: 0x%08X, 0x%08X" % (size, dev.read_register(dmar.reg_size0))
                        #print "control: 0x%08X" % dev.get_control()
                        #print "status:  0x%08X" % dev.read_register(dmar.reg_status)
                        if self.dwq.empty():
                            rdata = self.dwq.get(block = True)
                        while not self.dwq.empty():
                            rdata = self.dwq.get(block = True)
                        #print "Got a response!"

                    except AttributeError:
                        #This occurs when the queue is destroyed remotely
                        #print "exit"
                        return

                    if rdata is not None:
                        #print "DMA Reader Enable: %s" % str(rdata)
                        enable = rdata
                        #print "control: 0x%08X" % dev.get_control()
                        #print "self.mem_base 0: 0x%08X, size: 0x%08X" % (dmar.mem_base[0], size)
                        #print "self.mem_base 1: 0x%08X, size: 0x%08X" % (dmar.mem_base[1], size)

                        continue

            if fs[0] and fs[1]:
                #both finished channels are ready
                if next == 0:
                    fs[0] = False
                    bs[0] = False
                    read_channel = 0
                    next = 1
                else:
                    fs[1] = False
                    bs[1] = False
                    read_channel = 1
                    next = 0
            else:
                #if only one of the finished status is ready, reset the tie
                #breaker
                next = 0
                if fs[0]:
                    fs[0] = False
                    bs[0] = False
                    read_channel = 0
                if fs[1]:
                    fs[1] = False
                    bs[1] = False
                    read_channel = 1

            #Now we know what channel we need to read
            #'read_channel' is the channel to use
            with self.locks[read_channel]:
                #lock the channel so the reading device is not getting garbage data
                #print "read channel: %d" % read_channel
                self.drd.data[read_channel] = dev.read_memory(dmar.mem_base[read_channel], size)
                self.drd.ready[read_channel] = True
                if self.drd.ready[0] and self.drd.ready[1]:
                    #if both are ready point to the previous one
                    if read_channel == 0:
                        self.drd.next = 1
                    else:
                        self.drd.next = 0
                else:
                    self.drd.next = read_channel

                if self.drd.callback is not None:
                    self.drd.callback()

                #initiate a new transfer before I leave so it will happen next
                if enable:
                    if read_channel == 0:
                        dev.write_register(dmar.reg_size0, size)
                    else:
                        dev.write_register(dmar.reg_size1, size)


class DMAReadController(object):
    '''
    Direct Memory Access Read controller

    Used to read data to from the core at a higher rate than by interfacing
    with the core alone.

    The core must be initialized with the following settings:

        mem_base0: The location of the first block of memory, usually this is
            0x00000000 for a single memory controller device
        mem_base1: The location ofthe second block of memory, this varies
            depending on the implementation and will define a size limitation
            between mem_base0 and mem_base1

            and example would be 0x00100000 for a maximum block size of

            4 bytes x 0x00100000 = 0x00400000 or 4 Megabytes

        size: if 'None' is specified then setup will define the maximum size of
            mem_base1 - mem_base0

        reg_status: the address of the status register for example 0x01 is
            the status register on most Cospan Design cores

        reg_base0: the address of the core where the user can set the location
            of the first memory block

            some cores specify this immediately after the standard 'control'
            and 'status' or 0x02

        reg_size0: the address of the core where the user can set the size of
            data that is in or can fit in memory block 0: The act of writing
            to this register initiates a data transfer from the core
            to the memory

            example: 0x03

        reg_base1: the address of the core where the user can set the location
            of the second memory block

            example: 0x04

        reg_size1: the address of the core where the user can set the size of
            data that is in or can fit in memory block 1: the act or writing
            to this register initiates a data transfer from the core to
            the memory

        timeout: If this value is 0 then the core will wait until a block of
            memory is available before returning if None then the core will
            return immediately when memory is not ready or any positive number
            the core will wait till that specified timeout in seconds

            timeout = None  : blocking, wait until it is ready
            timeout = 0     : Return immediately
            timeout > 0.0   : Wait the specified amount of seconds
                                (or fraction of seconds)
        finished0: bit address of a status flag
            Reading: memory 0 is ready for reading
                (NOTE this flag will be reset upon reading so allow the DMA
                core to manage this)

            example (first bit of the status flag): 0

        finished1:
            Reading: memory 1 is ready for reading
                (NOTE this flag will be reset upon reading so allow the DMA
                core to manage this)

            example (second bit of the status flag): 1


        empty0: bit address of a status flag
            Reading: the memory is not being written to

            example (first bit of the status flag): 2

        empty1: bit address of a status flag
            Reading: the memory is not being written to

            example (second bit of the status flag): 3

    Exceptions:
        NysaDMAException:
            Thrown when:
                DMA has incorrectly been setup

    '''
    def __init__(self,
                device,
                mem_base0,
                mem_base1,
                size,
                reg_status,
                reg_base0,
                reg_size0,
                reg_base1,
                reg_size1,
                timeout = 3,
                finished0 = 0,
                finished1 = 1,
                empty0 = 2,
                empty1 = 3):

        self.device = device
        self.mem_base = [0, 1]
        self.mem_base[0] = mem_base0
        self.mem_base[1] = mem_base1
        if size is None:
            self.size = (self.mem_base[1] - self.mem_base[0])
        else:
            self.size = size
        self.reg_status = reg_status
        self.reg_base0 = reg_base0
        self.reg_size0 = reg_size0
        self.reg_base1 = reg_base1
        self.reg_size1 = reg_size1
        self.timeout = timeout

        self.empty = [0, 1]
        self.finished = [2, 3]
        self.empty[0] = 1 << empty0
        self.empty[1] = 1 << empty1
        self.finished[0] = 1 << finished0
        self.finished[1] = 1 << finished1

        self.device.write_register(self.reg_base0, self.mem_base[0])
        self.device.write_register(self.reg_base1, self.mem_base[1])

        self.finished_status = [False, False]
        self.busy_status = [False, False]
        self.next_finished = 0


        self.dma_read_data = DMAReaderData()
        self.dma_read_data.data = [None, None]
        self.dma_read_data.ready = [False, False]
        self.dma_read_data.callback = None
        self.dma_write_queue = Queue.Queue(4)
        self.locks = [Lock(), Lock()]

        self.worker = DMAReadWorker(device,
                                    self,
                                    self.dma_write_queue,
                                    self.dma_read_data,
                                    self.locks)
        self.worker.setDaemon(True)
        self.worker.start()
        self.debug = False

    def dma_read_callback(self):
        if self.debug: print "Entered DMA read callback"
        #send a message queue to the worker thread to start processing the
        #incomming data
        if not self.dma_write_queue.full():
            self.dma_write_queue.put(None)

    def enable_asynchronous_read(self, callback):
        self.dma_read_data.callback = callback
        self.device.register_interrupt_callback(self.dma_read_callback)
        self.dma_write_queue.put(True)
        #set up a callback with the dma device to call

    def disable_asynchronous_read(self):
        #Disable callback
        self.dma_write_queue.put(False)
        self.dma_read_data.callback = None
        self.device.unregister_interrupt_callback(self.dma_read_callback)

    def async_read(self):
        pos = self.dma_read_data.next
        with self.locks[pos]:
            self.dma_read_data.ready[pos] = False
            return self.dma_read_data.data[pos]

    def _get_finished_block(self):
        """
        Uses either cached data or if not available reads the status from the
        core to determine if there is any available blocks of data to be read

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError:
                An error in communication (Timeout, Disconnected)
        """
        #self.debug = True
        if (not self.finished_status[0]) and (not self.finished_status[1]):
            if self.debug: print "GFS: Finished status: 0, 0"
            status = self.device.read_register(self.reg_status)
            if self.debug: print "GFS: status: 0x%0X" % status
            self.finished_status[0] = ((status & self.finished[0]) > 0)
            self.finished_status[1] = ((status & self.finished[1]) > 0)
            self.busy_status[0] = ((status & self.empty[0]) == 0)
            self.busy_status[1] = ((status & self.empty[1]) == 0)
            if self.debug: print "GFS: busy Status: %s, %s" % \
                (str(self.busy_status[1]), str(self.busy_status[0]))
            if self.debug: print "GFS: Finished: Status: %s, %s" % \
                (str(self.finished_status[1]), str(self.finished_status[0]))

        if self.finished_status[0] and self.finished_status[1]:
            if self.debug: print "GFS: Both Channels are ready"
            if self.next_finished == 0:
                if self.debug: print "GFS: Get data from channel 0"
                self.finished_status[0] = False
                self.busy_status[0] = False
                self.next_finished = 1
                #self.debug = False
                return 1
            else:
                if self.debug: print "GFS: Get data from channel 1"
                self.finished_status[1] = False
                self.busy_status[1] = False
                self.next_finished = 0
                #self.debug = False
                return 2

        self.next_finished = 0

        if self.finished_status[0]:
            if self.debug: print "GFS: Channel 0 is ready"
            self.finished_status[0] = False
            self.busy_status[0] = False
            #self.debug = False
            return 1

        if self.finished_status[1]:
            if self.debug: print "GFS: Channel 1 is ready"
            self.finished_status[1] = False
            self.busy_status[1] = False
            #self.debug = False
            return 2

        #self.debug = False
        if self.debug: print "GFS: No Channels are ready now"
        return 0

    def is_busy(self):
        """
        Returns true if the core is currently reading the data in the memory
        """
        if self.busy_status[0] or self.busy_status[1]:
            return True
        return False

    def read(self, anticipate = False):
        """
        Returns a block of data and prepare for consequtive reads when the
        anticipate flag is set.

        When the anticipate flag is set the function will initiate a new
        request for a block of data before leaving the function so that when
        the user calls this function consqutively the function will return
        faster because a read has already been requested.

        This is useful when the user knows they will be reading from the core
        consequtively


        Args:
            anticipate (Boolean): if true will aggressively start consecutive
            reads.

        Returns:
            Array of bytes, the length of the array is defined from the size
            value set when initialized

        Raises:
            NysaCommError:
                Error in communication
        """

        #print "DMA READER READ FUNCTION ENTERED!"
        buf = Array('B')
        if self.debug: print "READ: Entered"
        finished_status = self._get_finished_block()
        if self.debug: print "READ: Busy: %s" % str(self.is_busy())
        if (finished_status == 0) and not self.is_busy():
            #Request more data
            if self.debug: print "READ: There is no data ready, initiate a capture"
            self.device.write_register(self.reg_size0, self.size)

        elif (finished_status == 0) and self.is_busy():
            #print "Waiting for interrupts",
            self.device.wait_for_interrupts(self.timeout)
            #print "Got interrupts"
            finished_status = self._get_finished_block()

        if (finished_status == 0):
            if self.debug: print "READ: No Data is ready, returning an empty buffer"
            return buf

        if finished_status == 1:
            if self.debug: print "READ: buffer 0 is ready"
            if self.debug: print "self.mem_base: 0x%08X, size: 0x%08X" % (self.mem_base[0], self.size)
            buf = self.device.read_memory(self.mem_base[0], self.size)
            if anticipate:
                if self.debug: print "READ: Setting up an anticipate read for channel 1"
                if self.debug: print "READ: Busy Status[1]: %s" % str(self.busy_status[1])
                if not self.busy_status[1]:
                    if self.debug: print "READ: Writing to register for size[1], to initiate a transfer"
                    self.device.write_register(self.reg_size1, self.size)
                else:
                    self.next_finished = 1
        else:
            if self.debug: print "READ: buffer 1 is ready"
            if self.debug: print "self.mem_base: 0x%08X, size: 0x%08X" % (self.mem_base[1], self.size)
            buf = self.device.read_memory(self.mem_base[1], self.size)
            if anticipate:
                if self.debug: print "READ: Setting up an anticipate read for channel 0"
                if self.debug: print "READ: Busy Status[0]: %s" % str(self.busy_status[0])
                if not self.busy_status[0]:
                    if self.debug: print "READ: Writing to register for size[0], to initiate a transfer"
                    self.device.write_register(self.reg_size0, self.size)
                else:
                    self.next_finished = 0

        self.debug = False
        return buf

class DMAWriteController(object):
    '''
    Direct Memory Access controller

    Used to write data to the core at a higher rate than by interfacing with
    the core alone.

    the values that must be passed to the controller:

        mem_base0: The location of the first block of memory, usually this is
            0x00000000 for a single memory controller device
        mem_base1: The location ofthe second block of memory, this varies
            depending on the implementation and will define a size limitation
            between mem_base0 and mem_base1

            and example would be 0x00100000 for a maximum block size of

            4 bytes x 0x00100000 = 0x00400000 or 4 Megabytes

        size: if 'None' is specified then setup will define the maximum size of
            mem_base1 - mem_base0

        reg_status: the address of the status register for example 0x01 is
            the status register on most Cospan Design cores

        reg_base0: the address of the core where the user can set the location
            of the first memory block

            some cores specify this immediately after the standard 'control'
            and 'status' or 0x02

        reg_size0: the address of the core where the user can set the size of
            data that is in or can fit in memory block 0: The act of writing
            to this register initiates a data transfer to the core
            from the memory

            example: 0x03

        reg_base1: the address of the core where the user can set the location
            of the second memory block

            example: 0x04

        reg_size1: the address of the core where the user can set the size of
            data that is in or can fit in memory block 1: the act or writing
            to this register initiates a data transfer to the core from the
            memory

        timeout:
            timeout = None  : blocking, wait until core is ready
            timeout = 0     : Return immediately
            timeout > 0.0   : Wait the specified amount of seconds
                                (or fraction of seconds)

        empty0: bit address of a status flag:
            memory 0 is ready to be written to

            example (first bit of the status flag): 0

        empty1: bit address of a status flag:
            memory 1 is ready to be written to

            example (second bit of the status flag): 1

    Exceptions:
        NysaDMAException:
            Thrown when:
                -DMA has incorrectly been setup

    '''
    def __init__(self,
                device,
                mem_base0,
                mem_base1,
                size,
                reg_status,
                reg_base0,
                reg_size0,
                reg_base1,
                reg_size1,
                timeout = 3,
                empty0 = 1,
                empty1 = 2):

        self.device = device
        self.mem_base = [0, 1]
        self.mem_base[0] = mem_base0
        self.mem_base[1] = mem_base1
        if size is None:
            self.size = self.mem_base[1] - self.mem_base[0]
        else:
            self.size = size
        self.reg_status = reg_status
        self.reg_base = [0, 0]
        self.reg_size = [0, 0]
        self.reg_base[0] = reg_base0
        self.reg_size0 = reg_size0
        self.reg_base[1] = reg_base1
        self.reg_size1 = reg_size1
        self.timeout = timeout

        self.empty = [0, 1]
        self.empty[0] = 1 << empty0
        self.empty[1] = 1 << empty1

        self.device.write_register(self.reg_base[0], self.mem_base[0])
        self.device.write_register(self.reg_base[1], self.mem_base[1])

    def get_size(self):
        return self.size

    def get_available_memory_blocks(self):
        """
        reads the status of the core and determine whether any memory
        blocks are available, Returns a value between 0 and 3

        Args;
            Nothing

        Returns:
            0 = No blocks free
            1 = block 0 is free
            2 = block 1 is free
            3 = both block 0 and 1 are free

        Raises
            NysaCommError: Error in communication
        """
        status = self.device.read_register(self.reg_status)
        return status & (self.empty[0] | self.empty[1])

    def write(self, buf):
        """
        Write a buffer of data down to the core using DMA. The buffer sent to
        the device can be arbitrarily long. The function will packetize the
        data and send it to the memory, then notify the core there is data
        available.

        Args:
            buf (Array of bytes): buffer of data to send down

        Returns:
            Nothing

        Raises:
            NysaCommError
                An error in communication
        """
        position = 0
        total_length = len(buf)
        if (self.timeout > 0):
            timeout = self.timeout
        while (len(buf[position:]) > 0):
            size = self.size
            if len(buf[position:]) < size:
                size = len(buf[position:])
                if size < 4:
                    size = 4
            available_blocks = self.get_available_memory_blocks()
            #print "Status: 0x%08X" % available_blocks

            if (available_blocks == 1):
                #Mem 0 is available
                #print "Block 1 is available"
                self.device.write_memory(self.mem_base[0], buf[position: position + size + 1])
                self.device.write_register(self.reg_size0, size / 4)
                position += size

            elif (available_blocks == 2):
                #Mem 1 is available
                #print "Block 2 is available"
                self.device.write_memory(self.mem_base[1], buf[position: position + size + 1])
                self.device.write_register(self.reg_size1, size / 4)
                position += size

            elif (available_blocks == 3):
                #print "Both Blocks Are available"
                self.device.write_memory(self.mem_base[0], buf[position: position + size + 1])
                self.device.write_register(self.reg_size0, size / 4)
                position += size

                if len(buf[position:]) > 0:
                    #print "writing second block!"
                    size = self.size
                    if len(buf[position:]) < size:
                        size = len(buf[position:])
                        if size < 4:
                            size = 4
                    self.device.write_memory(self.mem_base[1], buf[position: position + size + 1])
                    self.device.write_register(self.reg_size1, size / 4)
                    position += size

            else:
                if timeout == 0:
                    return

                if timeout > 0:
                    #XXX: I should be reducing this timeout each time
                    #print "Wait for interrupts"
                    self.device.wait_for_interrupts(timeout)

                elif timeout is None:
                    self.device.wait_for_interrupts(10)


            #print "Size: 0x%08X" % size
            if len(buf[position:]) == 0:
                #print "\tfinished"
                return

            if len(buf[position:]) < self.size:
                size = len(buf[position:])
                #print "\t0x%08X more to write!" % size

            #print "Wrote: 0x%08X" % position



