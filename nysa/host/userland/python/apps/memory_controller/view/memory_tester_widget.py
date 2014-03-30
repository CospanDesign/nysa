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
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel

RESULT_ENUM = [
        "Not Tested",
        "Running",
        "Failed",
        "Passed"
]


class MemoryTesterWidget(QWidget):

    def __init__(self):
        super (MemoryTesterWidget, self).__init__()
        self.lyt = QGridLayout()
        self.test_enabled = []
        self.test_funcs = []
        self.test_results = []
        self.pos = 1

        self.single_rw_cb = QCheckBox()
        self.single_rw_cb.setChecked(True)

        self.single_rw_end_cb = QCheckBox()
        self.single_rw_end_cb.setChecked(True)

        self.small_burst_rw_start_cb = QCheckBox()
        self.small_burst_rw_start_cb.setChecked(True)

        self.long_burst_rw_cb = QCheckBox()
        self.long_burst_rw_cb.setChecked(True)

        self.setLayout(self.lyt)


    def add_row(self, name, default_enable, func):
        cb = QCheckBox()
        cb.setChecked(default_enable)
        
        self.test_funcs.append(func)
        self.test_results.append(QLabel(RESULT_ENUM[0]))
        self.test_enabled.append(cb)
        self.lyt.addWidget(cb, self.pos, 0)
        self.lyt.addWidget(QLabel(name), self.pos, 1)
        self.lyt.addWidget(self.test_results[self.pos - 1], self.pos, 2)
        self.pos += 1
       

    def set_test_results(self, pos, result):
        self.test_results[pos].setText(result)

    def get_num_tests(self):
        return len(self.test_funcs)

    def is_test_enabled(self, pos):
        return self.test_enabled[pos].isChecked()

    def get_test_function(self, pos):
        return self.test_funcs[pos]

