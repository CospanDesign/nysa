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

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QIntValidator
from PyQt4.QtCore import Qt


sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                os.pardir))

from apps.common.register_view import RegisterView

sys.path.append(os.path.join(os.path.dirname(__file__),
                os.pardir))


from gpio_actions import GPIOActions


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
        " QPushButton:checked {         "\
        "   color            : white;   "\
        "   background-color : black;   "\
        "   border-color     : black;   "\
        "   border-style     : inset;   "\
        " }                             "\


INFO = open(os.path.join(os.path.dirname(__file__), os.pardir, "doc", "gpio.txt"), "r").read()
class ControlView(QWidget):

    def __init__(self, gpio_actions = None):
        super (ControlView, self).__init__()
        self.gpio_actions = gpio_actions
        layout = QGridLayout()

        #Info
        info = QLabel(INFO)
        info.setMaximumWidth(500)
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignTop)

        #Interrupt/Polling
        int_poll = QLabel("Interrupt/Polling")

        #Interrupt/Pollinb Button
        self.int_poll_btn = QPushButton("Polling Mode")
        self.int_poll_btn.setStyleSheet(STYLE)
        self.int_poll_btn.setCheckable(True)
        self.int_poll_btn.clicked.connect(self.int_poll_clicked)

        #Interrupt/Polling Timeout
        int_poll_timeout_label = QLabel("Timeout (ms)")

        #Interrupt/Polling Timeout LineEdit
        val = QIntValidator()
        val.setBottom(20)
        val.setTop(1000)

        self.int_poll_te  = QLineEdit("100")
        self.int_poll_te.setAlignment(Qt.AlignRight)
        self.int_poll_te.setValidator(val)
        self.int_poll_te.textChanged.connect(self.poll_te_changed)

        #Enable Reading
        self.en_reading_btn = QPushButton("Start Reading")
        self.en_reading_btn.setStyleSheet(STYLE)
        self.en_reading_btn.setCheckable(True)
        self.en_reading_btn.clicked.connect(self.en_reading_clicked)

        #Whitespace Killer!
        space = QLabel("Control/Status")

        #Register View
        self.rv = RegisterView()
        self.rv.set_pressed_signal.connect(self.register_set_pressed)
        self.rv.get_pressed_signal.connect(self.register_get_pressed)
        #self.add_register(0, "test")
        #self.set_register(0, 100)
        #self.add_register(1, "testificate")

        #Add Widgets to layout
        layout.addWidget(info,                   0, 0, 1, 3)
        layout.addWidget(int_poll,               1, 0, 1, 1)
        layout.addWidget(self.int_poll_btn,      1, 1, 1, 2)

        layout.addWidget(int_poll_timeout_label, 2, 0, 1, 1)
        layout.addWidget(self.int_poll_te,       2, 1, 1, 2)

        layout.addWidget(self.en_reading_btn,    3, 0, 1, 3)
        layout.addWidget(space,                  4, 0, 1, 3)
        layout.addWidget(self.rv,                5, 0, 1, 3)

        #Set the layout
        self.setLayout(layout)
        self.show()

    def int_poll_clicked(self):
        if self.int_poll_btn.isChecked():
            self.int_poll_btn.setText("Interrupt Mode")
        else:
            self.int_poll_btn.setText("Polling Mode")

    def en_reading_clicked(self):
        #if self.en_reading_btn.isChecked():
        #    self.en_reading_btn.setText("Stop Reading")
        #else:
        #    self.en_reading_btn.setText("Start Reading")
        text = self.int_poll_te.text()
        timeout = 20
        try:
            timeout = int(str(self.int_poll_te.text()), 10)
        except ValueError:
            pass

        if timeout < 20:
            timeout = 20
        timeout_float = 0.001
        timeout_float = timeout_float * timeout

        self.gpio_actions.read_start_stop.emit(self.en_reading_btn.isChecked(), timeout_float)

    def poll_te_changed(self):
        text = self.int_poll_te.text()
        timeout = 100
        try:
            timeout = int(str(self.int_poll_te.text()), 10)
        except ValueError:
            pass

        if timeout < 100:
            timeout = 100
        timeout_float = 0.001
        timeout_float = timeout_float * timeout

        print "te changed to: %f (seconds)" % timeout_float
        self.gpio_actions.read_rate_change(timeout_float)


    def add_register(self, index, name, initial_value = 0):
        self.rv.add_register(index, name, initial_value)

    def set_register(self, index, value):
        self.rv.set_register(index, value)

    def register_set_pressed(self, index, value):
        self.gpio_actions.set_pressed.emit(index, value)

    def register_get_pressed(self, index):
        self.gpio_actions.get_pressed.emit(index)


