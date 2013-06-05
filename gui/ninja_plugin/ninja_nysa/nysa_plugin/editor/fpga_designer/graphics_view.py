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

from box import Box
from box_list import BoxList

class GraphicsView(QGraphicsView):
  def __init__(self, parent=None):
    super(GraphicsView, self).__init__(parent)
    self.setDragMode(QGraphicsView.RubberBandDrag)
    self.setRenderHint(QPainter.Antialiasing)
    self.setRenderHint(QPainter.TextAntialiasing)
    self.setAcceptDrops(True)
    self.icon = QIcon()

  def dragEnterEvent(self, event):
    #print "view Drag Event Entered"
    if event.mimeData().hasFormat("application/flowchart-data"):
      #print "Good"
      event.accept()
    else:
      event.ignore()

  def set_add_box(self, add_box):
    self.add_box = add_box

  def dragMoveEvent(self, event):
    #print "view Drag Event Entered"
    if event.mimeData().hasFormat("application/flowchart-data"):
      #print "Good"
      event.setDropAction(Qt.CopyAction)
      event.accept()
    else:
      event.ignore()

  def wheelEvent(self, event):
    factor = 1.41 ** (-event.delta() / 240.0)
    self.scale(factor, factor)

  def mouseMoveEvent(self, event):
    #print "Mouse Move Event"
    #self.startDrag()
    QGraphicsView.mouseMoveEvent(self, event)

  def dropEvent(self, event):
    if event.mimeData().hasFormat("application/flowchart-data"):
      data = event.mimeData().data("application/flowchart-data")
      #print "Data: %s" % str(data)
      d = json.loads(str(data))
      #print "view drop event"
      self.add_box(d["name"], d["color"])
      event.accept()
    else:
      event.ignore()


