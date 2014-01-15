# -*- coding: utf-8 *-*

import os
import sys
import json

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMessageBox
#from PyQt4.QtCore import Qt

#from ninja_ide.core import plugin
from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager


from ninja_ide.tools import json_manager

from menu import Menu

from wizard import PagePluginProperties
from wizard import SLAVE_TYPE
from wizard import CoreCustomize

from cbuilder import CBUILDER_EXT
from cbuilder import PROJECT_TYPE



sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "scripts"))

from cbuilder_factory import CBuilderFactory



class ProjectCbuilder(plugin_interfaces.IProjectTypeHandler, QObject):

    output = None
    path = None

    def __init__(self, output=None, locator=None):
        self.locator = locator
        self.output = output
        self.explorer_s = self.locator.get_service('explorer')
        self.output.Debug(self, "Cbuilder Project instantiated")

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
        ids = wizard.pageIds()
        main_core_page = wizard.page(ids[1])
        core_prop_page = wizard.page(ids[2])
        ninja_page = wizard.page(ids[3])
        cb_dict = {}

        self.path = str(ninja_page.txtPlace.text())
        if not self.path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be created"))
            return

        cb_dict["name"] = str(main_core_page.txtCore.text())

        name = str(ninja_page.txtName.text())
        project = {}
        project['name'] = str(name)
        project['project-type'] = str(PROJECT_TYPE)
        project['description'] = str(ninja_page.txtDescription.toPlainText())
        #project['url'] = 'hello'
        project['license'] = str(ninja_page.cboLicense.currentText())
        #project['venv'] = str(ninja_page.vtxtPlace.text())
        project["supported-extensions"] = ['.py', '.json', '', '.txt', '.v']
        project["mainFile"] = cb_dict["name"] + ".v"
        #project['preExecScript'] = ''
        #project['postExecScript'] = ''
        #project['identation'] = ''
        #project['use-tabs'] = ''
        #project['additional_builtins'] = []
        #project['programParams'] = self.project_execute
        #project['relatedProjects'] = []


        self.path = os.path.join(self.path, name)
        print "Creating Directory: %s" % self.path
        self.output.Info(self, "Creating directory: %s" % self.path)
        file_manager.create_folder(self.path, add_init_file=False)
        #Create the Ninja interface
        json_manager.create_ninja_project(self.path, name, project)

        #plugin_dict = self.create_descriptor(page, self.path)
        self.output.Debug(self, "Creating Directory")
        self.plugin_dict = self.create_descriptor(main_core_page, self.path)


        self.output.Info(self, "Path: %s" % self.path)

        #Create a dictionary to be fed into the cbuilder script

        cb_dict["drt_id"] = 1
        cb_dict["drt_flags"] = 1
        cb_dict["drt_size"] = 3

        cb_dict["bus_type"] = "slave"

        cb_dict["type"] = "wishbone"
        if main_core_page.axi_radio.isChecked():
          cb_dict["type"] = "axi"

        cb_dict["subtype"] = "peripheral"
        if main_core_page.memory_radio.isChecked():
          cb_dict["subtype"] = "memory"

        cb_dict["base"] = self.path
        self.output.Debug(self, "Creating Core Project directory")
        self.create_core_builder(cb_dict)
        self.output.Debug(self, "Created Core Project directory")

        #self.create_plugin_class(page, self.path, plugin_dict)
        wizard._load_project(self.path)

    def create_core_builder(self, cb_dict):
        self.output.Info(self, "Creating folder structure for new core")
        CBuilderFactory(cb_dict)

    def create_descriptor(self, page, path):
        plugin = {}

        core_name = str(page.txtCore.text())
        plugin['core'] = core_name
        authors = str(page.txtAuthors.text())
        plugin['authors'] = authors
        version = str(page.txtVersion.text())
        plugin['version'] = version

        fileName = os.path.join(path, core_name + "." + CBUILDER_EXT)
        # Create the .plugin file with metadata
        self.create_file(fileName, plugin)
        # Return the dictionary
        return plugin

    def create_file(self, fileName, structure):
        self.output.Info(self, "Creating file: %s" % fileName)
        f = open(fileName, mode='w')
        json.dump(structure, f, indent=2)
        f.close()

    def fix_wizard_output_place(self):
        #XXX: This is a hack but I need to set the project page
        #XXX: To a default directory
        print "wizard members: %s" % str(getattr(self.wizard, "method"))
        page_ids = self.wizard.pageIds()
        page = None
        for pgid in range(0, page_ids):
          page = self.wizard.page(pgid)
          if 'txtPlace' in getattr(page.txtPlace, '*'):
            self.output.Debug(self, "Found the last page!")
            break
          else:
            page = None

        if page is None:
          self.output.Debug(self, "Didn't find the last page")
          return

        page.txtPlace.setText("Does this work?")


    def project_execute(self, project_path):
        self.output.Debug(self, "Execute Project at path: %s" % project_path)
