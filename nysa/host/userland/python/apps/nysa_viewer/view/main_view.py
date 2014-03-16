# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "common"))
import status

os.path.join(os.path.dirname(__file__), os.pardir)


import actions
from common.utils import get_color_from_id
from view.platform_tree.platform_tree import PlatformTree

from main_tab_view import MainTabView
from tab_manager import TabManager

from fpga_view.fpga_view import FPGAImage

p = os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             "gui",
                             "pvg",
                             "visual_graph")
p = os.path.abspath(p)
#print ("Dir: %s" % p)

sys.path.append(p)

class MainPanel(QWidget):
    def __init__(self):
        super (MainPanel, self).__init__()
        layout = QVBoxLayout()
        self.status = status.Status()
        self.actions = actions.Actions()

        self.platform_tree = PlatformTree(self)
        self.platform_tree.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)
        self.main_splitter = QSplitter(Qt.Horizontal)

        #Add Nysa FPGAImage Tree View
        self.tab_view = MainTabView()
        self.tab_view.setSizePolicy(QSizePolicy.Preferred,
                                    QSizePolicy.Preferred)
        self.fpga_image = FPGAImage()
        self.fpga_image.setSizePolicy(QSizePolicy.MinimumExpanding,
                               QSizePolicy.Preferred)

        self.main_splitter.addWidget(self.platform_tree)
        self.main_splitter.addWidget(self.tab_view)

        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.MinimumExpanding)

        self.tm = TabManager(self.tab_view)

        #Create the main window
        #Add Main Tabbed View
        layout.addWidget(self.main_splitter)
        #self.tab_view.add_tab(self.fpga_image, "main tab")
        self.add_tab(None, self.fpga_image, "main tab", False)
        #self.tab_view.add_tab(self.fpga_image, "main tab")

        #Add Status View
        layout.addWidget(status.Status())

        #Set the layout
        self.setLayout(layout)
        self.actions.platform_tree_changed_signal.connect(self.platform_tree_changed)

    def platform_tree_changed(self, uid, nysa_type, nysa_dev):
        l = self.platform_tree.selectedIndexes()
        if len(l) == 0:
            return
        index = l[0]
        if index is None:
            return
        color = self.platform_tree.get_node_color(index)
        self.tm.set_tab_color(self.fpga_image, color) 

    def toggle_status_view(self):
        if self.status.isVisible():

            self.status.setVisible(False)
        else:
            self.status.setVisible(True)

    def get_fpga_view(self):
        return self.fpga_image

    def add_tab(self, nysa_id, widget, name, removable = True):
        self.tm.add_tab(name, nysa_id, widget, False)

        if widget is not self.fpga_image:
            l = self.platform_tree.selectedIndexes()
            if len(l) == 0:
                return
            index = l[0]
            if index is None:
                return
            color = self.platform_tree.get_node_color(index)
            self.tm.set_tab_color(self.fpga_image, color) 


    def remove_tab(self, index):
        self.tab_view.removeTab(index)


class MainForm(QMainWindow):
    def __init__(self):
        super (MainForm, self).__init__()
        self.actions = actions.Actions()
        self.setWindowTitle("Nysa Host")
        self.main_panel = MainPanel()
        self.setCentralWidget(self.main_panel)

        #### Actions

        #Exit the application
        exit_action = QAction('&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(quit)

        #Show the status window
        status_window_action = QAction("View Status Window", self)
        status_window_action.setShortcut('F4')
        status_window_action.triggered.connect(self.main_panel.toggle_status_view)

        #Refresh Platform Tree
        refresh_platform = QAction("Refresh &Platform Tree", self)
        refresh_platform.setShortcut('F2')
        refresh_platform.triggered.connect(self.actions.refresh_signal)

        #Toolbar
        self.toolbar = self.addToolBar("main")
        self.toolbar.addAction(exit_action)

        #Menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        nysa_menu = menubar.addMenu('&Nysa')
        nysa_menu.addAction(refresh_platform)

        view_menu = menubar.addMenu('&View')
        view_menu.addAction(status_window_action)

        self.show()

    def get_fpga_view(self):
        return self.main_panel.get_fpga_view()

    def closeEvent(self, event):
        super (MainForm, self).closeEvent(event)
        quit()

    def add_tab(self, widget, name):
        """
        Returns an index of the tab
        """
        return self.main_panel.add_tab(widget, name)

    def remove_tab(self, index):
        self.main_panel.remove_tab(index)


