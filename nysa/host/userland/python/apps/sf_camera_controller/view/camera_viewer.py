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


""" camera viewer
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4 import QtGui

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))

from sf_camera_actions import SFCameraActions

class CameraViewer(QGraphicsView):
    def __init__(self, status, actions):
        super(CameraViewer, self).__init__()
        self.status = status
        self.actions = actions
        self.image_viewer = ImageViewer(640, 480, status, actions)
        self.scene = QGraphicsScene(self)
        self.scene.addItem(self.image_viewer)
        self.fitInView(QRectF(0.0, 0.0, 640.0, 480.0), Qt.KeepAspectRatio)

    def scale_view(self, factor):
        factor = self.transform().scale(factor,
                                        factor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor > 0.05 and factor < 15:
            #Only scale if we are not too small or too big
            self.scale(factor, factor)

    def scale_fit(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def reload_image(self):
        self.image_viewer.new_image()

    def keyPressEvent(self, event):
        task_list = {
                Qt.Key_Plus:  lambda: self.scale_view(1.2),
                Qt.Key_Minus: lambda: self.scale_view(1/1.2),
                Qt.Key_Space: lambda: self.reload_image(),
                Qt.Key_Equal: lambda: self.scale_fit(),
        }

class ImageViewer(QGraphicsWidget):
    def __init__(self, width, height, status, actions):
        super (ImageViewer, self).__init__()
        self.status = status
        self.actions = actions

        self.setGeometry(0, 0, width, height)
        self.actions.sf_camera_read_ready.connect(self.new_image)

    def resize_view(self, width, height):
        self.setGeometry(0, 0, width, height)

    def new_image(self, image):
        self.img = image
        self.scene().invalidate()

    def paint(self, painter, option, widget):
        painter.drawImage(QPoint(0, 0), self.img)
