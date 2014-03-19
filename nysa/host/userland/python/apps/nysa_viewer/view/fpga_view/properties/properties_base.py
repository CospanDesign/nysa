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
        self.actions = actions

    def initialize_default_form_view(self):
        self.layout = QFormLayout(self)
        self.name = QLabel("")

        self.info_text = QLabel("")
        self.info_text.setWordWrap(True)
        self.script_list = None
        self._scripts = []

        self.setLayout(self.layout)
        self.layout.addRow(QLabel("Name"), self.name)
        self.layout.addRow(QLabel("Info"), self.info_text)
        self.hide()
        

    def set_name(self, name):
        self.name.setText(name)

    def set_info(self, info):
        self.info_text.setText(info)

    def set_scripts_list(self, scripts):
        self._scripts = []
        #print "Scripts: %s" % scripts
        self._scripts = scripts
        for s in self._scripts:
            self.script_list.addItem(s)
        
    def initialize_script_list(self):
        self.script_list = QListWidget()
        self.script_list.doubleClicked.connect(self.script_item_double_clicked)
        return self.script_list

    def clear_scripts_list(self):
        self._scripts = []
        if self.script_list is not None:
            self.script_list.clear()


    def script_item_double_clicked(self, item):
        name = str(item.data(Qt.DisplayRole).toString())
        item_name = self.name.text()
        self.actions.script_item_selected.emit(str(item_name),
                                               self._scripts[name])

