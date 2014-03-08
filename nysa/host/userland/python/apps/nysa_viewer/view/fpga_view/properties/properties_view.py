import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__),
             os.pardir,
             os.pardir,
             os.pardir)

import status
import actions

from nothing import NothingProperties
from main_bus import MainBusProperties
from host_interface import HostInterfaceProperties
from master import MasterProperties
from peripheral_bus import PeripheralBusProperties
from memory_bus import MemoryBusProperties
from peripheral_slave import PeripheralSlaveProperties
from memory_slave import MemorySlaveProperties

class PropertiesView(QWidget):

    def __init__(self, parent):
        super(PropertiesView, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()
        self.setMaximumWidth(300)

        self.layout = QVBoxLayout(self)
        #self.layout.RowWrapPolicy(QFormLayout.WrapAllRows)
        #self.layout.FieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.setLayout(self.layout)


        #self.info_text = QLabel("Info!")
        #sp = QSizePolicy()
        #self.info_text.setSizePolicy(sp)
        #self.info_text.setWordWrap(True)
        self.nothing_params = NothingProperties()
        self.host_interface_params = HostInterfaceProperties()
        self.main_bus_params = MainBusProperties()
        self.master_params = MasterProperties()
        self.peripheral_bus_params = PeripheralBusProperties()
        self.memory_bus_params = MemoryBusProperties()
        self.peripheral_slave_params = PeripheralSlaveProperties()
        self.memory_slave_params = MemorySlaveProperties()

        self.ps = []
        self.ps.append(self.nothing_params)
        self.ps.append(self.host_interface_params)
        self.ps.append(self.main_bus_params)
        self.ps.append(self.master_params)
        self.ps.append(self.peripheral_bus_params)
        self.ps.append(self.memory_bus_params)
        self.ps.append(self.peripheral_slave_params)
        self.ps.append(self.memory_slave_params)

        for p in self.ps:
            self.layout.addWidget(p)

        #Connect the Signals
        self.actions.module_selected.connect(self.module_selected)
        self.actions.module_deselected.connect(self.module_deselected)

        self.actions.slave_selected.connect(self.slave_selected)
        self.actions.slave_deselected.connect(self.slave_deselected)

        #Setup the initial view
        self.setup_nothing_selected()

    def setup_nothing_selected(self):
        self.clear_layout()
        self.nothing_params.show()
        self.config_dict = {}

    def setup_bus(self, config_dict, n):
        #Populate the view for an entire bus
        self.clear_layout()
        self.config_dict = config_dict
        self.nysa = n
        self.main_bus_params.set_config_dict(config_dict)
        self.main_bus_params.show()

    def setup_host_interface(self):
        self.clear_layout()
        self.host_interface_params.show()

    def setup_master(self):
        self.clear_layout()
        self.master_params.show()

    def setup_peripheral_bus(self):
        self.clear_layout()
        self.peripheral_bus_params.show()

    def setup_memory_bus(self):
        self.clear_layout()
        self.memory_bus_params.show()

    def setup_peripheral_slave(self, name):
        self.clear_layout()
        self.peripheral_slave_params.set_slave(name, self.config_dict, self.nysa)
        self.peripheral_slave_params.show()

    def setup_memory_slave(self, name):
        self.clear_layout()
        self.memory_slave_params.set_slave(name, self.config_dict, self.nysa)
        self.memory_slave_params.show()

    def module_selected(self, name):
        if name == "master":
            self.setup_master()

        if name == "host_interface":
            self.setup_host_interface()

        if name == "peripheral_bus":
            self.setup_peripheral_bus()

        if name == "memory_bus":
            self.setup_memory_bus()


    def module_deselected(self, name):
        print "Module: %s deselected" % name
        self.setup_bus(self.config_dict, self.nysa)

    def slave_selected(self, name, bus):
        if bus == "Peripherals":
            self.setup_peripheral_slave(name)
        if bus == "Memory":
            self.setup_memory_slave(name)

    def slave_deselected(self, name, bus, config_dict):
        print "Slave: %s deselected" % name
        self.setup_bus(self.config_dict, self.nysa)

    def device_selected(self, device_type, nysa):
        print "device: selected: %s" % device_type
        self.setup_bus(self.config_dict, self.nysa)


    def clear_layout(self):
        for p in self.ps:
            p.hide()

