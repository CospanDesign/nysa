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
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QIntValidator

class StepperConfigurationView(QWidget):

    def __init__(self, status, actions):
        super (StepperConfigurationView, self).__init__()
        self.status = status
        self.actions = actions

        #Setup values of the widget
        self.setMinimumWidth(100)
        self.setMaximumWidth(400)

        name = QLabel("Configuration")
        name.setStyleSheet(
            "QLabel{                "\
            "   font : bold 16px;   "\
            "   padding: 2px;       "\
            "   min-width : 3em;    "\
            "}                      "
        )
        name.setAlignment(Qt.AlignCenter | Qt.AlignTop) 


        self.manufacturer = QLineEdit("")
        self.model = QLineEdit("")
        self.num_steps = QLineEdit("")
        self.walk_period = QLineEdit("")
        self.run_period = QLineEdit("")
        self.accelleration = QLineEdit("")
        self.stepper_type = QLineEdit("")

        layout = QVBoxLayout()
        layout.addWidget(name)
        config_form_layout = QFormLayout()

        config_form_layout.addRow(QString("Motor Manufacturer"), self.manufacturer)
        config_form_layout.addRow(QString("Motor Model"), self.model)
        config_form_layout.addRow(QString("Number of Steps"), self.num_steps)
        config_form_layout.addRow(QString("Walk Period"), self.walk_period)
        config_form_layout.addRow(QString("Run Period"), self.run_period)
        config_form_layout.addRow(QString("Accelleration"), self.accelleration)
        config_form_layout.addRow(QString("Stepper Type"), self.stepper_type)
        layout.addLayout(config_form_layout)

        self.setLayout(layout)
        config_dict = {}
        config_dict["manufacturer"]     = "Manufacturer"
        config_dict["model"]            = "Motor 1"
        config_dict["accelleration"]    = "0.01"
        config_dict["num_steps"]        = '200'
        config_dict["walk_period"]      = '0.1'
        config_dict["run_period"]       = '0.01'
        config_dict["stepper_type"]     = "bipolar"
        self.load_configuration(config_dict)

    def load_configuration(self, config_dict):
        if "manufacturer" in config_dict:
            self.manufacturer.setText(config_dict["manufacturer"])
        if "model" in config_dict:
            self.model.setText(config_dict["model"])
        if "num_steps" in config_dict:
            self.num_steps.setText(str(config_dict["num_steps"]))
        if "walk_period" in config_dict:
            self.walk_period.setText(str(config_dict["walk_period"]))
        if "run_period" in config_dict:
            self.run_period.setText(str(config_dict["run_period"]))
        if "accelleration" in config_dict:
            self.accelleration.setText(str(config_dict["accelleration"]))
        if "stepper_type" in config_dict:
            self.stepper_type.setText(str(config_dict["stepper_type"]))

        self.actions.stepper_update_configuration.emit(config_dict)

    def get_configuration(self):
        d = {}
        d["manufacturer"] = str(self.manufacturer.text())
        d["model"] = str(self.model.text())
        d["num_steps"] = int(str(self.num_steps.text()))
        d["walk_period"] = float(str(self.walk_period.text()))
        d["run_period"] = float(str(self.run_period.text()))
        d["accelleration"] = float((self.accelleration.text()))
        d["stepper_type"] = str(self.stepper_type.text())
        return d


