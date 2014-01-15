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

"""
GPIO

Facilitates communication with the GPIO core

For more details see:

http://wiki.cospandesign.com/index.php?title=Wb_gpio

TODO: Implement Debounce

"""

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

import time
from array import array as Array

import nysa
from nysa.host.userland.python.nysa import Nysa
from nysa.host.userland.python.nysa import NysaCommError

#Register Constants
GPIO_PORT           =   0x00000000
GPIO_OUTPUT_ENABLE  =   0x00000001
INTERRUPTS          =   0x00000002
INTERRUPT_ENABLE    =   0x00000003
INTERUPT_EDGE       =   0x00000004

class GPIO(object):
    """ GPIO

        Communication with a GPIO Core
    """
    def __init__(self, nysa, dev_id, debug = False):
        self.dev_id = dev_id
        self.n = nysa
        self.debug = debug

    def get_core_id(self):
        #This core corresponds to a GPIO (Numbers are found in DRT.json)
        return 0x00000001

    def set_dev_id(self, dev_id):
        self.dev_id = dev_id

    def set_port_direction(self, direction):
        """set_port_direction

        Sets the direction of the port

        Args:
            direction: 32-bit value that will set the direction of all the ports

        Return:
            Nothing

        Raises:
            NysaCommError
        """
        if self.debug:
            print "Writing GPIO Direction"

        self.n.write_register(self.dev_id, GPIO_OUTPUT_ENABL, direction)


    def set_port_raw(self, value):
        """set_port_raw

        set multiple GPIO output values

        Args:
            value: 32-bit value that will replace the current ports

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.n.write_register(self.dev_id, GPIO_PORT, value)

    def get_port_raw(self):
        """get_port_raw

        Get multiple GPIO input values

        Args:
            Nothing

        Return:
            32-bit value representing the port values

        Raises:
            NysaCommError
        """
        return self.n.read_register(self.dev_id, GPIO_PORT)

    def set_bit_value(self, bit, value):
        """set_bit_value

        Sets an individual bit with the specified value (1, or 0)

        Args:
            bit: the bit of the port to set
            value: 1 or 0

        Return:
            Nothing

        Raises:
            NysaCommError
        """
        if self.debug:
            print "Setting individual bit value"

        port_raw = self.get_port_raw()

        bit_shifted = 1 << bit
        
        if self.debug:
            print "Value: 0x%08X" % value
            print "Bit: 0x%08X" % bit
            print "Bit Shift Value 0x%08X" % bit_shifted
            print "Port Value: 0x%08X" % port_raw

        if value != 0:
            port_raw |= bit_shifted

        else:
            port_raw &= ~bit_shifted

        if self.debug:
            print "New Port Value: 0x%08X" % port_raw

        self.set_port_raw(port_raw)

    def get_bit_value(self, bit):
        """get_bit_value

        Gets an individual bit value

        Args:
            bit

        Returns:
            1, 0

        Raises:
            NysaCommError
        """
        if self.debug:
                print "Getting individual bit value"

        port = self.get_port_raw()
        bit_shifted = 1 << bit

        if (bit_shifted & port) > 0:
            return 1

        return 0

    def set_interrupt_enable(self, interrupt_enable):
        """set_interrupt_enable
       
        Enables/Disables interrupts
       
        Args:
            interrupt_enable: 32-bit enable (1), disable(0) mask
       
        Return:
            Nothing
       
        Raises:
            NysaComError
        """
        self.n.write_register(self.dev_id, INTERRUPT_ENABLE, interrupt_enable)
 
    def get_interrupt_enable(self):
        """get_interrupt_enable
       
        Returns the interrupt mask
       
        Args:
            Nothing
       
        Returns:
            32-bit interrupt mask value
       
        Raises:
            Nothing
        """
        return self.n.get_register(self.dev_id, INTERRUPT_ENABLE)
 
    def set_interrupt_edge(self, interrupt_edge):
        """set_interrupt_edge
       
        Interrupt triggers on high (1) or low (0)
       
        Args:
            Interrupt_level: 32-bit enable (1), disable (0) mask
       
        Return:
            Nothing
       
        Raises:
            NysaCommError
        """
        self.n.write_register(self.dev_id, INTERRUPT_EDGE, interrupt_edge)
 
    def get_interrupt_edge(self):
        """get_interrupt_edge
       
        Returns the interrupt level
       
        Args:
            Nothing
       
        Returns:
            32-bit value contiaining the interrupt level
       
        Raises:
            NysaCommError
        """
        return self.n.read_register(self.dev_id, INTERRUPT_EDGE)
 
    def get_interrupts(self):
        """get_interrupts
       
        Returns a 32-bit value representing the interrupts on the specified pins
       
        Args:
            Nothing
       
        Returns:
            32-bit value containing the interrupts
       
        Raises:
            NysaCommError
        """
        return self.n.read_register(self.dev_id, INTERRUPTS)


def unit_test(n, dev_index):
    """unit_test
 
    Run the unit test of the GPIO
    """
    gpio = GPIO(n, dev_index)
 
    print "Testing output ports (like LEDs)"
 
    print "Flashing all the outputs for one second"
 
    print "Set all the ports to outputs"
    gpio.set_port_direction(0xFFFFFFFF)
 
    print "Set all the values to 0"
    gpio.set_port_raw(0xFFFFFFFF)
    time.sleep(1)
    gpio.set_port_raw(0x00000000)
 
    print "Reading inputs (Like buttons) in 2 second"
    gpio.set_port_direction(0x00000000)
    
    time.sleep(2)
    print "Read value: 0x%08X", gpio.get_port_raw()
    print "Reading inputs (Like buttons) in 2 second"
    time.sleep(2)
    print "Read value: 0x%08X", gpio.get_port_raw()
 
 
    print "Testing Interrupts, setting interrupts up for positive edge detect"
    gpio.set_interrupt_edge(0xFFFFFFFF)
    gpio.set_interrupt_enable(0xFFFFFFFF)
 
    print "Waiting for 5 seconds for the interrupts to fire"
    if gpio.n.wait_for_interrupts(5):
        if gpio.n.is_interrupt_for_slave(gpio.dev_id):
            print "Interrupt for GPIO detected!"
            print "Interrupts: 0x%08X", gpio.get_interrupts()
            print "Read value: 0x%08X", gpio.get_port_raw()


 
