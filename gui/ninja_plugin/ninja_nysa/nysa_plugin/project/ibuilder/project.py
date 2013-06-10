# -*- coding: utf-8 -*-

import os
import sys
import json

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMessageBox

from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager

from ninja_ide.tools import json_manager

from .menu import Menu

from .wizard import PageBoardSelection 
from .wizard import ImageCustomizeSelection

from .ibuilder import DESIGNER_EXT

PROJECT_TYPE = "FPGA Image Builder"


sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder"))


class ProjectIbuilder (plugin_interfaces.IProjectTypeHandler, QObject):
    EXT = 'ibuilder'
    output = None
    path = None

    def __init__(self, output=None, locator=None):
        self.locator = locator
        self.output = output
        self.editor = self.locator.get_service('editor')
        self.explorer = self.locator.get_service('explorer')
        self.output.Debug(self, "IBuilder Project instantiated")
        self.board_dict = {}
        self.ics = None

           
    def get_context_menus(self):
        return (Menu(self.locator, self.output), )

    def get_pages(self):
        pages = []
        self.output.Debug(self, "Getting board selection page")
        page = PageBoardSelection(self.locator, self, self.output)
        self.output.Debug(self, "Got board select page")
        pages.append(page)
        
        self.output.Debug(self, "Getting image customization Page")
        self.ics = ImageCustomizeSelection(self.locator, self.output, self.board_dict)
        self.output.Debug(self, "Got image customization Page")
        pages.append(self.ics)
        return pages

    def update_board_selection(self, board_dict):
        self.board_dict = board_dict
        if self.ics is not None:
          self.ics.update_user_selection(self.board_dict)

    def on_wizard_finish(self, wizard):
        self.output.Info(self, "Wizard Finished")
        global PROJECT_TYPE
        ids = wizard.pageIds()
        ninja_page = wizard.page(ids[-1])
        board_select_page = wizard.page(ids[0])
        custom_image = wizard.page(ids[1])
        bus = self.ics.get_bus()


        self.path = str(ninja_page.txtPlace.text())
        if not self.path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be created"))
            return

        name = str(ninja_page.txtName.text())
        project = {}
        project['name'] = name
        project['project-type'] = str(PROJECT_TYPE)
        project['description']  = str(ninja_page.txtDescription.toPlainText())
        #project['url'] = 'http://www.cospandesign.com'
        project['license'] = str(ninja_page.cboLicense.currentText())
        designer_ibd = ".%s" % DESIGNER_EXT
        project['supported-extensions'] = ['py', '.json', '.txt', '.v', '.ucf', designer_ibd]
        #project['preExecScript'] = ''
        #project['postExecScript'] = ''
        #project['identation'] = ''
        #project['use-tabs'] = ''
        #project['additional_builtins'] = []
        #project['programParams'] = self.project_execute
        #project['relatedProjects'] = []

        self.path = os.path.join(self.path, name)
        self.output.Info(self, "Creating Directory: %s" % self.path)
        file_manager.create_folder(self.path, add_init_file = False)

        #Crete the ninja interface
        json_manager.create_ninja_project(self.path, name, project)
        self.plugin_dict = self.create_descriptor(name, self.path)

        self.output.Info(self, "Path: %s" % self.path)

        #Populate the directory
        #proj_dir = os.path.join(self.path, name)
        #file_manager.create_folder(proj_dir)
        proj_dir = self.path
        out_dir = os.path.join(self.path, "build")

        ibd = {}
        ibd["BASE_DIR"] = out_dir
        ibd["board"] = self.board_dict["board_name"]
        self.output.Debug(self, "Bus: %s" % bus)
        ibd["TEMPLATE"] = {}
        if bus == "wishbone":
            ibd["TEMPLATE"] = "wishbone_template.json"
        elif bus == "axi":
            ibd["TEMPLATE"] = "axi_template.json"
            
        ibd["SLAVES"] = {}
        ibd["MEMORY"] = {}
        ibd["internal_bind"] = {}
        ibd["bind"] = {}
        ibd["constraint_files"] = {}
                
        fn = "%s.%s" % (name, DESIGNER_EXT)
        fn = os.path.join(proj_dir, fn)
        self.create_file(fn, ibd)

        wizard._load_project(self.path)

    def create_descriptor(self, name, path):
        plugin = {}

        plugin['name'] = name
        fileName = os.path.join(path, name + "." + self.EXT)
        # Create the .plugin file with metadata
        self.create_file(fileName, plugin)
        # Return the dictionary
        return plugin

    def create_file(self, fileName, structure):
        self.output.Info(self, "Creating file: %s" % fileName)
        f = open(fileName, mode='w')
        json.dump(structure, f, indent=2)
        f.close()


