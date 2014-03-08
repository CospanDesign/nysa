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


class PeripheralSlaveProperties(QWidget):

    def __init__(self):
        super (PeripheralSlaveProperties, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()

        self.layout = QFormLayout(self)
        self.slave_name = QLabel("")

        self.script_list = QListWidget()
        self.script_list.addItem("Hello")

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Module Type"), QLabel("Peripheral Slave"))
        self.layout.addRow(QLabel("Name"), self.slave_name)
        self.layout.addRow(QLabel("Scripts"), self.script_list)
        self.hide()


    def set_slave(self, name, config_dict, n):
        self.slave_name.setText(name)
        self.config_dict = config_dict
        self.nysa = n
        self.slave_name.setText(name)
        if name == "DRT":
            print "DRT Found!"
        #Setup the reset of the config dict

    def clear_scripts_list(self):
        for l in self.script_list.clear()
