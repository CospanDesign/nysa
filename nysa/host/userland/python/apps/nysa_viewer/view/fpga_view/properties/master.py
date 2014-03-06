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

class MasterProperties(PropertiesBase):

    def __init__(self):
        super (MasterProperties, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()

        self.features_text = QLabel("2 Bus Controllers\n\n"
                                    "Single or Burst Reads/Writes\n\n"
                                    "Configuration Address Control\n\n"
                                    "Core Dump")
        self.features_text.setWordWrap(True)

        self.set_name("Master")
        self.set_info("Reads/Writes Data to and from the cores and the host")

        self.layout.addRow(QLabel("Features"), self.features_text)


    def set_config_dict(self, config_dict):
        self.config_dict = config_dict
        #Setup the reset of the config dict
