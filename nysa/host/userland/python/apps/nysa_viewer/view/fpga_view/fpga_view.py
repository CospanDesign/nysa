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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

import status
import actions

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg",
                             "visual_graph")
p = os.path.abspath(p)
sys.path.append(p)

from graphics_view import GraphicsView
from graphics_scene import GraphicsScene
#from default_graphics_scene import GraphicsScene
from graphics_widget import GraphicsWidget



class FPGAImage(GraphicsWidget):
    def __init__(self):
        super (FPGAImage, self).__init__()
        self.actions = actions.Actions()
        #Create a view
        self.view = GraphicsView()
        #Create a scene
        self.scene = GraphicsScene(self.view)
        self.status = status.Status()
        self.status.Debug(self, "Started FPGAImage View")

    def clear(self):
        self.status.Verbose(self, "Clearing the FPGA Image")
        self.view = GraphicsView()

    def device_selected(self, device_type, nysa):
        pass


