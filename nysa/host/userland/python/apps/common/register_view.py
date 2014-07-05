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
from functools import partial

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
#from PyQt4.QtGui import QIntValidator

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

STYLE = "                               "\
        "QPushButton{                   "\
        "   color            : black;   "\
        "   background-color : white;   "\
        "   border-style     : outset;  "\
        "   border-width     : 2px;     "\
        "   border-radius    : 8px;     "\
        "   border-color     : black;   "\
        "   font             : bold 8px;"\
        "   min-width        : 3em;     "\
        "   padding          : 2px;     "\
        " }                             "\
        " QPushButton:pressed {         "\
        "   color            : white;   "\
        "   background-color : gray;    "\
        "   border-color     : black;   "\
        "   border-style     : inset;   "\
        " }                             "\
        " QPushButton:checked {         "\
        "   color            : white;   "\
        "   background-color : black;   "\
        "   border-color     : black;   "\
        "   border-style     : inset;   "\
        " }                             "\


BAD_VAL = "QLineEdit {                  "\
          " background-color : red      "\
          "}                            "
GOOD_VAL ="QLineEdit {                  "\
          " background-color : white    "\
          "}                            "

class RegisterView(QWidget):

    get_pressed_signal = pyqtSignal(int, name = "register_get_pressed")
    set_pressed_signal = pyqtSignal(int, int, name = "register_set_pressed")

    def __init__(self):
        super(RegisterView, self).__init__()
        layout = QGridLayout()
        self.registers = []
        self.get_buttons = []
        self.set_buttons = []
        layout.addWidget(QLabel("Name")        , 0 , 0, 1, 1, Qt.AlignCenter)
        layout.addWidget(QLabel("Get")         , 0 , 1, 1, 1, Qt.AlignCenter)
        layout.addWidget(QLabel("Value (HEX)") , 0 , 2, 1, 1, Qt.AlignCenter)
        layout.addWidget(QLabel("Set")         , 0 , 3, 1, 1, Qt.AlignCenter)
        self.pos = 0

        self.setLayout(layout)
        self.show()

    def add_register(self, index, name, initial_value = 0):
        r = self._create_register_controller()
        self.get_buttons.append(r[0])
        self.registers.append(r[1])
        self.set_buttons.append(r[2])
        #val = QIntValidator()
        #val.setBottom(0x00000000)
        #val.setTop(0xFFFFFFFF)
        #r[1].setValidator(val)
        r[1].setText("0x%08X" % initial_value)
        r[1].textChanged.connect(partial(self.custom_validator, index))

        try:
            int(str(self.registers[index].text()), 16)
        except ValueError:
            self.registers[index].setStyleSheet(BAD_VAL)
            return
        self.registers[index].setStyleSheet(GOOD_VAL)

        self.layout().addWidget(QLabel(name) , index + 1, 0)
        self.layout().addWidget(r[0]         , index + 1, 1)
        self.layout().addWidget(r[1]         , index + 1, 2)
        self.layout().addWidget(r[2]         , index + 1, 3)

        r[0].clicked.connect(partial(self.get_pressed, index))
        r[2].clicked.connect(partial(self.set_pressed, index))

    def set_register(self, index, value):
        self.registers[index].setText("0x%08X" % value)

    def _create_register_controller(self):
        l = [QPushButton("Get >>"), QLineEdit(), QPushButton("Set >>")]
        l[1].setText("00000000")
        l[1].setAlignment(Qt.AlignRight)

        l[0].setStyleSheet(STYLE)
        l[2].setStyleSheet(STYLE)
        return l

    def get_pressed(self, index):
        print "Get Button %d pressed" % index
        self.get_pressed_signal.emit(index)

    def set_pressed(self, index):
        print "Set Button %s pressed" % index
        try:
            val = int(str(self.registers[index].text()), 16)
        except ValueError:
            pass
        print "Setting: 0x%08X" % val
        self.set_pressed_signal.emit(index, val)

    def custom_validator(self, index):
        try:
            val = int(str(self.registers[index].text()), 16)
            if val < 0:
                self.registers[index].setStyleSheet(BAD_VAL)
                return
            elif val > 0xFFFFFFFF:
                self.registers[index].setStyleSheet(BAD_VAL)
                return

        except ValueError:
            self.registers[index].setStyleSheet(BAD_VAL)
            return
        self.registers[index].setStyleSheet(GOOD_VAL)
