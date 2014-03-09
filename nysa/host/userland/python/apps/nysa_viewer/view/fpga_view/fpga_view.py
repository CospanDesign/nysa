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


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "common"))
import status

os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
import actions


from defines import *

from wishbone_controller import WishboneController

from fpga_bus_view import FPGABusView
from properties.properties_view import PropertiesView

class FPGAImage(QWidget):

    def __init__(self):
        super (FPGAImage, self).__init__()
        self.status = status.Status()
        self.actions = actions.Actions()
        self.fbv = FPGABusView(self)
        self.fbv.setSizePolicy(QSizePolicy.Preferred,
                               QSizePolicy.Preferred)

        self.bpv = PropertiesView(self)
        self.bpv.setSizePolicy(QSizePolicy.Maximum,
                               QSizePolicy.Preferred)

        self.n = None
        self.controller = None
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.fbv)
        self.main_splitter.addWidget(self.bpv)
        self.main_splitter.setStretchFactor(1, 0)
        layout = QHBoxLayout()
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

    def update_nysa_image(self, n, config_dict):
        self.n = n
        self.fbv.clear()
        if self.n is None:
            return
        if config_dict["bus_type"] == "wishbone":
            self.controller = WishboneController(config_dict, self.fbv.scene)
        else:
            raise NotImplemented("Implement AXI Interface!")

        self.controller.initialize_view()
        self.controller.refresh_slaves()
        m = self.controller.get_model()
        npslaves = m.get_number_of_peripheral_slaves()

        height = (SLAVE_RECT.height() * npslaves + SLAVE_VERTICAL_SPACING)
        width = (SLAVE_RECT.width() +
                 PERIPHERAL_BUS_RECT.width() +
                 MASTER_RECT.width() +
                 HOST_INTERFACE_RECT.width() +
                 (SLAVE_HORIZONTAL_SPACING * 4))
        r = QRectF(0, 0, height, 100)
        self.fbv.view.fitInView(r, Qt.KeepAspectRatio)
        self.bpv.setup_bus(config_dict, n)

    def sizeHint (self):
        size = QSize()
        size.setWidth(600)
        return size

    def drag_enter(self, event):
        print "FV: Drag Enter"
    
    def drag_move(self, event):
        print "FV: Drag Move"

    def drop_event(self, event):
        print "FV: Drop Event"
        event.ignore()
        #self.vc.drop_event(self.position(), event)


