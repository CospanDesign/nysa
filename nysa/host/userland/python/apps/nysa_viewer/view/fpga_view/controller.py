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
import copy


from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir))

from status import Status


p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg")
p = os.path.abspath(p)
sys.path.append(p)


from visual_graph.box import Box

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

lt = enum(   "bus",
             "host_interface",
             "arbitor",
             "slave",
             "port",
             "arbitor_master")


st = enum(   "top",
             "bottom",
             "right",
             "left")

from defines import HI_COLOR
from defines import PS_COLOR
from defines import MS_COLOR


sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "lib"))

import utils
import constraint_utils as cu

sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "gui"))


sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "drt"))

sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir))


no_detect_ports = [
    "rst",
    "clk",
    "o_in_address",
    "i_out_address",
    "o_oh_ready",
    "o_in_data_count",
    "o_ih_ready",
    "o_in_command",
    "i_ftdi_suspend_n",
    "o_ih_reset",
    "i_out_status",
    "i_master_ready",
    "i_out_data",
    "i_out_data_count",
    "i_oh_en",
    "io_ftdi_data",
    "o_in_data"
]



def enum(*sequential, **named):
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)

BoxType = enum('HOST_INTERFACE',
               'MASTER',
               'MEMORY_INTERCONNECT',
               'PERIPHERAL_INTERCONNECT',
               'SLAVE')


class DesignControlError(Exception):
    """
    Errors associated with the Controller

    Error associated with:
        -bus/axi model not configured correclty
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Controller (QObject):

    def __init__(self, model):
        self.status = Status()
        QObject.__init__(self)

        self.fd = None
        self.model = model
        self.canvas = None
        self.boxes = {}
        self.constraint_editor = None
        """
        Go through view and connect all relavent events
        """

    def set_canvas(self, canvas):
        self.canvas = canvas
        self.canvas.set_controller(self)

    def set_fpga_designer(self, fd):
        self.fd = fd

    def add_user_dir(self, user_dir):
        self.model.add_user_path(user_dir)

    def remove_user_dir(self, user_dir):
        self.model.remove_user_path(user_dir)

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
        This class should be subclassed for bus or Axi because Axi
        can add and remove masters
        """
        raise NotImplementedError("This function should be subclassed")

    def drop_event(self, position, event):
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
            fn = utils.find_module_filename(name, self.get_user_dirs())
            fn = utils.find_rtl_file_location(fn, self.get_user_dirs())

        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")
        #self.model.add_slave
        return Box(position=position,
                   scene=scene,
                   name=name,
                   color=color,
                   select_func=self.box_select,
                   deselect_func=self.box_deselect,
                   user_data=ID)

    def get_index_from_position(self, position):
        #Check if this is the peripheral bus or the memory slave
        #If this is the peripheral bus then
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
        #m = self.model

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

    def set_config_file(self, config_file):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")
        self.status.Debug(self, "set the configuration file")
        self.model.load_config_file(config_file)
        self.model.initialize_graph(self)

    def set_default_board_project(self, board_name):
        if self.model is None:
            raise DesignControlError("Bus type is not set up corretly," +
                                     "please select either axi or bus")

        self.model.set_default_board_project(board_name)
        self.model.initialize_graph(self)

    def set_bus(self, bus):
        raise NotImplementedError("This function should be subclassed")

    def get_bus(self):
        return self.bus

    def add_link(self, from_box, to_box, link_type, side):
        from_box.add_connection(to_box, link_type, side)

    def add_slave_link(self, bus, slave):
        self.add_link(bux, slave, lt.bus_bus, st.right)

    def add_host_interface_link(self, hi, m):
        self.add_link(hi, m, lt.host_interface, st.right)

    def add_bus_link(self, m, bus):
        self.add_link(m, bus, lt.bus, st.right)


    def get_project_name(self):
        raise NotImplementedError("This function should be subclassed")

    def item_is_enabled(self, path):
        #print "VC: Path: %s" % path
        return True

    def connect_signal(self, module_name, signal_name, direction, index, pin_name):
        #print "Connect"
        self.model.set_binding(module_name, signal_name, pin_name, index)

    def disconnect_signal(self, module_name, signal_name, direction, index, pin_name):
        #Remove signal from model
        print "Controller: Disconnect"
        uname = self.model.get_unique_from_module_name(module_name)
        self.model.unbind_port(uname, signal_name, index)

    def get_model(self):
        return self.model

    def get_project_location(self):
        return self.model.get_project_location()


