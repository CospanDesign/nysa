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

""" I2C

Facilitates communication with the I2C core independent of communication
medium

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_i2c

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import time

from array import array as Array

from userland.python import nysa
from userland.python.nysa import NysaCommError

#Register Constants
CONTROL               = 0
STATUS                = 1
CLOCK_RATE            = 2
CLOCK_DIVISOR         = 3
COMMAND               = 4
TRANSMIT              = 5
RECEIVE               = 6

#Control bit values
CONTROL_EN            = 1 << 0
CONTROL_INTERRUPT_EN  = 1 << 1
CONTROL_SET_100KHZ    = 1 << 2
CONTROL_SET_400KHZ    = 1 << 3
CONTROL_RESET         = 1 << 7

#Status
STATUS_IRQ_FLAG       = 1 << 0
STATUS_TIP            = 1 << 1
STATUS_ARB_LOST       = 1 << 5
STATUS_BUSY           = 1 << 6
STATUS_READ_ACK_N     = 1 << 7

#Command
COMMAND_START         = 1 << 0
COMMAND_STOP          = 1 << 1
COMMAND_READ          = 1 << 2
COMMAND_WRITE         = 1 << 3
COMMAND_NACK           = 1 << 4

class I2CError (Exception):
    """I2C Error:

    Errors associated with I2C
        I2C Bus Busy
        Incorrect Settings
    """
    pass


class I2C(object):
    """I2C
    """
    def __init__(self, nysa, dev_id, debug = False):
        self.dev_id = dev_id
        self.n = nysa
        self.debug = debug

    def set_dev_id(self, dev_id):
        self.dev_id = dev_id

    def get_control(self):
        """get_control

        Read the control register

        Args:
            Nothing

        Return:
            32-bit control register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.read_register(self.dev_id, CONTROL)

    def set_control(self):
        """set_control

        Write the control register

        Args:
            control: 32-bit control value

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.write_register(self.dev_id, CONTROL, control)


    def get_status(self):
        """get_status

        read the status register

        Args:
            Nothing

        Return:
            32-bit status register value

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.read_register(self.dev_id, STATUS)

    def set_command(self, command):
        """set_command

        set the command register

        Args:
            command: 32-bit command value

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.o.write_register(self.dev_id, COMMAND, command)

    def reset_i2c_core(self):
        """reset_i2c_core

        reset the i2c core

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError
        """
        #The core will clear disable the reset the control bit on it's own
        self.n.set_register_bit(self.dev_id, CONTROL, CONTROL_RESET)


    def get_clock_rate(self):
        """get_clock_rate

        returns the clock rate from the module

        Args:
            Nothing

        Returns:
            32-bit representation of the clock

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.read_register(self.dev_id, CLOCK_RATE)

    def get_clock_divider(self):
        """get_clock_divider

        returns the clock divider from the module

        Args:
            Nothing

        Returns:
            32-bit representation of the clock divider

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.read_register(self.dev_id, CLOCK_DIVISOR)

    def set_speed_to_100khz(self):
        """set_speed_to_100khz

        sets the flag for 100khz mode

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.set_register_bit(self.dev_id, CONTROL, CONTROL_SET_100KHZ)

    def set_speed_to_400khz(self):
        """set_speed_to_400khz

        sets the flag for 400khz mode

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.set_register_bit(self.dev_id, CONTROL, CONTROL_SET_400KHZ)

    def set_custom_speed(self, rate):
        """set_custom_speed

        sets the clock divisor to generate the custom speed

        Args:
            rate: speed of I2C

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        clock_rate = self.get_clock_rate()
        divisor = clock_rate / (5 * rate)
        self.set_clock_divider(divisor)

    def set_clock_divider(self, clock_divider):
        """set_clock_divider

        set the clock divider

        Args:
            clock_divider: 32-bit value to write into the register

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.write_register(self.dev_id, CLOCK_DIVISOR, clock_divider)

    def enable_i2c(self, enable):
        """enable_i2c

        Enable the I2C core

        Args:
            enable:
                True
                False

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.enable_register_bit(self.dev_id, CONTROL, CONTROL_EN, enable)

    def is_i2c_enabled(self):
        """is_i2c_enabled

        returns true if i2c is enabled

        Args:
            Nothing

        Returns:
            True: Enabled
            False: Not Enabled

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.is_register_bit_set(self.dev_id, CONTROL, CONTROL_EN)

    def enable_interrupt(self, enable):
        """enable_interrupts

        Enable interrupts upon completion of sending a byte and arbitrattion
        lost

        Args:
            enable:
                True
                False

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.n.enable_register_bit(self.dev_id, CONTROL, CONTROL_INTERRUPT_EN,
                                  enable)

    def is_interrupt_enabled(self):
        """is_i2c_enabled

        returns true if i2c is enabled

        Args:
            Nothing

        Returns:
            True: Enabled
            False: Not Enabled

        Raises:
            NysaCommError: Error in communication
        """
        return self.n.is_register_bit_set(self.dev_id, CONTROL,
                                          CONTROL_INTERRUPT_EN)


    def print_control(self, control):
        """print_control

        print out the control in an easily readible format

        Args:
            status: The control to print out

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        print "Control (%X): " % control
        if (control & CONTROL_EN) > 0:
            print "\tI2C Core Enabled"
        if (control & CONTROL_INTERRUPT_EN) > 0:
            print "\tI2C Interrupt Enabled"

    def print_command(self,command):
        """print_command

        print out the command in an easily readible format

        Args:
            status: The command to print out

        Returns:
            Nothing

        Raises:
            Nothing
        """
        print "Command (%X): " % command
        if (command & COMMAND_START) > 0:
            print "\tSTART"
        if (command & COMMAND_STOP) > 0:
            print "\tSTOP"
        if (command & COMMAND_READ) > 0:
            print "\tREAD"
        if (command & COMMAND_WRITE) > 0:
            print "\tWRITE"
        if (command & COMMAND_NACK) > 0:
            print "\tACK"

    def print_status(self, status):
        """print_status

        print out the status in an easily readible format

        Args:
            status: The status to print out

        Returns:
            Nothing

        Raises:
            Nothing
        """

        print "Status (%X): " % status
        if (status & STATUS_IRQ_FLAG) > 0:
            print "\tInterrupt pending"
        if (status & STATUS_TIP) > 0:
            print "\tTransfer in progress"
        if (status & STATUS_ARB_LOST) > 0:
            print "\tArbitration lost"
        if (status & STATUS_BUSY) > 0:
            print "\tTransaction in progress"
        if (status & STATUS_READ_ACK_N) > 0:
            print "\tNo ack from slave"
        else:
            print "\tAck from slave"

    def reset_i2c_device(self):
        """reset_i2c_device

        resets the I2C devices

        Args:
            Nothing

        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.print_control(self.get_control())
        #send the write command / i2c identification
        self.n.write_register(self.dev_id, TRANSMIT, 0xFF)
        self.n.write_register(self.dev_id, COMMAND, COMMAND_WRITE | COMMAND_STOP)
        self.n.write_register(self.dev_id, TRANSMIT, 0xFF)
        self.n.write_register(self.dev_id, COMMAND, COMMAND_WRITE | COMMAND_STOP)

        time.sleep(.1)
        if self.debug:
            self.print_status(self.get_status())

    def write_to_i2c(self, i2c_id, i2c_data):
        """write_to_i2c_register

        write to a register in the I2C device

        Args:
            i2c_id: Identification byte of the I2C (7-bit)
                this value will be shifted left by 1
            i2c_data: data to write to that register Array of bytes

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
            I2CError: Errors associated with the I2C protocol
        """
        #set up a write command
        write_command = i2c_id << 1

        #set up interrupts
        self.enable_interrupt(True)

        #send the write command / i2c identification
        self.o.write_register(self.dev_id, TRANSMIT, write_command)


        command = COMMAND_START | COMMAND_WRITE
        if self.debug:
            self.print_command(command)
        #send the command to the I2C command register to initiate a transfer
        self.o.write_register(self.dev_id, COMMAND, command)

        #wait 1 second for interrupt
        if self.o.wait_for_interrupts(wait_time = 1):
            if self.debug:
                print "got interrupt for start"
            if self.o.is_interrupt_for_slave(self.dev_id):
                status = self.get_status()
                if self.debug:
                    self.print_status(status)
                if (status & STATUS_READ_ACK_N) > 0:
                    raise I2CError("Did not recieve an ACK while writing I2C ID")

        else:
            if self.debug:
                self.print_status(self.get_status())
            raise I2CError("Timed out while waiting for interrupt durring a start")

        #send the data
        count = 0
        if self.debug:
            print "total data to write: %d" % len(i2c_data)
        if len(i2c_data) > 1:
            while count < len(i2c_data) - 1:
                if self.debug:
                    print "Writing %d" % count
                data = i2c_data[count]
                self.o.write_register(self.dev_id, TRANSMIT, data)
                self.o.write_register(self.dev_id, COMMAND, COMMAND_WRITE)
                if self.o.wait_for_interrupts(wait_time = 1):
                    if self.debug:
                        print "got interrupt for data"
                    if self.o.is_interrupt_for_slave(self.dev_id):
                        status = self.get_status()
                        if (status & STATUS_READ_ACK_N) > 0:
                            raise I2CError("Did not receive an ACK while writing data")
                else:
                    raise I2CError("Timed out while waiting for interrupt durring send data")

                count = count + 1

        #send the last peice of data
        data = i2c_data[count]
       
        self.o.write_register(self.dev_id, TRANSMIT, data)
        self.o.write_register(self.dev_id, COMMAND, COMMAND_WRITE | COMMAND_STOP)
        if self.o.wait_for_interrupts(wait_time = 1):
            if self.debug:
                print "got interrupt for the last byte"
            if self.o.is_interrupt_for_slave(self.dev_id):
                status = self.get_status()
                if (status & STATUS_READ_ACK_N) > 0:
                    raise I2CError("Did not receive an ACK while writing data")
        else:
            raise I2CError("Timed out while waiting for interrupt while sending the last byte")



    def read_from_i2c(self, i2c_id, i2c_write_data, read_length):
        """read_from_i2c_register
       
        read from a register in the I2C device
       
        Args:
            i2c_id: Identification byte of the I2C (7-bit)
                this value will be shifted left by 1
            i2c_write_data: data to write to that register (Array of bytes)
                in order to read from an I2C device the user must write some
                data to set up the device to read
            read_length: Length of bytes to read from the device
       
        Returns:
            Array of bytes read from the I2C device
       
        Raises:
            NysaCommError: Error in communication
            I2CError: Errors associated with the I2C protocol
        """
        #self.debug = True
        #set up a write command
        read_command = (i2c_id << 1) | 0x01
        read_data = Array('B')
       
        #setup the registers to read
        self.write_to_i2c(i2c_id, i2c_write_data)
       
        #set up interrupts
        self.enable_interrupt(True)
       
        #send the write command / i2c identification
        self.o.write_register(self.dev_id, TRANSMIT, read_command)
       
       
        command = COMMAND_START | COMMAND_WRITE
        if self.debug:
            self.print_command(command)
        #send the command to the I2C command register to initiate a transfer
        self.o.write_register(self.dev_id, COMMAND, command)
       
        #wait 1 second for interrupt
        if self.o.wait_for_interrupts(wait_time = 1):
            if self.debug:
                print "got interrupt for start"
            if self.o.is_interrupt_for_slave(self.dev_id):
                status = self.get_status()
                if self.debug:
                    self.print_status(status)
                if (status & STATUS_READ_ACK_N) > 0:
                    raise I2CError("Did not recieve an ACK while writing I2C ID")
       
        else:
            if self.debug:
                self.print_status(self.get_status())
            raise I2CError("Timed out while waiting for interrupt durring a start")
       
        #send the data
        count = 0
        if read_length > 1:
            while count < read_length - 1:
                self.get_status()
                if self.debug:
                    print "\tReading %d" % count
                self.o.write_register(self.dev_id, COMMAND, COMMAND_READ)
                if self.o.wait_for_interrupts(wait_time = 1):
                    if self.get_status() & 0x01:
                        #print "Status: 0x%08X" % self.get_status()
                        if self.debug:
                            print "got interrupt for data"
                        #if self.o.is_interrupt_for_slave(self.dev_id):
                        status = self.get_status()
                        #if (status & STATUS_READ_ACK_N) > 0:
                        #  raise I2CError("Did not receive an ACK while reading data")
                        value = self.o.read_register(self.dev_id, RECEIVE)
                        if self.debug:
                            print "value: %s" % str(value)
                        read_data.append((value & 0xFF))
               
               
                else:
                    raise I2CError("Timed out while waiting for interrupt during read data")
               
                count = count + 1
       
        #read the last peice of data
        self.get_status()
        self.o.write_register(self.dev_id, COMMAND, COMMAND_READ | COMMAND_NACK | COMMAND_STOP)
        if self.o.wait_for_interrupts(wait_time = 1):
            if self.debug:
                print "got interrupt for the last byte"
            if self.get_status() & 0x01:
                #if self.o.is_interrupt_for_slave(self.dev_id):
                #status = self.get_status()
                #if (status & STATUS_READ_ACK_N) > 0:
                #  raise I2CError("Did not receive an ACK while writing data")
               
                value = self.o.read_register(self.dev_id, RECEIVE)
                if self.debug:
                  print "value: %d" % value
                read_data.append(value & 0xFF)
        else:
            raise I2CError("Timed out while waiting for interrupt while reading the last byte")
       
        return read_data
       
def unit_test(nysa, dev_id):
    print "Unit test!"
    i2c = I2C(nysa, dev_id)
 
    print "Check if core is enabled"
    print "enabled: " + str(i2c.is_i2c_enabled())
 
 
    print "Disable core"
    i2c.enable_i2c(False)
 
    print "Check if core is enabled"
    print "enabled: " + str(i2c.is_i2c_enabled())
 
    print "Enable core"
    i2c.enable_i2c(True)
 
    print "Check if core is enabled"
    print "enabled: " + str(i2c.is_i2c_enabled())
 
    print "Check if interrupt is enabled"
    print "enabled: " + str(i2c.is_interrupt_enabled())
 
    print "Enable interrupt"
    i2c.enable_interrupt(True)
    print "Check if interrupt is enabled"
    print "enabled: " + str(i2c.is_interrupt_enabled())
 
    clock_rate = i2c.get_clock_rate()
    print "Clock Rate: %d" % clock_rate
 
    print "Get clock divider"
    clock_divider = i2c.get_clock_divider()
    print "Clock Divider: %d" % clock_divider
 
    print "Set clock divider to generate 100kHz clock"
    i2c.set_speed_to_100khz()
 
    print "Get clock divider"
    clock_divider = i2c.get_clock_divider()
    print "Clock Divider: %d" % clock_divider
 
    print "Set clock divider to generate 400kHz clock"
    i2c.set_speed_to_400khz()
 
    print "Get clock divider"
    clock_divider = i2c.get_clock_divider()
    print "Clock Divider: %d" % clock_divider
 
    print "Set a custom clock divider to get 1MHz I2C clock"
    i2c.set_custom_speed(1000000)
 
    print "Get clock divider"
    clock_divider = i2c.get_clock_divider()
    print "Clock Divider: %d" % clock_divider
 
    print "Setting clock rate back to 100kHz"
    i2c.set_speed_to_100khz()
 
    print "testing HMC compass"
 
    print "Resetting I2C device"
    #i2c.reset_i2c_device()
 
    i2c_id = 0x21
    data   = Array('B', [0x47, 0x7F, 0x55])
 
    i2c.write_to_i2c(i2c_id, data)
 
    #reading from I2C device
    print "Reading from register"
    data  = Array('B', [0x41])
    read_data = i2c.read_from_i2c(i2c_id, data, 2)
    print "Read Data: %s" % str(read_data)






