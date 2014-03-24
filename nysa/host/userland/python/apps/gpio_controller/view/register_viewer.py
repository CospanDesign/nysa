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


""" Register Viewer

Used to get and set registers of a generic core
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel

from PyQt4.QtCore import SIGNAL


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))


from gpio_actions import GPIOActions

class RegisterViewer(QWidget):

    def __init__(self, count = 8):
        super(RegisterViewer, self).__init__()
        self.actions = GPIOActions()
        layout = QGridLayout()
        self.registers = []
        self.get_buttons = []
        self.set_buttons = []

        for i in range(count):
            value = i
            l = self._create_register_controller()
            layout.addWidget(QLabel(hex(i)), i, 0)
            layout.addWidget(l[0], i, 1)
            layout.addWidget(l[1], i, 2)
            layout.addWidget(l[2], i, 3)

            self.registers.append(l[1])
            self.get_buttons.append(l[0])
            self.set_buttons.append(l[2])
            l[0].connect(l[0], SIGNAL("clicked()"), lambda: self.get_pressed(i))
            #self.get_buttons[i].clicked.connect(self.get_pressed)
            #self.set_buttons[i].clicked.connect(self.set_pressed)

        self.setLayout(layout)

    def _create_register_controller(self):
        l = [QPushButton("Get >>"), QLineEdit(), QPushButton("Set >>")]
        return l

    def get_pressed(self, i):
        print "Get Button %d pressed" % i

    def set_pressed(self, event):
        print "Set Button %s pressed" % event

