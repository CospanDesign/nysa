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
I2S

Facilitates communication with the I2S core

for more details see:

http://wiki.cospandesign.com/index.php?title=Wb_i2s
"""

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from driver import Driver
from driver import DMAWriteController

#Register Constants
CONTROL         = 0
STATUS          = 1
CLOCK_RATE      = 2
CLOCK_DIVISOR   = 3
MEM_0_BASE      = 4
MEM_0_SIZE      = 5
MEM_1_BASE      = 6
MEM_1_SIZE      = 7

#Control bit values
CONTROL_ENABLE            = 0
CONTROL_INTERRUPT_ENABLE  = 1
CONTROL_WAVE_POST_FIFO    = 2
CONTROL_WAVE_PRE_FIFO     = 3

#Status bit values
STATUS_MEM_0_EMPTY        = 0
STATUS_MEM_1_EMPTY        = 1

#Default Memory Base
MEM_OFFSET0 = 0x00000000
#AUDIO_BUF_SIZE = 0x00080000
AUDIO_BUF_SIZE = 1000000


#Sub ID
COSPAN_DESIGN_I2S_MODULE = 0x01

class I2SError(Exception):
    pass

class I2S(Driver):
    """
    I2S
    """

    @staticmethod
    def get_abi_class(self):
        return 0

    @staticmethod
    def get_abi_major(self):
        return Driver.get_device_id_from_name("i2s")

    @staticmethod
    def get_abi_minor(self):
        return COSPAN_DESIGN_I2S_MODULE

    def __init__(self, nysa, urn, debug = False):
        super(I2S, self).__init__(nysa, urn, debug)
        self.wdma = DMAWriteController(device       = self,
                                       mem_base0    = MEM_OFFSET0,
                                       mem_base1    = AUDIO_BUF_SIZE,
                                       size         = AUDIO_BUF_SIZE,
                                       reg_status   = STATUS,
                                       reg_base0    = MEM_0_BASE,
                                       reg_size0    = MEM_0_SIZE,
                                       reg_base1    = MEM_1_BASE,
                                       reg_size1    = MEM_1_SIZE,
                                       timeout      = 3,
                                       empty0       = STATUS_MEM_0_EMPTY,
                                       empty1       = STATUS_MEM_1_EMPTY)

    def get_mem_block_size(self):
        return self.wdma.get_size()

    def get_available_memory_blocks(self):
        return self.wdma.get_available_memory_blocks()

    def get_status(self):
        return self.read_register(STATUS)

    def enable_i2s(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE, enable)

    def is_i2s_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE)

    def enable_interrupt(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_INTERRUPT_ENABLE, enable)

    def is_interrupt_enabled(self):
        return self.is_register_bit_set(CONTROL, CONTROL_INTERRUPT_ENABLE)

    def enable_post_fifo_test(self, enable):
        """
        Enable the FIFO test after the Memory interface and the final FIFO,
        this is used for debugging the I2S phy layer,

        a sine wave within the FPGA is outputted over the I2S bus

        Args:
            enable (Boolean):
                True: Enable FIFO Test
                False: Disable FIFO Test

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_WAVE_POST_FIFO, enable)

    def is_post_fifo_test_enabled(self):
        """
        Returns true if currently testing the I2S phy

        Args:
            Nothing

        Returns (Boolean):
            True: Post FIFO test is enabled
            False: Post FIFO test is not enabled

        Raises:
            NysaCommError: Error in communication
        """
        return self.is_register_bit_set(CONTROL, CONTROL_WAVE_POST_FIFO)

    def enable_pre_fifo_test(self, enable):
        """Enable the FIFO test before the both the final FIFO and the I2S
        phy layer, this is usefule to determine if there is an error with
        the final FIFO

        Args:
            Enable (Boolean):
                True: Enable pre FIFO test
                False: Disable pre FIFO test

        Returns:
            Nothing


        Raises:
            NysaCommError: Error in communication
        """
        self.enable_register_bit(CONTROL, CONTROL_WAVE_PRE_FIFO, enable)

    def is_pre_fifo_test_enabled(self):
        """
        Returns true if the core is currently sending data through the
        final FIFO.

        If this test is used after the 'post_fifo_test' a problem within
        the final FIFO can be isolated.

        Also if passing this test (the user hears a sine wave) then if
        there is an issue it is more than likely related to a memory
        interface

        Args:
            Nothing

        Returns (Boolean):
            True: Pre FIFO test is enabled
            False: Pre FIFO test is not enabled

        Raises:
            NysaCommError: Error in communication
        """
        return self.is_register_bit_set(CONTROL, CONTROL_WAVE_PRE_FIFO)

    def get_clock_rate(self):
        """Returns the clock rate of the FPGA,

        This can be used to generate a platform independent clock divisor

        Args:
            Nothing

        Returns (Integer):
            Clock rate of the FPGA (IE: 50000000 = 50MHz)

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CLOCK_RATE)

    def get_clock_divisor(self):
        """
        Returns the clock divisor

        The audio phy layer speed is determined by this register value

        Args:
            Nothing

        Returns (Integer):
            The number used to divide the clock down for the I2S Phy

        Raises:
            NysaCommError: Error in communication
        """
        return self.read_register(CLOCK_DIVISOR)

    def set_clock_divisor(self, divisor):
        """
        Setup the clock divisor for the I2S core

        Args:
            divisor (Integer): Divide the clock down by this number for the
            I2S Phy

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.write_register(CLOCK_DIVISOR, divisor)

    def set_custom_sample_rate(self, sample_rate, audio_bits = 24, channels = 2):
        """
        Sets the clock divisor to generate the requested sample rate

        Args:
            sample_rate (integer): desired sample rate of I2S phy
            channels (integer): 2 are supported right now

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
            I2SError: Channel != 2
        """
        if channels != 2:
            #XXX: Fix me!
            raise I2SError("Channels can only be 2 at this time");
        clock_rate = self.get_clock_rate()
        divisor = clock_rate / ((sample_rate * audio_bits * channels) + 1)
        self.set_clock_divisor(divisor)

    def get_sample_rate(self, audio_bits = 24, channels = 2):
        """
        Gets the sample rate of the I2S phy

        Args:
            audio_bits (Integer): number of audio sample bits
            channels (Integer): 2 (left/right) are supported now

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
            I2SError: Channel != 2
        """
        if channels != 2:
            #XXX: Fix me!
            raise I2SError("Channels can only be 2 at this time");

        clock_rate = self.get_clock_rate()
        divisor = self.get_clock_divisor()
        sample_rate = clock_rate / ((divisor * audio_bits * channels) + 1)
        return sample_rate

    def write_audio_data(self, audio_data):
        """
        Writes the audio data

        writes the raw PCM data to memory, the memory data is in the format of:

        32-bits

        31: left = 0, right = 1 channel
        30 - 24: Reserved
        23 - 0: Audio data

        This will automatically detect where the memory should be written, it
        will set up interrupts and attempt to continuously write down data to
        the device.

        Args:
            aduio_data (Array of bytes): corresponding to the audio data in the
            format described above

        Returns:
            Nothing


        Raises:
            NysaCommError: Error in communication
        """
        self.wdma.write(audio_data)


