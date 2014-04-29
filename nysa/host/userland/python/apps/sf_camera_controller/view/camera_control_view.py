# Copyright (c) 2014 Cospan Design

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


""" Sparkfun Camera Control View
"""

import sys
import os

from PyQt4.QtGui import *

class SFCameraControlView(QWidget):

    def __init__(self, status, actions):
        super(SFCameraControlView, self).__init__()
        self.status = status
        self.actions = actions

        run_button = QPushButton("Run")
        run_button.setToolTip("Start Capturing Images")
        run_button.clicked.connect(self.actions.sf_camera_run)

        stop_button = QPushButton("Stop")
        stop_button.setToolTip("Stop Capturing Images")
        stop_button.clicked.connect(self.actions.sf_camera_stop)

        reset_button = QPushButton("Reset")
        reset_button.setToolTip("Reset Camera")
        reset_button.clicked.connect(self.actions.sf_camera_reset)

        layout = QGridLayout()
        
        button_layout = QGridLayout()
        button_layout.addWidget(run_button, 0, 0, 1, 2)
        button_layout.addWidget(stop_button, 1, 0, 1, 2)
        button_layout.addWidget(reset_button, 2, 0, 1, 2)

        layout.addLayout(button_layout, 1, 0, 3, 2)
        self.setLayout(layout)


