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
from PyQt4.QtGui import QHBoxLayout

from uart_control_view import UARTControlView
from uart_console import UARTConsole

class UARTWidget(QWidget):

    def __init__(self, status, actions):
        super (UARTWidget, self).__init__()
        self.status = status
        self.actions = actions
        self.setWindowTitle("Standalone UART Widget")
        layout = QHBoxLayout()

        self.te = UARTConsole(status, actions)
        self.te.setText("Text!")
        self.ucv = UARTControlView(status, actions)
        layout.addWidget(self.te)
        layout.addWidget(self.ucv)
        self.setLayout(layout)
        self.show()

    def append_text(self, text):
        self.te.append(text)

    def clear_text(self):
        self.te.setText("")

