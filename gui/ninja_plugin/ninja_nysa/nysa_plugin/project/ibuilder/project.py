# -*- coding: utf-8 -*-

import os
import sys
import json

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QMessageBox

from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager

from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager

from ninja_ide.tools import json_manager

from .menu import Menu

from .wizard import PageBoardSelection 
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
    EXT = 'ibldr'
    output = None
    path = None

    def __init__(self, output=None, locator=None):
        self.locator = locator
        self.output = output
        self.explorer = self.locator.get_service('explorer')
        self.output.Debug(self, "IBuilder Project instantiated")

    def get_context_menus(self):
        return (Menu(self.locator, self.output), )

    def get_pages(self):
        pages = []
        bs = PageBoardSelection(self.locator, self.output)
        pages.append(bs)
        return pages

    def on_wizard_finished(self, wizard):
        global PROJECT_TYPE
        ids = wizard.pageIds()
        ninja_page = wizard.page(ids[-1])
        self.path = str(ninja_page.txtPlace.text())
        if not self.path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be created"))
            return
        wizard._load_project(self.path)
