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
CMD0            = Array('B', [0x40, 0x00, 0x00, 0x00, 0x00])
CMD8            = Array('B', [0x48, 0x00, 0x00, 0x01, 0x08])
CMD58           = Array('B', [0x7A, 0x00, 0x00, 0x00, 0x00])
CMD55           = Array('B', [0x77, 0x00, 0x00, 0x00, 0x00])
#SDC Support
ACMD41          = Array('B', [0x69, 0x10, 0x00, 0x00, 0x00])
#SDHC/SDXC Support
#ACMD41          = Array('B', [0x69, 0x50, 0x00, 0x00, 0x00])

CMD13           = Array('B', [0x4D, 0x00, 0x00, 0x00, 0x00])

#Register Definitions
R1_IDLE_STATE                   = 1 << 0
R1_ERASE_RESET                  = 1 << 1
R1_ILLEGAL_CMD                  = 1 << 2
R1_CRC_ERR                      = 1 << 3
R1_ERASE_SEQ_ERR                = 1 << 4
R1_ADDR_ERR                     = 1 << 5
R1_PARAM_ERR                    = 1 << 6

R2_PARAMETER_ERROR              = 1 << 14
R2_ADDRESS_ERROR                = 1 << 13
R2_ERASE_SEQ_ERROR              = 1 << 12
R2_COMM_CRC_ERROR               = 1 << 11
R2_ILLEGAL_CMD                  = 1 << 10
R2_ERASE_RESET                  = 1 << 9
R2_IN_IDLE_STATE                = 1 << 8
R2_OUT_OF_RANGE                 = 1 << 7
R2_ERASE_PARAM                  = 1 << 6
R2_WP_VIOLATION                 = 1 << 5
R2_CARD_ECC_FAILED              = 1 << 4
R2_CC_ERROR                     = 1 << 3
R2_ERRROR                       = 1 << 2
R2_WP_ERASE_SKIP                = 1 << 1
R2_CARD_IS_LOCKED               = 1 << 0


STATE_START                     = 0
STATE_VOLTAGE_CHECK             = 1
STATE_VOLTAGE_CHECK_RESPONSE    = 2
STATE_READ_OCR                  = 3
STATE_INIT_CARD_1               = 4
STATE_INIT_CARD_2               = 5
STATE_READY                     = 6
STATE_ERROR                     = -1

class SDCARDEngineError(Exception):
    pass

class SDCARDWorker(QtCore.QThread):
    init_transaction = QtCore.pyqtSignal(object, int, name = "init_transaction")
    init_worker = QtCore.pyqtSignal(object, object, name="sdcard_worker_init")
    sdcard_response = QtCore.pyqtSignal(object, name = "sdcard_response")

    def __init__(self):
        super(SDCARDWorker, self).__init__()
        self.init_worker.connect(self.init_sdcard_worker)
        self.init_transaction.connect(self.process_transaction)

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

    def init_sdcard_worker(self, spi, actions):
        print "SDWorker Engine: Initializing worker"
        self.spi = spi
        self.actions = actions

        self.spi.set_tx_polarity(True)
        self.spi.set_rx_polarity(True)
        self.spi.set_spi_slave_select(SLAVE_SELECT_BIT, False)
        self.spi.auto_ss_control_enable(False)
        self.spi.set_lsb_enable(False)

        #Set Clock Rate to 1MHz
        self.spi.set_spi_clock_rate(400000)
        self.spi.set_slave_select_raw(0x00)
        self.spi.set_character_length(80)
        self.spi.set_write_data(Array('B'))
        self.spi.start_transaction()

        time.sleep(0.10)
        while self.spi.is_busy():
            time.sleep(0.01)

        self.spi.set_spi_slave_select(SLAVE_SELECT_BIT, True)
        self.spi.auto_ss_control_enable(True)

    def process_transaction(self, data, response_byte_length):
        en_crc = True
        if en_crc:
            crc = self.generate_crc(data)
            data.append(crc)

        #response_bit_length = response_byte_length * 8 + 8
        response_bit_length = response_byte_length * 8
        #print "SDWorker Engine: Full Command: ",
        #for d in data:
        #    print "%02X " % d,
        #print ""

        self.spi.enable_manual_slave_select(SLAVE_SELECT_BIT, True)
        read_data = self.spi.transaction(data, 8, SLAVE_SELECT_BIT, False)
        #read_data = self.spi.transaction(data, response_bit_length, SLAVE_SELECT_BIT, False)
        while read_data[0] == 0xFF:
            read_data = self.spi.transaction(Array('B'), 8, SLAVE_SELECT_BIT, False)

        if (response_bit_length - 8) > 0:
            read_data.extend(self.spi.transaction(Array('B'), response_bit_length - 8, SLAVE_SELECT_BIT, False))

        self.spi.enable_manual_slave_select(SLAVE_SELECT_BIT, True)
        #print "SDWorker Engine: Read Data: %s" % str(read_data)
        self.sdcard_response.emit(read_data)

class SDCARDEngine (QtCore.QObject):

    def __init__(self, spi_driver, status, actions):
        super (SDCARDEngine, self).__init__()

        self.status = status
        self.status.Info(self, "Reset SPI-SDCARD Interface")
        self.sdcard_worker = None
        self.spi = spi_driver

        self.actions = actions
        self.status.Verbose(self, "Starting SDCARD Engine")
        self.state = STATE_START
        #Create a worker object and move it to it's own thread
        self.sdcard_worker = SDCARDWorker()

        self.sdcard_worker.sdcard_response.connect(self.state_machine)
        self.worker_thread = QtCore.QThread()
        self.worker_thread.setObjectName("SDCard Worker")
        self.sdcard_worker.moveToThread(self.worker_thread)

        self.sdcard_worker.init_worker.emit(self.spi, self.actions)
        self.state_machine(None)

        #self.sdcard_worker.spi = self.spi
        #self.sdcard_worker.actions = self.actions
        #self.sdcard_worker.process_transaction(CMD0, 1)

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

    def check_r1_response(self, r1):
        if (r1 & 0xFE) > 0:
            return False
        if (r1 & R1_IDLE_STATE) > 0:
            return True
        return False

    def check_r2_response(self, r2):
        r = ((r2[0] << 8) | r2[1])

        if (r & R2_PARAMETER_ERROR):
            print "R2 Parameter Error"
        if (r & R2_ADDRESS_ERROR):
            print "R2 Address Error"
        if (r & R2_ERASE_SEQ_ERROR):
            print "R2 Sequence Error"
        if (r & R2_COMM_CRC_ERROR):
            print "R2 Comm CRC Error"
        if (r & R2_ILLEGAL_CMD):
            print "R2 Illegal Command"
        if (r & R2_ERASE_RESET):
            print "R2 Erase Reset"
        if (r & R2_IN_IDLE_STATE):
            print "R2 Idle"
        if (r & R2_OUT_OF_RANGE):
            print "R2 Out of range error"
        if (r & R2_ERASE_PARAM):
            print "R2 Erase Parameter"
        if (r & R2_WP_VIOLATION):
            print "R2 Write Violation"
        if (r & R2_CARD_ECC_FAILED):
            print "R2 ECC Failed"
        if (r & R2_CC_ERROR):
            print "R2 CC Error"
        if (r & R2_ERRROR):
            print "R2 Error!"
        if (r & R2_WP_ERASE_SKIP):
            print "R2 Write Protect Erase Skipped"
        if (r & R2_CARD_IS_LOCKED):
            print "R2 Card is locked"


    def check_r3_response(self, r3):
        if not self.check_r1_response(r3[0]):
            print "Card standard response failed..."
            self.print_r1_response(r7[0])
            return False
        print "r3 Response (OCR): %s" % str(r3[1:])

    def check_r7_response(self, r7):
        if not self.check_r1_response(r7[0]):
            print "Card standard response failed..."
            self.print_r1_response(r7[0])
            return False

        #Check Voltage Acceptable
        if r7[3] & 0x3 == 0:
            #Voltage Accepted:
            #0000b: Not Defined
            #0001b: 2.7V - 3.6V
            #0010b: Reserved for low voltage
            #0100b: Reserved
            #1000b: Reserved
            #Others (Not Defined)
            return False

        return True

    def state_machine(self, response):
        if self.state == STATE_START:
            print "CMD0: Reset Card"
            self.state = STATE_VOLTAGE_CHECK
            self.sdcard_worker.init_transaction.emit(CMD0, 1)

        elif self.state == STATE_VOLTAGE_CHECK:
            self.print_r1_response(response[0])
            print "CMD8: Voltage Check"
            self.state = STATE_VOLTAGE_CHECK_RESPONSE
            self.sdcard_worker.init_transaction.emit(CMD8, 5)

        elif self.state == STATE_VOLTAGE_CHECK_RESPONSE:
            print "Checking response from command 8"
            if not self.check_r7_response(response):
                print "Found F8 Flags, device is good!"
                self.state = STATE_ERROR
                return

            self.state = STATE_READ_OCR
            print "CMD58: Get OCR"
            self.sdcard_worker.init_transaction.emit(CMD58, 5)

        elif self.state == STATE_READ_OCR:
            print "OCR Response"
            self.check_r3_response(response)
            self.state = STATE_INIT_CARD_1
            self.sdcard_worker.init_transaction.emit(CMD55, 1)

        elif self.state == STATE_INIT_CARD_1:
            self.check_r1_response(response[0])
            self.state = STATE_INIT_CARD_2
            self.sdcard_worker.init_transaction.emit(ACMD41, 1)

        elif self.state == STATE_INIT_CARD_2:
            #print "Initialize card response"
            self.check_r1_response(response[0])
            self.state = STATE_READY

        elif self.state == STATE_READY:
            print "Card Ready!"
            self.check_r1_response(response[0])

        elif self.state == STATE_ERROR:
            print "ERROR STATE!"
        else:
            print "Error in state machine"
            return


    def write(self, data):
        pass

    def read(self, length):
        pass

