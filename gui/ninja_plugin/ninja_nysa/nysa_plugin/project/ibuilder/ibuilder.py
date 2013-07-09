# -*- coding: utf-8 -*-

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


import sys
import os
import json
import glob

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.core import file_manager


sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir,
                                "editor",
                                "fpga_designer"))

from controller.wishbone_controller import WishboneController
from controller.axi_controller import AxiController
from fpga_designer import FPGADesigner

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir,
                                "editor",
                                "constraint_editor"))

from constraint_editor import ConstraintEditor

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                "cbuilder"))

sys.path.append(os.path.join( os.path.dirname(__file__),
                                os.pardir,
                                os.pardir))
import nysa_actions



from cbuilder import PROJECT_TYPE as CBUILDER_PROJECT_TYPE

'''
Functions independent of the project used to build/simulate/debug
'''

DESIGNER_EXT = "ibd"
PROJECT_TYPE = "FPGA Image Builder"



class IBuilder (QObject):
    output = None

    def __init__(self, output, locator):
        QObject.__init__(self)
        self.output = output
        self.locator = locator
        self.editor = self.locator.get_service('editor')
        self.explorer = self.locator.get_service('explorer')
        self.builder = self.locator.get_service('misc')._misc

        self.output.Debug(self, "create ibuilder!")
        self.designers = {}
        self.load_designers()
        self.controller = None
        self.actions = None
        self.commands = {}
        self.setup_commands()
        self.actions = nysa_actions.NysaActions()
        self.actions.set_ibuilder(self)
        self.connect(self.actions, SIGNAL("module_built(QString)"), self.module_built)

    def setup_controller(self, filename):
        d = {}
        controller = None
        #try:
        f = open(filename, "r")
        d = json.loads(f.read())
        #except IOError, err:
        #    raise FPGADesignerError("IOError: %s" % str(err))

        #except TypeError, err:
        #    raise FPGADesignerError("JSON Type Error: %s" % str(err))

        #A Pathetic factory pattern, select the controller based on the bus
        print "Getting Wishbone Controller"
        if d["TEMPLATE"] == "wishbone_template.json":
            controller = WishboneController(output = self.output, config_dict = d)
        elif d["TEMPLATE"] == "axi_template.json":
            controller = AxiController(self, self.output)
        else:
            raise FPGADesignerError(    "Bus type (%s) not recognized, view " +
                                        "controller cannot be setup, set the " +
                                        "TEMPLATE value to either " +
                                        "wishbone_template or " +
                                        "axi_tmeplate.json" % str(d["TEMPLATE"])
                                   )
        return controller


    def setup_commands(self):
        #This is sort of like the actions for the entire IDE but I only need
        #This locally (for ibuilder)
        self.commands["constraint_editor"] = self.open_constraint_editor


    def open_constraint_editor(self, view_controller, filename, name = None):
        print "open constraint editor"
        tab_manager = self.editor.get_tab_manager()
        ce = view_controller.get_constraint_editor()
        if ce is None or (tab_manager.is_open(ce) == -1):
            self.output.Debug(self, "Constraint editor is not open")
            if ce is not None:
                self.output.Debug(self, "There is a bogus constraint editor in the controller")
            ce = ConstraintEditor(parent=tab_manager,
                                  actions=self.actions,
                                  output=self.output,
                                  controller = view_controller,
                                  filename = filename,
                                  project_name = view_controller.get_project_name())

            name = "%s ce" % view_controller.get_project_name()
            tab_manager.add_tab(ce, name)
            view_controller.initialize_constraint_editor(ce)

        else:
            tab_manager.move_to_open(ce)


    def file_open(self, filename):
        ext = file_manager.get_file_extension(filename)
        projects = self.explorer._explorer.get_opened_projects()

        print "projects: %s" % str(projects)
        if ext == DESIGNER_EXT:
            self.output.Debug(self, "Found designer extension")
            tab_manager = self.editor.get_tab_manager()

            name = filename.split(os.path.sep)[-1]

            user_dirs = []
            #Look for cbuilder projects
            #if they exist, add them into the user directories

            #Project Trees
            for p in projects:
                print "looking for cbuilder"
                print "Project path: %s" % p.get_full_path()
                f = open(p.get_full_path(), "r")
                j = json.loads(f.read())
                if j["project-type"] == CBUILDER_PROJECT_TYPE:
                    path = os.path.split(p.get_full_path())[0]
                    print "ading: %s" % path
                    user_dirs.append(path)


            fd = None
            index = -1
            #filename = None

            if name in self.designers.keys():
                fd, index, filename = self.designers[name]
                #we have a reference to this in the local
                self.output.Debug(self, "Manager open value: %d" % tab_manager.is_open(fd))
                controller = fd.get_controller()
                for udir in user_dirs:
                    controller.add_user_dir(udir)

                #Check to see if the widget is in the tab manager
                if tab_manager.is_open(fd) == -1:
                    self.output.Debug(self, "Did not find name in opened tabs")
                    if name in self.designers.keys():
                        del self.designers[name]

                else:
                    tab_manager.move_to_open(fd)
                    self.output.Debug(self, "FPGA Designer is already is open")


            if name not in self.designers.keys():
                self.output.Debug(self, "Open up a new tab")
                project = self.explorer._explorer.get_project_given_filename(filename)
                #Not Opened
                fd = FPGADesigner(actions=self.actions,
                                  commands = self.commands,
                                  filename = filename,
                                  project=project,
                                  parent=tab_manager,
                                  output=self.output)

                #I'm assuming there is no controller set already so create a new one
                controller = self.setup_controller(filename)
                for udir in user_dirs:
                    print "adding %s to user paths" % udir
                    controller.add_user_dir(udir)
                fd.set_controller(controller)

                index = tab_manager.add_tab(fd, name)
                self.designers[name] = (fd, index, filename)
                controller.initialize_view()
                print "Initialize slave list"
                fd.initialize_slave_lists()

            return True

        return False

    def file_save(self, editor):
        filename = editor.ID
        ext = file_manager.get_file_extension(filename)
        if ext == DESIGNER_EXT:
            print "Found fpga_designer extension"
            self.output.Debug(self, "Found designer extension")
            controller = editor.get_controller()
            model = controller.get_model()
            model.apply_slave_tags_to_project(debug = True)
            model.save_config_file(filename)
            print "Saved file: %s" % filename
            return True

        return False

    def file_closed(self, filename):
        self.output.Debug(self, "Filename: %s" % filename)
        name = filename.split(os.path.sep)[-1]

        if filname in self.designers.keys():
            fd = None
            index = -1
            filename = None
            fd, index, filename = self.designers[name]
            self.output.Debug(self, "Remove: %s from designer" % filename)
            tab_manager = self.editor.get_tab_manager()
            #Go to the correct tab
            tab_manager.remove_tab(index)
            name = filename.split(os.path.sep)[-1]
            self.designers.remove(filename)

    def load_designers(self):
        tab_manager = self.editor.get_tab_manager()

    def build_project(self, project):
        print "Build project: %s" % str(project)

    def generate_project(self, project):
        print "Generate project: %s" % str(project)

    def module_built(self, module_name):
        print "ibuilder module built: %s" % module_name
        #Go through all editors, if they are ibuilder then
