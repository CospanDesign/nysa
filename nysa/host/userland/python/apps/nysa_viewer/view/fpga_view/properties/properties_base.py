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


class PropertiesBase(QWidget):

    def __init__(self):
        super (PropertiesBase, self).__init__()
        self.layout = QFormLayout(self)
        self.name = QLabel("")

        self.info_text = QLabel("")
        self.info_text.setWordWrap(True)

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Name"), self.name)
        self.layout.addRow(QLabel("Info"), self.info_text)
        self.hide()

    def set_name(self, name):
        self.name.setText(name)

    def set_info(self, info):
        self.info_text.setText(info)
