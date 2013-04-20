# -*- coding: utf-8 *-*
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit


class NysaPreferences(QWidget):

    pdict = {}
  
    def __init__(self, locator, output):
        QWidget.__init__(self)
        self.locator = locator
        self.output = output
        self.output.Debug(self, "Creating preference widget")
        pdict = {}
        user_dir = os.path.expanduser("~")
        pdict["CBuilder_location"] = os.path.join(user_dir,
          "/Projects/cbuilder_projects")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Preference')
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Core Builder Base Directory:'), 0, 0)
        self.txtCBuilderLocation = QLineEdit(pdict["CBuilder_location"])
        grid.addWidget(self.txtCBuilderLocation, 1, 0)

    def get_preference_dict(self):
      return self.pdict
    
