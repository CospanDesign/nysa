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


""" nysa interface
"""

__author__ = 'email@example.com (name)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIntValidator

from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QAction
from PyQt4 import QtCore
from PyQt4 import Qt

BAD_VAL = "QLineEdit {                  "\
          " background-color : red      "\
          "}                            "
GOOD_VAL ="QLineEdit {                  "\
          " background-color : white    "\
          "}                            "


class I2CControlView(QWidget):

    def __init__(self, status, actions):
        super (I2CControlView, self).__init__()
        self.status = status
        self.actions = actions

        run_button = QPushButton("Run")
        run_button.setToolTip("Execute the I2C Transaction")
        run_button.clicked.connect(self.actions.i2c_run)

        reload_button = QPushButton("Reload")
        reload_button.setToolTip("Reload I2C Transactions")
        reload_button.clicked.connect(self.actions.i2c_run)

        pause_button = QPushButton("Pause")
        pause_button.setToolTip("Pause I2C Execution flow")
        pause_button.clicked.connect(self.actions.i2c_pause)

        stop_button = QPushButton("Stop")
        stop_button.setToolTip("Stop I2C Execution")
        stop_button.clicked.connect(self.actions.i2c_stop)

        reset_button = QPushButton("Reset")
        reset_button.setToolTip("Reset the current execution")
        reset_button.clicked.connect(self.actions.i2c_run)

        step_button = QPushButton("Step")
        step_button.setToolTip("Execute one I2C Transaction")
        step_button.clicked.connect(self.actions.i2c_step)
       
        loop_step_button = QPushButton("Loop Step")
        loop_step_button.setToolTip("Iterate through the I2C Loop one time")
        loop_step_button.clicked.connect(self.actions.i2c_loop_step)

        update_delay_button = QPushButton("Update Delay (ms)")
        update_delay_button.setToolTip("Update the delay in ms between I2C Transactions")
        update_delay_button.clicked.connect(self.update_delay)

        self.delay_le = QLineEdit("100")
        self.delay_le.setAlignment(QtCore.Qt.AlignRight)
        v = QIntValidator()
        v.setBottom(1)


        self.execute_status = QLabel("Idle")

        self.default_slave_addr = QLineEdit()
        self.default_slave_addr.setAlignment(QtCore.Qt.AlignRight)
        self.default_slave_addr.setText("0x10")
        self.default_slave_addr.textChanged.connect(self.custom_validator)
        self.default_slave_addr.returnPressed.connect(self.update_all_slave_addresses)
        self.update_all_slave_addr = QPushButton("Update All Slave Addr")
        self.update_all_slave_addr.clicked.connect(self.update_all_slave_addresses)
        '''
        self.name_line_edit = QLineEdit("test")
        load_config = QPushButton("Load")
        save_config = QPushButton("Save")


        layout = QFormLayout()

        layout.addRow("Name:", self.name_line_edit)
        layout.addRow(save_config)
        layout.addRow(load_config)
        layout.addRow(QWidget())

        #Add Default I2C Address
        layout.addRow(QLabel("Default Slave Addr:"), self.default_slave_addr)
        layout.addRow(self.update_all_slave_addr)


        layout.addRow(run_button)
        layout.addRow(pause_button)
        layout.addRow(stop_button)
        layout.addRow(reset_button)
        layout.addRow(QLabel("Status:"), self.execute_status)

        '''


        layout = QGridLayout()

        #file_layout.addWidget(QLabel("Name:"), 0, 0, 1, 1)
        #file_layout.addWidget(self.name_line_edit, 0, 1, 1, 1)
        #file_layout.addWidget(save_config, 1, 0, 1, 2)
        #file_layout.addWidget(load_config, 2, 0, 1, 2)

        #layout.addLayout(file_layout, 0, 0, 1, 2)

        #Add Default I2C Address
        default_addr_layout = QGridLayout()

        default_addr_layout.addWidget(QLabel("Default Slave Addr"), 0, 0, 1, 1)
        default_addr_layout.addWidget(self.default_slave_addr, 0, 1, 1, 1)
        default_addr_layout.addWidget(self.update_all_slave_addr, 1, 0, 1, 2)

        #Add Buttons/Status Layout
        layout.addLayout(default_addr_layout,         2, 0, 1, 2)
                                                      

        buttons_layout = QGridLayout()
        buttons_layout.addWidget(run_button,          0, 0, 1, 2)
        buttons_layout.addWidget(reload_button,       1, 0, 1, 2)
        buttons_layout.addWidget(step_button,         2, 0, 1, 2)
        buttons_layout.addWidget(loop_step_button,    3, 0, 1, 2)
        buttons_layout.addWidget(pause_button,        4, 0, 1, 2)
        buttons_layout.addWidget(stop_button,         5, 0, 1, 2)
        buttons_layout.addWidget(reset_button,        6, 0, 1, 2)
        buttons_layout.addWidget(update_delay_button, 7, 0, 1, 1)
        buttons_layout.addWidget(self.delay_le,       7, 1, 1, 1)
        buttons_layout.addWidget(QLabel("Status:"),   8, 0, 1, 1)
        buttons_layout.addWidget(self.execute_status, 8, 1, 1, 1)

        layout.addLayout(buttons_layout,              3, 0, 1, 2)





        self.setLayout(layout)
        self.show()

    def update_delay(self):
        value = int(str(self.delay_le.text()), 10)
        self.actions.i2c_execute_delay_change.emit(value)

    def update_all_slave_addresses(self):
        val = 0
        try:
            val = int(str(self.default_slave_addr.text()), 16)
        except ValueError:
            self.status.Error(self, "I2C Address Formatted incorrectly, must be a number")
            return

        if not self.is_address_good(val):
            self.status.Error(self, "Unable to update I2C address with invalid value")
            return

        self.status.Important(self, "Update all base address with: 0x%02X" % val)
        self.actions.i2c_default_i2c_address.emit(val)

    def is_address_good(self, value):
        if value < 0:
            return False
        if value > 127:
            return False
        return True

    def custom_validator(self):
        try:
            val = int(str(self.default_slave_addr.text()), 16)
            if not self.is_address_good(val):
                self.default_slave_addr.setStyleSheet(BAD_VAL)
                return

        except ValueError:
            self.default_slave_addr.setStyleSheet(BAD_VAL)
            return
        self.default_slave_addr.setStyleSheet(GOOD_VAL)

