#Distributed under the MIT licesnse.
#Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" UART

Facilitates communication with the UART core independent of communication
medium

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_uart

"""


import sys
import os
import time

from array import array as Array


from nysa.host.nysa import Nysa
from nysa.host.nysa import NysaCommError

from driver import Driver

COSPAN_DESIGN_UART_MODULE = 0x01

#Register Constants
CONTROL             = 0
STATUS              = 1
PRESCALER           = 2
CLOCK_DIVIDER       = 3
WRITE_AVAILABLE     = 4
WRITE_DATA          = 5
READ_COUNT          = 6
READ_DATA           = 7

#Control Bit values
CONTROL_RESET       = 0
CONTROL_RTS_CTS_FC  = 1
CONTROL_DTS_DSR_FC  = 2
CONTROL_INT_READ    = 3
CONTROL_INT_WRITE   = 4

#Status Bit values
STATUS_OVFL_TX      = 0
STATUS_OVFL_RX      = 1
STATUS_UFL_RX       = 2
STATUS_INT_READ     = 3
STATUS_INT_WRITE    = 4


class UARTError (Exception):
    """UART Error:

    Errors associated with UART
        UART Bus Busy
        Incorrect Settings
    """
    pass


class UART(Driver):
    """UART
    """

    @staticmethod
    def get_core_id():
        """
        Returns the identification number of the device this module controls

        Args:
            Nothing

        Returns (Integer):
            Number corresponding to the device in the drt.json file

        Raises:
            DRTError: Device ID Not found in drt.json
        """
        return Nysa.get_id_from_name("UART")

    @staticmethod
    def get_core_sub_id():
        """Returns the identification of the specific implementation of this
        controller

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
        return COSPAN_DESIGN_UART_MODULE

    def __init__(self, nysa, dev_id, debug = False):
        print "dev id: %d" % dev_id
        super(UART, self).__init__(nysa, dev_id, debug)

    def get_control(self):
        """get_control

        reads the control register

        Args:
          Nothing

        Return:
          32-bit control register value

        Raises:
          NysaCommError: Error in communication
        """
        return self.read_register(CONTROL)

    def set_control(self, control):
        """set_control

        write the control register

        Args:
          control: 32-bit control value

        Return:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        self.write_register(CONTROL, control)

    def get_status(self):
        """get_status

        get the status of the UART

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          32-bit status value

        Raises:
          NysaCommError: Error in communication
        """
        self.status =  self.read_register(STATUS)
        return self.status

    def reset(self):
        self.get_status()
        self.set_control(0)
        self.set_register_bit(CONTROL, CONTROL_RESET)

    def is_read_overflow(self):
        """is_read_overflow

        if read overfow

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          True: empty
          False: not empty

        Raises:
          NysaCommError
        """
        #status = self.get_status()
        if ((self.status & STATUS_OVFL_RX) > 0):
            return True
        return False

    def is_write_overflow(self):
        """is_write_overflow

        if write is buffer overflowed

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          True: Overflow
          False: No Overflow

        Raises:
          NysaCommError
        """
        #status = self.get_status()
        if ((self.status & STATUS_OVFL_TX) > 0):
            return True
        return False

    def is_read_underflow(self):
        """is_read_underflow

        Read too many bytes from the read

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          True: read underflow
          False: not read underflow

        Raises:
          NysaCommError
        """
        #status = self.get_status()
        if ((self.status & STATUS_UFL_RX) > 0):
            return True
        return False

    def is_read_interrupt(self):
        """is_read_interrupt

        test if a read interrupt has occured

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          True: read interrupt
          False: read interrupt did not occure

        Raises:
          NysaCommError

        """
        #status = self.get_status()
        if ((self.status & STATUS_INT_READ) > 0):
            return True
        return False

    def is_write_interrupt(self):
        """is_write_interrupt

        test if a write interrupt has occured

        *** NOTE:
        *** because the status is reset by the core
        *** the status should only be read once
        *** Read the status with get_status
        *** then perform the tests on the status

        Args:
          Nothing

        Return:
          True: write interrupt
          False: not write interrupt

        Raises:
          NysaCommError
        """
        #status = self.get_status()
        if ((self.status & STATUS_INT_WRITE) > 0):
            return True
        return False

    def write_string(self, string = ""):
        """write_string

        Writes a string of data over the UART

        Args:
          string: String to send

        Return:
          Nothing

        Raises:
          NysaCommError
        """
        if self.debug:
            print "Writing a string"

        data = Array('B')
        data.fromstring(string)
        self.write_raw(data)

    def write_byte(self, data):
        """write_byte

        Writes a byte of data over the UART

        Args:
          int: byte of data to send

        Return:
          Nothing

        Raises:
          NysaCommError
        """
        write_data = Array('B', [data])
        self.write_raw(write_data)

    def write_raw(self, data = Array('B')):
        """write_raw

        formats the data to write to the UART device

        the format of the data can be found on

        http://wiki.cospandesign.com/index.php?title=Wb_uart#Write_Data

        Args:
          data: data (in raw byte array) to send down to the UART

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "Writing to the UART device"


        length = len(data)

        data_array = Array('B')
        data_array.extend([((length >> 8) & 0xFF), (((length) & 0xFF))])
        data_array.extend(data)

        if self.debug:
            print "sending: %s" % str(data_array)
            print "Length: %d" % length

        pad = (len(data_array) % 4)
        for i in range (0, pad):
            data_array.extend([0])

        self.write(WRITE_DATA, data_array)

    def read_string(self, count = 1):
        """read_string

        Read a string of characters

        Args:
          count: the number of characters and returns a string
                  if -1 read all characters

        Returns:
          string

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "read_string"

        data = Array('B')
        if count == -1:
            data = self.read_all_data()
        else:
            data = self.read_raw(count)

        string = data.tostring()
        return string

    def read_raw(self, count = 1):
        """read_raw

        reads the number of bytes specified by count from the UART and
        extracts/returns only the raw bytes to the user

        Args:
          count: the number of bytes to read from the UART core, if
            left blank this will read just one byte

        Returns:
          An array of raw bytes read from the core

        Raises:
          NysaCommError: Error in communication
        """
        available = self.get_read_count()
        if available < count:
            count = available

        if count <= 4:
            word_count = 1
        else:
            #count = ((count - 2) / 4) + 1
            word_count = (count / 4) + 1


        #Tell the core we are going to read the specified amount of bytes
        self.write_register(READ_COUNT, count)
        data = self.read(READ_DATA, word_count)[0:count]

        self.debug = True 
        if self.debug:
            print "Reading %d bytes" % count
            print "Output byte count: " + str(count)
            print "Byte Data: %s" %  str(data)
        self.debug = False


        return data

    def get_read_count(self):
        """get_read_count

        reads the number of bytes available in the read FIFO

        Args:
          Nothing

        Returns:
          Number of bytes available in the read FIFO

        Raises:
          NysaCommError
        """
        return self.read_register(READ_COUNT)

    def read_all_data(self):
        """read_all_data

        reads all the data in the UART read FIFO

        Uses 'get_read_count' to find the number of bytes available
        then read those number of bytes and return them to the user

        Args:
          Nothing

        Returns:
          An array of raw bytes read from the core

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "read all the data in the UART input FIFO"

        count = self.get_read_count()
        data = Array('B')
        while count > 0:
            data.extend(self.read_raw(count))
            count = self.get_read_count()
            #time.sleep(0.05)
        return data

    def get_write_available(self):
        """get_write_available

        returns the number of bytes that can be written into the write buffer

        Args:
          Nothing

        Returns:
          Number of bytes that can be written into the write buffer

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "getting available space in the write buffer"

        return self.read_register(WRITE_AVAILABLE)

    def get_baudrate(self):
        """get_baudrate

        returns the baudrate of the UART

        This function performs the calculations required to extract the baudrate
        from the value within the UART core.

        For details on the calculations see:

        http://wiki.cospandesign.com/index.php?title=Wb_uart#Prescaler

        Args:
          Nothing

        Return:
          The baudrtate: e.g.: 115200

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "getting baurdrate"

        prescaler = self.read_register(PRESCALER)
        print "prescaler: %d" % prescaler
        clock_divider = self.read_register(CLOCK_DIVIDER)
        print "clock divide: %d" % clock_divider

        if prescaler == 0:
            raise UARTError("Prescaler read from UART core is 0 (That's bad)")
        return prescaler / clock_divider

    def set_baudrate(self, baudrate=115200):
        """set_baudrate

        sets the baudrate of the UART core

        This function performs the required calculations to generate the correct
        clock value used by the low level core.

        For details on the calculations see:

        http://wiki.cospandesign.com/index.php?title=Wb_uart#Clock_Divider

        Args:
          baudrate: e.g.: 115200

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "setting baudrate"
        prescaler = self.read_register(PRESCALER)
        clock_divider = prescaler / baudrate
        self.write_register(CLOCK_DIVIDER, clock_divider)

    def enable_hard_flowcontrol(self):
        """enable_hard_flowcontrol

        enables the use of CTS/RTS hardware flow control

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "setting cts/rts flowcontrol"
        self.set_register_bit(CONTROL, CONTROL_RTS_CTS_FC)

    def enable_soft_flowcontrol(self):
        """enable_soft_flowcontrol

        enables the use of XON XOFF software flow control

        ***NOTE THIS FUNCTION IS NOT IMPLEMENTED IN THE CORE YET***

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        Exception("Soft flow control not implemented yet!")

    def disable_flowcontrol(self):
        """disable_flowcontrol

        disable flow control (this is the default setting)

        Args:
          Nothing

        Returns:
          Nothing

        Raises:
          NysaCommError: Error in communication
        """
        if self.debug:
            print "Disable flow control"
        control = self.get_control()
        control = control & ~(CONTROL_RTS_CTS_FC | CONTROL_DTS_DSR_FC)
        self.set_control(control)


    def enable_read_interrupt(self):
        """enable_read_interrupt

        enable the read interrupt for the UART
        """
        if self.debug:
            print "Enable the read interrupt"

        self.set_register_bit(CONTROL, CONTROL_INT_READ)

    def disable_read_interrupt(self):
        """disable_read_interrupt

        disable the read interrupt for the UART
        """
        if self.debug:
            print "Disable the read interrupt"

        self.clear_register_bit(CONTROL, CONTROL_INT_READ)


    def enable_write_interrupt(self):
        """enable_write_interrupt

        Enable the write interrupt
        """
        if self.debug:
            print "Enable the write interrupt"

        self.set_register_bit(CONTROL, CONTROL_INT_WRITE)

    def disable_write_interrupt(self):
        """disable_write_interrupt

        Disable the write interrupt
        """
        if self.debug:
          print "Disable the write interrupt"

        self.clear_register_bit(CONTROL, CONTROL_INT_WRITE)


    def disable_interrupts(self):
        """disable_interrupts

        Disable all interrupts
        """
        if self.debug:
          print "Disable interrupts"

        control = self.get_control()
        control = control & ~(CONTROL_INT_WRITE | CONTROL_INT_READ)
        self.set_control(control)
        self.get_status()


def unit_test(nysa, dev_id, debug = False):
    """Unit test for UART
    """
    uart = UART(nysa, dev_id, debug = debug)
    #uart.reset()
    uart.set_control(0)
    print "Testing UART config"
    baudrate = uart.get_baudrate()
    print "Initial baudrate = %d" % baudrate
    print "Setting baudrate to 115200"
    uart.set_baudrate(115200)
    '''
    uart.set_baudrate(57600)
    if uart.get_baudrate() > (57600 - (57600 * .01)) and uart.get_baudrate() < (57600 + (57600 * .01)) :
        print "Baudrate is within 1% of target"
    else:
        print "Baudrate is not correct!"

    print "Reverting back to initial baudrate"
    uart.set_baudrate(baudrate)

    print "\tXXX: Cannot test hardware flow control!"
    '''
    print "\tControl: 0x%08X" % uart.get_control()

    print "Writing a string"
    uart.write_string("STEAM ROXORS THE BIG ONE!1!!\r\n")


    print "disable all interrupts"
    uart.disable_interrupts()
    print "Testing receive interrupt"
    uart.enable_read_interrupt()
    print "\tControl: 0x%08X" % uart.get_control()

    print "Read: %s " % uart.read_string(-1)
    uart.get_status()

    print "Waiting 5 second for receive interrupts"
    if uart.wait_for_interrupts(10) > 0:
        #if uart.is_interrupt_for_slave():
        print "Found a read interrupt"

        print "Read: %s" % uart.read_string(-1)

    print "After waiting for interupt"

    print "\tControl: 0x%08X" % uart.get_control()

    #uart.disable_read_interrupt()

    print "Testing write interrupt"
    uart.enable_write_interrupt()
    print "Waiting 1 second for write interrupts"
    #if uart.wait_for_interrupts(1) > 0:
    #    if uart.is_interrupt_for_slave():
    #        print "Found a write interrupt!"
    
    #uart.disable_write_interrupt()

    #print "Testing write"

    """
    print "Writing the maximum amount of data possible"
    write_max = uart.get_write_available() - 2
    print "Max: %d" % write_max
    data_out = Array('B')
    num = 0
    try:
        for i in range (0, write_max):
            num = (i) % 256
            if (i / 256) % 2 == 1:
                data_out.append( 255 - (num))
            else:
                data_out.append(num)


    except OverflowError as err:
        print "Overflow Error: %d >= 256" % num
        sys.exit(1)
    uart.write_raw(data_out)

    print "Testing read: Type something"


    time.sleep(3)

    fail = False
    fail_count = 0
    data = uart.read_all_data()

    if len(data_out) != len(data):
        print "data_in length not equal to data_out length:"
        print "\totugoing: %d incomming: %d" % (len(data_out), len(data))
        fail = True

    else:
        for i in range (0, len(data_out)):
            if data[i] != data_out[i]:
                fail = True
                print "Mismatch at %d: READ DATA %d != WRITE DATA %d" % (i, data[i], data_out[i])
                fail_count += 1


    if len(data) > 0:
        print "Read some data from the UART"
        print "data (raw): %s" % str(data)
        print "data (string): %s" % str(data.tostring())


    if not fail:
        print "UART test passed!"
    elif (fail_count == 0):
        print "Data length of data_in and data_out do not match"
    else:
        print "Failed: %d mismatches" % fail_count


    uart.write_raw(data_out)
    print "look for the status conditions"
    print "Status: " + hex(uart.get_status())

    if uart.is_read_overflow():
        print "Read overflow"

    """









