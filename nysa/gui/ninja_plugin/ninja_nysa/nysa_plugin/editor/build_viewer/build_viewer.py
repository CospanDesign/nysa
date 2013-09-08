# -*- coding: utf-8 *-*

# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

'''
Log
  07/20/2013: Initial commit
'''

import os
import sys
import json
import glob

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ninja_ide.gui import actions
from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.editor.editor import Editor

from graphics_view import GraphicsView
from graphics_scene import GraphicsScene

from info_view import InfoView
from build_flow_view import BuildFlowView
from tool_properties_view import ToolPropertiesView
from build_controller import BuildController

sys.path.append(os.path.join(os.pardir,
                             os.pardir))

import nysa_actions

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common",
                             "xmsgs_tree_model"))

import xmsgs_tree_model

sys.path.append(os.path.join(os.pardir,
                             os.pardir,
                             "projects",
                             "ibuilder"))


from ibuilder import PROJECT_TYPE as IBUILDER_PROJECT_TYPE


ID = "build viewer"

class BuildViewerError(Exception):
    """
    Errors associated with the Build Viewer

    Error associated with:
        -loading the project config
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



class BuildViewer(QWidget, itab_item.ITabItem):

    def __init__(self, xmsgs_viewer, locator):
        QWidget.__init__(self)
        itab_item.ITabItem.__init__(self)
        self.ID = ID

        self.actions = actions.Actions()
        self.nactions = nysa_actions.NysaActions()

        self.config = {}
        self.info = InfoView(self)
        self.bfv = BuildFlowView(self)
        self.tpv = ToolPropertiesView(locator)

        layout = QVBoxLayout()
        layout.addWidget(self.info)
        layout.addWidget(self.bfv)
        layout.addWidget(self.tpv)
        self.setLayout(layout)

        self.controller = BuildController(locator, self.info, self.bfv, xmsgs_viewer)

        self.locator = locator
        self.explorer = self.locator.get_service('explorer')

        self.ibuilder_project = None
        self.builder_dir = None

        mc = self.actions.ide.mainContainer
        self.connect(mc,
                     SIGNAL("currentTabChanged(QString)"),
                     self.tab_changed)
        self.scan_for_ibuilder_projects()

    def tab_changed(self, tab_name):
        print "Tab Changed to %s" % tab_name
        if tab_name == self.ID:
            self.scan_for_ibuilder_projects()

    def scan_for_ibuilder_projects(self):
        print "Scanning for ibuilder projects"
        projects = self.explorer._explorer.get_opened_projects()
        print "len: %d" % len(projects)
        for project in projects:
            print "name: %s" % str(project.name)
            project_config = None
            #There shouldn't be an error here
            path = project.get_full_path()
            try:
                f = open(path, "r")
                project_config = json.load(f)
                f.close()
            except IOError, err:
                raise BuildViewerError("Error attempting to open file %s: %s" %
                        path, str(err))
            except KeyError, err:
                raise BuildViewerError("Error parsing JSON file: %s: %s" %
                        path, str(err))

            if project_config["project-type"] == IBUILDER_PROJECT_TYPE:
                #print "Found ibuilder project, adding to path"
                self.info.add_project_to_selector(path)

    def set_ibuilder_project(self, ibuilder_project):
        self.ibuilder_project

    def set_builder_dir(self, builder_dir):
        self.builder_dir

    def setup_filewatcher(self):
        print "setup file watcher"

    def build_viewer_update(self, project_path):
        print "Update to build view"
        #now I have the configuration of the build directory
        path = os.path.split(project_path)[0]
        if os.path.exists(path):
            project_config = os.path.join(path, "*.ibd")
            #print "path: %s" % project_config
            #print "%s" % str(os.listdir(path))
            cfiles = glob.glob(project_config)
            #print "cfiles: %s" % str(cfiles)
            if len(cfiles) == 0:
                self.info.set_status("<Not a Valid Project>")
                self.info.reset_labels()
                return
            self.config = {}
            try:
                self.config = json.load(open(cfiles[0], "r"))
                #print "config file:\n %s" % str(config)
            except IOError as err:
                self.info.set_status("File Error: %s" % str(err))
                self.info.reset_labels()
                return
            
            except ValueError as err:
                self.info.set_status("JSON Error: %s" % str(err))
                self.info.reset_labels()
                return
            
            except KeyError as err:
                self.info.set_status("JSON Error: %s" % str(err))
                self.info.reset_labels()
                return

            self.info.update_info(path, self.config)
        
    def ibuilder_project_opened(self, project_path):
        print "ibuilder project %s opened" % project_path
        self.controller.update(project_path)

