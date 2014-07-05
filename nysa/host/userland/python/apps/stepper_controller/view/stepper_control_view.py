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


""" stepper configuration view
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QString

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QIntValidator

from stepper_motor_widget import StepperMotorWidget

class StepperControlView(QWidget):

    def __init__(self, status, actions):
        super (StepperControlView, self).__init__()
        self.status = status
        self.actions = actions
        self.smv = StepperMotorWidget(self.status, self.actions)

        #Setup values of the widget
        self.setMinimumWidth(400)

        name = QLabel("Control")
        name.setStyleSheet(
            "QLabel{                "\
            "   font : bold 16px;   "\
            "   padding: 2px;       "\
            "   min-width : 3em;    "\
            "}                      "
        )
        name.setAlignment(Qt.AlignCenter)

        self.clock_rate = QLabel("Unknown")

        self.step_type = QComboBox()
        self.step_type.addItem(QString("Full Step"))
        self.step_type.addItem(QString("Half Step"))
        self.step_type.addItem(QString("Micro Step"))
        self.step_type.setCurrentIndex(2)
        self.step_type.currentIndexChanged.connect(self.step_type_changed)

        self.rate = QLineEdit("0.1")
        self.rate.setAlignment(Qt.AlignRight)

        self.direction = QComboBox()
        self.direction.addItem(QString("Forward"))
        self.direction.addItem(QString("Reverse"))

        self.num_rotations = QLabel("0")
        self.num_rotations.setAlignment(Qt.AlignCenter)
        self.extra_rotation = QLabel("0")
        self.extra_rotation.setAlignment(Qt.AlignCenter)

        self.total_rotation = QLabel("0")
        self.total_rotation.setAlignment(Qt.AlignCenter)

        self.full_step_widget = StepWidget("Full Step")
        self.half_step_widget = StepWidget("Half Step")
        self.micro_step_widget = StepWidget("Micro Step")

        layout = QVBoxLayout()
        layout.addWidget(name)

        form_layout = QFormLayout()
        form_layout.addRow(QString("FPGA Clock Rate"), self.clock_rate)
        form_layout.addRow(QString("Step Type"), self.step_type)
        #form_layout.addRow(QString("Direction"), self.direction)
        form_layout.addRow(QString("Stepper Rate (Steps Per Second)"), self.rate)
        form_layout.addRow(QString("Number Full Rotations"), self.num_rotations)
        form_layout.addRow(QString("Rotation"), self.extra_rotation)
        form_layout.addRow(QString("Total Rotation"), self.total_rotation)
        form_layout.addRow(QString("Single Step"), self.full_step_widget)
        form_layout.addRow(QString("Single Step"), self.half_step_widget)
        form_layout.addRow(QString("Single Step"), self.micro_step_widget)

        layout.addLayout(form_layout)
        layout.addWidget(self.smv)
        self.setLayout(layout)

        self.actions.stepper_update_clock_rate.connect(self.update_clock_rate)
        self.actions.stepper_update_angle.connect(self.update_angle)
        self.actions.stepper_initial_angle.connect(self._update_angle)

    def update_clock_rate(self, clock_rate):
        mhz = clock_rate / 1000000
        self.clock_rate.setText("%f" % mhz)

    def update_angle(self, angle):
        self._update_angle(angle)
        self.actions.stepper_move_event.emit(angle)

    def _update_angle(self, angle):
        print "Rotate by: %f" % angle
        direction = 1
        if angle < 0:
            direction = -1
        num_turns = ((int(abs(angle)) / 360) * direction)
        extra = direction * (abs(angle) - abs((num_turns * 360)))
        #print "\t\t# of Rotations:        %d" % num_turns
        #print "\t\t# left over rotations: %f" % extra

        if direction == 1:
            self.direction.setCurrentIndex(0)
        else:
            self.direction.setCurrentIndex(1)

        self.num_rotations.setText(QString("%d" % num_turns))
        self.extra_rotation.setText(QString("%f" % extra))
        self.total_rotation.setText(QString("%f" % angle))


    def step_type_changed(self, index):
        self.actions.stepper_update_step_type.emit(index)

class StepWidget(QWidget):
    def __init__(self, name):
        super (StepWidget, self).__init__()
        layout = QHBoxLayout()
        self.setMinimumWidth(200)
        self.reverse_step = QPushButton("<")
        self.forward_step = QPushButton(">")
        label = QLabel(QString(name))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.reverse_step)
        layout.addWidget(label)
        layout.addWidget(self.forward_step)
        self.setLayout(layout)
        self.show()

