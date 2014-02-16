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

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

view_state = enum(  "normal",
                    "abby_normal")


class GraphicsScene(QGraphicsScene):
    def __init__(self, view, parent):
        super(GraphicsScene, self).__init__()
        self.view = view
        #self.parent = parent
        self.parent = parent
        self.arbitor_selected = None
        self.state = view_state.normal
        self.links = []
        self.dbg = True
        if self.dbg: print "GS: Set state for normal"
        #self.setAcceptDrops(True)

    def get_view(self):
        if self.dbg: print "GS: get_view()"
        return self.view

    def box_selected(self, data):
        if self.dbg: print "GS: box_selected()"
        #if type(data) is dict and "module" in data.keys():
        #    if self.dbg: print "\tbox: %s" % data["module"]

    def box_deselected(self, data):
        if self.dbg: print "GS: box_deselected()"
        #if type(data) is dict and "module" in data.keys():
        #    if self.dbg: print "\tbox: %s" % data["module"]
        #    self.fd.clear_param_table()

    def get_state(self):
        if self.dbg: print "GS: get_state()"
        return self.state

    def fit_view(self):
        self.parent.fit_view()

    def remove_selected(self, reference):
        if self.dbg: print "GS: remove_selected()"

    #Links
    def set_link_ref(self, lref):
        if self.dbg: print "GS: set_link_ref()"
        if self.dbg: print "\tlink_ref: %s - %s" % (lref.from_box.box_name, lref.to_box.box_name)
        self.links.append(lref)

    def clear_links(self):
        for i in range (len(self.links)):
            self.removeItem(self.links[i])

    def mouseMoveEvent(self, event):
        if self.dbg: print "GS: mouse move event"
        super (GraphicsScene, self).mouseMoveEvent(event)
        for l in self.links:
            if l.is_center_track():
                l.auto_update_center()


    def mousePressEvent(self, event):
        if self.dbg: print "GS: mouse press event"
        super (GraphicsScene, self).mousePressEvent(event)
        for l in self.links:
            if l.is_center_track():
                l.auto_update_center()

    def dropEvent(self, event):
        if self.dbg: print "GS: Drag Event"
        super (GraphicsScene, self).dropEvent(event)

    def startDrag(self, event):
        if self.dbg: print "GS: Drag start event"

