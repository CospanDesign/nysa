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
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QPushButton

from memory_tester_widget import MemoryTesterWidget

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

class View(QWidget):

    def __init__(self, status, memory_actions):
        super (View, self).__init__()
        self.memory_actions = memory_actions

    def setup_view(self):
        self.setWindowTitle("Memory Controller")
        self.mem_size_label = QLabel("Memory Size:")
        layout = QVBoxLayout()
        self.mtw = MemoryTesterWidget()
        btn = QPushButton("Run Tests")
        btn.clicked.connect(self.memory_actions.memory_test_start.emit)
        layout.addWidget(self.mem_size_label)
        layout.addWidget(self.mtw)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.show()

    def add_test(self, name, default_enabled, func):
        self.mtw.add_row(name, default_enabled, func)

    def set_test_results(self, pos, result):
        self.mtw.test_results[pos].setText(result)

    def get_num_tests(self):
        return self.mtw.get_num_tests()

    def is_test_enabled(self, pos):
        return self.mtw.is_test_enabled(pos)

    def get_test_function(self, pos):
        return self.mtw.get_test_function(pos)

    def set_memory_size(self, size):
        self.mem_size_label.setText("Memory Size: 0x%08X" % size)
        

