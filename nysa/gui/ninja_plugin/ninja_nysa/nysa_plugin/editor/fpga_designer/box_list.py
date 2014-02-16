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

import os
import sys
import random
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
#from PyQt4 import QtCore
from PyQt4.QtGui import *

from visual_graph.box import Box

class BoxList(QListWidget):
  """A list of items that can be dropped onto the main flowchart canvas"""

  def __init__(self, parent=None, color = "blue"):
    super(BoxList, self).__init__(parent)
    self.setDragEnabled(True)
    #self.setViewMode(QListWidget.IconMode)
    #Create a dictionary to grab all the data associated with a box
    self.d = {}
    self._color = color

  def add_items(self, items_dict, box_type):
    #print "Adding items to box list"
    for key in items_dict:
      self.add_item(key, items_dict[key], box_type)

  def add_item(self, name, item_data, box_type):
    #print "Name: %s" % name
    lwi = QListWidgetItem(name)
    lwi.setIcon(self.create_icon(name, self._color))
    mime_data = {}
    mime_data["name"] = name
    mime_data["color"] = self._color
    mime_data["data"] = item_data
    mime_data["type"] = box_type
    mime_data["move_type"] = "copy"
    js = json.dumps(mime_data)
    #Reference the json version of the data with the list widget item
    self.d[name] = js
    self.addItem(lwi)

  def create_icon(self, name, color):
    pm = QPixmap(100, 50)
    label = QLabel(name)
    palette = QPalette()
    palette.setColor(QPalette.Background, QColor(color))
    label.setPalette(palette)
    pm.fill(label, 0, 0)
    icon = QIcon(pm)
    return icon

  def startDrag(self, dropActions):
    #print "Real Drag start"
    item = self.currentItem()
    name = str(item.data(0))
    icon = item.icon()
    mime_data = QMimeData()
    d = self.d[name]
    mime_data.setData("application/flowchart-data", d)
    drag = QDrag(self)
    drag.setMimeData(mime_data)
    pixmap = icon.pixmap(24, 24)
    drag.setHotSpot(QPoint(12, 12))
    drag.setPixmap(pixmap)
    drag.start(Qt.CopyAction)


