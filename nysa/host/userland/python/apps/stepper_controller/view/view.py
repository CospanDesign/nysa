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

__author__ = 'info@cospandesign.com (name)'

import sys
import os
import yaml

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QTextEdit

from stepper_side_pane import StepperSidePane
from stepper_configuration_view import StepperConfigurationView
from stepper_control_view import StepperControlView

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from save_loader import SaveLoader

p = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class View(QWidget):

    def __init__(self, status, actions):
        super (View, self).__init__()
        self.status = status
        self.actions = actions

        self.setWindowTitle("Stepper Motor Controller")
        self.side_pane = StepperSidePane(self.status, self.actions)
        self.config_view = StepperConfigurationView(self.status, self.actions)
        self.control_view = StepperControlView(self.status, self.actions)
        self.sl = SaveLoader(extensions = ["yaml"],
                             directory = p,
                             initial_file = "motor_test")

        self.sl.set_load_callback(self.load_callback)
        self.sl.set_save_callback(self.save_callback)

        layout = QVBoxLayout()
        interface_layout = QHBoxLayout()
        main_layout = QVBoxLayout()
        control_layout = QVBoxLayout()


        #self.te = QTextEdit()
        #self.te.setText("Text!")

        #Add the save/loader and the rest of the main interface views
        layout.addWidget(self.sl)
        layout.addLayout(interface_layout)

        #Add the main layout
        interface_layout.addLayout(main_layout)
        control_layout.addWidget(self.control_view)
        main_layout.addWidget(self.config_view)
        #main_layout.addWidget(self.te)
        interface_layout.addLayout(control_layout)

        #interface_layout.addWidget(self.te)
        interface_layout.addWidget(self.side_pane)

        self.setLayout(layout)
        self.show()

    def load_callback(self):
        print "Loading file: %s" % self.sl.get_filename()
        config_dict = yaml.load(open(self.sl.get_filename(), 'r'))
        self.config_view.load_configuration(config_dict)

    def save_callback(self):
        config_dict = self.config_view.get_configuration()
        print "Saving file..."
        f = open(self.sl.get_filename(), 'w')
        print yaml.dump(config_dict, default_flow_style=False)
        f.write(yaml.dump(config_dict, default_flow_style=False))
        f.close()

    def get_configuration(self):
        return self.config_view.get_configuration()
