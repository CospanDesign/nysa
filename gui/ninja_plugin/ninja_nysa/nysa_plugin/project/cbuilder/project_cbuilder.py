# -*- coding: utf-8 *-*

import os
import sys
#try:
#  import json
#except ImportError:
#  import simplejson as json

from PyQt4.QtGui import QMessageBox
#from PyQt4.QtCore import Qt

#from ninja_ide.core import plugin
from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager
from ninja_ide.tools import json_manager

from menu import Menu
from wizard import PagePluginProperties

PROJECT_TYPE = "Verilog Core Builder"

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


class ProjectCbuilder(plugin_interfaces.IProjectTypeHandler):

  EXT = 'cbldr'
  output = None

  def __init__(self, output = None, locator = None):
      self.locator = locator
      self.output = output

  def get_context_menus(self):
    return (Menu(self.locator, self.output), )

  def get_pages(self):
    return [PagePluginProperties(self.locator)]

  def on_wizard_finish(self, wizard):
    global PROJECT_TYPE
    ids = wizard.pageIds()
    self.output.Debug(self, "ids: %s" % str(ids))
    page = wizard.page(ids[2])
    path = unicode(page.txtPlace.text())
    if not path:
      QMessageBox.critical(self, self.tr("Incorrect Location"),
        self.tr("The project couldn\'t be created"))
      return
    name = unicode(page.txtName.text())
    project = {}
    project['name'] = name
    project['project-type'] = PROJECT_TYPE
    project['description'] = unicode(page.txtDescription.toPlainText())
    project['license'] = unicode(page.cboLicense.currentText())
    project['venv'] = unicode(page.vtxtPlace.text())



    path = os.path.join(path, name)

    file_manager.create_folder(path, add_init_file=False)
    json_manager.create_ninja_project(path, name, project)

    plugin_dict = self.create_descriptor(page, path)
    self.create_plugin_class(page, path, plugin_dict)
    wizard._load_project(path)



  def create_descriptor(self, page, path):
    plugin = {}

    #module = unicode(page.txtModule.text())
    #plugin['module'] = module
    #className = str(page.txtClass.text())
    #plugin['class'] = className
    authors = unicode(page.txtAuthors.text())
    plugin['authors'] = authors
    url = unicode(page.txtUrl.text())
    plugin['url'] = url
    version = unicode(page.txtVersion.text())
    plugin['version'] = version

    fileName = os.path.join(path, module + self.EXT)
    # Create the .plugin file with metadata
    self.create_file(fileName, plugin)
    # Return the dictionary
    return plugin


