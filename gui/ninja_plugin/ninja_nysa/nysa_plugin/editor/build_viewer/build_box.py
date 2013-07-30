# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  7/21/2013: Initial commit
'''

import os
import sys
import json
import inspect

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from box import Box
from build_status import BuildStatus

class BuildBox(Box):

    def __init__(self,
                 scene,
                 position,
                 name,
                 ID,
                 color,
                 parameter,
                 rect):

        super(BuildBox, self).__init__(position = position,
                                       scene = scene,
                                       name = name,
                                       color = color,
                                       rect = rect,
                                       user_data = parameter)
        self.movable(False)
        self.label_rect = QRectF(self.rect)
        self.label_rect.setWidth(self.rect.width() * 0.75)
        self.status_rect = QRectF(self.rect)
        self.status_rect.setTopLeft(self.label_rect.topRight())
        self.status_rect.setWidth(self.rect.width() * 0.25)
        self.status_box = BuildStatus(scene, self.label_rect.topRight(), self.status_rect, self)
        self.build_cb = None
        self.ID = ID

    def contextMenuEvent(self, event):
        menu_items = (("&Help", self.build_help),)
        menu = QMenu(self.parentWidget())
        for text, func in menu_items:
            menu.addAction(text, func)
        menu.exec_(event.screenPos())

    def set_build_callback(self, build_cb):
        self.build_cb = build_cb

    def build_help(self):
        print "Help"

    def get_status(self):
        return self.status_bux.get_status()

    def set_status(self, status):
        self.status_box.set_status(status)

    def status_update(self):
        #print "animation update"
        self.scene().invalidate(self.mapToScene(self.rect).boundingRect())

    def mouseDoubleClickEvent(self, event):
        print "Mouse double click event"
        if self.build_cb is not None:
            self.build_cb(self.ID)

    #Paint
    def paint(self, painter, option, widget):

        highlight_width = 8

        pen = QPen(self.style)
        pen.setColor(Qt.black)
        pen.setWidth(1)
        if option.state & QStyle.State_Selected:
            #Selected
            pen.setColor(QColor("black"))
            pen.setWidth(highlight_width)

        painter.setPen(pen)

        painter.drawRect(self.rect)
        rect = self.label_rect
        painter.drawRect(rect)
        painter.fillRect(rect, QColor(self.color))
        painter.setFont(self.text_font)

        #draw text
        pen.setColor(Qt.black)
        painter.setPen(pen)

        self.add_label_to_rect(painter, rect, self.box_name)
        self.status_box.paint(painter, option, widget)
        #Draw Status


