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

from nysa.host.userland.python.nysa import Nysa
from nysa.host.userland.python.nysa import NysaCommError
from nysa.host.userland.python.nysa import NysaError


class Driver(object):
    def __init__(self,
                 n,
                 dev_id,
                 debug):
        self.n = n
        self.dev_id = dev_id
        self.debug = debug

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
        return self.n.read_register(self.dev_id, address)

    def read(self, address, length = 1):
        """read

        Args:
          length (int): Number of 32 bit words to read from the FPGA
          address (int):  Address of the register/memory to read

        Returns:
          (Array of unsigned bytes): A byte array containtin the raw data
                                     returned from Nysa

        Raises:
          NysaCommError: Error in communication
        """
        return self.n.read(self.dev_id, address, length, memory_device = False)

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
        self.n.write_register(self.dev_id, address, value)

    def write(self, address, data = None):
        """write

        Generic write command usd to write data to an Nysa image, this will be
        overriden based on the communication method with the specific FPGA board

        Args:
          address (int): Address of the register/memory to read
          data (array of unsigned bytes): Array of raw bytes to send to the
                                          device

        Returns:
          Nothing

        Raises:
          AssertionError: This function must be overriden by a board specific
          implementation
        """
        self.n.write(self.dev_id, address, data, mem_device = False)

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
        self.n.enable_register_bit(self.dev_id, address, bit, enable)

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
        self.n.set_register_bit(self.dev_id, address, bit)


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
        self.n.clear_register_bit(self.dev_id, address, bit)

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
        return self.n.is_register_bit_set(self.dev_id, address, bit)

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
        self.n.wait_for_interrupts(wait_time)
        return self.n.is_interrupt_for_slave(self.dev_id)

    def is_interrupt_for_slave(self):
        """
        Pass through for nysa 'is_interrupt_for_slave()
        """
        return self.n.is_interrupt_for_slave(self.dev_id)

    def register_dump(self):
        """
        Display All the Register Values

        Reads the size number of registers from the DRT and
        prints them all out
        """
        count = self.n.get_device_size(self.dev_id - 1)
        print "Register Dump"
        for i in range(count):
            print "Register [0x%02X]: 0x%08X" % (i, self.read_register(i))

        print ""


class NysaDMAException(Exception):
    '''
    DMA has incorrectly been setup
    DMA setup for write is read from
    DMA setup for read has ben written to
    '''


    pass

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
        self.mem_base[0] = memory_base0
        self.mem_base[1] = memory_base1
        if size is None:
            self.size = self.mem_base[1] - self.mem_base[0]
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
        self.empty[0] = empty0
        self.empty[1] = empty1
        self.finished[0] = finished0
        self.finished[1] = finished1

        self.device.write_register(self.reg_base[0], self.mem_base[0])
        self.device.write_register(self.reg_base[1], self.mem_base[1])

        self.finished_status = [False, False]
        self.busy_status = [False, False]
        self.next_finished = 0

    def get_finished_block(self):
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
        if (not self.finished_status[0]) and (not self.finished_status[1]):
            status = self.device.read_register(self.reg_status)
            self.finished_status[0] = ((status & self.finished[0]) > 0)
            self.finished_status[1] = ((status & self.finished[1]) > 0)
            self.busy_status[0] = ((status & self.empty[0]) == 0)
            self.busy_status[1] = ((status & self.empty[1]) == 0)

        if self.finished_status[0] and self.finished_status[1]:
            if self.next_finished == 0:
                self.finished_status[0] = False
                self.busy_status[0] = False
                self.next_finished = 1
                return 1
            else:
                self.finished_status[1] = False
                self.busy_status[1] = False
                self.next_finished = 0
                return 2

        self.next_finished = 0

        if self.finished_status[0]:
            self.finished_status[0] = False
            self.busy_status[0] = False
            return 1

        if self.finished_status[1]:
            self.finished_status[1] = False
            self.busy_status[1] = False
            return 2

        return 0

    def is_busy(self):
        """
        Returns true if the core is currently reading the data in the memory
        """
        if self.busy_status[0] or self.busy_status[1]:
            return True
        return False

    def anticipate_read(self, single = True):
        if self.finished_status[0] and self.finished_status[1]:
            #Both blocks are already ready
            return

        if self.finished_status[0]:
            if self.busy_status[1]:
                #One side is busy the other is finished
                return
            #Side 0 is finished but and side 1 is not busy
            self.device.write_register(self.reg_size[1], self.size)
            if self.finished_status[0]:
                self.next_finished = 0
            if single:
                return

        if self.finished_status[1]:
            if self.busy_status[0]:
                #One side is busy and the other is finshed
                return
            #Side 1 is finished and side 0 is not busy
            self.device.write_register(self.reg_size[0], self.size)
            if self.finished_status[1]:
                self.next_finished = 1
            if single:
                return

        #Both sides are not finished
        if self.busy_status[0] and self.busy_status[1]:
            #Both sides are busy
            return

        if self.busy_status[0]:
            #Block 1 is not doing anything
            self.device.write_register(self.reg_size[1], self.size)
            self.next_finished = 0
            if single:
                return

        if self.busy_status[1]:
            #Block 0 is not doing anything
            self.device.write_register(self.reg_size[0], self.size)
            self.next_finished = 1
            if single:
                return

        #Both sides are not busy and are not doign anything
        self.device.write_register(self.reg_size[0], self.size)
        self.next_finished = 0
        if single:
            return
        self.device.write_register(self.reg_size[1], self.size)


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
            Array of bytes

        Raises:
            NysaCommError:
                Error in communication
        """

        buf = Array('B')
        finished_status = self.get_finished_block()
        if (finished_status == 0) and not self.is_busy():
            #Request more data
            self.device.write_register(self.reg_size[0], self.size)

        self.device.wait_for_interrupt(self.timeout)
        finished_status = self.get_finished_block()
        if (finished_status == 0) and not self.is_busy():
            return buf

        if finished_status == 1:
            buf = self.device.read_memory(self.mem_block[0], self.size)
            if anticipate:
                self.device.write_register(self.reg_size[0], self.size)
                if self.busy_status[1]:
                    self.next_finished = 1
        else:
            buf = self.device.read_memory(self.mem_block[1], self.size)
            if anticipate:
                self.device.write_register(self.reg_size[1], self.size)
                if self.busy_status[0]:
                    self.next_finished = 0

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
        self.reg_size[0] = reg_size0
        self.reg_base[1] = reg_base1
        self.reg_size[1] = reg_size1
        self.timeout = timeout

        self.empty = [0, 1]
        self.empty[0] = 1 << empty0
        self.empty[1] = 1 << empty1

        self.device.write_register(self.reg_base[0], self.mem_base[0])
        self.device.write_register(self.reg_base[1], self.mem_base[1])

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

    def write(buf):
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
            if len(buf[position:] < size):
                size = len(buf[position:])
            available_blocks = self.get_available_memory_blocks()

            if (available_blocks == 1):
                #Mem 0 is available
                self.device.write_memory(self.mem_base[0], buf[position: position + size + 1])
                self.device.write_register(self.reg_size[0], size / 4)
                position += size

            elif (available_blocks == 2):
                #Mem 1 is available
                self.device.write_memory(self.mem_base[1], buf[position: position + size + 1])
                self.device.write_register(self.reg_size[1], size / 4)
                position += size

            elif (available_blocks == 3):
                self.device.write_memory(self.mem_base[0], buf[position: position + size + 1])
                self.device.write_register(self.reg_size[0], size / 4)
                position += size

                size = self.size
                if len(buf[position:] < size):
                    size = len(buf[position:])

                if size == 0:
                    return

                self.device.write_memory(self.mem_base[1], buf[position: position + size + 1])
                self.device.write_register(self.reg_size[1], size / 4)
                position += size

            else:
                if timeout == 0:
                    return

                if timeout > 0:
                    #XXX: I should be reducing this timeout each time
                    self.device.wait_for_interrupts(timeout)

                elif timeout is None:
                    self.device.wait_for_interrupt(10)



