# -*- coding: utf-8 *-*
import os
import sys
#import zipfile

from PyQt4.QtGui import QMenu
#from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QProcess

#from ninja_ide import resources
#from ninja_ide.tools import json_manager

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

#from ninja_nysa.misc.nysa_status import NysaStatus

class Menu(QMenu):
  output = None
  def __init__(self, locator, output):
    QMenu.__init__(self, 'Nysa')
    self.output = output
    self._proc = QProcess(self)
    action_test = self.addAction('Test Menu Item')
    self.connect(action_test, SIGNAL("triggered()"), self.test_action)

  def test_action(self):
    self.output.Debug(self, "Menu item selected")

