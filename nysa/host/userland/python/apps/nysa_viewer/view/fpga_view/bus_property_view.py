import sys
import os
import time

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

import status
import actions


class BusPropertyView(QWidget):

    def __init__(self, parent):
        super(BusPropertyView, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()
        self.setMaximumWidth(300)

        self.layout = QFormLayout(self)
        #self.layout.RowWrapPolicy(QFormLayout.WrapAllRows)
        #self.layout.FieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.setLayout(self.layout)


        self.info_text = QLabel("Info!")
        sp = QSizePolicy()
        self.info_text.setSizePolicy(sp)
        self.info_text.setWordWrap(True)

        self.setup_nothing_selected()
        self.actions.module_selected.connect(self.module_selected)
        self.actions.module_deselected.connect(self.module_deselected)

        self.actions.slave_selected.connect(self.slave_selected)
        self.actions.slave_deselected.connect(self.slave_deselected)

    def setup_nothing_selected(self):
        self.clear_layout()
        self.layout.addRow(QLabel("Nothing selected"),
                           self.info_text.setText("Select a platform in the platform tree"))
        self.config_dict = {}

    def setup_bus(self, config_dict):
        #Populate the view for an entire bus
        self.clear_layout()
        self.config_dict = config_dict


        nlabel = QLabel("Name")
        name_label = QLabel("Nothing")
        ilabel = QLabel("Info")
        info_text = QLabel("Info!")
        sp = QSizePolicy()
        info_text.setSizePolicy(sp)
        info_text.setWordWrap(True)


        name_label.setText(config_dict["board"])

        #Setup the Grid
        self.layout.addRow(nlabel, name_label)
        info_text.setText("Select a module block")
        self.layout.addRow(ilabel, info_text)
        #print "config dict: %s" % str(config_dict)

    def setup_host_interface(self):
        self.clear_layout()
        nlabel = QLabel("Name")
        name_label = QLabel("Host Interface")
        dlabel = QLabel("Description")
        desc_text = QTextEdit("Nothing")
        desc_text.setReadOnly(True)
        ilabel = QLabel("Info")
        info_text = QLabel("Info!")
        sp = QSizePolicy()
        info_text.setSizePolicy(sp)
        info_text.setWordWrap(True)



        #Setup the Grid
        self.layout.addRow(nlabel, name_label)

    def setup_master(self):
        #Populate the view for the master selected
        self.clear_layout()
        nlabel = QLabel("Name")
        name_label = QLabel("Master")



        self.layout.addRow(nlabel, name_label)

    def setup_peripheral_bus(self):
        self.clear_layout()
        nlabel = QLabel("Name")
        name_label = QLabel("Peripheral Bus")



        self.layout.addRow(nlabel, name_label)

    def setup_memory_bus(self):
        self.clear_layout()
        nlabel = QLabel("Name")
        name_label = QLabel("Memory Bus")



        self.layout.addRow(nlabel, name_label)

    def setup_peripheral_slave(self, slave_dict, name):
        self.clear_layout()
        nlabel = QLabel("Peripheral Slave")
        name_label = QLabel(name)



        self.layout.addRow(nlabel, name_label)

    def setup_memory_slave(self, slave_dict, name):
        self.clear_layout()
        nlabel = QLabel("Memory Slave")
        name_label = QLabel(name)
        self.layout.addRow(nlabel, name_label)

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
        self.setup_bus(self.config_dict)

    def slave_selected(self, name, bus, config_dict):
        if bus == "Peripherals":
            self.setup_peripheral_slave(config_dict, name)
        if bus == "Memory":
            self.setup_memory_slave(config_dict, name)

    def slave_deselected(self, name, bus, config_dict):
        print "Slave: %s deselected" % name
        self.setup_bus(self.config_dict)

    def device_selected(self, device_type, nysa):
        print "device: selected: %s" % device_type
        self.setup_bus(self.config_dict)


    def clear_layout(self):
        while self.layout.count():

            child = self.layout.takeAt(0)
            child.widget().deleteLater()
