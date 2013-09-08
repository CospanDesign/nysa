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

import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *



class IBuilderPropertiesDialog(QDialog):

    def __init__(self, project_directory, relative):
        super (IBuilderPropertiesDialog, self).__init__()

        #User variables
        self.success = False

        self.initial_relative = relative
        self.initial_output_dir = ""


        self.project_directory = project_directory

        output_location_label = QLabel("Output Location")
        self.relative_checkbox = QCheckBox("Relative to Project")
        self.relative_checkbox.setChecked(relative)
        self.output_location = QLineEdit("output")
        choose_destination_button = QPushButton("Browse...")

        #Accept/Reject buttons
        ok_button = QPushButton("&OK")
        cancel_button = QPushButton("Cancel")

        #Main Layout
        layout = QGridLayout()
        layout.addWidget(output_location_label, 0, 0)
        layout.addWidget(self.relative_checkbox, 0, 1)
        layout.addWidget(self.output_location, 1, 0, 1, 4)
        layout.addWidget(choose_destination_button, 1, 4)

        #Button Layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout, 2, 0, 1, 5)

        self.setLayout(layout)

        #Connect signals to slots
        self.connect(ok_button, SIGNAL("clicked()"), self, SLOT("accept()"))
        self.connect(cancel_button, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.connect(choose_destination_button, SIGNAL("clicked()"), 
                self.load_folder)
        self.relative_checkbox.stateChanged.connect(self.relative_state_changed)

        self.setWindowTitle("IBuilder Properties")

    def relative_state_changed(self):
        print "relative state changed"
        directory = ""
        if self.relative_checkbox.isChecked():
            directory = self.output_location.text()
            if self.project_directory in directory:
                directory = directory.partition(self.project_directory)[2]
                directory = directory.strip(os.path.sep)
            else:
                directory = self.initial_output_dir
        else:
            directory = (self.project_directory + 
                         os.path.sep +
                         self.output_location.text())

        self.output_location.setText(directory)
        
    def load_folder(self):
        start_dir = ""
        if self.relative_checkbox.isChecked():
            start_dir = os.path.join(self.project_directory,
                                     self.output_location.text())
        else:
            start_dir = (self.project_directory + 
                        os.path.sep + 
                        self.output_location.text())


        text = QFileDialog.getExistingDirectory(self,
                caption = "Select An Output Directory",
                directory = start_dir)

        if self.relative_checkbox.isChecked():
            if self.project_directory in text:
                text = text.partition(self.project_directory)[2]
                text = text.strip(os.path.sep)

        self.output_location.setText(text)

    def set_initial_absolute_output_directory(self, output_dir):
        self.initial_relative = False
        self.initial_output_dir = output_dir
        self.relative_checkbox.setChecked(False)
        self.output_location.setText(output_dir)

    def set_initial_relative_output_directory(self, output_dir):
        self.initial_relative = True
        self.initial_output_dir = output_dir
        self.relative_checkbox.setChecked(True)
        self.output_location.setText(output_dir)

    def go(self):
        if self.exec_():
            self.success = True
        else:
            self.success = False

    def results(self):
        #Return everything in the form of a tuple
        results = [] 
        if self.success:
            results = [self.relative_checkbox.isChecked(),
                       self.output_location.text()]
        else:
            results = [self.initial_relative,
                       self.initial_output_dir]
        return tuple(results)

def ibuilder_properites_dialog(project_directory, relative, output_directory):
    dlg = IBuilderPropertiesDialog(project_directory, relative)
    if relative:
        dlg.set_initial_relative_output_directory(output_directory)
    else:
        dlg.set_initial_absolute_output_directory(output_directory)
    dlg.go()
    return dlg.results()


