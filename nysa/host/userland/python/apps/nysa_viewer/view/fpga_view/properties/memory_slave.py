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


from properties_base import PropertiesBase

class MemorySlaveProperties(PropertiesBase):

    def __init__(self):
        super (MemorySlaveProperties, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()

        self.layout = QFormLayout(self)
        self.slave_name = QLabel("")

        self.initialize_script_list()

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Module Type"), QLabel("Memory Slave"))
        self.layout.addRow(QLabel("Name"), self.slave_name)
        self.layout.addRow(QLabel("Scripts"), self.script_list)
        self.hide()


    def set_slave(self, name, config_dict, n, scripts):
        self.slave_name.setText(name)
        self.clear_scripts_list()
        self.set_scripts_list(scripts)
        self.config_dict = config_dict
        self.nysa = n
        self.slave_name.setText(name)
        #Setup the reset of the config dict
