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


""" stepper control view
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIntValidator

from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QAction
from PyQt4 import QtCore
from PyQt4 import Qt

Stepper_DESC_LOC = os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            "docs",
                            "stepper.txt")

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from register_view import RegisterView


class StepperSidePane(QWidget):

    def __init__(self, status, actions):
        super (StepperSidePane, self).__init__()
        self.status = status
        self.actions = actions
        self.rv = RegisterView()
        self.rv.add_register(0,  "Config",              0)
        self.rv.add_register(1,  "Control",             0)
        self.rv.add_register(2,  "Command",             0)
        self.rv.add_register(3,  "Status",              0)
        self.rv.add_register(4,  "Clock Rate",          0)
        self.rv.add_register(5,  "Steps",               0)
        self.rv.add_register(6,  "Walk Period",         0)
        self.rv.add_register(7,  "Run Period",          0)
        self.rv.add_register(8,  "Step Accelleration",  0)
        self.rv.add_register(9,  "Micro Step Hold",     0)
        self.rv.add_register(10,  "Shoot Through Delay", 0)
        self.rv.add_register(11, "Current Position",    0)
        self.rv.add_register(12, "Max Position",        0)

        f = open(Stepper_DESC_LOC, 'r')
        s = f.read()
        f.close()
        s = s.split("DESCRIPTION START")[1]
        s = s.split("DESCRIPTION END")[0]
        #print "s: %s" % s
        stepper_desc = QLabel(s)
        stepper_desc.setMaximumWidth(500)
        stepper_desc.setWordWrap(True)
        stepper_desc.setAlignment(QtCore.Qt.AlignTop)

        layout = QGridLayout()

        layout.addWidget(stepper_desc, 0, 0, 1, 2)

        #Add Register View
        layout.addWidget(self.rv, 1, 0, 1, 2)

        self.setLayout(layout)
        self.show()
        self.actions.stepper_update_register.connect(self.update_register)


    def update_register(self, address, value):
        self.rv.set_register(address, value)

