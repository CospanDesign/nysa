# -*- coding: utf-8 *-*

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
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.editor.editor import Editor

#from graph_utils import Box

from box import Box
from box_list import BoxList
from graphics_view import GraphicsView
from graphics_scene import GraphicsScene
#from view_controller.wishbone_controller import WishboneController
#from view_controller.axi_controller import AxiController


from errors import FPGADesignerError
from peripheral_bus import *
from memory_bus import *

from defines import PERIPHERAL_COLOR
from defines import MEMORY_COLOR

NO_MODULE_SEL = "No Slave Selected"

sys.path.append(os.path.join( os.path.dirname(__file__),
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
                              "ibuilder",
                              "gui"))

from graph_manager import SlaveType

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "drt"))



import utils
import drt


class FPGADesigner(QWidget, itab_item.ITabItem):
#class FPGADesigner(Editor):
    output = None

    def __init__(self, actions, filename, project, parent=None, output=None):
        QWidget.__init__(self, parent)
        itab_item.ITabItem.__init__(self)
        #super(FPGADesigner, self).__init__(filename, project, project_obj=None)

        self.actions = actions
        self.ID = filename
        self.lang = "fpga designer"
        self.view = GraphicsView(self)
        self.view.set_fpga_designer(self)
        self.scene = GraphicsScene(self.view, self)
        self.view.setScene(self.scene)
        self.prevPoint = QPoint()

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.view)
        self.main_splitter.setStretchFactor(0, 1)
        #self.setCenterWidget(self.main_splitter)
        layout = QHBoxLayout()
        layout.addWidget(self.main_splitter)
        self.setLayout(layout)

        #Need to windows for both the peripheral and memory slaves
        self.slave_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(self.slave_splitter)
        self.slave_splitter.setStretchFactor(0, 1)

        self.peripheral_list = BoxList(parent = None, color = PERIPHERAL_COLOR)
        self.memory_list = BoxList(parent = None, color = MEMORY_COLOR)

        self.slave_splitter.addWidget(self.peripheral_list)
        self.slave_splitter.addWidget(self.memory_list)

        #Add Parameter windows
        pt = self.create_parameter_table()
        self.slave_splitter.addWidget(pt)

        #My variables

        self.output = output
        self.output.Debug(self, "Initialized")

        self.vc = None
        #self.setup_controller()

    def set_controller(self, controller):
        #d = {}
        #try:
        #    f = open(self.ID, "r")
        #    d = json.loads(f.read())
        #except IOError, err:
        #    raise FPGADesignerError("IOError: %s" % str(err))

        #except TypeError, err:
        #    raise FPGADesignerError("JSON Type Error: %s" % str(err))

        ##A Pathetic factory pattern, select the controller based on the bus
        #if d["TEMPLATE"] == "wishbone_template.json":
        #    self.vc = WishboneController(self, self.view, self.output, config_dict = d)
        #elif d["TEMPLATE"] == "axi_template.json":
        #    self.vc = AxiController(self, self.view, self.output)
        #else:
        #    raise FPGADesignerError(    "Bus type (%s) not recognized, view " +
        #                                "controller cannot be setup, set the " +
        #                                "TEMPLATE value to either " +
        #                                "wishbone_template or " +
        #                                "axi_tmeplate.json" % str(d["TEMPLATE"])
        #                           )
        self.vc = controller
        self.vc.set_fpga_designer(self)
        self.vc.set_canvas(self.view)
        self.view.set_controller(self.vc)

    def get_controller(self):
        return self.vc

    def is_controller_defined(self):
        return self.vc is not None

    def get_type_index_from_slave(self, slave):
        typ = None
        index = None
        if slave is None:
            raise FPGADesignerError("Cannot get type or index from None!")

        if type(slave.bus) is PeripheralBus:
            print "\t%s: Peripheral Bus" % slave.box_name
            typ = SlaveType.PERIPHERAL
        elif type(slave.bus) is MemoryBus:
            print "\t%s: Memory Bus" % slave.box_name
            typ = SlaveType.MEMORY

        index = slave.bus.get_slave_index(slave.box_name)
        return typ, index


    def connect_arbitor_master(self, from_slave, arbitor_name, to_slave):
        from_type = None
        from_index = 0

        to_type = None
        to_index = 0
        from_type, from_index = self.get_type_index_from_slave(from_slave)
        to_type, to_index = self.get_type_index_from_slave(to_slave)

        print "FD: Connect: %s - %s - %s" % (from_slave.box_name, arbitor_name, to_slave.box_name)
        self.vc.connect_arbitor_master(from_type,
                                       from_index,
                                       arbitor_name,
                                       to_type,
                                       to_index)

    def disconnect_arbitor_master(self, from_slave, arbitor_name, to_slave):
        from_type = None
        from_index = 0

        to_type = None
        to_index = 0

        from_type, from_index = self.get_type_index_from_slave(from_slave)
        to_type, to_index = self.get_type_index_from_slave(to_slave)

        self.vc.disconnect_arbitor_master(  from_type, 
                                            from_index,
                                            arbitor_name,
                                            to_type,
                                            to_index)

        print "FD: Disconnect: %s - %s - %s" % (from_slave.box_name, arbitor_name, to_slave.box_name)
        self.output.Info(self, "Disconnect Arbitor master: %s from slave: %s" % (arbitor_name, to_slave.box_name))


    def get_arbitor_master_connected(self, from_slave, arbitor_name):
        typ = None
        index = None

        typ, index = self.get_type_index_from_slave(from_slave)
        return self.vc.get_arbitor_master_connected(typ, index, arbitor_name)

    def set_config_file(self, config_file):
        self.vc.set_config_file(config_file)

    def set_default_board_project(self, board_name):
        self.vc.set_default_board_project(board_name)

    def create_parameter_table(self):
        pt = QWidget(self)
        self.sel_slave_name = QLabel(NO_MODULE_SEL)
        layout = QVBoxLayout()
        layout.addWidget(self.sel_slave_name)
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(2)
        self.param_table.setRowCount(1)
        self.param_table.setHorizontalHeaderLabels(["Name", "Value"])
        self.param_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.param_table)
        pt.setLayout(layout)

        self.user_dirs = []

        return pt

    def add_user_dir(self, user_dir):
        self.user_dirs.append(user_dir)

    def populate_param_table(self, tags):
        #print "Populating Parameter Table"
        #print "Module tags: %s" % str(tags)
        self.sel_slave_name.setText(tags["module"])
        if "parameters" in tags:
            pcnt = len(tags["parameters"])
            keys = tags["parameters"].keys()
            self.param_table.setRowCount(pcnt)
            for i in range(len(keys)):
                name = keys[i]
                value = tags["parameters"][name]
                self.param_table.setCellWidget(i, 0, QLabel(keys[i]))
                self.param_table.setCellWidget(i, 1, QLabel(value))

    def clear_param_table(self):
        self.sel_slave_name.setText(NO_MODULE_SEL)
        self.param_table.clear()
        self.param_table.setRowCount(0)
        self.param_table.setHorizontalHeaderLabels(["Name", "Value"])

    def addBox(self, name, color = "black"):
        fn = utils.find_module_filename(name, self.user_dirs)
        fn = utils.find_rtl_file_location(fn, self.user_dirs)
        mt = utils.get_module_tags(fn)

        Box(  position = self.position(),
              scene = self.scene,
              name = name,
              select_func = self.populate_param_table,
              deselect_func = self.clear_param_table,
              color = color,
              user_data = mt)

    def position(self):
        point = self.mapFromGlobal(QCursor.pos())
        if not self.view.geometry().contains(point):
            coord = random.randint(10, 10)
            point = QPoint(coord, coord)
        else:
            if point == self.prevPoint:
                point += QPoint(self.addOffset, self.addOffset)
                self.addOffset += 5
            else:
                self.addOffset = 5
                self.prevPoint = point
        return self.view.mapToScene(point)

    def mousePressEvent(self, event):
        QWidget.mousePressEvent(self, event)

    def fileSaved(self, val):
        self.output.Debug(self, "Saving File")

    def initialize_peripheral_list(self, d = {}):
        self.peripheral_list.add_items(d, "peripheral_slave")

    def initialize_memory_list(self, d = {}):
        self.memory_list.add_items(d, "memory_slave")

    def set_output(self, output):
        self.output = output

    def initialize_slave_lists(self, user_paths = []):
        slave_list = utils.get_slave_list( bus = self.vc.get_bus(),
                                          user_cbuilder_paths = user_paths)
        peripheral_dict = {}
        memory_dict = {}

        for slave in slave_list:
            tags = utils.get_module_tags(   filename = slave,
                                            keywords=["DRT_FLAGS"],
                                            bus = self.vc.get_bus())
            #print "Tags: %s" % str(tags)
            flag = int(tags["keywords"]["DRT_FLAGS"])
            if drt.is_memory_core(flag):
                memory_dict[tags["module"]] = tags
            else:
                peripheral_dict[tags["module"]] = tags

        self.initialize_peripheral_list(peripheral_dict)
        self.initialize_memory_list(memory_dict)

    def drop_event(self, event):
        self.vc.drop_event(self.position(), event)

    def fit_view(self):
        self.view._scale_fit()

    def remove_slave(self, bus, index):
        self.output.Debug(self, "Removing slave from bus")
        self.vc.remove_slave(bus, index)

