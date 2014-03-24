#! /usr/bin/python

# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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


"""
DRT Viewer controller
"""
import os
import sys
import argparse


p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "cbuilder",
                 "drt")

#print os.path.abspath(p)
sys.path.append(p)

import drt as drt_controller

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

drt_description = []
drt_description.append("Version (2 Bytes)/DRT ID (2 Bytes)")
drt_description.append("Number of Devices (4 Bytes)")
drt_description.append("String Data Address (4 Bytes)")
drt_description.append("Board ID (4 Bytes)")
drt_description.append("Image ID (4 Bytes)")
drt_description.append("Reserved (2 Bytes)/Flags (2 Bytes)")
drt_description.append("Reserved (4 Bytes)")
drt_description.append("Reserved (4 Bytes)")

device_description = []
device_description.append("Device Sub ID (2 Bytes)/Device ID (2 Bytes)")
device_description.append("Device Flags (4 Bytes)")
device_description.append("Address (4 Bytes)")
device_description.append("Peripheral Register/Memory Size (4 Bytes)")
device_description.append("Device Unique ID (4 Bytes)")
device_description.append("Reserved (4 Bytes)")
device_description.append("Reserved (4 Bytes)")
device_description.append("Reserved (4 Bytes)")

class AppModel(object):

    def __init__(self):
        super(AppModel, self).__init__()

    def setup_model(self, controller, n):
        self.n = n
        self.controller = controller
        self.drt = self.n.read_drt()
        self.drt_string = ""
        self.num_of_devices = drt_controller.get_number_of_devices(self.drt)
        display_len = 8 + self.num_of_devices * 8
        for i in range (0, display_len):
            self.drt_string += "%02X%02X%02X%02X\n"% (self.drt[i * 4],
                                                      self.drt[i * 4 + 1],
                                                      self.drt[i * 4 + 2],
                                                      self.drt[i * 4 + 3])
 
        self.drt_lines = self.drt_string.splitlines()

    #ADD FUNCTIONS HERE TO CONTROL NYSA DEVICE/IMAGE
    def get_row_height(self, row):
        """
        Return the number of sub rows the constitute this row

        Args:
            row (int): the row to query

        Returns (int):
            the number of sub rows that are in this row

        Raises:
            Nothing
        """
        return 0

    def get_row_count (self):
        return len(self.drt_lines)

    def get_row_data(self, row):
        """
        Returns a list of row data for this row

        Args:
            row (int): the row to query

        Returns (list of strings):
            first index is the raw DRT value

        Raises:
            Nothing

        """
        row_data = []
        row_data.append(self.drt_lines[row])
        row_data.append(self.get_row_description(row))
        row_data.append(self.get_row_device_type(row))
        row_data.append(self._get_row_data(row))
        return row_data

    def get_row_device_type(self, row):
        if row < 8:
            return None
        index = (row / 8) - 1
        if self.n.is_memory_device(index):
            return "memory"
        return "peripheral"

    def get_row_description(self, row):
        if row < 8:
            return drt_description[row]
        else:
            offset = row % 8
            return device_description[offset]
            
    def _get_row_data(self, row):
        row_data = []
        if row < 8:
            if row == 0:
                version = int(self.drt_lines[0][0:4], 16)
                drt_id = int(self.drt_lines[0][4:8], 16)
                row_data.append("Version: 0x%04X" % version)
                row_data.append("DRT ID: 0x%04X" % drt_id)
                return row_data

            elif row == 1:
                row_data.append("Number of Devices: %d" % int(self.drt_lines[1], 16))
                return row_data

            elif row == 2:
                string_offset = int(self.drt_lines[2], 16)
                if string_offset == 0:
                    row_data.append("No String Data")
                else:
                    row_data.append("String Offset: 0x%08X" % string_offset)
                return row_data

            elif row == 3:
                board_id = int(self.drt_lines[3], 16)
                board_name = drt_controller.get_board_list()[board_id]
                #board_name = str(drt_controller.get_board_list())
                row_data.append("Board ID: 0x%08X" % int(self.drt_lines[3], 16))
                row_data.append("Board Name: %s" % board_name)
                return row_data

            elif row == 4:
                image_id = int(self.drt_lines[4], 16)
                if image_id == 0:
                    row_data.append("No Image ID")
                else:
                    row_data.append("Image ID: 0x%08X" % int(self.drt_lines[4], 16))
                return row_data
           
            elif row == 5:
                flags_data = (0x03 & int (self.drt_lines[5], 16))
                if flags_data == 0:
                    row_data.append("Bus Flags (Addr [1:0]) == 0: Wishbone")
                elif flags_data == 1:
                    row_data("Bus Flags (Addr [1:0]) == 1: AXI")
                elif flags_data == 2:
                    row_data("Bus Flags (Addr [1:0]) == 2: Reserved")
                elif flags_data == 3:
                    row_data("Bus Flags (Addr [1:0]) == 3: Reserved")
                return row_data

            elif row == 6:
                row_data.append("Reserved")
                return row_data

            elif row == 7:
                row_data.append("Reserved")
                return row_data

        else:
            offset = row % 8
            if offset == 0:
                dev_id = ((int(self.drt_lines[row], 16)) & 0xFFFF)
                dev = devices = drt_controller.get_device_list()[dev_id]
                #print "%s" % str(dev)
                
                row_data.append("Device ID: 0x%04X" % (int (self.drt_lines[row], 16) & 0xFFFF))
                row_data.append("Device Sub ID: 0x%04X" % (((int (self.drt_lines[row], 16)) >> 16) & 0xFFFF))
                row_data.append("%s: %s" % (dev["name"], dev["description"]))
                return row_data

            if offset == 1:
                row_data.append("Device Flags:")

                flags = int (self.drt_lines[row], 16)
                if (flags & 0x00000002) == 0:
                    row_data.append("Addr [1] == 0: Peripheral Slave")
                if (flags & 0x00000002) > 0:
                    row_data.append("Addr [1] == 1: Memory Slave")
                if (flags & 0x00000001) == 0:
                    row_data.append("Addr [0] == 0: Non-Standard Device")
                if (flags & 0x00000001) > 0:
                    row_data.append("Addr [0] == 1: Standard Device")

                return row_data

            if offset == 2:
                flags = int (self.drt_lines[row - 1], 16)
                addr = int (self.drt_lines[row], 16)
                if (flags & 0x00000002) == 0:
                    row_data.append ("Address of Peripheral on Peripheral Bus: 0x%08X" % addr)
                    row_data.append("Peripheral Device Index: 0x%02X" % ((addr >> 24) & 0xFF))
                else:
                    row_data.append("Address of Memory on Memory Bus: 0x%08X" % addr)

                return row_data

            if offset == 3:
                flags = int (self.drt_lines[row - 2], 16)
                if (flags & 0x00000002) > 0:
                    row_data.append("Memory Size (32-Bit Values): 0x%08X" % int(self.drt_lines[row], 16))
                    row_data.append("Memory Size (8-Bit Values): 0x%08X" % (4 * int(self.drt_lines[row], 16)))
                else:
                    row_data.append("Number of Peripheral Slave Registers: 0x%08X" % int (self.drt_lines[row], 16))
                return row_data

            if offset == 4:
                user_id = int (self.drt_lines[row], 16)
                if user_id == 0:
                    row_data.append("Device has no unique ID")
                else:
                    row_data.append("Unique Deivce ID: 0x%08X" % user_id)
                return row_data

            if offset == 5:
                return row_data

            if offset == 6:
                return row_data

            if offset == 7:
                return row_data

