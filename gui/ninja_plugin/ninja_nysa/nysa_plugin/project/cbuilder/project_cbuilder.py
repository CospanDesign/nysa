# -*- coding: utf-8 *-*

import os
import sys
import json

from PyQt4.QtGui import QMessageBox
#from PyQt4.QtCore import Qt

#from ninja_ide.core import plugin
from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager
from ninja_ide.tools import json_manager

from .menu import Menu
from .wizard import PagePluginProperties
from .wizard import CoreCustomize

PROJECT_TYPE = "Verilog Core Builder"

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


class ProjectCbuilder(plugin_interfaces.IProjectTypeHandler):

    EXT = 'cbldr'
    output = None
    path = None

    def __init__(self, output=None, locator=None):
        self.locator = locator
        self.output = output

        self.wspath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
          os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, 
          "cbuilder", "templates", "wishbone", "slave"))

        self.whipath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
          os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, 
          "cbuilder", "templates", "wishbone", "host_interface"))

        self.aspath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
          os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, 
          "cbuilder", "templates", "axi", "slave"))

        self.ahipath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
          os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, os.pardir, 
          "cbuilder", "templates", "axi", "host_interface"))

        self.output.Debug(self, "Dir: %s" % self.wspath)

    def get_context_menus(self):
        return (Menu(self.locator, self.output), )

    def get_pages(self):
        pages = []
        ppp = PagePluginProperties(self.locator, self.output)
        cc = CoreCustomize(self.locator, self.output)
        ppp.set_slave_type_func(cc.set_slave_type)
        pages.append(ppp)
        pages.append(cc)
        return pages

    def on_wizard_finish(self, wizard):
        global PROJECT_TYPE
        ids = wizard.pageIds()
        page = wizard.page(ids[3])
        self.path = str(page.txtPlace.text())
        if not self.path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be created"))
            return
        name = str(page.txtName.text())
        project = {}
        project['name'] = str(name)
        project['project-type'] = str(PROJECT_TYPE)
        project['description'] = str(page.txtDescription.toPlainText())
        project['license'] = str(page.cboLicense.currentText())
        project['venv'] = str(page.vtxtPlace.text())

        self.path = os.path.join(self.path, name)
        self.output.Info(self, "Creating directory: %s" % self.path)
        file_manager.create_folder(self.path, add_init_file=False)
        #Create the Ninja interface
        json_manager.create_ninja_project(self.path, name, project)

        page = wizard.page(ids[1])
        #plugin_dict = self.create_descriptor(page, self.path)
        self.plugin_dict = self.create_descriptor(page, self.path)
        #self.create_plugin_class(page, self.path, plugin_dict)
        wizard._load_project(self.path)

    def create_core_builder(self):
        self.output.Info("Creating folder structure for new core")
        rtl = os.path.join(self.path, "rtl")
        sim = os.path.join(rtl, "sim")
         
        file_manager.create_folder(rtl, add_init_file=False)
        file_manager.create_folder(sim, add_init_file=False)

    def create_descriptor(self, page, path):
        plugin = {}

        core_name = str(page.txtCore.text())
        plugin['core'] = core_name
        authors = str(page.txtAuthors.text())
        plugin['authors'] = authors
        version = str(page.txtVersion.text())
        plugin['version'] = version

        fileName = os.path.join(path, core_name + "." + self.EXT)
        # Create the .plugin file with metadata
        self.create_file(fileName, plugin)
        # Return the dictionary
        return plugin

    def create_file(self, fileName, structure):
        self.output.Info(self, "Creating file: %s" % fileName)
        f = open(fileName, mode='w')
        json.dump(structure, f, indent=2)
        f.close()
