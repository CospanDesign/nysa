# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#A huge thanks to 'Rapid GUI Programming with Python and Qt' by Mark Summerfield

'''
Log
  6/05/2013: Initial commit
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"

import sys
import random
import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from link import Link
from link import link_type
from box import Box
from box_list import BoxList

class GraphicsView(QGraphicsView):
    def __init__(self, parent = None):
        super(GraphicsView, self).__init__(parent)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setAcceptDrops(True)
        self.icon = QIcon()
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def wheelEvent(self, event):
        factor = 1.41 ** (-event.delta() / 240.0)
        self.scale(factor, factor)

    def dragEnterEvent(self, event):
        self.controller.drag_enter(event)

    def dragMoveEvent(self, event):
        self.controller.drag_move(event)

    def mouseMoveEvent(self, event):
        QGraphicsView.mouseMoveEvent(self, event)

    def dropEvent(self, event):
        self.controller.drop_event(event)

    def keyPressEvent(self, event):
        print "Key press event"
        task_list = {
        Qt.Key_Plus:  lambda: self._scale_view(1.2),
        Qt.Key_Minus: lambda: self._scale_view(1 / 1.2),
        Qt.Key_Equal: lambda: self._scale_normal()
        #TODO: Add more key interfaces here
        }
        if event.key() in task_list:
            task_list[event.key()]()

        else:
            #Pass the key event to the system
            QWidget.keyPressEvent(self, event)

    def _scale_view(self, scale_factor):
        """Scale the view"""
        #print "Canvas: Scale view by: %f" % scale_factor

        #check if the scale factor is alright
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()

        if factor > self.scale_min and factor < self.scale_max:
            #Scale factor is within limits
            self.scale(scale_factor, scale_factor)
        elif factor < self.scale_min:
            if self.debug: print "Canvas: Scale too small: %f" % factor
        elif factor > self.scale_max:
            if self.debug: print "Canvas: Scale too large: %f" % factor

    def _scale_normal(self):
        scale_factor = 1.0
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()
        scale_factor = 1.0 / factor
        if self.debug: print "Canvas: Set scale back to 1.0"
        self.scale(scale_factor, scale_factor)

    def _scale_fit(self):
        if self.debug: print "Canvas: Set scale to fit all items"
        self.fitInView(self.scene)

