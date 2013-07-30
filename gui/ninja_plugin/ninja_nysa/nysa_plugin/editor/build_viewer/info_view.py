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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from defines import NO_BOARD_IMAGE
from defines import GENERIC_BOARD_IMAGE

sys.path.append(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              os.pardir,
                              "ibuilder",
                              "lib"))

import utils


MANUAL_SELECT_NAME = "Manually Select Project Directory"

NO_PROJECT_SELECTED = "<No Project Selected>"
NO_DIRECTORY_SELECTED = "<No Directory Selected>"
NO_BOARD_SELECTED = "<No Board Selected>"

class InfoView(QWidget):


    def __init__(self, build_viewer):
        super(InfoView, self).__init__()
        self.board_url = ""
        self.board_image = None
        self.build_viewer = build_viewer

        #Add the project/board inforamtion to the grid
        grid = QGridLayout(self)
        select_project_button = QPushButton("Select Project (Scan)")
        grid.addWidget(select_project_button, 0, 0)
        grid.addWidget(QLabel("Project Name:"), 1, 0)
        grid.addWidget(QLabel("Directory"), 2, 0)
        grid.addWidget(QLabel("Board Name"), 3, 0)
        grid.addWidget(QLabel("Status"), 4, 0)
        #grid.addWidget(QLabel("Bus Type:"), 5, 0)

        self.project_name_label = QLabel(NO_PROJECT_SELECTED)
        self.directory_label = QLabel(NO_DIRECTORY_SELECTED)
        self.board_name_link = QLabel(NO_BOARD_SELECTED)
        self.status = QLabel(NO_PROJECT_SELECTED)
        self.connect(self.board_name_link,
                     SIGNAL("linkActivated(QString)"),
                     self.board_link_activated)

        #self.bus_type_link = QLabel("<No Bus Selected>")
        #self.connect(self.bus_type_link,
        #             SIGNAL("linkActivated(QString)"),
        #             self.bus_link_activated)
        self.project_paths = []

        self.project_selector = QComboBox()
        self.update_project_selector()
        self.project_selector.setCurrentIndex(0)
        self.project_select_button = QPushButton("Select")

        grid.addWidget(self.project_selector, 0, 1, 1, 2)
        grid.addWidget(self.project_select_button, 0, 3, 1, 1)

        grid.addWidget(self.project_name_label, 1, 1, 1, 3)
        grid.addWidget(self.directory_label, 2, 1, 1, 3)
        grid.addWidget(self.board_name_link, 3, 1, 1, 3)
        grid.addWidget(self.status, 4, 1, 1, 3)
        #grid.addWidget(self.bus_type_link, 4, 1, 1, 3)

        #Add the board image
        self.image_view = QLabel("No Image")
        self.board_image_view = QPixmap(NO_BOARD_IMAGE)
        self.image_view.setPixmap(self.board_image_view)
        #grid.addWidget(self.image_view, 0, 2, 4, 4)
        self.grid_widget = QWidget()
        self.grid_widget.setLayout(grid)


        self.main_layout = QHBoxLayout()
        
        self.main_layout.addWidget(self.grid_widget, stretch=1)
        self.main_layout.addWidget(self.image_view)

        #self.setLayout(grid)
        self.setLayout(self.main_layout)
        #self.main_layout.addWidget(self.main_layout())
        self.connect(self.project_selector,
                     SIGNAL("currentIndexChanged(int)"),
                     self.selector_changed)
        self.connect(self.project_select_button,
                     SIGNAL("clicked()"),
                     self.select_project_dir_clicked)
        self.connect(select_project_button,
                     SIGNAL("clicked()"),
                     self.build_viewer.scan_for_ibuilder_projects)

    def set_project_name(self, project_name = None):
        if project_name is None:
            self.project_name_label.setText("<No Project Selected>")
            return

        self.project_name_label.setText(project_name)

    def set_project_directory(self, directory = None):

        if directory is None:
            self.directory_label.setText("<No Diretory Set>")
            return

        self.directory_label.setText(directory)

    def set_board_name(self, name = None, link = None):
        if name is None:
            self.board_name_link("<No Board Selected>")
            self.bus_link = None
            return
        self.board_name_link.setText(name)
        self.board_url = link


#    def set_bus_type(self, bus_type = None, link = None):
#        if bus_type is None:
#            self.bus_type_link("<No Bus Selected>")
#            self.bus_link = None
#            return
#
#        self.bus_type_link(bus_type)
#        self.bus_url = link
#
#    def bus_link_activated(self, link):
#        if self.bus_url is None:
#            print "Bus URL is None"
#            return
#        print "Open link at %s" % self.bus_link


    def board_link_activated(self, link):
        #Don't use this link (it sucks), use the link in self.board_url
        if self.board_url is None:
            print "Board URL is None"
            return

        print "Open link at %s" % self.board_url

    def set_board_image_view(self, filename):
        self.board_image_view = QPixmap(filename)
        self.image_view.setPixmap(self.board_image_view)

    def set_status(self, status):
        self.status.setText(status)

    def reset_labels(self):
        self.set_project_name(NO_PROJECT_SELECTED)
        self.set_project_directory(NO_DIRECTORY_SELECTED)
        self.set_board_name(NO_BOARD_SELECTED)
        self.board_image_view = QPixmap(NO_BOARD_IMAGE)
        self.image_view.setPixmap(self.board_image_view)

    def update_info(self, path, config):
        #print "Update info view"
        #Project Directory should have the name of the project
        #Look for a configuration file
        #set the project name
        self.set_project_name(config["PROJECT_NAME"])
        
        #set the board name
        if "board" in config.keys():
            self.set_board_name(config["board"])
            board_config = utils.get_board_config(config["board"].lower())
            if "image" in board_config.keys():
                image_path = os.path.join(utils.get_nysa_base(),
                                          "ibuilder", 
                                          "boards", 
                                          config["board"].lower(),
                                          board_config["image"])
                #print "image path: %s" % image_path
                if os.path.exists(image_path):
                    self.set_board_image_view(image_path)
                else:
                    self.set_board_image_view(GENERIC_BOARD_IMAGE)
            else:
                self.set_board_image(GENERIC_BOARD_IMAGE)
        
        else:
            self.set_board_name("<No Board Name Found in Config.json>")
            self.set_board_image(GENERIC_BOARD_IMAGE)
        
        self.set_project_directory(path)
        self.set_status("Project %s Loaded" % config["PROJECT_NAME"])
        #set the board image

    def remove_project_from_selector(self, project_path):
        if project_path in self.project_paths:
            self.project_paths.remove(project_path)

        self.update_project_selector()

    def add_project_to_selector(self, project_path):
        #print "Project Path %s" % project_path
        if project_path not in self.project_paths:
            self.project_paths.append(project_path)
            self.update_project_selector()

    def update_project_selector(self):
        count = self.project_selector.count()
        for i in range(count):
            self.project_selector.removeItem(0)
        self.project_selector.addItem(MANUAL_SELECT_NAME)
        self.project_selector.setCurrentIndex(0)
        for i in range(len(self.project_paths)):
            self.project_selector.addItem(self.project_paths[i])


    def selector_changed(self, index):
        #print "selector changed to: %d" % index
        if index == 0:
            self.project_select_button.setEnabled(True)
            path = ""
        else:
            self.project_select_button.setEnabled(False)
            path = self.project_selector.itemText(index)
        self.build_viewer.build_viewer_update(path)
        #self.update_info(path)
        self.build_viewer.ibuilder_project_opened(path)

    def select_project_dir_clicked(self):
        path = QFileDialog.getExistingDirectory(self,
                caption = "Select A Project Directory File",
                directory = ".")
        #TODO: Setup the start directory!
        self.build_viewer.build_viewer_update(path)


