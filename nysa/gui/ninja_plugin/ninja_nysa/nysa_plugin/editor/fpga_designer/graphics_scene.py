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

from visual_graph.graphics_scene import GraphicsScene as gs

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "gui"))

from graph_manager import SlaveType

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

view_state = enum(  "normal",
                    "arbitor_master_selected")


class GraphicsScene(QGraphicsScene):
    def __init__(self, view, fpga_designer):
        super(GraphicsScene, self).__init__()
        self.view = view
        #self.parent = parent
        self.fd = fpga_designer
        self.arbitor_selected = None
        self.state = view_state.normal
        self.links = []
        self.dbg = False
        if self.dbg: print "GS: Set state for normal"
        #self.setAcceptDrops(True)

    def get_view(self):
        if self.dbg: print "GS: get_view()"
        return self.view

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

    def get_state(self):
        if self.dbg: print "GS: get_state()"
        return self.state

    def fit_view(self):
        self.fd.fit_view()

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

    def constraint_item_selected(self, module_name=None):
        if self.dbg: print "GS: constraint item clicked"
        self.fd.show_constraint_editor(module_name)



    
    #def mouseMoveEvent(self, event):
    #    if self.dbg: print "GS: mouse move event"
    #    super (GraphicsScene, self).mouseMoveEvent(event)
    #    for l in self.links:
    #        if l.is_center_track():
    #            l.auto_update_center()


    def mousePressEvent(self, event):
        if self.dbg: print "GS: mouse press event"
        super (GraphicsScene, self).mousePressEvent(event)
        #for l in self.links:
        #    if l.is_center_track():
        #        l.auto_update_center()

    def dropEvent(self, event):
        if self.dbg: print "GS: Drag Event"
        super (GraphicsScene, self).dropEvent(event)

    def startDrag(self, event):
        if self.dbg: print "GS: Drag start event"


