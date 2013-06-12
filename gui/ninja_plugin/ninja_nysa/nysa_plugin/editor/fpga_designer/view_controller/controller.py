# -*- coding: utf-8 -*-

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
  6/10/2013: Initial commit
'''

import os
import sys


from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from box import Box
from link import Link
from link import link_type as lt


sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "lib"))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "gui"))


sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "drt"))


import utils


def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

BoxType = enum('HOST_INTERFACE',
               'MASTER',
               'MEMORY_INTERCONNECT',
               'PERIPHERAL_INTERCONNECT',
               'SLAVE')


WISHBONE_LINK_COLOR = QColor("blue")
AXI_LINK_COLOR = QColor("blue")
HOST_INTERFACE_LINK_COLOR = QColor("green")
ARBITOR_LINK_COLOR = QColor("black")

class DesignControlError(Exception):
    """
    Errors associated with the Controller

    Error associated with:
        -wishbone/axi model not configured correclty
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Controller (QObject):
    output = None

    def __init__(self, fpga_designer, model, canvas, output):
        QObject.__init__(self)

        self.fd = fpga_designer
        self.model = model
        self.canvas = canvas
        self.output = output
        #Connect events
        """
        Go through view and connect all relavent events
        """

        self.canvas.set_controller(self)

    def drag_enter(self, event):
        """
        An item has entered the canvas
        """
        #Check if the item is the correct type
        raise NotImplementedError("This function should be subclassed")

    def drag_move(self, event):
        """
        An item is dragged around the canvas

        Detect if a movement is valid
        """
        #get the type of device (slave/host interface/master)
        """
        This class should be subclassed for wishbone or Axi because Axi
        can add and remove masters
        """
        raise NotImplementedError("This function should be subclassed")

    def drop (self, event):
        """
        An item has been dropped
        """
        #Handle an addition/move of a slave
        #Handle an addition/remove of a host interface
        raise NotImplementedError("This function should be subclassed")

    def add_box(self, box_type, color, name, ID, position, rect=QRect()):
        """Add a box to the canvas"""
        scene = self.canvas.scene()
        if box_type == BoxType.SLAVE:
            fn = utils.find_module_filename(name, self.fd.user_dirs)
            fn = utils.find_rtl_location(fn, self.fd.user_dirs)

        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or wishbone")

        #self.model.add_slave

        return Box(     position = position,
                        scene = scene,
                        name = name,
                        color = color,
                        select_func = self.box_select,
                        deselect_func = self.box_deselect,
                        user_data = ID)

    def get_index_from_position(self, position):
        return -1

    def remove_box(self, ID):
        """
        Remove the slave from both the visual interface and from the model
        """
        pass

    def box_select(self, data):
        """An item has been selected"""
        #Get the module tags for this item
        #XXX:Need to get the module tags for this
        m = self.model

        if type(data) is str:
            d = {}
            d["module"] = data
            d["parameters"] = {}
            self.fd.populate_param_table(d)
        else:
            self.fd.populate_param_table(data)

    def box_deselect(self):
        """No item is selected"""
        self.fd.clear_param_table()

    def valid_box_area(self, ID, rect, position):
        """
        This class should be subclassed

        Description: Analyzes whether the box should be allowed to be dropped
        """
        raise NotImplementedError("This function should be subclassed")

    def zoom_rect(self, rect):
        """
        Zoom to a selected region
        """
        #The user may not be able to actually zoom to a region (it may not be
        #   the correct geometry, how to handle this?

        #Can this be animated :) ??

    def connect(self, box_ID1, box_ID2, box1_side=None, box2_side=None):
        """
        Connect box with ID1 to box with ID2 if box1_side and box2_side
        is specfiied then connect them on that specific side, otherwise
        just connect automatically
        """
        pass



    def set_config_file(self, config_file):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or wishbone")
        self.output.Debug(self, "set the configuration file")
        self.model.load_config_file(config_file)
        self.model.initialize_graph(self)

    def set_default_board_project(self, board_name):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or wishbone")

        self.model.set_default_board_project(board_name)
        self.model.initialize_graph(self)


    def set_bus(self, bus):
        raise NotImplementedError("This function should be subclassed")

    def get_bus(self):
        return self.bus

    def add_link(self, from_box, to_box, link_type):
        color = QColor("black")
        if link_type == lt.host_interface:
            color = HOST_INTERFACE_LINK_COLOR
        elif link_type == lt.wishbone_bus:
            color = WISHBONE_LINK_COLOR
        elif link_type == lt.axi_bus:
            color = AXI_LINK_COLOR
        elif link_type == lt.arbitor:
            color = ARBITOR_LINK_COLOR

        l = Link(from_box, to_box, self.canvas.scene(), color, link_type)

