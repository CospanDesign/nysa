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


""" camera widget
"""


import sys
import os

from PyQt4.QtGui import *

from camera_control_view import SFCameraControlView
from camera_viewer import CameraViewer

class CameraWidget(QWidget):

    def __init__(self, status, actions):
        super (CameraWidget, self).__init__()
        layout = QHBoxLayout()

        layout.addWidget(CameraViewer(status, actions))
        layout.addWidget(SFCameraControlView(status, actions))

        self.setLayout(layout)
        self.show()



