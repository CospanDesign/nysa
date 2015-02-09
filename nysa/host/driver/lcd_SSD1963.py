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

Facilitates communication with the New Haven 4.3 LCD

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time
import i2c
import random

from array import array as Array

import driver
from driver import NysaDMAException
from driver import DMAWriteController

LCD_SSD1963                   = 1



#LCD Constants
LCD_WIDTH                   = 480
LCD_HEIGHT                  = 272
BYTE_SIZE                   = LCD_WIDTH * LCD_HEIGHT * 4

HSYNC_TOTAL                 = 525
HBLANK                      = 68
HSYNC_PULSE                 = 40
HSYNC_PULSE_START           = 0

VSYNC_TOTAL                 = 360
VBLANK                      = 12
VSYNC_PULSE                 = 9
VSYNC_PULSE_START           = 0

COLUMN_START                = 0
COLUMN_END                  = LCD_WIDTH
PAGE_START                  = 0
PAGE_END                    = LCD_HEIGHT

#Register Constants
CONTROL                     = 0x00
STATUS                      = 0x01
COMMAND_DATA                = 0x02
PIXEL_COUNT                 = 0x03
MEM_0_BASE                  = 0x04
MEM_0_SIZE                  = 0x05
MEM_1_BASE                  = 0x06
MEM_1_SIZE                  = 0x07

#Control Bit Values
CONTROL_ENABLE              = 0
CONTROL_ENABLE_INTERRUPT    = 1
CONTROL_COMMAND_MODE        = 2
CONTROL_BACKLIGHT_ENABLE    = 3
CONTROL_RESET_DISPLAY       = 4
CONTROL_COMMAND_WRITE       = 5
CONTROL_COMMAND_READ        = 6
CONTROL_COMMAND_PARAMETER   = 7
CONTROL_WRITE_OVERRIDE      = 8
CONTROL_CHIP_SELECT         = 9
CONTROL_ENABLE_TEARING      = 10

#Status Bit Values
STATUS_MEMORY_0_EMPTY       = 0
STATUS_MEMORY_1_EMPTY       = 1

#MCU Addresses
MEM_ADR_NOP                 = 0x00
MEM_ADR_RESET               = 0x01
MEM_ADR_PWR_MODE            = 0x0A
MEM_ADR_ADR_MODE            = 0x0B
MEM_ADR_DISP_MODE           = 0x0D
MEM_ADR_GET_TEAR_EF         = 0x0E
MEM_ADR_ENTER_SLEEP_MODE    = 0x10
MEM_ADR_EXIT_SLEEP_MODE     = 0x11
MEM_ADR_ENTER_PARTIAL_MODE  = 0x12
MEM_ADR_EXIT_PARTIAL_MODE   = 0x13
MEM_ADR_EXIT_INVERT_MODE    = 0x20
MEM_ADR_ENTER_INVERT_MODE   = 0x21
MEM_ADR_SET_GAMMA_CURVE     = 0x26
MEM_ADR_SET_DISPLAY_OFF     = 0x28
MEM_ADR_SET_DISPLAY_ON      = 0x29
MEM_ADR_SET_COLUMN_ADR      = 0x2A
MEM_ADR_SET_PAGE_ADR        = 0x2B
MEM_ADR_WRITE_MEM_START     = 0x2C
MEM_ADR_READ_MEM_START      = 0x2E
MEM_ADR_SET_PARTIAL_AREA    = 0x30
MEM_ADR_SET_SCROLL_AREA     = 0x33
MEM_ADR_SET_TEAR_OFF        = 0x34
MEM_ADR_SET_TEAR_ON         = 0x35
MEM_ADR_SET_ADR_MODE        = 0x36
MEM_ADR_SET_SCROLL_START    = 0x37
MEM_ADR_EXIT_IDLE_MODE      = 0x38
MEM_ADR_ENTER_IDLE_MODE     = 0x39
MEM_ADR_SET_PIXEL_FORMAT    = 0x3A
MEM_ADR_WRITE_MEM_CONT      = 0x3C
MEM_ADR_READ_MEM_CONT       = 0x3E
MEM_ADR_SET_TEAR_SCANLINE   = 0x44
MEM_ADR_GET_SCANLINE        = 0x45
MEM_ADR_READ_DDB            = 0xA1
MEM_ADR_SET_LCD_MODE        = 0xB0
MEM_ADR_GET_LCD_MODE        = 0xB1
MEM_ADR_SET_HORIZ_PERIOD    = 0xB4
MEM_ADR_GET_HORIZ_PERIOD    = 0xB5
MEM_ADR_SET_VERT_PERIOD     = 0xB6
MEM_ADR_GET_VERT_PERIOD     = 0xB7
MEM_ADR_SET_GPIO_CONF       = 0xB8
MEM_ADR_GET_GPIO_CONF       = 0xB9
MEM_ADR_SET_GPIO_VAL        = 0xBA
MEM_ADR_GET_GPIO_STATUS     = 0xBB
MEM_ADR_SET_POST_PROC       = 0xBC
MEM_ADR_GET_POST_PROC       = 0xBD
MEM_ADR_SET_PWM_CONF        = 0xBE
MEM_ADR_GET_PWM_CONF        = 0xBF
MEM_ADR_SET_LCD_GEN0        = 0xC0
MEM_ADR_GET_LCD_GEN0        = 0xC1
MEM_ADR_SET_LCD_GEN1        = 0xC2
MEM_ADR_GET_LCD_GEN1        = 0xC3
MEM_ADR_SET_LCD_GEN2        = 0xC4
MEM_ADR_GET_LCD_GEN2        = 0xC5
MEM_ADR_SET_LCD_GEN3        = 0xC6
MEM_ADR_GET_LCD_GEN3        = 0xC7
MEM_ADR_SET_GPIO0_ROP       = 0xC8
MEM_ADR_GET_GPIO0_ROP       = 0xC9
MEM_ADR_SET_GPIO1_ROP       = 0xCA
MEM_ADR_GET_GPIO1_ROP       = 0xCB
MEM_ADR_SET_GPIO2_ROP       = 0xCC
MEM_ADR_GET_GPIO2_ROP       = 0xCD
MEM_ADR_SET_GPIO3_ROP       = 0xCE
MEM_ADR_GET_GPIO3_ROP       = 0xCF
MEM_ADR_SET_DBC_CONF        = 0xD0
MEM_ADR_GET_DBC_CONF        = 0xD1
MEM_ADR_SET_DBC_TH          = 0xD4
MEM_ADR_GET_DBC_TH          = 0xD5
MEM_ADR_SET_PLL             = 0xE0
MEM_ADR_SET_PLL_MN          = 0xE2
MEM_ADR_GET_PLL_MN          = 0xE3
MEM_ADR_GET_PLL_STATUS      = 0xE4
MEM_ADR_SET_LSHIFT_FREQ     = 0xE6
MEM_ADR_GET_LSHIFT_FREQ     = 0xE7
MEM_ADR_SET_PIX_DAT_INT     = 0xF0
MEM_ADR_GET_PIX_DAT_INT     = 0xF1


class LCDSSD1963Error(Exception):
    pass

class LCDSSD1963(driver.Driver):

    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name("LCD")

    @staticmethod
    def get_abi_minor():
        return LCD_SSD1963

    def __init__(self, nysa, urn, debug = False):
        super(LCDSSD1963, self).__init__(nysa, urn, debug)
        self.status = 0
        try:
            self.dma_writer = DMAWriteController(device     = self,
                                                mem_base0  = 0x00000000,
                                                #mem_base1  = 0x00100000,
                                                mem_base1  = BYTE_SIZE,
                                                size       = BYTE_SIZE,
                                                reg_status = STATUS,
                                                reg_base0  = MEM_0_BASE,
                                                reg_size0  = MEM_0_SIZE,
                                                reg_base1  = MEM_1_BASE,
                                                reg_size1  = MEM_1_SIZE,
                                                timeout    = 3,
                                                empty0     = STATUS_MEMORY_0_EMPTY,
                                                empty1     = STATUS_MEMORY_1_EMPTY)
        except NysaDMAException as ex:
            raise LCDSSD1963_ERROR("Error initializing the DMA Writer: %s" % str(ex))

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

        read the status register

        Args:
          Nothing

        Return:
          32-bit status register value

        Raises:
          NysaCommError: Error in communication
        """
        return self.read_register(STATUS)

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
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_TEARING, enable)

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
        return self.is_register_bit_set(CONTROL, CONTROL_ENABLE_TEARING)

    def get_image_width(self):
        return LCD_WIDTH

    def get_image_height(self):
        return LCD_HEIGHT

    def enable_lcd(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_ENABLE, enable)
        self.enable_register_bit(CONTROL, CONTROL_ENABLE_INTERRUPT, enable)
        mode = Array('B')
        if enable:
            mode.append(0x01)
        else:
            mode.append(0x00)
        self.write_command(MEM_ADR_SET_GPIO_VAL, mode)

    def reset_lcd(self):
        self.set_register_bit(CONTROL, CONTROL_RESET_DISPLAY)
        #Sleep for 400ms
        time.sleep(.4)
        self.clear_register_bit(CONTROL, CONTROL_RESET_DISPLAY)

    def enable_backlight(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_BACKLIGHT_ENABLE, enable)

    def override_write_en(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_WRITE_OVERRIDE, enable)

    def enable_chipselect(self, enable):
        self.enable_register_bit(CONTROL, CONTROL_CHIP_SELECT, enable)

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
        self.set_register_bit(CONTROL, CONTROL_COMMAND_MODE)
        #Tell the lcd command controller we are sending the command
        self.clear_register_bit(CONTROL, CONTROL_COMMAND_PARAMETER)
        #Put the data in the register
        self.write_register(COMMAND_DATA, address)
        self.set_register_bit(CONTROL, CONTROL_COMMAND_WRITE)
        #We are going to be writing
        for param in parameters:
            #We are going to be writing
            self.set_register_bit(CONTROL, CONTROL_COMMAND_PARAMETER)

            #waste of space but put the data into a 32-bit format
            p = 0x00
            p |= param

            #Put the data in the register
            self.write_register(COMMAND_DATA, p)
            #Initiate the transaction
            self.set_register_bit(CONTROL, CONTROL_COMMAND_WRITE)

        self.clear_register_bit(CONTROL, CONTROL_COMMAND_MODE)

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
        output = Array('B')
        #Get the control register
        self.set_register_bit(CONTROL, CONTROL_COMMAND_MODE)
        #Tell the lcd command controller we are sending the command
        self.clear_register_bit(CONTROL, CONTROL_COMMAND_PARAMETER)
        #Put the data in the register
        self.write_register(COMMAND_DATA, address)
        #We are going to be writing
        self.set_register_bit(CONTROL, CONTROL_COMMAND_WRITE)
        for i in range (length):
            #Tell the lcd command controller we are sending parameters
            self.set_register_bit(CONTROL, CONTROL_COMMAND_PARAMETER)
            #We are going to be reading
            self.set_register_bit(CONTROL, CONTROL_COMMAND_READ)

            #Read the data from the data register
            output.append(self.read_register(COMMAND_DATA))

        self.clear_register_bit(CONTROL, CONTROL_COMMAND_MODE)
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

        #Break Large value into byte size ones
        lcd_width_hb = (((LCD_WIDTH - 1) >> 8) & 0xFF)
        lcd_width_lb = ((LCD_WIDTH - 1) & 0xFF)

        lcd_height_hb = (((LCD_HEIGHT - 1) >> 8) & 0xFF)
        lcd_height_lb = ((LCD_HEIGHT - 1) & 0xFF)

        #Horizontal
        hsync_hb = (((HSYNC_TOTAL) >> 8) & 0xFF)
        hsync_lb = ((HSYNC_TOTAL) & 0xFF)

        hblank_hb = (((HBLANK) >> 8) & 0xFF)
        hblank_lb = ((HBLANK) & 0xFF)

        hsync_pulse_start_hb = (((HSYNC_PULSE_START) >> 8) & 0xFF)
        hsync_pulse_start_lb = ((HSYNC_PULSE_START) & 0xFF)

        #Vertical
        vsync_hb = (((VSYNC_TOTAL) >> 8) & 0xFF)
        vsync_lb = ((VSYNC_TOTAL) & 0xFF)

        vblank_hb = (((VBLANK) >> 8) & 0xFF)
        vblank_lb = ((VBLANK) & 0xFF)

        vsync_pulse_start_hb = (((VSYNC_PULSE_START) >> 8) & 0xFF)
        vsync_pulse_start_lb = ((VSYNC_PULSE_START) & 0xFF)

        column_start_hb = (((COLUMN_START) >> 8) & 0xFF)
        column_start_lb = ((COLUMN_START) & 0xFF)

        column_end_hb = (((COLUMN_END - 1) >> 8) & 0xFF)
        column_end_lb = ((COLUMN_END - 1) & 0xFF)

        page_start_hb = (((PAGE_START) >> 8) & 0xFF)
        page_start_lb = ((PAGE_START) & 0xFF)

        page_end_hb = (((PAGE_END - 1) >> 8) & 0xFF)
        page_end_lb = ((PAGE_END - 1) & 0xFF)

        if self.debug: print "Enable the LCD"
        #Reset the LCD
        self.enable_chipselect(True)
        self.enable_lcd(True)
        self.enable_backlight(True)
        self.override_write_en(True)
        self.reset_lcd()
        self.override_write_en(False)

        self.enable_chipselect(False)
        self.enable_chipselect(True)
        #Soft Reset the MCU
        self.write_command(MEM_ADR_RESET)
        time.sleep(.5)

        if self.debug: print_debug("MEM_ADR_RESET", True)
        #The example code reset this twice
        self.write_command(MEM_ADR_RESET)
        time.sleep(.2)
        if self.debug: print_debug("MEM_ADR_RESET", True)
        self.enable_chipselect(False)

        #self.write_command(MEM_ADR_SET_DISPLAY_OFF)
        #self.write_command(MEM_ADR_EXIT_SLEEP_MODE)

        self.enable_chipselect(True)

        mode = Array('B')
        mode.append(0x00)
        mode.append(0x01)
        self.write_command(MEM_ADR_SET_GPIO_CONF, mode)
        if self.debug: print_debug("MEM_ADR_SET_GPIO_CONF", True, mode)

        '''
        if self.debug:
            value = self.read_command(MEM_ADR_PWR_MODE, 1)
            print_debug("Power Mode", False, value)

        if self.debug:
            value = self.read_command(MEM_ADR_DISP_MODE, 1)
            print_debug("Display Mode", False, value)


        if self.debug:
            value = self.read_command(MEM_ADR_READ_DDB, 5)
            print_debug("Device Descriptor", False, value)
        if self.debug:
            value = self.read_command(MEM_ADR_GET_LCD_MODE, 7)
            print_debug("LCD Mode", False, value)
        '''

        #Start the PLL
        self.write_command(MEM_ADR_SET_PLL, Array('B', [0x01]))
        if self.debug: print_debug("MEM_ADR_SET_PLL", True, Array('B', [0x01]))
        time.sleep(.1)
        #Lock the PLL
        self.write_command(MEM_ADR_SET_PLL, Array('B', [0x03]))
        if self.debug: print_debug("MEM_ADR_SET_PLL", True, Array('B', [0x03]))

        #Setup the LCD Mode
        mode = Array('B')
        mode.append(0x20)          # Set TFT Mode - 0x0C ??
        #mode.append(0x80)          # Set TFT Mode & hsync + vsync + DEN Mode
        mode.append(0x00)          # Set TFT Mode & hsync + vsync + DEN Mode
        mode.append(lcd_width_hb)  # Set Horizontal size high byte
        mode.append(lcd_width_lb)  # Set Horizontal size low byte
        mode.append(lcd_height_hb) # Set Vertical size high byte
        mode.append(lcd_height_lb) # Set Vertical size low byte
        mode.append(0x00)          # Set even/odd line RGB sequence = RGB
        self.write_command(MEM_ADR_SET_LCD_MODE, mode)
        if self.debug: print_debug("MEM_ADR_LCD_MODE", True, mode)

        #if self.debug:
        #    value = self.read_command(MEM_ADR_GET_PIX_DAT_INT, 1)
        #    print_debug("MEM_ADR_GET_PIX_DAT_IN", False, value)
        #if self.debug:
        #    value = self.read_command(MEM_ADR_GET_PIX_DAT_INT, 1)
        #    print_debug("MEM_ADR_GET_PIX_DAT_IN", False, value)


        self.write_command(MEM_ADR_SET_PIXEL_FORMAT, Array('B', [0x70]))  # Set R G B Format: 6 6 6
        if self.debug: print_debug("MEM_ADR_SET_PIXEL_FORMAT", True, [0x70])
        #if self.debug:
        #    value = self.read_command(0x3B, 1)
        #    print_debug("MEM_ADR_GET_PIXEL_FORMAT", False, value)


        self.write_command(MEM_ADR_SET_PIX_DAT_INT, Array('B', [0x00]))  # Set pixel data I/F format = 8 bit
        if self.debug: print_debug("MEM_ADR_SET_PIX_DAT_IN", True, [0x00])

        #Setup PCLK frequency
        mode = pixel_frequency_to_array(pll_clock = 100, pixel_freq = 4.94)
        mode = Array('B')           #Setting pixel clock frequency to 4.94MHz
        #mode.append(0x05)
        mode.append(0x01)
        mode.append(0x45)
        mode.append(0x47)

        #if self.debug:
        #    value = self.read_command(MEM_ADR_GET_LSHIFT_FREQ, 3)
        #    print_debug("MEM_ADR_GET_LSHIFT_FREQ", False, value)


        self.write_command(MEM_ADR_SET_LSHIFT_FREQ, mode)     # Set PCLK Frequency = 4.94MHz
        if self.debug: print_debug("MEM_ADR_SET_LSHIFT_FREQ", True, mode)
        if self.debug:
            value = self.read_command(MEM_ADR_GET_LSHIFT_FREQ, 3)
            print_debug("MEM_ADR_GET_LSHIFT_FREQ", False, value)

        #Setup horizontal behavior
        mode = Array('B')
        mode.append(hsync_hb)               #(high byte) Set HSYNC Total Lines: 525
        mode.append(hsync_lb)               #(low byte) Set HSYNC Total Lines: 525
        mode.append(hblank_hb)              #(high byte) Set Horizonatal Blanking Period: 68
        mode.append(hblank_lb)              #(low byte) Set Horizontal Blanking Period: 68
        mode.append(HSYNC_PULSE)            #Set horizontal balnking period 16 = 15 + 1
        mode.append(hsync_pulse_start_hb)   #(high byte) Set Hsync pulse start position
        mode.append(hsync_pulse_start_lb)   #(low byte) Set Hsync pulse start position
        self.write_command(MEM_ADR_SET_HORIZ_PERIOD, mode)

        if self.debug: print_debug("MEM_ADR_SET_HORIZ_PERIOD", True, mode)
        #Setup Vertical Blanking Period
        mode = Array ('B')
        mode.append(vsync_hb)               #(high byte) Set Vsync total: 360
        mode.append(vsync_lb)               #(low byte) Set vsync total: 360
        mode.append(vblank_hb)              #(high byte) Set Vertical Blanking Period: 19
        mode.append(vblank_lb)              #(low byte) Set Vertical Blanking Period: 19
        mode.append(VSYNC_PULSE)            #Vsync pulse: 8 = 7 + 1
        mode.append(vsync_pulse_start_hb)   #(high byte) Set Vsync pusle start position
        mode.append(vsync_pulse_start_lb)   #(low byte) Set Vsync pusle start position
        self.write_command(MEM_ADR_SET_VERT_PERIOD, mode)

        if self.debug: print_debug("MEM_ADR_SET_VERT_PERIOD", True, mode)
        #Setup column address
        mode = Array('B')
        mode.append(column_start_hb) #(high byte) Set start column address: 0
        mode.append(column_start_lb) #(low byte) Set start column address: 0
        mode.append(column_end_hb)   #(high byte) Set end column address: 479
        mode.append(column_end_lb)   #(low byte) Set end column address: 479
        self.write_command(MEM_ADR_SET_COLUMN_ADR, mode)

        if self.debug: print_debug("MEM_ADR_SET_COLUMN_ADR", True, mode)
        #Setup page address
        mode = Array('B')
        mode.append(page_start_hb)   #(high byte) Start page address: 0
        mode.append(page_start_lb)   #(low byte) Start page address: 0
        mode.append(page_end_hb)     #(high byte) end page address: 271
        mode.append(page_end_lb)     #(low byte) end page address: 271
        self.write_command(MEM_ADR_SET_PAGE_ADR, mode)
        if self.debug: print_debug("MEM_ADR_SET_PAGE_ADR", True, mode)

        #Setup image configuration
        mode = Array('B')
        mode.append(0x00)
        self.write_command(MEM_ADR_SET_ADR_MODE, mode)

        if self.debug: print_debug("MEM_ADR_SET_ADR_MODE", True, mode)
        self.write_command(MEM_ADR_EXIT_PARTIAL_MODE)

        if self.debug: print_debug("MEM_ADR_EXIT_PARTIAL_MODE", True)
        self.write_command(MEM_ADR_EXIT_IDLE_MODE)

        if self.debug: print_debug("MEM_ADR_EXIT_IDLE_MODE", True)
        self.write_command(MEM_ADR_SET_DISPLAY_ON)

        if self.debug: print_debug("MEM_ADR_SET_DISPLAY_ON", True)
        #Setup the correct pixel count
        pixel_count = LCD_WIDTH * LCD_HEIGHT
        self.write_register(PIXEL_COUNT, pixel_count)
        pc = self.read_register(PIXEL_COUNT)
        if self.debug: print "Pixel Height x Width: (%d x %d):  %d" % (LCD_WIDTH, LCD_HEIGHT, pixel_count)
        if self.debug: print "Control: 0x%08X" % self.read_register(CONTROL)

        #Enable Tearing
        mode = Array('B')
        mode.append(0x00)   #Only send on VBLANKs
        self.write_command(MEM_ADR_SET_TEAR_ON, mode)
        self.enable_tearing(True)

        '''
        if self.debug: print_debug("MEM_ADR_SET_TEAR_ON", True, mode)
        t = time.time() + .1
        self.enable_tearing(True)
        if self.debug:
            while (time.time() < t):
                ef = self.read_command(MEM_ADR_GET_TEAR_EF, 1)
                print "Tear Effect: 0x%01X" % ef[0]
                print_debug("MEM_ADR_GET_TEAR_EF", False, ef)
        '''
        #Enable the backlight
        mode = Array('B')
        mode.append(0x0E)
        mode.append(0xFF)
        mode.append(0x01)
        mode.append(0x00)
        mode.append(0x00)
        mode.append(0x00)

        self.write_command(MEM_ADR_SET_PWM_CONF, mode)
        if self.debug: print_debug ("MEM_ADR_SET_PWM_CONF", True, mode)
        mode = self.read_command(MEM_ADR_GET_PWM_CONF, 6)
        if self.debug: print_debug ("MEM_ADR_SET_PWM_CONF", False, mode)

        #Define Threshold Values for things

        #DBC
        #mode = Array('B')
        #mode.append(0xD0)
        #self.write_command(MEM_ADR_SET_DBC_CONF, mode)

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
