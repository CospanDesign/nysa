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


from PyQt4.QtCore import *
from PyQt4.QtGui import *


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
        print "GS: Set state for normal"
        self.links = []

    def set_link_ref(self, lref):
        self.links.append(lref)

    def set_master(self, master):
        self.master = master

    def set_peripheral_bus(self, peripheral_bus):
        self.peripheral_bus = peripheral_bus

    def set_memory_bus(self, memory_bus):
        self.memory_bus = memory_bus

    def get_view(self):
        return self.view

    def box_selected(self, data):
        if type(data) is dict and "module" in data.keys():
            self.fd.populate_param_table(data)

    def box_deselected(self, data):
        if type(data) is dict and "module" in data.keys():
            self.fd.clear_param_table()

    def slave_selected(self, name, bus, tags):
        print "GS: Slave: %s" % tags["module"]
        if self.arbitor_selected is None:
            print "GS: Arbitor master is not selected"
            self.state = view_state.normal
            print "GS: Set state for normal"
            return

        print "GS: Arbitor master is selected: %s" % self.arbitor_selected.box_name

        if  name == "DRT":
            print "GS: Can't attach to the DRT"
            return

        if self.arbitor_selected.get_slave().box_name == name:
            print "GS: Can't attach to ourselves"
            #self.arbitor_master_deselected(tags, self.arbitor_selected)
            #self.state = view_state.normal
            return

        from_slave = self.arbitor_selected.get_slave()
        arbitor_name = self.arbitor_selected.box_name
        to_slave = bus.get_slave(name)
        
        if self.arbitor_selected.get_connected_slave() is not None:
            connected_slave = self.arbitor_selected.get_connected_slave()
            self.arbitor_master_disconnect(self.arbitor_selected, connected_slave)

        self.fd.connect_arbitor_master(from_slave, arbitor_name, to_slave)
        self.arbitor_selected.set_activate(True)
        self.arbitor_selected.connect_slave(to_slave)

    def get_state(self):
        return self.state

    def slave_deselected(self, name, bus, tags):
        #print "GS: Slave deselected: %s" % tags["module"]

        pass

    def arbitor_master_selected(self, slave, arbitor_master):
        print "GS: arbitor master selected"
        name = arbitor_master.box_name
        self.state = view_state.arbitor_master_selected
        print "GS: Set state for arbitor master"
        self.arbitor_selected = arbitor_master
        self.peripheral_bus.enable_expand_slaves(name, True)
        self.memory_bus.enable_expand_slaves(name, True)
        slave.arbitor_master_selected(name)

    def arbitor_master_deselected(self, slave_tags, arbitor_master):
        print "GS: arbitor master deselected"
        name = arbitor_master.box_name
        self.state = view_state.normal
        print "GS: Set state for normal"
        self.peripheral_bus.enable_expand_slaves(name, False)
        self.memory_bus.enable_expand_slaves(name, False)
        self.arbitor_selected = None
        slave = arbitor_master.get_slave()
        slave.remove_arbitor_masters()
        slave.show_arbitor_masters()
        for i in range (len(self.links)):
            self.removeItem(self.links[i])

        self.links = []


    def arbitor_master_fake_selected(self, slave, arbitor_master):
        print "GS: arbitor master selected selected"
        self.arbitor_selected = arbitor_master

    def is_arbitor_master_selected(self):
        return self.arbitor_selected is not None

    def arbitor_master_disconnect(self, arbitor_master, to_slave):
        from_slave = arbitor_master.get_slave()
        arbitor_name = arbitor_master.box_name

        #XXX: Remove the arbitor connctor
        self.fd.disconnect_arbitor_master(from_slave, arbitor_name, to_slave)
        arbitor_master.disconnect_slave()

    def fit_view(self):
        self.fd.fit_view()


    def remove_selected(self, reference):
        print "GS: User removed"



