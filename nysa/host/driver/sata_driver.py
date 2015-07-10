# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)

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

"""Sata Driver

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
from driver import DMAReadController

#Register Constants
CONTROL                     = 0x00
STATUS                      = 0x01

COSPANDESIGN_SATA_ID        = 0x01


CONTROL                         = 0
STATUS                          = 1

HARD_DRIVE_STATUS               = 2
HARD_DRIVE_SECTOR_COUNT         = 3
HARD_DRIVE_ADDRESS_HIGH         = 4
HARD_DRIVE_ADDRESS_LOW          = 5
DEBUG_STATUS                    = 6
DEBUG_LINKUP_DATA               = 7
HARD_DRIVE_COMMAND              = 8
HARD_DRIVE_FEATURES             = 9
LOCAL_BUFFER_WRITE_SIZE         = 10
DEBUG_HD_COUNTS                 = 11

SATA_BUFFER_OFFSET              = 0x100
SATA_BUFFER_SIZE                = 2**9


#Control
BIT_HD_COMMAND_RESET            = 0
BIT_EN_INT_HD_INTERRUPT         = 2
BIT_EN_INT_DMA_ACTIVATE_STB     = 3
BIT_EN_INT_D2H_REG_STB          = 4
BIT_EN_INT_PIO_SETUP_STB        = 5
BIT_EN_INT_D2H_DATA_STB         = 6
BIT_EN_INT_DMA_SETUP_STB        = 7
BIT_EN_INT_SET_DEVICE_BITS_STB  = 9
BIT_HD_RESET                    = 10
BIT_EN_DMA_CONTROL              = 11
BIT_STB_WRITE_LOCAL_BUFFER      = 12
BIT_STB_WRITE                   = 13
BIT_STB_READ                    = 14
BIT_STB_SYNC_ESCAPE             = 15

#Status
BIT_PLATFORM_READY              = 0
BIT_PLATFORM_ERROR              = 1
BIT_LINKUP                      = 2
BIT_COMMAND_LAYER_READY         = 3
BIT_SATA_BUSY                   = 4
BIT_PHY_READY                   = 5
BIT_LINK_LAYER_READY            = 6
BIT_TRANSPORT_LAYER_READY       = 7
BIT_HARD_DRIVE_ERROR            = 8
BIT_PIO_DATA_READY              = 9
BIT_RESET_ACTIVE                = 10
BIT_RX_COMM_INIT_DETECT         = 11
BIT_RX_COMM_WAKE_DETECT         = 12
BIT_TX_COMM_RESET               = 13
BIT_TX_COMM_WAKE                = 14
BIT_TX_OOB_COMPLETE             = 15
BIT_DIN_FIFO_READY0             = 16
BIT_DIN_FIFO_READY1             = 17


#Hard Drive Status
BIT_D2H_INTERRUPT               = 0
BIT_D2H_NOTIFICATION            = 1
BIT_D2H_PMULT_LOW               = 4
BIT_D2H_PMULT_HIGH              = 7
BIT_D2H_FIS_LOW                 = 8
BIT_D2H_FIS_HIGH                = 15
BIT_D2H_STATUS_LOW              = 16
BIT_D2H_STATUS_HIGH             = 23
BIT_D2H_ERROR_LOW               = 24
BIT_D2H_ERROR_HIGH              = 31

#Debug
BIT_OOB_STATE_HIGH              = 3
BIT_OOB_STATE_LOW               = 0
BIT_RESET_COUNT_HIGH            = 11
BIT_RESET_COUNT_LOW             = 4
BIT_D2H_INTERRUPT_EN            = 12
BIT_DMA_ACTIVATE_EN             = 13
BIT_D2H_PIO_SETUP_EN            = 14
BIT_D2H_DATA_EN                 = 15
BIT_DMA_SETUP_EN                = 16
BIT_CMD_WR_ST_HIGH              = 31
BIT_CMD_WR_ST_LOW               = 28
BIT_TRSPRT_HIGH                 = 27
BIT_TRSPRT_LOW                  = 24
BIT_LLW_ST_HIGH                 = 23
BIT_LLW_ST_LOW                  = 20

BIT_ACTIVATE_COUNT_HIGH         = 23
BIT_ACTIVATE_COUNT_LOW          = 16
BIT_ROK_COUNT_HIGH              = 15
BIT_ROK_COUNT_LOW               = 8
BIT_RERR_COUNT_HIGH             = 7
BIT_RERR_COUNT_LOW              = 0







class SATAError(Exception):
    pass

class SATADriver(driver.Driver):

    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return driver.get_device_id_from_name("storage manager")

    @staticmethod
    def get_abi_minor():
        return COSPANDESIGN_SATA_ID

    def __init__(self, nysa, urn, debug = False):
        super(SATADriver, self).__init__(nysa, urn, debug)
        self.config = SataConfig()

    def enable_sata_reset(self, enable):
        self.enable_register_bit(CONTROL, BIT_HD_RESET, enable)

    def is_sata_reset(self):
        return self.is_register_bit_set(CONTROL, BIT_HD_RESET)

    def is_sata_reset_active(self):
        return self.is_register_bit_set(CONTROL, BIT_RESET_ACTIVE)

    def enable_sata_command_layer_reset(self, enable):
        """
        Reset the SATA the command layer

        Args:
            enable: Reset
            enable: Release Reset

        Returns:
            Nothing

        Raises:
            Nothing
        """

        self.enable_register_bit(CONTROL, BIT_HD_COMMAND_RESET, enable)

    def is_sata_command_layer_reset(self):
        """
        Return true if the command layer is reset

        Args:
            Nothing

        Returns (Boolean):
            True: command layer is in a reset state
            False: command layer is not in a reset state

        Raises:
            Nothing
        """
        return self.is_register_bit_set(CONTROL, BIT_HD_COMMAND_RESET)

    def enable_hd_interrupt(self, enable):
        """
        Enable the module to interrupt the host when the hard drive issues an
        interrupt

        Args:
            Enable (boolean)
                True: Enable Interrupt
                False: Disable Interrupt

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.enable_register_bit(CONTROL, BIT_EN_INT_HD_INTERRUPT, enable)

    def is_hd_interrupt(self):
        """
        Returns True if the hard drive interrupt is enabled

        Args:
            Nothing

        Returns (Boolean):
            True: Hard Drive interrupt is enabled
            False: Hard Drive interrupt is not enabled

        Raises:
            Nothing
        """
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_HD_INTERRUPT)

    def enable_dma_activate_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_DMA_ACTIVATE_STB, enable)

    def is_dma_activate_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_DMA_ACTIVATE_STB)

    def enable_d2h_reg_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_D2H_REG_STB, enable)

    def is_d2h_reg_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_D2H_REG_STB)

    def enable_pio_setup_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_PIO_SETUP_STB, enable)

    def is_pio_setup_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_PIO_SETUP_STB)

    def enable_d2h_data_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_D2H_DATA_STB, enable)

    def is_d2h_data_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_D2H_DATA_STB)

    def enable_dma_setup_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_DMA_SETUP_STB, enable)

    def is_dma_setup_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_DMA_SETUP_STB)

    def enable_set_device_bits_stb(self, enable):
        self.enable_register_bit(CONTROL, BIT_EN_INT_SET_DEVICE_BITS_STB, enable)

    def is_set_device_bits_stb(self):
        return self.is_register_bit_set(CONTROL, BIT_EN_INT_SET_DEVICE_BITS_STB)

    def is_platform_ready(self):
        return self.is_register_bit_set(STATUS, BIT_PLATFORM_READY)

    def is_platform_error(self):
        return self.is_register_bit_set(STATUS, BIT_PLATFORM_ERROR)

    def is_linkup(self):
        return self.is_register_bit_set(STATUS, BIT_LINKUP)

    def is_command_layer_ready(self):
        return self.is_register_bit_set(STATUS, BIT_COMMAND_LAYER_READY)

    def is_transport_layer_ready(self):
        return self.is_register_bit_set(STATUS, BIT_TRANSPORT_LAYER_READY)

    def is_link_layer_ready(self):
        return self.is_register_bit_set(STATUS, BIT_LINK_LAYER_READY)

    def is_phy_ready(self):
        return self.is_register_bit_set(STATUS, BIT_PHY_READY)

    def is_sata_busy(self):
        return self.is_register_bit_set(STATUS, BIT_SATA_BUSY)

    def is_hard_drive_error(self):
        return self.is_register_bit_set(STATUS, BIT_HARD_DRIVE_ERROR)

    def is_pio_data_ready(self):
        return self.is_register_bit_set(STATUS, BIT_PIO_DATA_READY)

    def is_d2h_interrupt(self):
        return self.is_register_bit_set(HARD_DRIVE_STATUS, BIT_D2H_INTERRUPT)

    def is_d2h_notification(self):
        return self.is_register_bit_set(HARD_DRIVE_STATUS, BIT_D2H_NOTIFICATION)

    def get_d2h_pmult(self):
        return self.read_register_bit_range(HARD_DRIVE_STATUS, BIT_D2H_PMULT_HIGH, BIT_D2H_PMULT_LOW)

    def get_d2h_status(self):
        return self.read_register_bit_range(HARD_DRIVE_STATUS, BIT_D2H_STATUS_HIGH, BIT_D2H_STATUS_LOW)

    def get_d2h_error(self):
        return self.read_register_bit_range(HARD_DRIVE_STATUS, BIT_D2H_ERROR_HIGH, BIT_D2H_ERROR_LOW)

    def get_rx_comm_init_detect(self):
        return self.is_register_bit_set(STATUS, BIT_RX_COMM_INIT_DETECT)

    def get_rx_comm_wake_detect(self):
        return self.is_register_bit_set(STATUS, BIT_RX_COMM_WAKE_DETECT)

    def get_tx_comm_reset(self):
        return self.is_register_bit_set(STATUS, BIT_TX_COMM_RESET)

    def get_tx_comm_wake(self):
        return self.is_register_bit_set(STATUS, BIT_TX_COMM_WAKE)

    def get_tx_oob_complete(self):
        return self.is_register_bit_set(STATUS, BIT_TX_OOB_COMPLETE)

    def get_oob_state(self):
        return self.read_register_bit_range(DEBUG_STATUS, BIT_OOB_STATE_HIGH, BIT_OOB_STATE_LOW)

    def get_reset_count(self):
        return self.read_register_bit_range(DEBUG_STATUS, BIT_RESET_COUNT_HIGH, BIT_RESET_COUNT_LOW)

    def set_sector_count(self, count):
        self.write_register(HARD_DRIVE_SECTOR_COUNT, count)

    def get_sector_count(self):
        return self.read_register(HARD_DRIVE_SECTOR_COUNT)

    def get_debug_linkup_data(self):
        return self.read_register(DEBUG_LINKUP_DATA)

    def set_hard_drive_lba(self, lba):
        self.write_register(HARD_DRIVE_ADDRESS_LOW, (0xFFFFFFFF & lba))
        self.write_register(HARD_DRIVE_ADDRESS_HIGH, ((0xFFFF00000000 & lba) >> 32))

    def get_hard_drive_lba(self):
        count = long(self.read_register(HARD_DRIVE_ADDRESS_HIGH))
        count = count << 32
        count |= long(self.read_register(HARD_DRIVE_ADDRESS_LOW))
        return count

    def get_d2h_fis(self):
        return self.read_register_bit_range(HARD_DRIVE_STATUS, BIT_D2H_FIS_HIGH, BIT_D2H_FIS_LOW)

    def send_hard_drive_command(self, command):
        """
        Send down a command to the hard drive and

        Args:
            command (8-bit hard drive command)

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.write_register(HARD_DRIVE_COMMAND, command)

    def send_hard_drive_features(self, features):
        """
        Send down the feature register in the hard drive, the features are
        similar to the arguments of the function

        Args:
            features: unsigned 16-bit: feature value to send

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.write_register(HARD_DRIVE_FEATURES, features)

    def get_hard_drive_features(self):
        """
        Return hard drive features

        Args:
            Nothing

        Returns (16-bit unsigned int):
            the features of the command

        Raises:
            Nothing
        """
        return self.read_register(HARD_DRIVE_FEATURES)

    def get_local_buffer_write_size(self):
        return self.read_register(LOCAL_BUFFER_WRITE_SIZE)

    def set_local_buffer_write_size(self, size):
        self.write_register(LOCAL_BUFFER_WRITE_SIZE, size)

    def read_local_buffer(self, address = 0x00, size = 2048):
        """
        Read the local buffer within the SATA core, if no size is specified
        read the entire buffer,
        if no address is specified read from the beginning

        Args:
            address (Integer): address of data (32-bit aligned) Default 0x00
            size (Integer): Size of read (32-bit words) Default 512

        Returns (Array of Bytes):
            Returns the data as an array of bytes

        Raises:
            Nothing
        """
        return self.read(address + (SATA_BUFFER_OFFSET), length = size)

    def write_local_buffer(self, data, address = 0x00):
        """
        Write data to the local buffer that be used to send to the Hard Drive
        By Default the address is set to 0x00

        Args:
            data (Array of bytes): data
            address (Integer): Address within local buffer 0 - 511 (Default 0)

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.write(address + (SATA_BUFFER_OFFSET), data)

    def enable_dma_control(self, enable):
        """
        When set to 0 use the local 512 block of data to read and write Data
        to the SATA Hard Drive

        When set to 1 use the DMA Controller to read and write data from
        another memory device such as DDR3 or a remote block RAM


        Args:
            enable (boolean):
                False: Use Local Buffer
                True: Use DMA Controller

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.enable_register_bit(CONTROL, BIT_EN_DMA_CONTROL, enable)

    def is_dma_control(self):
        """
        Return True if the Data interface is controlled by the DMA or false
        if it is controlled by the local buffer

        Args:
            Nothing

        Returns (Boolean):
            True: Data is connected to the DMA Controller
            False: Data is attached to the local buffer

        Raises:
            Nothing
        """
        return self.is_register_bit_set(CONTROL, BIT_EN_DMA_CONTROL)

    def load_local_buffer(self):
        """
        Load the local buffer into the block to send to the hard drive
        NOTE: 'enable_dma_control' must be set to false
        This is a self clearning bit

        Args:
            Nothing

        Returns:
            Nothing

        Raises:
            Nothing
        """
        self.set_register_bit(CONTROL, BIT_STB_WRITE_LOCAL_BUFFER)

    def send_sync_escape(self):
        self.set_register_bit(CONTROL, BIT_STB_SYNC_ESCAPE)

    def get_hard_drive_native_size(self):
        """
        Returns the hard drive size in bytes

        Args:
            Nothing

        Returns (long):
            returns the maximum address of the hard drive
            multiplies by the address sector size
            max_sector_address * size_of_sector in bytes = max_size (bytes)

        Raises:
            Nothing

        """
        return self.get_hard_drive_max_native_lba() * 512

    def get_hard_drive_max_native_lba(self):
        self.send_hard_drive_features(0x00)
        self.send_hard_drive_command(0x27)
        time.sleep(0.2)
        return self.get_hard_drive_lba()

    def identify_hard_drive(self):
        self.send_hard_drive_features(0x00)
        #Send Identify Device Command
        #print "Requesting the ID from the hard drive..."
        self.send_hard_drive_command(0xEC)
        time.sleep(0.2)
        data = self.read_local_buffer()
        self.config.set_configuration_data(data)
        return data
        #print "data: %s" % str(data[0:128])

    def get_config(self):
        return self.config

    def hard_drive_sleep(self):
        self.send_hard_drive_command(0xE6)

    def hard_drive_configuration_identify(self):
        self.send_hard_drive_features(0xC2)
        self.send_hard_drive_command(0xB1)
        time.sleep(0.2)
        return self.read_local_buffer()

    def hard_drive_read(self, address, length):
        if length == 0:
            return
        if length == 0x10000:
            length = 0
        self.send_hard_drive_features(0x00)
        self.set_sector_count(length)
        self.set_hard_drive_lba(address)
        #self.send_hard_drive_command(0x24)
        self.send_hard_drive_command(0x25)

    def hard_drive_write(self, address, length):
        if length == 0:
            return
        if length == 0x10000:
            length = 0
        self.send_hard_drive_features(0x00)
        self.set_sector_count(length)
        self.set_hard_drive_lba(address)
        self.send_hard_drive_command(0x35)
        #self.send_hard_drive_command(0x34)

    def hard_drive_idle(self):
        self.send_hard_drive_features(0x00)
        self.set_sector_count(0x00)
        self.send_hard_drive_command(0x97)

    def get_din_fifo_status(self):
        return self.read_register_bit_range(STATUS, BIT_DIN_FIFO_READY1, BIT_DIN_FIFO_READY0)

    def is_d2h_interrupt_en(self):
        return self.is_register_bit_set(DEBUG_STATUS, BIT_D2H_INTERRUPT_EN)

    def is_dma_activate_en(self):
        return self.is_register_bit_set(DEBUG_STATUS, BIT_DMA_ACTIVATE_EN)

    def is_d2h_pio_setup_en(self):
        return self.is_register_bit_set(DEBUG_STATUS, BIT_D2H_PIO_SETUP_EN)

    def is_d2h_data_en(self):
        return self.is_register_bit_set(DEBUG_STATUS, BIT_D2H_DATA_EN)

    def is_dma_setup_en(self):
        return self.is_register_bit_set(DEBUG_STATUS, BIT_DMA_SETUP_EN)

    def get_cmd_wr_state(self):
        return self.read_register_bit_range(DEBUG_STATUS, BIT_CMD_WR_ST_HIGH, BIT_CMD_WR_ST_LOW)

    def get_transport_state(self):
        return self.read_register_bit_range(DEBUG_STATUS, BIT_TRSPRT_HIGH, BIT_TRSPRT_LOW)

    def get_link_layer_write_state(self):
        return self.read_register_bit_range(DEBUG_STATUS, BIT_LLW_ST_HIGH, BIT_LLW_ST_LOW)

    def get_activate_count(self):
        return self.read_register_bit_range(DEBUG_HD_COUNTS, BIT_ACTIVATE_COUNT_HIGH, BIT_ACTIVATE_COUNT_LOW)

    def get_r_ok_count(self):
        return self.read_register_bit_range(DEBUG_HD_COUNTS, BIT_ROK_COUNT_HIGH, BIT_ROK_COUNT_LOW)

    def get_r_err_count(self):
        return self.read_register_bit_range(DEBUG_HD_COUNTS, BIT_RERR_COUNT_HIGH, BIT_RERR_COUNT_LOW);

class SataConfig(object):
    def __init__(self, data = None):
        if data is None:
            self.data = None
            return
        self.set_configuration_data(data)

    def set_configuration_data(self, data):
        self.raw_data = data

    def _create_dword(data):
        return int(data[0] << 8 | data[1])

    def serial_number(self):
        data = self.raw_data
        d = Array('B')
        for i in range (20, 38, 4):
            d.append(data[i + 2])
            d.append(data[i + 3])
            d.append(data[i + 0])
            d.append(data[i + 1])

        return d.tostring()

    def max_number_of_sectors_that_can_transfer_per_interrupt(self):
        return self.raw_data[97]

    def capacity_in_sectors(self):
        data = self.raw_data
        sectors =   long((data[114] << 24) | \
                         (data[115] << 16) | \
                         (data[116] <<  8) | \
                         (data[117]      ))

        return sectors

    def max_user_sectors(self):
        data = self.raw_data
        sectors =   long((data[100] << 24) | \
                         (data[101] << 16) | \
                         (data[102] <<  8) | \
                         (data[103]      ))
        return sectors

    def dma_transfer_mode(self):
        tm = int((self.raw_data[176] << 8) |
                 (self.raw_data[177]     ))
        if (tm & 0x01) > 0:
            print "Ultra DMA Mode 0 is Supported"
        if (tm & 0x02) > 0:
            print "Ultra DMA Mode 1 is Supported"
        if (tm & 0x04) > 0:
            print "Ultra DMA Mode 2 is Supported"
        if (tm & 0x08) > 0:
            print "Ultra DMA Mode 3 is Supported"
        if (tm & 0x10) > 0:
            print "Ultra DMA Mode 4 is Supported"
        if (tm & 0x20) > 0:
            print "Ultra DMA Mode 5 is Supported"
        if (tm & 0x40) > 0:
            print "Ultra DMA Mode 6 is Supported"


        if (tm & 0x0100) > 0:
            print "Ultra DMA Mode 0 is Selected"
        if (tm & 0x0200) > 0:
            print "Ultra DMA Mode 1 is Selected"
        if (tm & 0x0400) > 0:
            print "Ultra DMA Mode 2 is Selected"
        if (tm & 0x0800) > 0:
            print "Ultra DMA Mode 3 is Selected"
        if (tm & 0x1000) > 0:
            print "Ultra DMA Mode 4 is Selected"
        if (tm & 0x2000) > 0:
            print "Ultra DMA Mode 5 is Selected"
        if (tm & 0x4000) > 0:
            print "Ultra DMA Mode 6 is Selected"

    def sata_enabled_features(self):

        f = int((self.raw_data[168] << 8 ) |
                (self.raw_data[169]      ))
        if (f & 0x02) > 0:
            print "Non Zero Buffer Offset in DMA Setup FIS Enabled"
        if (f & 0x04) > 0:
            print "DMA Setup Auto-Activate Optimization Enabled"
        if (f & 0x08) > 0:
            print "Device Initiated Interface Power Management Enabled"
        if (f & 0x010) > 0:
            print "In Order Delivery Enabled"
        if (f & 0x040) > 0:
            print "Software Settings Preseved After Reset Enabled"

        f = int((self.raw_data[258] << 8 ) |
                (self.raw_data[259]      ))

        if (f & 0x01):
            print "Write Cache Enabled"
        if (f & 0x02):
            print "Read Look Ahead Enabled"
        if (f & 0x04):
            print "Reverting Enabled"
        if (f & 0x08):
            print "Auto Reassign Enabled"

    def hard_drive_buffer_size(self):
        return self.raw_data[42]

