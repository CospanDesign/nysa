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

class NothingProperties(PropertiesBase):

    def __init__(self):
        #super (NothingProperties, self).__init__(parent)
        super (NothingProperties, self).__init__()
        self.actions = actions.Actions()
        self.status = status.Status()

        self.layout = QFormLayout(self)

        self.ilabel = QLabel("Info")
        self.info_text = QLabel("Nothing Selected, Choose a device in the Platform Tree")
        self.info_text.setWordWrap(True)

        self.setLayout(self.layout)
        self.layout.addRow(self.ilabel, self.info_text)
        self.hide()

