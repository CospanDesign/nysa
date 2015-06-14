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
HARD_DRIVE_ADDRESS_LOW          = 4
HARD_DRIVE_ADDRESS_HIGH         = 5
DEBUG_STATUS                    = 6
DEBUG_LINKUP_DATA               = 7
HARD_DRIVE_COMMAND              = 8
HARD_DRIVE_FEATURES             = 9

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

BIT_OOB_STATE_HIGH              = 3
BIT_OOB_STATE_LOW               = 0
BIT_RESET_COUNT_HIGH            = 11
BIT_RESET_COUNT_LOW             = 4


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

    def get_debug_linkup_data(self):
        return self.read_register(DEBUG_LINKUP_DATA)

    def get_hard_drive_lba(self):
        count = long(self.read_register(HARD_DRIVE_ADDRESS_HIGH))
        count = count << 32
        count += long(self.read_register(HARD_DRIVE_ADDRESS_LOW))
        return count

    def get_d2h_fis(self):
        return self.read_register_bit_range(HARD_DRIVE_STATUS, BIT_D2H_FIS_HIGH, BIT_D2H_FIS_LOW)

    def send_hard_drive_command(self, command):
        self.write_register(HARD_DRIVE_COMMAND, command)

    def send_hard_drive_features(self, features):
        self.write_register(HARD_DRIVE_FEATURES, features)

    def get_hard_drive_features(self):
        return self.write_register(HARD_DRIVE_FEATURES)


    def read_local_buffer(self, address = 0x00, size = 512):
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

