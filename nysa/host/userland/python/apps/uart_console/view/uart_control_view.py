# Copyright (c) 2014 Cospan Design

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


""" UART Control View
"""

import sys
import os

from PyQt4.QtGui import *
from PyQt4 import Qt

class UARTControlView(QWidget):

    def __init__(self, status, actions):
        super(UARTControlView, self).__init__()
        self.status = status
        self.actions = actions

        #run_button = QPushButton("Run")
        #run_button.setToolTip("Start Capturing Images")
        #run_button.clicked.connect(self.actions.sf_camera_run)

        #stop_button = QPushButton("Stop")
        #stop_button.setToolTip("Stop Capturing Images")
        #stop_button.clicked.connect(self.actions.sf_camera_stop)

        #reset_button = QPushButton("Reset")
        #reset_button.setToolTip("Reset Camera")
        #reset_button.clicked.connect(self.actions.sf_camera_reset)

        layout = QFormLayout()

        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["110",
                                      "300",
                                      "600",
                                      "1200",
                                      "2400",
                                      "4800",
                                      "9600",
                                      "14400",
                                      "19200",
                                      "28800",
                                      "38400",
                                      "56000",
                                      "57600",
                                      "115200"])

        self.baudrate_combo.setCurrentIndex(self.baudrate_combo.count() - 1)
        self.baudrate_combo.currentIndexChanged.connect(self.baudrate_changed)

        self.local_echo_cb = QCheckBox()
        self.local_echo_cb.clicked.connect(self.local_echo_changed)

        self.flowcontrol_combo = QComboBox()
        self.flowcontrol_combo.addItems(["None",
                                         "Hardware"])
        self.flowcontrol_combo.setCurrentIndex(0)
        self.flowcontrol_combo.currentIndexChanged.connect(self.flowcontrol_changed)

        self.read_button = QPushButton("Read UART")
        self.read_button.clicked.connect(self.actions.uart_read_data)

        layout.addRow("Set Baudrate", self.baudrate_combo)
        layout.addRow("Flow Control", self.flowcontrol_combo)
        layout.addRow("Local Echo", self.local_echo_cb)
        layout.addRow("Read the UART Data", self.read_button)

        self.setLayout(layout)
        self.setMaximumWidth(500)

    def baudrate_changed(self):
        br = self.get_baudrate()
        self.status.Verbose(self, "Set Baudrate to: %d" % br)
        self.actions.uart_baudrate_change.emit(br)

    def local_echo_changed(self):
        self.actions.uart_local_echo_en.emit(self.local_echo_cb.isChecked())

    def flowcontrol_changed(self):
        self.actions.uart_flowcontrol_change.emit(self.get_flowcontrol())

    def get_baudrate(self):
        br = self.baudrate_combo.currentText()
        br = int(str(br), 10)
        return br

    def get_flowcontrol(self):
        return self.flowcontrol_combo.currentText()
