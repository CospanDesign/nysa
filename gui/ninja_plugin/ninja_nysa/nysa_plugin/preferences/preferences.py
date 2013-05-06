# -*- coding: utf-8 *-*
import os

from ninja_ide.core import plugin_interfaces
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit


class NysaPreferences(QWidget, plugin_interfaces.IPluginPreferences):

    pdict = {}
  
    def __init__(self, locator, output):
        QWidget.__init__(self)
        self.locator = locator
        self.output = output
        self.output.Debug(self, "Creating preference widget")
        self.pdict = {}
        self.load_default()
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('Preference')
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Core Builder Base Directory:'), 0, 0)
        self.txtCBuilderLocation = QLineEdit(self.pdict["CBuilder_location"])
        grid.addWidget(self.txtCBuilderLocation, 0, 1)
        grid.addWidget(QLabel("Xilinx Base Directory"), 1, 0)
        self.txtXilinxLocation = QLineEdit(self.pdict["Xilinx_location"])
        grid.addWidget(self.txtXilinxLocation, 1, 1)


    def get_preference_dict(self):
        return self.pdict
    
    def save(self):
        self.output.Debug(self, "Preferences save")

    def load_default(self):
        user_dir = os.path.expanduser("~")
        self.pdict["CBuilder_location"] = os.path.join(user_dir,
          "/Projects/cbuilder_projects")
        self.pdict["Xilinx_location"] = os.path.join("?")

