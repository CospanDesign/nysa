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


""" GPIO Widget
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
from functools import partial

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QPushButton

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))




from control_view import ControlView
direction_ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")


INDEX_POS          = 0
DIR_POS            = 1
IN_VAL_POS         = 2
OUT_VAL_POS        = 3
INT_EN_POS         = 4
INT_EDGE_POS       = 5
STATUS_POS         = 6


REG_INPUT          = 0
REG_OUTPUT         = 1
REG_DIRECTION      = 2
REG_INTERRUPT_EN   = 3
REG_INTERRUPT_EDGE = 4


class GPIOWidget(QWidget):

    def __init__(self, count = 32, gpio_actions = None):
        super (GPIOWidget, self).__init__()
        self.gpio_actions = gpio_actions
        layout = QGridLayout()
        #status_layout = QVBoxLayout

        self.direction_buttons = []
        self.input_values = []
        self.output_values = []
        self.interrupt_enables = []
        self.interrupt_edges = []

        style = open(direction_ss, "r").read()

        layout.addWidget(QLabel("Index"          ), 0, INDEX_POS    , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Direction"      ), 0, DIR_POS      , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Input"          ), 0, IN_VAL_POS   , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Output"         ), 0, OUT_VAL_POS  , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Interrupt En"   ), 0, INT_EN_POS   , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Interrupt Edge" ), 0, INT_EDGE_POS , QtCore.Qt.AlignCenter)
        layout.addWidget(QLabel("Status/Comm"    ), 0, STATUS_POS   , QtCore.Qt.AlignCenter)

        for i in range (0, count):
            #Index
            ilabel = QLabel("%d" % i)
            #ilabel.setObjectName("index_label")
            ilabel.setStyleSheet(style)

            #Direction
            dir_btn = QPushButton("IN")
            dir_btn.setObjectName("direction_button")
            self.direction_buttons.append(dir_btn)
            dir_btn.setStyleSheet(style)
            dir_btn.setCheckable(True)

            #input Values
            input_btn = QPushButton("0")
            input_btn.setObjectName("input_button")
            self.input_values.append(input_btn)
            input_btn.setStyleSheet(style)
            input_btn.setCheckable(True)
            input_btn.setEnabled(False)

            #Output Values
            output_btn = QPushButton("HiZ")
            output_btn.setObjectName("output_button")
            self.output_values.append(output_btn)
            output_btn.setStyleSheet(style)
            output_btn.setCheckable(True)
            output_btn.setEnabled(False)

            #Interrupt En
            int_en_btn = QPushButton("Dis")
            int_en_btn.setObjectName("interrupt_enable_button")
            self.interrupt_enables.append(int_en_btn)
            int_en_btn.setStyleSheet(style)
            int_en_btn.setCheckable(True)

            #Interrupt Edge
            int_edge_btn = QPushButton("\\")
            int_edge_btn.setObjectName("interrupt_edge_button")
            self.interrupt_edges.append(int_edge_btn)
            int_edge_btn.setStyleSheet(style)
            int_edge_btn.setCheckable(True)

            #Connect callbacks
            dir_btn.clicked.connect(partial(self.direction_clicked, i))
            output_btn.clicked.connect(partial(self.out_clicked, i))
            int_en_btn.clicked.connect(partial(self.int_en_clicked, i))
            int_edge_btn.clicked.connect(partial(self.int_edge_clicked, i))

            #Add to layout
            #Index
            layout.addWidget(ilabel       , i + 1 , INDEX_POS    , QtCore.Qt.AlignCenter)
            layout.addWidget(dir_btn      , i + 1 , DIR_POS      , QtCore.Qt.AlignCenter)
            layout.addWidget(input_btn    , i + 1 , IN_VAL_POS   , QtCore.Qt.AlignCenter)
            layout.addWidget(output_btn   , i + 1 , OUT_VAL_POS  , QtCore.Qt.AlignCenter)
            layout.addWidget(int_en_btn   , i + 1 , INT_EN_POS   , QtCore.Qt.AlignCenter)
            layout.addWidget(int_edge_btn , i + 1 , INT_EDGE_POS , QtCore.Qt.AlignCenter)

            layout.setRowStretch(i + 1, 8)
            layout.setRowMinimumHeight(i + 1, 8)

        self.cv = ControlView(self.gpio_actions)

        layout.addWidget(self.cv, 0, STATUS_POS, count, 1)
        self.setLayout(layout)

        self.show()

    def direction_clicked(self, index):
        self.direction_changed(index)
        btn = self.direction_buttons[index]
        self.gpio_actions.direction_changed.emit(index, btn.isChecked())

    def direction_changed(self, index):
        btn = self.direction_buttons[index]
        if btn.isChecked():
            btn.setText("OUT")
            if self.output_values[index].isChecked():
                self.output_values[index].setText("1")
            else:
                self.output_values[index].setText("0")
            self.output_values[index].setEnabled(True)
        else:
            btn.setText("IN")
            self.output_values[index].setEnabled(False)
            self.output_values[index].setText("HiZ")

    def out_clicked(self, index):
        self.out_changed(index)
        btn = self.output_values[index]
        self.gpio_actions.gpio_out_changed.emit(index, btn.isChecked())

    def out_changed(self, index):
        btn = self.output_values[index]
        if btn.isChecked():
            btn.setText("1")
        else:
            btn.setText("0")

    def int_en_clicked(self, index):
        self.int_en_changed(index)
        btn = self.interrupt_enables[index]
        self.gpio_actions.interrupt_en_changed.emit(index, btn.isChecked())

    def int_en_changed(self, index):
        btn = self.interrupt_enables[index]
        if btn.isChecked():
            btn.setText("En")
        else:
            btn.setText("Dis")

    def int_edge_clicked(self, index):
        self.int_edge_changed(index)
        btn = self.interrupt_edges[index]
        self.gpio_actions.interrupt_edge_changed.emit(index, btn.isChecked())

    def int_edge_changed(self, index):
        btn = self.interrupt_edges[index]
        if btn.isChecked():
            btn.setText("/")
        else:
            btn.setText("\\")


    def add_register(self, index, name, initial_value = 0):
        self.cv.add_register(index, name, initial_value)

    def update_all_direction(self, value):
        for i in range(len(self.direction_buttons)):
            reg = self.direction_buttons[i]
            if ((value & (1 << i)) != 0):
                reg.setChecked(True)
            else:
                reg.setChecked(False)
            self.direction_changed(i)

    def update_all_interrupt_en(self, value):
        for i in range(len(self.interrupt_enables)):
            reg = self.interrupt_enables[i]
            if ((value & (1 << i)) != 0):
                reg.setChecked(True)
            else:
                reg.setChecked(False)
            self.int_en_changed(i)

    def update_all_interrupt_edge(self, value):
        for i in range(len(self.interrupt_edges)):
            reg = self.interrupt_edges[i]
            if ((value & (1 << i)) != 0):
                reg.setChecked(True)
            else:
                reg.setChecked(False)
            self.int_edge_changed(i)

    def set_input_values(self, value):
        for i in range(len(self.input_values)):
            reg = self.input_values[i]
            if ((value & (1 << i)) != 0):
                reg.setChecked(True)
                reg.setText("1")
            else:
                reg.setChecked(False)
                reg.setText("0")

    def set_register(self, index, value):
        if index == 0:
            self.set_input_values(value)
        elif index == 1:
            self.update_all_direction(value)
        elif index == 3:
            self.update_all_interrupt_en(value)
        elif index == 4:
            self.update_all_interrupt_edge(value)

        self.cv.set_register(index, value)

