# -*- coding: utf-8 -*-
import os
import sys
#import zipfile

from PyQt4.QtGui import QMenu
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QProcess

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir))
import nysa_actions



sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

class Menu(QMenu):
  output = None
  def __init__(self, locator, output):
    QMenu.__init__(self, 'Nysa')
    self.output = output
    self._proc = QProcess(self)
    self.explorer = locator.get_service('explorer')
    self.nactions = nysa_actions.NysaActions()
    action_ib_properties = self.addAction('IBuilder Properties')
    self.connect(action_ib_properties, SIGNAL("triggered()"), self.ib_properties)

  def ib_properties(self):
    p_path = self.explorer.get_tree_projects()._get_project_root().path
    self.output.Debug(self, "Menu item selected")
    self.nactions.ibuilder_properties_triggered(p_path)


