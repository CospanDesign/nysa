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

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "common")

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QAction
from PyQt4 import QtGui
from PyQt4 import QtCore

from i2c_control_view import I2CControlView
from i2c_table import I2CTable

from save_loader import SaveLoader


class I2CWidget(QWidget):

    def __init__(self, status, actions):
        super (I2CWidget, self).__init__()
        self.status =  status
        self.actions = actions

        self.row_add_action = QAction("Add Row", self)
        self.row_add_action.triggered.connect(self.add_row)

        self.row_delete_action = QAction("Delete Row", self)
        self.row_delete_action.triggered.connect(self.remove_row)

        self.setWindowTitle("Standalone I2C Widget")
        layout = QHBoxLayout()
        self.toolbar = QToolBar()

        self.save_loader = SaveLoader(extensions = ["i2c"],
                                      initial_file = "i2c_confic_file")

        self.toolbar.setOrientation(QtCore.Qt.Vertical)
        self.toolbar.addAction(self.row_add_action)
        self.toolbar.addAction(self.row_delete_action)
        self.tab_view = QTabWidget()

        self.init_table = I2CTable(self.status, self.actions, loop = False)
        self.loop_table = I2CTable(self.status, self.actions, loop = True)
        self.tab_view.addTab(self.init_table, "Start")
        self.tab_view.addTab(self.loop_table, "Loop")

        self.control_view = I2CControlView(self.status, self.actions)
        self.actions.i2c_update_view.connect(self.update_i2c_transactions)

        layout.addWidget(self.toolbar)

        io_layout = QVBoxLayout()
        io_layout.addWidget(self.save_loader)
        io_layout.addWidget(self.tab_view)

        layout.addLayout(io_layout)

        #layout.addWidget(self.tab_view)
        layout.addWidget(self.control_view)

        self.setLayout(layout)
        self.show()


    def add_row(self):
        if self.tab_view.currentWidget() is self.loop_table:
            self.actions.i2c_row_add.emit(True)
        else:
            self.actions.i2c_row_add.emit(False)

    def remove_row(self):
        if self.tab_view.currentWidget() is self.loop_table:
            self.actions.i2c_row_delete.emit(True)
        else:
            self.actions.i2c_row_delete.emit(False)


    def update_i2c_transactions(self, loop, transactions):
        if not loop:
            self.update_i2c_init_transactions(transactions)
        else:
            self.update_i2c_loop_transactions(transactions)

    def update_i2c_init_transactions(self, transactions):
        self.init_table.update_i2c_transactions(transactions)

    def update_i2c_loop_transactions(self, transactions):
        self.loop_table.update_i2c_transactions(transactions)

    def set_save_callback(self, callback):
        self.save_loader.set_save_callback(callback)

    def set_load_callback(self, callback):
        self.save_loader.set_load_callback(callback)

    def get_filename(self):
        return self.save_loader.get_filename()

