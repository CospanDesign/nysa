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


class GraphicsScene(QGraphicsScene):
    def __init__(self, view, app):
        super(GraphicsScene, self).__init__()
        self.view = view
        self.app = app
        self.links = []
        self.dbg = False
        if self.dbg: print "GS: Set state for normal"
        #self.setAcceptDrops(True)

    def get_view(self):
        return self.view

    def fit_view(self):
        self.app.fit_view()

    def box_selected(self, data):
        #raise AssertionError ("box_selected() is not defined")
        pass

    def box_deselected(self, data):
        #raise AssertionError ("box_deselected() is not defined")
        pass

    def remove_selected(self, reference):
        #raise AssertionError ("remove_selected() is not defined")
        pass

    #Links
    def set_link_ref(self, lref):
        if self.dbg: print "\tlink_ref: %s - %s" % (lref.from_box.box_name, lref.to_box.box_name)
        self.links.append(lref)

    def clear_links(self):
        for i in range (len(self.links)):
            self.removeItem(self.links[i])

    def auto_update_all_links(self):
        for l in self.links:
            if l.is_center_track():
                l.auto_update_center()


    '''
    #The user should override the following methods:
    def mouseMoveEvent(self, event):
        super (GraphicsScene, self).mouseMoveEvent(event)
        self.auto_update_all_links()

    def mousePressEvent(self, event):
        super (GraphicsScene, self).mousePressEvent(event)
        self.auto_update_all_links()

    def dropEvent(self, event):
        super (GraphicsScene, self).dropEvent(event)

    def startDrag(self, event):
        pass
    '''



