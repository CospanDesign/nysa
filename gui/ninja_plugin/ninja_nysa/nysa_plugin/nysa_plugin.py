# -*- coding: UTF-8 -*-

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



import os
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from ninja_ide.core import plugin
from ninja_ide.core import file_manager
from ninja_ide.gui import actions
from ninja_ide import resources

#from ninja_ide.tools import json_manager
#from ninja_ide.core import plugin_interfaces
from project.cbuilder import project as cbuilder_project
from project.cbuilder.cbuilder import PROJECT_TYPE as CBUILDER_PROJECT_TYPE
from project.ibuilder.ibuilder import PROJECT_TYPE as IBUILDER_PROJECT_TYPE
from project.cbuilder.cbuilder import CBuilder
from project.cbuilder.cbuilder import CBUILDER_EXT
from project.ibuilder.ibuilder import IBuilder
from project.ibuilder.ibuilder import DESIGNER_EXT
from project.ibuilder import project as ibuilder_project
from misc import nysa_status
from preferences import preferences
from toolbar import toolbar

#This is here only for testing
from .editor.fpga_designer.fpga_designer import FPGADesigner
from .editor.constraint_editor.constraint_editor import ConstraintEditor

from project.ibuilder import properties_dialog as ibuilder_dialog


LOG_FORMAT = "%(asctime)s %(name)s:%(levelname)-8s %(message)s"
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


main = None
nysa_plugin = None

class NysaPlugin(plugin.Plugin):

    #output = None
    #cbuilder = None
    #ibuilder = None

    def initialize(self):
        # Init your plugin
        global nysa_plugin
        nysa_plugin = self

        #Locator
        self.editor_s = self.locator.get_service('editor')
        self.toolbar_s = self.locator.get_service('toolbar')
        self.menuApp_s = self.locator.get_service('menuApp')
        self.misc_s = self.locator.get_service('misc')
        self.explorer_s = self.locator.get_service('explorer')

        self.load_status()

        self.output.Info(self, "Started Nysa Plugin")

        self.cbuilder = CBuilder(self.output, self.locator)
        self.ibuilder = IBuilder(self.output, self.locator)

        self.load_cbuilder_project()
        self.load_ibuilder_project()
        self.tb = toolbar.Toolbar(self.toolbar_s, self.output)
        #self.tb.create_test_icon(self.toolbar_test)
        self.tb.create_status_icon(self.view_status)
        self.tb.create_wave_icon(self.cbuilder.waveforms)
        self.tb.create_sim_icon(self.cbuilder.simulate)

        #Add all the toolbar items
        self.tb.add_toolbar_items()
        tab_manager = self.editor_s.get_tab_manager()


        self.actions = actions.Actions()

        #self.connect(tab_manager, SIGNAL("changeActualTab(QWidget)"),
        #    self.tab_changed)

        self.connect(self.editor_s._main, SIGNAL("fileClosed(QString)"),
            self.file_closed)

        self.connect(self.actions.shortSave, SIGNAL("activated()"),
            self.save_file)


        #Really big hack to make the 'save' from the menu work
        self.actions.ide._menuFile.connect(self.actions.ide._menuFile.toolbar_items["save-file"], SIGNAL("triggered()"), self.save_file)
        self.actions.ide._menuFile.connect(self.actions.ide._menuFile.toolbar_items["save-as"], SIGNAL("triggered()"), self.save_file_as)


        #Steal the build commands
        #self.actions_execute_file = self.actions.execute_file
        #self.actions_execute_project = self.actions.execute_project



        #DEMO STUFF
        #self.test_editor()
        self.inject_functions()
        self.actions.update_shortcuts()

        #self.connect(self.actions, SIGNAL("projectExecuted(QString)"),
        #    self.build_command)
        #self.cbuilder.build_core)

        self.connect(self.actions.shortRunFile, SIGNAL("activated()"), self.build_file_command)
        self.actions.disconnect(self.actions.shortRunFile, SIGNAL("activated()"), self.actions.execute_file)


        #self.cbuilder.build_core)

        self.actions.connect(self.actions.shortRunProject, SIGNAL("activated()"), self.build_command)
        self.actions.disconnect(self.actions.shortRunProject, SIGNAL("activated()"), self.actions.execute_project)

        #self.dialog_test()
        self.modify_context_menus()
        self.modify_file_icons()


    def modify_context_menus(self):
        tp = self.editor_s._explorer._treeProjects
        self.normal_add_context_menu_for_root = tp._add_context_menu_for_root
        self.normal_add_context_menu_for_folders = tp._add_context_menu_for_folders

        tp._add_context_menu_for_root = self.add_context_menu_for_root
        tp._add_context_menu_for_folders = self.add_context_menu_for_folders

    def modify_file_icons(self):
        tp = self.editor_s._explorer._treeProjects

        tp._get_file_icon = self.get_file_icon
        self.images = tp.images

    def get_file_icon(self, filename):

        file_ext = file_manager.get_file_extension(filename)
        icon = None
        icon = self.cbuilder.get_file_icon(filename, file_ext)
        if isinstance(icon, QIcon):
            return icon

        icon = self.ibuilder.get_file_icon(filename, file_ext)
        if isinstance(icon, QIcon):
            return icon

        return QIcon(self.images.get(file_ext, resources.IMAGES['tree-generic']))


        #tp.normal_get_file_icon(filename)

    def add_context_menu_for_root(self, menu, item):
        #print "Take menu over!"
        #tp = self.editor_s._explorer._treeProjects
        if self.ibuilder.is_ibuilder_project(item):
            self.ibuilder.ibuilder_menu(menu, item)
            return
        if self.cbuilder.is_cbuilder_project(item):
            self.cbuilder.cbuilder_menu(menu, item)
            return

        self.normal_add_context_menu_for_root(menu, item)

    def add_context_menu_for_folders(self, menu, item):
        print "contect menu for folders"
        if self.cbuilder.is_cbuilder_project(item):
            return
        if self.ibuilder.is_ibuilder_project(item):
            return

        self.normal_add_context_menu_for_folders(menu, item)

    def inject_functions(self):
        print "Injecting functions"
        global main
        main = self.editor_s._main

        self.output.Debug(self, "Replacing main open function")

        #Save the current versions to a new place
        main.main_open_file = main.open_file
        main.main_save_file = main.save_file
        main.main_save_file_as = main.save_file_as


        main.open_file = nysa_open_file
        main.save_file = self.save_file
        main.save_file_as = nysa_save_file_as

    def build_command(self):
        print "Entering custom build"
        editor = self.locator.get_service('editor')
        project = editor.get_project_owner()
        if project is None or len(project) == 0:
            filename = ""
            print "Project is None attempt to find the widget, not editor"
            tab_manager = editor.get_tab_manager()
            widget = tab_manager.currentWidget()
            print "widget: %s" % str(widget)
            filename = widget.ID

            print "Filename: %s" % str(filename)
            project_tree = self.explorer_s._explorer.get_project_given_filename(filename)
            project = project_tree.get_full_path()
            project = os.path.split(project)[0]

            if project is None:
                print "Unable to find project name"
                return

            print "Project: %s" % str(project)

        print "editor: %s" % editor
        print "project: %s" % project

        cbuilder_project = glob.glob(project + os.path.sep + "*.%s" % CBUILDER_EXT)
        ibuilder_project = glob.glob(project + os.path.sep + "*.%s" % DESIGNER_EXT)
        print "cbuilder_project: %s" % str(cbuilder_project)
        print "ibuilder_project: %s" % str(ibuilder_project)

        if len(cbuilder_project) > 0:
            print "Build cbuilder project"
            self.cbuilder.build_core()
            return

        elif len(ibuilder_project) > 0:
            print "Build ibuilder project"
            self.ibuilder.build_project(project)
            return

        print "Normal build"
        self.actions.execute_project()


    def build_file_command(self):
        print "Enterring custom file build"
        editor = self.locator.get_service('editor')
        #project = editor.get_project_owner()
        #user_paths = []
        #if project is None or len(project) == 0:
        filename = ""
        print "Project is None attempt to find the widget, not editor"
        tab_manager = editor.get_tab_manager()
        widget = tab_manager.currentWidget()
        print "widget: %s" % str(widget)
        filename = widget.ID

        print "Filename: %s" % str(filename)
        project_tree = self.explorer_s._explorer.get_project_given_filename(filename)
        project = project_tree.get_full_path()
        project = os.path.split(project)[0]

        if project is None:
            print "Unable to find project name"
            return

        print "Project: %s" % str(project)


        cbuilder_project = glob.glob(project + os.path.sep + "*.%s" % CBUILDER_EXT)
        ibuilder_project = glob.glob(project + os.path.sep + "*.%s" % DESIGNER_EXT)
        print "project file: %s" % cbuilder_project
        if len(cbuilder_project) > 0:
            print "Build corebuilder file"
            self.cbuilder.build_core()
            return

        if len(ibuilder_project) > 0:
            print "Build ibuilder file"
            user_paths = widget.get_controller().get_user_dirs()
            self.ibuilder.generate_project(project, user_paths)
            return
           

        print "Normal file build"
        self.actions.execute_file()


    def open_file(self, filename):
        self.output.Debug(self, "Open file detect")
        return self.ibuilder.file_open(filename)

    def save_file(self, editorWidget=None):
        self.output.Debug(self, "Custom save file")
        main = self.editor_s._main

        if editorWidget is None:
            editorWidget = main.actualTab.currentWidget()

        if self.ibuilder.file_save(editorWidget):
            self.output.Debug(self, "Saved designer file")
            return

        self.output.Debug(self, "Saving normal file")
        main.main_save_file(editorWidget)

    def save_file_as(self):
        self.output.Debug(self, "Custom save as file")
        main = self.editor_s._main
        main.main_save_file_as()

    def file_closed(self, filename):
        self.output.Debug(self, "File close detected")
        return self.ibuilder.file_closed(filename)



    def view_status(self):
        self.misc_s._misc.gain_focus()
        self.misc_s._misc._item_changed(self.status_index)

    def finish(self):
        # Shutdown your plugin
        self.logger.info("Shutdown Nysa Plugin")

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        return preferences.NysaPreferences(self.locator, self.output)

    def load_status(self):
        self.status_index = self.misc_s._misc.stack.count()
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
        self.explorer_s.set_project_type_handler(CBUILDER_PROJECT_TYPE,
        cbuilder_project.ProjectCbuilder(self.output, self.locator))

    def load_ibuilder_project(self):
        self.output.Info(self, "Loading ibuilder project")
        self.explorer_s.set_project_type_handler(IBUILDER_PROJECT_TYPE,
        ibuilder_project.ProjectIbuilder(self.output, self.locator))

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

    #def tab_changed(self, widget):
    #    print "tab changed"
    #    tab_manager = self.editor_s.get_tab_manager()
    #    editor = actualTab.currentWidget()
    #    if isinstance(editor, ConstraintEditor):
    #        editor.refresh_tables()
            

    def test_editor(self):
        #This doesn't belong here but when I work on ibuilder then I need to
        #implement this
        tab_manager = self.editor_s.get_tab_manager()
        #fpgaDesigner = FPGADesigner(actions=None, parent=tab_manager, output=self.output)
        #tab_manager.add_tab(fpgaDesigner, self.tr("FPGA Designer"))
        #fpgaDesigner.initialize_slave_lists()
        constraintEditor = ConstraintEditor(parent=tab_manager,
                                            actions=None,
                                            output=self.output,
                                            controller=self,
                                            project_name = "Demo")
        constraintEditor.initialize_view()
        tab_manager.add_tab(constraintEditor, self.tr("Constraint Editor"))


        #Add signals
        constraintEditor.add_signal("blue", "Module1", "Port1", None, "input")
        constraintEditor.add_signal("blue", "Module1", "Port2", (0,1), "output")
        constraintEditor.add_signal("yellow", "Module2", "Port1", (3, 0), "output")
        constraintEditor.add_signal("yellow", "Module2", "Port2", None, "input")

        #Remove Signals
        constraintEditor.remove_signal("Module2", "Port1")

        #Add pins
        constraintEditor.add_pin("NAME1")
        constraintEditor.add_pin("NAME2")
        constraintEditor.add_pin("NAME3")

        #Remove Pins
        constraintEditor.remove_pin("NAME2")


        #Add Connections
        print "Adding connections"
        constraintEditor.add_connection(color = "green",
                                        module_name = "ModuleB", 
                                        port = "PortC", 
                                        direction = "output", 
                                        pin_name = "PIN_NAME_ALSO")
        constraintEditor.add_connection(color = "blue",
                                        module_name = "ModuleC", 
                                        port = "PortC", 
                                        direction = "output", 
                                        pin_name = "PIN_NAME_ALSO", 
                                        index = 0)
        constraintEditor.add_connection(color = "orange",
                                        module_name = "ModuleD", 
                                        port = "PortC", 
                                        direction = "output", 
                                        pin_name = "PIN_NAME_ALSO")
        constraintEditor.add_connection(color = "red",
                                        module_name = "ModuleA", 
                                        port = "PortB", 
                                        direction = "inout", 
                                        pin_name = "PIN_NAME",
                                        index = 2)
        print "Added connections"

        #Remove Connections
        constraintEditor.remove_connection("ModuleA", "PortB")

    def item_is_enabled(self, path):
        print "Path: %s" % path
        return True



    def toolbar_test(self):
        self.logger.info("Toolbar test triggered")
        self.output.Info(self, "Toolbar test triggered")
        self.dialog_test()


    def dialog_test(self):
        print "Dialog Test"
        results = ibuilder_dialog.ibuilder_properites_dialog(os.path.dirname(__file__), True, "out_dir")
        if results[0]:
            print "Relative: %s" % results[1]
        else:
            print "Absolute: %s" % results[1]



def nysa_open_file(     filename='',
                        cursorPosition=-1,
                        tabIndex=None,
                        positionIsLineNumber=False,
                        notStart=True):

    if filename is not None:
        if nysa_plugin.open_file(filename):
            #print "Don't send the open file control to the main controller"
            return
    #print "Openeing: %s" % filename
    main.main_open_file(filename, cursorPosition, tabIndex, positionIsLineNumber, notStart)



def nysa_save_file(     editorWidget=None):
    print "Entering Nysa customm save"
    nysa_plugin.save_file(editorWidget)
    main.main_save_file(editorWidget)

def nysa_save_file_as():
    print "Entering Nysa custom save as"
    #print "I'm 1337 again"
    main.main_save_file_as()


