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

sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "editor",
                              "fpga_editor"))

from box import Box
from link import link_type as lt
from link import side_type as st

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

import nysa_actions


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
    output = None

    def __init__(self, model, output):
        QObject.__init__(self)

        self.fd = None
        self.model = model
        self.canvas = None
        self.output = output
        self.boxes = {}
        self.user_dirs = []
        self.constraint_editor = None
        self.actions  = nysa_actions.NysaActions()
        self.connect(self.actions, SIGNAL("module_built(QString)"), self.module_built)
        #Connect events
        """
        Go through view and connect all relavent events
        """


    def set_canvas(self, canvas):
        self.canvas = canvas
        self.canvas.set_controller(self)

    def set_fpga_designer(self, fd):
        self.fd = fd

    def add_user_dir(self, user_dir):
        self.user_dirs.append(user_dir)

    def remove_user_dir(self, user_dir):
        self.user_dirs.remove(user_dir)

    def get_user_dirs(self):
        return self.user_dirs

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
            fn = utils.find_module_filename(name, self.user_dirs)
            fn = utils.find_rtl_file_location(fn, self.user_dirs)

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
        self.output.Debug(self, "set the configuration file")
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


    #Constraint Editor interface
    def initialize_constraint_editor(self, constraint_editor):
        #print "Initialize constraint editor"
        self.constraint_editor = constraint_editor
        self.constraint_editor.set_connect_callback(self.connect_signal)
        self.constraint_editor.set_disconnect_callback(self.disconnect_signal)
        self.constraint_editor.initialize_view()
        self.refresh_constraint_editor()

    def refresh_constraint_editor(self, name = None):
        #If a name is present just populate connections for that one item
        #   e.g. the host interface, master, etc...
        if self.constraint_editor is None:
            print "constraint editor is none"
            return

        mbd = self.model.get_consolodated_master_bind_dict()
        self.constraint_editor.clear_all()

        if name is None or name == "Host Interface":
            #for key in mbd:
            #    print "%s: %s" % (key, mbd[key])

            #print "Get bindings for host_interface"
            hib = self.model.get_host_interface_bindings()
            hip = self.model.get_host_interface_ports()
            signals = copy.deepcopy(hip.keys())
            #print "signals: %s" % str(signals)
            for s in hip.keys():
                if s in no_detect_ports:
                    signals.remove(s)

            bound_count = 0
            for key in hib:
                if not hib[key]["range"]:
                    self.constraint_editor.add_connection(color = HI_COLOR,
                                                          module_name = "Host Interface",
                                                          port = key,
                                                          direction = hib[key]["direction"],
                                                          pin_name = hib[key]["loc"])
                else:
                    indexes = copy.deepcopy(hib[key].keys())
                    indexes.remove("range")
                    bound_count = 0
                    for i in indexes:
                        bound_count += 1
                        #n = "%s[%d]" % (key, i)
                        self.constraint_editor.add_connection(color = HI_COLOR,
                                                              module_name = "Host Interface",
                                                              port = key,
                                                              direction = hib[key][i]["direction"],
                                                              pin_name = hib[key][i]["loc"],
                                                              index = i)

                #Remove signals from ports list
                if key in signals:
                    if not hib[key]["range"]:
                        #print "remove an item that has only no range: %s" % key
                        signals.remove(key)
                    else:
                        #print "Signal: %s" % key
                        #print "Checking if bound count: %d == %d" % (bound_count, ports[key]["size"])
                        if bound_count == ports[key]["size"]:
                            #print "All of the items in the bus are constrained"
                            signals.remove[key]
                else:
                    #print "%s is not a port of %s" % (key, name)
                    pass


            #print "Hports keys: %s" % str(signals)
            for signal in signals:

                if hip[signal]["size"] > 1:
                    rng = (hip[signal]["max_val"], hip[signal]["min_val"])
                    self.constraint_editor.add_signal(HI_COLOR,
                                                      "Host Interface",
                                                      signal,
                                                      rng,
                                                      hip[signal]["direction"])
                else:
                    self.constraint_editor.add_signal(HI_COLOR,
                                                      "Host Interface",
                                                      signal,
                                                      None,
                                                      hip[signal]["direction"])


        if name is None or name != "Host Interface":
            #Call the bus specific interface
            self.bus_refresh_constraint_editor(name)

        #populate the constraint view
        cfiles = self.model.get_constraint_filenames()
        constraints = []
        for f in cfiles:
            constraints.extend(utils.get_net_names(f))

        #Don't let the user select where the clk and rst are, let the board file do this
        constraints.remove("clk")
        if "rst" in constraints:
            constraints.remove("rst")
        if "rst_n" in constraints:
            constraints.remove("rst_n")

        #Go through all the connected signals and create a list of constraint that are not used
        mbd = self.model.get_expanded_master_bind_dict()
        #print "mbd: %s" % str(mbd)
        #print "constraints: %s" % str(constraints)
        for module in mbd:
            module_dict = mbd[module]
            for signal in module_dict:
                signal_dict = module_dict[signal]

                #print "signal: %s" % str(signal)
                if signal_dict["range"]:
                    #print "check range"
                    ikeys = copy.deepcopy(signal_dict.keys())
                    ikeys.remove("range")
                    for i in ikeys:
                        if signal_dict[i]["loc"] in constraints:
                            #print "Checking: %s" % signal_dict[i]["loc"]
                            constraints.remove(signal_dict[i]["loc"])
                else:   
                    if signal_dict["loc"] in constraints:
                        constraints.remove(signal_dict["loc"])
            
        for c in constraints:
            self.constraint_editor.add_pin(c)

    def item_is_enabled(self, path):
        #print "VC: Path: %s" % path
        return True

    def get_constraint_editor(self):
        return self.constraint_editor

    def connect_signal(self, module_name, signal_name, direction, index, pin_name):
        #print "Connect"
        self.model.set_binding(module_name, signal_name, pin_name, index)
        self.refresh_constraint_editor()

    def disconnect_signal(self, module_name, signal_name, direction, index, pin_name):
        #Remove signal from model
        print "Controller: Disconnect"
        uname = self.model.get_unique_from_module_name(module_name)
        self.model.unbind_port(uname, signal_name, index)
        self.constraint_editor.remove_connection(module_name, signal_name, index)
        self.refresh_constraint_editor()


    def bus_refresh_constraint_editor(self, name = None):
        raise NotImplementedError("This function should be subclassed")

    def get_model(self):
        return self.model

    def module_built(self, module_name):
        print "controller module built: %s" % module_name
        #Go through all editors, if they are ibuilder then
        self.model.update_module_ports(module_name, self.user_dirs)
        self.refresh_constraint_editor()

