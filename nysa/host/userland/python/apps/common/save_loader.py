# Copyright (c) 2014 name (dave.mccoy@cospandesign.com)

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


"""
Save and Load Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QFileDialog

"""
Use callbacks as apposed to signals because there can be multiple instantiations
of this widget and becaue the signals names would be the same we would have
PYQT signal name conflicts
"""
class SaveLoader(QWidget):

    def __init__(self, extensions = [], directory = None, initial_file = None):
        super(SaveLoader, self).__init__()

        #Move all incoming values to class vaues
        self.extensions = extensions
        self.directory = os.path.expanduser("~")
        if directory is not None:
            self.directory = directory
        filename = "new"
        if initial_file is not None:
            filename = initial_file

        #If there are extensions then add the first available one
        if len(self.extensions) > 0:
            filename += "." + self.extensions[0]
        
        self.filename_le = QLineEdit(os.path.join(self.directory, filename))
        #Setup view
        layout = QHBoxLayout()
        load_from_button = QPushButton("Load From >>")
        load_from_button.clicked.connect(self.load_from)

        load_button = QPushButton("Load >")
        load_button.clicked.connect(self.load)

        save_button = QPushButton("> Save")
        save_button.clicked.connect(self.save)

        save_as_button = QPushButton (">> Save As")
        save_as_button.clicked.connect(self.save_as)

        
        layout.addWidget(load_from_button)
        layout.addWidget(load_button)
        layout.addWidget(self.filename_le)
        layout.addWidget(save_button)
        layout.addWidget(save_as_button)

        self.load_callback = None
        self.save_callback = None

        self.setLayout(layout)

    def set_directory(self, directory):
        self.directory = directory

    def set_extensions(self, extensions):
        self.extensions = extensions

    def set_filename(self, filename):
        self.filename_le.setText(filename)

    def get_filename(self):
        return self.filename_le.text()

    def set_load_callback(self, callback):
        self.load_callback = callback

    def set_save_callback(self, callback):
        self.save_callback = callback

    def load_from(self):
        #Show Load Dialog
        filters = None
        if len(self.extensions) == 0:
            filters = ""
        else:
            filters = "Files ("
            for ex in self.extensions:
                filters += " *.%s" % ex
            filters += ")"
 
        #Show Save Dialog
        filename = QFileDialog.getOpenFileName(self,
                                              "Select a location..",
                                              self.directory,
                                              filters)

        if len(filename) > 0:
            self.set_filename(filename)
            self.load()
 
    def load(self):
        if self.load_callback is not None:
            self.load_callback()

    def save(self):
        if self.save_callback is not None:
            self.save_callback()

    def save_as(self):
        filters = None
        if len(self.extensions) == 0:
            filters = ""
        else:
            filters = "Files ("
            for ex in self.extensions:
                filters += " *.%s" % ex
            filters += ")"
            
        #Show Save Dialog
        filename = QFileDialog.getSaveFileName(self,
                                               "Select a location..",
                                               self.directory,
                                               filters)
        if len(filename) > 0:
            self.set_filename(filename)
            self.save() 

