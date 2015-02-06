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

import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from nysa.host.nysa import Nysa
from nysa.host.nysa import NysaCommError

from driver import Driver

#Sub Module ID
COSPAN_DESIGN_GPIO_MODULE = 0x01

#Register Constants
GPIO_PORT           =   0x00000000
GPIO_OUTPUT_ENABLE  =   0x00000001
INTERRUPTS          =   0x00000002
INTERRUPT_ENABLE    =   0x00000003
INTERRUPT_EDGE      =   0x00000004
INTERRUPT_BOTH_EDGE =   0x00000005
INTERRUPT_TIMEOUT   =   0x00000006
READ_CLOCK_RATE     =   0x00000007

class GPIO(Driver):

    """ GPIO

        Communication with a GPIO Core
    """
    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return Nysa.get_id_from_name("GPIO")

    @staticmethod
    def get_abi_minor():
        return COSPAN_DESIGN_GPIO_MODULE

    def __init__(self, nysa, urn, debug = False):
        super(GPIO, self).__init__(nysa, urn, debug)

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

        self.write_register(GPIO_OUTPUT_ENABLE, direction)

    def get_port_direction(self):
        """get_port_direction

        Gets the direction of the port

        Args:
            Nothing

        Return (Integer):
            32-bit value that will set the direction of all the ports

        Raises:
            NysaCommError
        """

        if self.debug:
            print "Reading GPIO Direction"

        return self.read_register(GPIO_OUTPUT_ENABLE)

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
        self.write_register(GPIO_PORT, value)

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
        return self.read_register(GPIO_PORT)

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
        self.enable_register_bit(GPIO_PORT, bit, value)

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
        return self.is_register_bit_set(GPIO_PORT, bit)

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
        self.write_register(INTERRUPT_ENABLE, interrupt_enable)

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
        return self.read_register(INTERRUPT_ENABLE)

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
        self.write_register(INTERRUPT_EDGE, interrupt_edge)

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
        return self.read_register(INTERRUPT_EDGE)

    def set_interrupt_both_edge(self, interrupt_both_edge):
        self.write_register(INTERRUPT_BOTH_EDGE, interrupt_both_edge)

    def get_interrupt_both_edge(self):
        return self.read_register(INTERRUPT_BOTH_EDGE)

    def set_interrupt_timeout(self, interrupt_timeout):
        self.write_register(INTERRUPT_BOTH_EDGE, interrupt_timeout)

    def get_interrupt_timeout(self):
        return self.read_register(INTERRUPT_TIMEOUT)

    def get_clock_rate(self):
        return self.read_register(READ_CLOCK_RATE)

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
        return self.read_register(INTERRUPTS)


