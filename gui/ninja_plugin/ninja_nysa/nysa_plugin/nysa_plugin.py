# -*- coding: UTF-8 -*-
import os
import sys

from ninja_ide.core import plugin
#from ninja_ide.tools import json_manager
#from ninja_ide.core import plugin_interfaces
from .project.cbuilder import project_cbuilder
from .misc import nysa_status
from .preferences import preferences
import StringIO

#This is here only for testing
from .editor.fpga_designer.fpga_designer import FPGADesigner


LOG_FORMAT = "%(asctime)s %(name)s:%(levelname)-8s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class NysaPlugin(plugin.Plugin):

    status = None

    def initialize(self):
        # Init your plugin

        #Locator
        self.editor_s = self.locator.get_service('editor')
        self.toolbar_s = self.locator.get_service('toolbar')
        self.menuApp_s = self.locator.get_service('menuApp')
        self.misc_s = self.locator.get_service('misc')
        self.explorer_s = self.locator.get_service('explorer')

        self.load_status()
        self.status.Info(self, "Started Nysa Plugin")
        self.load_cbuilder_project()

        #print ("Logger: %s" % str(dir(self.logger)))
        #self.logger.addHandler()
        #self.shandler = StringIO.StringIO()
        #self.logger.StreamHandler(sys.stdout)

        #self.logger.add_handler(self.shandler, 
        #self.logger.add_handler(sys.stdout,
        #    'w', 
        #    LOG_FORMAT, 
        #    TIME_FORMAT, 
        #    stream=True)
        #self.register_syntax()
        #self.editor_s.fileOpened.connect(self.open_verilog)
        #self.test_editor()
        #self.open_verilog("afifo.v")

    def finish(self):
        # Shutdown your plugin
        self.logger.Info("Shutdown Nysa Plugin")

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        return preferences.NysaPreferences(self.locator, self.status)

    def load_status(self):
        self.logger.info("Load Nysa Status")
        self.status = nysa_status.NysaStatus()
        status_icon_path = os.path.join(os.path.dirname(__file__),
                                        "images",
                                        "status.png")

        self.misc_s.add_widget(self.status,
                               status_icon_path,
                               "Displays events at runtime")

    def load_cbuilder_project(self):
        self.status.Info(self, "Loading cbuilder project")
        self.explorer_s.set_project_type_handler(project_cbuilder.PROJECT_TYPE,
        project_cbuilder.ProjectCbuilder(self.status, self.locator))

    def open_verilog(self, filename):
        f_path = os.path.join("home", "cospan", "Projects", "olympus",
          "cbuilder", "rtl", "generic", "afifo.v")
        #loc = os.path.dirname(__file__)
        #vpath = os.path.join(loc, "syntax", "verilog.json")
        #vdict = json_manager.parse(vpath)

        #self.editor_s.add_editor(filename, syntax=vdict)
        self.status.Info(self, "afifo.v path: %s" % f_path)

    def register_syntax(self):
        loc = os.path.dirname(__file__)
        vpath = os.path.join(loc, "syntax", "verilog.json")
        #vdict = json_manager.parse(vpath)
        #self.editor_s.register_syntax(lang="v", syntax=vdict)
        #self.editor_s.get_editor().register_syntax(lang="v", syntax=vdict)
        #print "Editor: %s" % str(dir(self.editor_s.get_editor()))
        self.status.Info(self, "vpath: %s" % vpath)

    def test_editor(self):
        #This doesn't belong here but when I work on ibuilder then I need to
        #implement this
        tab_manager = self.editor_s.get_tab_manager()
        fpgaDesigner = FPGADesigner(actions=None, parent=tab_manager)
        tab_manager.add_tab(fpgaDesigner, self.tr("FPGA Designer"))
