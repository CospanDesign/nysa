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
  7/20/2013: Initial commit
'''

__author__ = "Dave McCoy dave.mccoy@cospandesign.com"

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from link import Link

class GraphicsScene(QGraphicsScene):

    def __init__(self, view, build_flow_viewer):
        super(GraphicsScene, self).__init__()
        self.bfv = build_flow_viewer
        self.dbg = False
        self.links = {}

    def box_selected(self, data):
        if self.dbg: print "GS: box_selected()"
        #Use this to populate the properties table
#        if type(data) is dict and "module" in data.keys():
#            if self.dbg: print "\tbox: %s" % data["module"]
#            self.fd.populate_param_table(data)

    def box_deselected(self, data):
        if self.dbg: print "GS: box_deselected()"
#        if type(data) is dict and "module" in data.keys():
#            if self.dbg: print "\tbox: %s" % data["module"]
#            self.fd.clear_param_table()
#


