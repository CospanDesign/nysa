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
  6/14/2013: Initial commit
'''

import os
import sys
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from box import Box

from defines import HOST_INTERFACE_RECT
from defines import HOST_INTERFACE_POS
from defines import HOST_INTERFACE_COLOR
from defines import HOST_INTERFACE_ID

from link import Link
from link import link_type as lt
from link import side_type as st

from link import get_inverted_side

class HostInterface(Box):
    """Host Interface Box"""

    def __init__(self,
                 scene,
                 name,
                 select_func,
                 deselect_func):

        super(HostInterface, self).__init__(position = HOST_INTERFACE_POS,
                                            scene = scene,
                                            name = name,
                                            color = HOST_INTERFACE_COLOR,
                                            select_func = select_func,
                                            deselect_func = deselect_func,
                                            rect = HOST_INTERFACE_RECT,
                                            user_data = HOST_INTERFACE_ID)
        self.master = None
        self.links = {}

    def link_master(self, master):
        self.master = master
        self.links[master] = Link(self, master, self.scene(), lt.host_interface)
        self.links[master].from_box_side(st.right)
        self.links[master].to_box_side(st.left)
        self.links[master].track_nodes()

    def paint(self, painter, option, widget):
        super(HostInterface, self).paint(painter, option, widget)
        for link in self.links:
            self.links[link].auto_update()


