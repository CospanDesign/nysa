# -*- coding: utf-8 *-*

import os
import sys
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4 import QtCore
from PyQt4.QtGui import *

from ninja_ide.gui.main_panel import itab_item

#from graph_utils import Box

from box import Box
from box_list import BoxList
from graphics_view import GraphicsView

PERIPHERAL_COLOR = "blue"
MEMORY_COLOR = "purple"

NO_SLAVE_SEL = "No Slave Selected"

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
import controller as model_controller

#print "utils.get_nysa_base: %s" % utils.get_nysa_base()

import drt


class FPGADesigner(QWidget, itab_item.ITabItem):
  output = None

  def __init__(self, actions, parent=None, output=None):
    QWidget.__init__(self, parent)
    itab_item.ITabItem.__init__(self)

    self.actions = actions
    self.view = GraphicsView(self)
    self.scene = QGraphicsScene()
    self.view.setScene(self.scene)
    self.view.set_add_box(self.addBox)
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
    self.bus = "wishbone"
    self.mc = model_controller.Controller()

    self.output = output
    #self.output.Debug(self, "Hello")

  #def set_config_file(self, config_file):
    #self.mc.load_config_file(config_file)
    #self.mc.initialize_graph(self)

  def create_parameter_table(self):
    pt = QWidget(self)
    self.sel_slave_name = QLabel(NO_SLAVE_SEL)
    layout = QVBoxLayout()
    layout.addWidget(self.sel_slave_name)
    self.param_table = QTableWidget()
    self.param_table.setColumnCount(2)
    self.param_table.setRowCount(1)
    self.param_table.setHorizontalHeaderLabels(["Name", "Value"])
    layout.addWidget(self.param_table)
    pt.setLayout(layout)

    self.user_dirs = []

    return pt

  def add_user_dir(self, user_dir):
    self.user_dirs.append(user_dir)

  def populate_param_table(self, module_tags):
    #print "Populating Parameter Table"
    #print "Module tags: %s" % str(module_tags)
    self.sel_slave_name.setText(module_tags["module"])
    if "parameters" in module_tags:
      pcnt = len(module_tags["parameters"])
      keys = module_tags["parameters"].keys()
      self.param_table.setRowCount(pcnt)
      for i in range(len(keys)):
        name = keys[i]
        value = module_tags["parameters"][name]
        self.param_table.setCellWidget(i, 0, QLabel(keys[i]))
        self.param_table.setCellWidget(i, 1, QLabel(value))
      
  def clear_param_table(self):
    self.sel_slave_name.setText(NO_SLAVE_SEL)
    self.param_table.clear()
    self.param_table.setRowCount(0)

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
    

  def initialize_peripheral_list(self, d = {}):
    self.peripheral_list.add_items(d)

  def initialize_memory_list(self, d = {}):
    self.memory_list.add_items(d)

  def set_output(self, output):
    self.output = output

  def set_bus_type(bus = "wishbone"):
    self.bus = bus

  def initialize_slave_lists(self, user_paths = []):
    slave_list = utils.get_slave_list( bus = self.bus, 
                                        user_cbuilder_paths = user_paths)
    peripheral_dict = {}
    memory_dict = {}

    for slave in slave_list:
      tags = utils.get_module_tags(filename = slave, keywords=["DRT_FLAGS"], bus = self.bus)
      #print "Tags: %s" % str(tags)
      flag = int(tags["keywords"]["DRT_FLAGS"])
      if drt.is_memory_core(flag):
        memory_dict[tags["module"]] = tags
      else:
        peripheral_dict[tags["module"]] = tags

    self.initialize_peripheral_list(peripheral_dict)
    self.initialize_memory_list(memory_dict)


