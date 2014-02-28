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

import actions
import status

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg",
                             "visual_graph")

from visual_graph.graphics_scene import GraphicsScene as gs
p = os.path.abspath(p)
sys.path.append(p)



def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

view_state = enum(  "normal",
                    "arbitor_master_selected")



class GraphicsScene(gs):

    def __init__(self, view):
        super (GraphicsScene, self).__init__(view, None)
        self.arbitor_selected = None
        self.state = view_state.normal
        self.dbg = False
        if self.dbg: print "GS: Set state for normal"
        #self.setAcceptDrops(True)

    #Overriden Methods
    def box_selected(self, data):
        if self.dbg: print "GS: box_selected()"
        if type(data) is dict and "module" in data.keys():
            if self.dbg: print "\tbox: %s" % data["module"]
            self.fd.populate_param_table(data)

    def box_deselected(self, data):
        if self.dbg: print "GS: box_deselected()"
        if type(data) is dict and "module" in data.keys():
            if self.dbg: print "\tbox: %s" % data["module"]
            self.fd.clear_param_table()

    def remove_selected(self, reference):
        if self.dbg: print "GS: remove_selected()"

    #Overriden PyQT4 Methods
    def mouseMoveEvent(self, event):
        super (GraphicsScene, self).mouseMoveEvent(event)
        self.auto_update_all_links()

    def mousePressEvent(self, event):
        super (GraphicsScene, self).mousePressEvent(event)
        self.auto_update_all_links()

    def dropEvent(self, event):
        if self.dbg: print "GS: Drag Event"
        super (GraphicsScene, self).dropEvent(event)

    def startDrag(self, event):
        if self.dbg: print "GS: Drag start event"


    def auto_update_all_links(self):
        #for l in self.links:
        #    if l.is_center_track():
        #        print "Center track!"
        #        print "\tlink_ref: %s - %s" % (l.from_box.box_name, l.to_box.box_name)
        #        l.auto_update_center()
        #self.peripheral_bus.update_links()
        #self.memory_bus.update_links()
        pass

    #States
    def get_state(self):
        if self.dbg: print "GS: get_state()"
        return self.state

    def set_master(self, master):
        self.master = master

    def set_peripheral_bus(self, peripheral_bus):
        self.peripheral_bus = peripheral_bus

    def set_memory_bus(self, memory_bus):
        self.memory_bus = memory_bus

    def slave_selected(self, name, bus, tags):
        if self.dbg: print "GS: slave_selected()"
        if self.dbg: print "\t%s" % name
        if self.arbitor_selected is None:
            if self.dbg: print "\tArbitor master is not selected"
            if self.dbg: print "\tSet state for normal"
            #slave = bus.get_slave(name)
            #bus.slave_selection_changed(slave)
            self.state = view_state.normal
            return

        self.state = view_state.arbitor_master_selected

        if self.dbg: print "\tArbitor master is selected: %s" % self.arbitor_selected.box_name

        if  name == "DRT":
            if self.dbg: print "\tCan't attach to the DRT"
            return

        from_slave = self.arbitor_selected.get_slave()
        if from_slave.box_name == name:
            if self.dbg: print "\tCan't attach to ourselves"
            return

        arbitor_name = self.arbitor_selected.box_name
        to_slave = bus.get_slave(name)
        
        connected_slave = self.get_arbitor_master_connected(self.arbitor_selected)
        if connected_slave is not None:
            self.arbitor_master_disconnect(self.arbitor_selected, connected_slave)

        self.fd.connect_arbitor_master(from_slave, arbitor_name, to_slave)
        self.arbitor_selected.update_view()
        self.arbitor_selected.connect_slave(to_slave)

    def is_arbitor_master_active(self):
        if self.dbg: print "GS: is_arbitor_master_active()"
        #return self.state == view_state.arbitor_master_selected
        return self.arbitor_selected is not None

    def slave_deselected(self, name, bus, tags):
        if self.dbg: print "GS: slave_deselect()"
        if self.arbitor_selected is None:
            self.state = view_state.normal

    def arbitor_master_selected(self, slave, arbitor_master):
        if self.dbg: print "GS: arbitor_master_selected()"
        name = arbitor_master.box_name
        self.state = view_state.arbitor_master_selected
        if self.dbg: print "\tSet state for arbitor master"
        self.arbitor_selected = arbitor_master
        self.peripheral_bus.enable_expand_slaves(name, True)
        self.memory_bus.enable_expand_slaves(name, True)
        slave.arbitor_master_selected(name)

    def arbitor_master_deselected(self, arbitor_master):
        if self.dbg: print "GS: arbitor_master_deselected()"
        for i in range (len(self.links)):
            self.removeItem(self.links[i])
        self.links = []
        self.arbitor_selected = None
        name = arbitor_master.box_name
        self.state = view_state.normal
        if self.dbg: print "\tSet state for normal"
        self.peripheral_bus.enable_expand_slaves(name, False)
        self.memory_bus.enable_expand_slaves(name, False)
        slave = arbitor_master.get_slave()
        slave.remove_arbitor_masters()
        slave.show_arbitor_masters()
        slave.setSelected(True)

    #def arbitor_master_fake_selected(self, slave, arbitor_master):
    #    print "GS: arbitor master selected selected"
    #    self.arbitor_selected = arbitor_master

    def is_arbitor_master_selected(self):
        if self.dbg: print "GS: is_arbitor_master_selected()"
        return self.arbitor_selected is not None

    def get_arbitor_master_selected(self):
        if self.dbg: print "GS: get_arbitor_master_selected()"
        return self.arbitor_selected

    def arbitor_master_disconnect(self, arbitor_master, to_slave):
        if self.dbg: print "GS: arbitor_master_disconnect()"
        from_slave = arbitor_master.get_slave()
        for i in range (len(self.links)):
            self.removeItem(self.links[i])

        arbitor_name = arbitor_master.box_name
        if self.dbg: print "\tarbitor_master: %s" % arbitor_master.box_name

        #XXX: Remove the arbitor connctor
        self.fd.disconnect_arbitor_master(from_slave, arbitor_name, to_slave)
        arbitor_master.disconnect_slave()

    def get_arbitor_master_connected(self, arbitor_master):
        if self.dbg: print "GS: get_arbitor_master_connected()"
        from_slave = arbitor_master.get_slave()
        arbitor_name = arbitor_master.box_name
        typ = None
        index = 0
        slave = None

        typ, index = self.fd.get_arbitor_master_connected(from_slave, arbitor_name)

        if typ is None:
            if self.dbg: print "\tNo slave is attached to the arbitor"
            return None

        if typ == SlaveType.PERIPHERAL:
            slave = self.peripheral_bus.get_slave_from_index(index)
        else:
            slave = self.memory_bus.get_slave_from_index(index)

        if self.dbg: print "\tGetting Arbitor Master connected for %s which is: %s" % (arbitor_name, slave.box_name)
        return slave

    def remove_slave(self, slave):
        if self.dbg: print "GS: Remove slave"
        index = slave.bus.get_slave_index(slave.box_name)
        bus_type = slave.bus.get_bus_type()
        self.fd.remove_slave(bus_type, index)


