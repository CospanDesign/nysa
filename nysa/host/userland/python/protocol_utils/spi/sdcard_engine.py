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
SDCARD Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import time
import json

from array import array as Array

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from driver.spi import SPIError
from driver.spi import SPI

SLAVE_SELECT_BIT = 0

#COMMANDS
CMD_IDLE        = Array('B', [0x40, 0x00, 0x00, 0x00, 0x00])
CMD_SETUP       = Array('B', [0x48, 0x00, 0x00, 0x01, 0x08])
#Setup Card
#High Capacity Card         (bit 38)
#High Power Mode            (bit 36)
#Use Current Voltage Level  (bit 24)
#Use 3.3V
#CMD_INIT        = Array('B', [0x41, 0x58, 0x10, 0x00, 0x00])
CMD_READ_CID    = Array('B', [0x42, 0x00, 0x00, 0x00, 0x00])
CMD_READ_CSD    = Array('B', [0x49, 0x00, 0x00, 0x00, 0x00])
CMD_READ_STATUS = Array('B', [0x41, 0x00, 0x00, 0x00, 0x00])


#Register Definitions
R1_IDLE_STATE     = 1 << 0
R1_ERASE_RESET    = 1 << 1
R1_ILLEGAL_CMD    = 1 << 2
R1_CRC_ERR        = 1 << 3
R1_ERASE_SEQ_ERR  = 1 << 4
R1_ADDR_ERR       = 1 << 5
R1_PARAM_ERR      = 1 << 6



class SDCARDEngineError(Exception):
    pass

class SDCARDWorker(QtCore.QThread):
    init_worker = QtCore.pyqtSignal(object, object, name="sdcard_worker_init")
    reset_sdcard = QtCore.pyqtSignal(name="sdcard_reset")
    setup_sdcard = QtCore.pyqtSignal(name="sdcard_setup")
    init_sdcard = QtCore.pyqtSignal(name="sdcard_init")
    read_sdcard_cid = QtCore.pyqtSignal(name="read_sdcard_cid")

    def __init__(self):
        super(SDCARDWorker, self).__init__()
        self.init_worker.connect(self.init_sdcard_worker)
        self.reset_sdcard.connect(self.reset_card)
        self.setup_sdcard.connect(self.setup_card)
        self.init_sdcard.connect(self.init_card)
        self.read_sdcard_cid.connect(self.read_cid)


    def generate_crc(self, data):
        crc = 0
        bits = len(data) * 8
        value = 0
        for d in data:
            value = (value << 8) | d

        while bits > 0:
            bits -= 1
            crc = (crc << 1) ^ (0, 9) [((crc >> 6) ^ (value >> bits)) & 1]

        crc = crc << 1
        crc = crc | 1   #Last bit is for the end of a transaction
        crc = crc & 0xFF
        return crc

    def send_command(self, command, response_bit_length, en_crc = True):
        length = len(command) * 8
        if en_crc:
            length = (len(command) + 1) * 8
        length += (response_bit_length * 8) + 8
        print "Command Length: %d" % length
        self.spi.set_character_length(length)
        crc = self.generate_crc(command)
        data = Array('B', command)
        if en_crc:
            data.append(crc)
        print "Full Command:"
        for d in data:
            print "%02X " % d,

        print ""
        self.spi.set_write_data(data)
        self.spi.start_transaction()
        while self.spi.is_busy():
            time.sleep(0.01)

        return self.spi.get_read_data(response_bit_length)

    def print_r1_response(self, r1):
        print "R1 (%02X) States:" % r1
        if (r1 & R1_IDLE_STATE) > 0:
            print "\tIDLE"
        if (r1 & R1_ERASE_RESET) > 0:
            print "\tERASE RESET"
        if (r1 & R1_ILLEGAL_CMD) > 0:
            print "\tILLEGAL COMMAND"
        if (r1 & R1_CRC_ERR) > 0:
            print "\tCRC ERROR"
        if (r1 & R1_ADDR_ERR) > 0:
            print "\tADDRESS ERROR"
        if (r1 & R1_PARAM_ERR) > 0:
            print "\tPARAMETER ERROR"

    def init_sdcard_worker(self, spi, actions):
        print "Initializing worker"
        self.spi = spi
        self.actions = actions

        self.spi.set_tx_polarity(True)
        self.spi.set_rx_polarity(True)
        self.spi.auto_ss_control_enable(False)
        self.spi.set_lsb_enable(False)
        #Set Clock Rate to 1MHz
        self.spi.set_spi_clock_rate(100000)
        self.spi.set_slave_select_raw(0x00)
        self.spi.set_character_length(80)
        self.spi.set_write_data(Array('B', [0xFF, 0xFF, 0xFF, 0xFF,
                                            0xFF, 0xFF, 0xFF, 0xFF,
                                            0xFF, 0xFF, 0xFF, 0xFF,
                                            0xFF, 0xFF, 0xFF, 0xFF]))
        self.spi.start_transaction()
        time.sleep(0.10)
        while self.spi.is_busy():
            time.sleep(0.01)
        self.spi.set_spi_slave_select(SLAVE_SELECT_BIT, True)
        self.spi.auto_ss_control_enable(True)

    def reset_card(self):
        read_data = self.send_command(CMD_IDLE, 1, True)
        print "read data: %s" % read_data
        r1 = read_data[0]
        self.print_r1_response(r1)
        self.actions.sdcard_reset.emit()

    def setup_card(self):
        read_data = self.send_command(CMD_SETUP, 5, True)
        print "read data: %s" % read_data
        r1 = read_data[0]
        r7 = read_data[3]
        self.print_r1_response(r1)
        print "0x%02X" % r7

    def init_card(self):
        read_data = self.send_command(CMD_INIT, 1, True)
        print "read data: %s" % read_data
        r1 = read_data[0]
        self.print_r1_response(r1)

    def read_cid(self):
        read_data = self.send_command(CMD_CID, 5, True)
        print "read data: %s" % read_data
        r1 = read_data[0]
        self.print_r1_response(r1)



class SDCARDEngine (QtCore.QObject):

    def __init__(self, spi_driver, status, actions):
        super (SDCARDEngine, self).__init__()

        self.status = status
        self.status.Info(self, "Reset SPI-SDCARD Interface")
        self.sdcard_worker = None
        self.spi = spi_driver

        self.actions = actions
        self.status.Verbose(self, "Starting SDCARD Engine")
        self.start_worker()

    def start_worker(self, delay = 0.1):
        self.sdcard_worker = SDCARDWorker()
        self.worker_thread = QtCore.QThread()
        self.worker_thread.setObjectName("SDCard Worker")
        self.sdcard_worker.moveToThread(self.worker_thread)
        self.sdcard_worker.init_worker.emit(self.spi, self.actions)
        self.sdcard_worker.reset_sdcard.emit()
        self.sdcard_worker.setup_sdcard.emit()
        #self.sdcard_worker.init_sdcard.emit()

    def set_custom_speed(self, rate):
        self.status.Debug(self, "Set SDCARD Rate to a custom rate: %dkHz" % rate)
        self.spi.set_custom_speed(rate)

