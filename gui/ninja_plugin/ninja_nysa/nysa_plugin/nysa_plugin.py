# -*- coding: UTF-8 -*-
import os


from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL


from ninja_ide.core import plugin
from ninja_ide.gui import actions
#from ninja_ide.tools import json_manager
#from ninja_ide.core import plugin_interfaces
from .project.cbuilder import project
from .project.cbuilder.cbuilder import CBuilder
from .misc import nysa_status
from .preferences import preferences
from .toolbar import toolbar

#This is here only for testing
from .editor.fpga_designer.fpga_designer import FPGADesigner


LOG_FORMAT = "%(asctime)s %(name)s:%(levelname)-8s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class NysaPlugin(plugin.Plugin):

    output = None
    cbuilder = None

    def initialize(self):
        # Init your plugin

        #Locator
        self.editor_s = self.locator.get_service('editor')
        self.toolbar_s = self.locator.get_service('toolbar')
        self.menuApp_s = self.locator.get_service('menuApp')
        self.misc_s = self.locator.get_service('misc')
        self.explorer_s = self.locator.get_service('explorer')

        self.load_status()
        self.output.Info(self, "Started Nysa Plugin")
        self.cbuilder = CBuilder(self.output, self.locator)
        self.load_cbuilder_project()
        self.tb = toolbar.nysaToolbar(self.toolbar_s, self.output)
        self.tb.create_test_icon(self.toolbar_test)
        self.tb.create_wave_icon(self.cbuilder.waveforms)
        self.tb.create_sim_icon(self.cbuilder.simulate)

        #Add all the toolbar items
        self.tb.add_toolbar_items()

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

        self._action = actions.Actions()
        self.connect(self._action, SIGNAL("projectExecuted(QString)"),
            self.cbuilder.build_core)

        self._action = actions.Actions()
        self.connect(self._action, SIGNAL("fileExecuted(QString)"),
            self.cbuilder.build_core)

        #*** This is where you get the misc_container
        #Run the application without the main file!
        #mc = self.misc_s._misc
        #print "misc container: %s" % str(dir(mc))



    def finish(self):
        # Shutdown your plugin
        self.logger.info("Shutdown Nysa Plugin")

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        return preferences.NysaPreferences(self.locator, self.output)

    def load_status(self):
        self.logger.info("Load Nysa Status")
        self.output = nysa_status.NysaStatus()
        status_icon_path = os.path.join(os.path.dirname(__file__),
                                        "images",
                                        "status.png")

        self.misc_s.add_widget(self.output,
                               status_icon_path,
                               "Displays events at runtime")

    def load_cbuilder_project(self):
        self.output.Info(self, "Loading cbuilder project")
        self.explorer_s.set_project_type_handler(project.PROJECT_TYPE,
        project.ProjectCbuilder(self.output, self.locator))

    def open_verilog(self, filename):
        f_path = os.path.join("home", "cospan", "Projects", "olympus",
          "cbuilder", "rtl", "generic", "afifo.v")
        #loc = os.path.dirname(__file__)
        #vpath = os.path.join(loc, "syntax", "verilog.json")
        #vdict = json_manager.parse(vpath)

        #self.editor_s.add_editor(filename, syntax=vdict)
        self.output.Info(self, "afifo.v path: %s" % f_path)

    def register_syntax(self):
        loc = os.path.dirname(__file__)
        vpath = os.path.join(loc, "syntax", "verilog.json")
        #vdict = json_manager.parse(vpath)
        #self.editor_s.register_syntax(lang="v", syntax=vdict)
        #self.editor_s.get_editor().register_syntax(lang="v", syntax=vdict)
        #print "Editor: %s" % str(dir(self.editor_s.get_editor()))
        self.output.Info(self, "vpath: %s" % vpath)

    def test_editor(self):
        #This doesn't belong here but when I work on ibuilder then I need to
        #implement this
        tab_manager = self.editor_s.get_tab_manager()
        fpgaDesigner = FPGADesigner(actions=None, parent=tab_manager)
        tab_manager.add_tab(fpgaDesigner, self.tr("FPGA Designer"))

    def toolbar_test(self):
        self.logger.info("Toolbar test triggered")
        self.output.Info(self, "Toolbar test triggered")
