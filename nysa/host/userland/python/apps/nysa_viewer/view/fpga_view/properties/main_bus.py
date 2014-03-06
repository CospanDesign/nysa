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


class MainBusProperties(QWidget):

    def __init__(self):
        #super (MainBusProperties, self).__init__(parent)
        super (MainBusProperties, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()

        self.layout = QFormLayout(self)
        self.name_label = QLabel("")

        self.info_text = QLabel("")
        self.info_text.setText("Select a module block")
        self.info_text.setWordWrap(True)

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Name"), self.name_label)
        self.layout.addRow(QLabel("Info"), self.info_text)
        self.hide()


    def set_config_dict(self, config_dict):
        self.config_dict = config_dict
        #Setup the reset of the config dict
        self.name_label.setText(config_dict["board"])
