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

"""New Haven LCD

Facilitates communication with the New Haven 2.8 LCD

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time
import i2c
import random

from array import array as Array

from nysa.host.nysa import Nysa
from nysa.host.nysa import NysaCommError

import driver
from driver import NysaDMAException
from driver import DMAWriteController

LCD_ST7781R                 = 3

#LCD Constants
LCD_WIDTH                   = 320
LCD_HEIGHT                  = 220
BYTE_SIZE                   = LCD_WIDTH * LCD_HEIGHT * 4

REG_CONTROL                 = 0x00000000
REG_STATUS                  = 0x00000001
REG_COMMAND_DATA            = 0x00000002
REG_PIXEL_COUNT             = 0x00000003
REG_MEM_0_BASE              = 0x00000004
REG_MEM_0_SIZE              = 0x00000005
REG_MEM_1_BASE              = 0x00000006
REG_MEM_1_SIZE              = 0x00000007
REG_DATA_ADDRESS            = 0x00000008
REG_TEAR_ADDRESS            = 0x00000009
REG_TEAR_COUNT              = 0x0000000A
REG_TEAR_VALUE              = 0x0000000B


CONTROL_ENABLE              = 0
CONTROL_ENABLE_INTERRUPT    = 1
CONTROL_BACKLIGHT_ENABLE    = 2
CONTROL_RESET_DISPLAY       = 3

CONTROL_COMMAND_MODE        = 4
CONTROL_COMMAND_WRITE       = 5
CONTROL_COMMAND_READ        = 6
CONTROL_COMMAND_RS          = 7

CONTROL_CHIP_SELECT         = 8
CONTROL_ENABLE_TEARING      = 9
CONTROL_SOFT_TEAR           = 10
CONTROL_TEAR_POLARITY       = 11

STATUS_MEMORY_0_EMPTY       = 0
STATUS_MEMORY_1_EMPTY       = 1



class LCDST7781RError(Exception):
    pass

class LCDST7781R(driver.Driver):

    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name("LCD")

    @staticmethod
    def get_abi_minor():
        return LCD_ST7781R

    def __init__(self, nysa, urn, debug = False):
        super(LCDST7781R, self).__init__(nysa, urn, debug)
        print "LCDST7781R_ LCD Device ID: %d" % self.dev_id
        #self.write_register(PIXEL_COUNT, LCD_WIDTH * LCD_HEIGHT)

        self.status = 0
        try:
            self.dma_writer = DMAWriteController(device     = self,
                                                mem_base0  = 0x00000000,
                                                mem_base1  = 0x00100000,
                                                size       = BYTE_SIZE / 4,
                                                reg_status = REG_STATUS,
                                                reg_base0  = REG_MEM_0_BASE,
                                                reg_size0  = REG_MEM_0_SIZE,
                                                reg_base1  = REG_MEM_1_BASE,
                                                reg_size1  = REG_MEM_1_SIZE,
                                                timeout    = 3,
                                                empty0     = STATUS_MEMORY_0_EMPTY,
                                                empty1     = STATUS_MEMORY_1_EMPTY)
        except NysaDMAException as ex:
            raise LCDST7781R_ERROR("Error initializing the DMA Writer: %s" % str(ex))

    def get_control(self):
        """get_control

        read the control register

        Args:
          Nothing

        Return:
          32-bit control register value

        Raises:
          NysaCommError: Error in communication
        """
        return self.read_register(REG_CONTROL)

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
        self.write_register(REG_CONTROL, control)

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
        return self.read_register(REG_STATUS)

    def enable_tearing(self, enable):
        """
        Enable tearing controller.

        Tearing is when the image data is written image buffer while the
        image controller is writing it to the screen. This causes a visible
        tearing effect.

        Enabling this value will poll the image controller as to the state of
        the write cycle and only write when the image controller is not writing
        to the screen

        Args:
            enable (boolean):
                True: Enable tearing
                False: Disable tearing

        Returns:
            Nothing

        Raises:
            NysaCommError
        """
        self.enable_register_bit(REG_CONTROL, CONTROL_ENABLE_TEARING, enable)

    def is_tearing_enabled(self):
        """
        Returns the state of the tearing effect

        Args:
            Nothing

        Returns (boolean):
            Tearing effect is enabled or not

        Raises:
            NysaCommError
        """
        return self.is_register_bit_set(REG_CONTROL, CONTROL_ENABLE_TEARING)

    def get_image_width(self):
        return LCD_WIDTH

    def get_image_height(self):
        return LCD_HEIGHT

    def enable_lcd(self, enable):
        self.enable_register_bit(REG_CONTROL, CONTROL_ENABLE, enable)
        self.enable_register_bit(REG_CONTROL, CONTROL_ENABLE_INTERRUPT, enable)

    def reset_lcd(self):
        self.set_register_bit(REG_CONTROL, CONTROL_RESET_DISPLAY)
        #Sleep for 400ms
        time.sleep(.4)
        self.clear_register_bit(REG_CONTROL, CONTROL_RESET_DISPLAY)

    def enable_backlight(self, enable):
        self.enable_register_bit(REG_CONTROL, CONTROL_BACKLIGHT_ENABLE, enable)

    def override_write_en(self, enable):
        self.enable_register_bit(REG_CONTROL, CONTROL_WRITE_OVERRIDE, enable)

    def enable_chipselect(self, enable):
        self.enable_register_bit(REG_CONTROL, CONTROL_CHIP_SELECT, enable)

    def write_command(self, address, parameters=Array('B')):
        """
        write data to the MCU register and, if specified, some parameters
        values, incomming data is in a byte array format

        Args:
            address (integer): register address to write to
            parameters (Array of bytes): bytes to write to the MCU
        Return:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        self.enable_chipselect(True)
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_MODE)
        #Tell the lcd command controller we are sending the command
        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)
        #Put the data in the register
        self.write_register(REG_COMMAND_DATA, 0x00)
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_WRITE)

        self.write_register(REG_COMMAND_DATA, address)
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_WRITE)
        #We are going to be writing
        for param in parameters:
            #We are going to be writing
            self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)

            #waste of space but put the data into a 32-bit format
            p = 0x00
            p |= param

            #Put the data in the register
            self.write_register(REG_COMMAND_DATA, p)
            #Initiate the transaction
            self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_WRITE)

        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_MODE)
        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)
        self.enable_chipselect(False)

    def read_command(self, address, length):
        """
        read data or status from the MCU, the length specifies how much
        data to read from the MCU after the address is written

        Args:
            address (integer): register address to write to
            length (integer): number of bytes to read from the register

        Returns:
            (Array of bytes) 8-bit value of the register

        Raises:
            NysaCommError: Error in communication
        """
        self.enable_chipselect(True)
        output = Array('B')
        #Get the control register
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_MODE)
        #Tell the lcd command controller we are sending the command
        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)

        self.write_register(REG_COMMAND_DATA, 0x00)
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_WRITE)
        #Put the data in the register
        self.write_register(REG_COMMAND_DATA, address)
        #We are going to be writing
        self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_WRITE)
        for i in range (length):
            #Tell the lcd command controller we are sending parameters
            self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)
            #We are going to be reading
            self.set_register_bit(REG_CONTROL, CONTROL_COMMAND_READ)

            #Read the data from the data register
            output.append(self.read_register(REG_COMMAND_DATA))

        self.enable_chipselect(False)
        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_MODE)
        self.clear_register_bit(REG_CONTROL, CONTROL_COMMAND_RS)
        return output

    def setup(self):
        """
        Sets up the LCD display

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            NysaCommError: Error in communication
        """
        if self.debug: print "Enable the LCD"
        #Reset the LCD

        self.enable_lcd(False)
        lcd_id = self.read_command(0x00, 2)
        print_debug("LCD ID: ", False, lcd_id)

        #Device Output:
        #   SM: 0
        #   SS (Shift Out, S1 => S720): 1
        self.write_command(0x01, Array('B', [0x01, 0x00]))
        #   ?? Undocumented
        self.write_command(0x02, Array('B', [0x07, 0x00]))
        #Entry Mode:
        #   AM: Sets the DRAM Update Direction: 1 (Horizontal)
        #   ID: 01 (Data goes left to right)
        #   ORG: Moves the origin address to the beginning
        #   HWM: Hardware Power Save Mode (Off) 0
        #   BGR: Chance color from RGB to BGR (Off) 0
        #   DFM: Data Format (8-Bit values)
        #   TRI: Data is triple (8-bit)
        self.write_command(0x03, Array('B', [0xC0, 0x98]))
        self.write_command(0x04, Array('B', [0x00, 0x00]))
        self.write_command(0x08, Array('B', [0x03, 0x02]))
        self.write_command(0x0A, Array('B', [0x00, 0x08]))

        self.write_command(0x0C, Array('B', [0x00, 0x02]))
        self.write_command(0x0D, Array('B', [0x00, 0x00]))
        self.write_command(0x0F, Array('B', [0x00, 0x00]))

        time.sleep(0.100)

        self.write_command(0x30, Array('B', [0x00, 0x00]))
        self.write_command(0x31, Array('B', [0x04, 0x05]))
        self.write_command(0x32, Array('B', [0x02, 0x03]))
        self.write_command(0x35, Array('B', [0x00, 0x04]))
        self.write_command(0x36, Array('B', [0x0B, 0x07]))
        self.write_command(0x37, Array('B', [0x00, 0x00]))
        self.write_command(0x38, Array('B', [0x04, 0x05]))
        self.write_command(0x39, Array('B', [0x02, 0x03]))
        self.write_command(0x3c, Array('B', [0x00, 0x04]))
        self.write_command(0x3d, Array('B', [0x0B, 0x07]))

        self.write_command(0x20, Array('B', [0x00, 0x00]))
        self.write_command(0x21, Array('B', [0x00, 0x00]))

        self.write_command(0x50, Array('B', [0x00, 0x00]))
        self.write_command(0x51, Array('B', [0x00, 0xEF]))
        self.write_command(0x52, Array('B', [0x00, 0x00]))
        self.write_command(0x53, Array('B', [0x01, 0x3F]))

        time.sleep(0.100)


        self.write_command(0x60, Array('B', [0xA7, 0x00]))
        self.write_command(0x61, Array('B', [0x00, 0x01]))

        self.write_command(0x90, Array('B', [0x00, 0x3A]))
        self.write_command(0x95, Array('B', [0x02, 0x1E]))
        self.write_command(0x80, Array('B', [0x00, 0x00]))
        self.write_command(0x81, Array('B', [0x00, 0x00]))
        self.write_command(0x82, Array('B', [0x00, 0x00]))
        self.write_command(0x83, Array('B', [0x00, 0x00]))
        self.write_command(0x84, Array('B', [0x00, 0x00]))
        self.write_command(0x85, Array('B', [0x00, 0x00]))
        self.write_command(0xFF, Array('B', [0x00, 0x01]))
        self.write_command(0xB0, Array('B', [0x14, 0x0D]))
        self.write_command(0xFF, Array('B', [0x00, 0x00]))
        time.sleep(0.100)
        self.write_command(0x07, Array('B', [0x01, 0x33]))
        time.sleep(0.050)

        self.write_command(0x10, Array('B', [0x14, 0xE0]))
        time.sleep(0.100)
        self.write_command(0x07, Array('B', [0x01, 0x33]))

        #pos = 0x2F
        #data = self.read_command(pos, 2)
        #print "Data: %s" % data
        #self.write_command(0x22, Array('B', [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        #data = self.read_command(pos, 2)
        #print "Data: %s" % data



        self.enable_lcd(True)

def pixel_frequency_to_array(pll_clock = 100, pixel_freq = 5.3):
    """
    change an interger frequency to value to a value that can be put into the
    MCU
    """
    output = Array('B')
    value = (((pixel_freq) / pll_clock) * (2 **20)) - 1
    value = int(value)
    #print "Value: 0x%08X" % value
    output.append((value >> 16) & 0xFF)
    output.append((value >> 8) & 0xFF)
    output.append(value & 0xFF)
    return output
    blue = '\033[94m'
    purple = '\033[95m'
    cyan = '\033[96m'
    if writing:
        print "%sLCD Write: %s%s" % (cyan, name, blue)
        if len(data) > 0:
            print "\t",
            for value in data:
                print "%02X " % value,
        print white,
    else:
        print "%sLCD Read:  %s%s" % (purple, name, yellow)
        if len(data) > 0:
            print "\t",
            for value in data:
                print "%02X " % value,
        print white,
    print ""


def print_debug(name = "Signal", writing = False, data = Array('B')):
    white = '\033[0m'
    gray = '\033[90m'
    red   = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[95m'
    cyan = '\033[96m'
    if writing:
        print "%sLCD Write: %s%s" % (cyan, name, blue)
        if len(data) > 0:
            print "\t",
            for value in data:
                print "%02X " % value,
        print white,
    else:
        print "%sLCD Read:  %s%s" % (purple, name, yellow)
        if len(data) > 0:
            print "\t",
            for value in data:
                print "%02X " % value,
        print white,
    print ""
