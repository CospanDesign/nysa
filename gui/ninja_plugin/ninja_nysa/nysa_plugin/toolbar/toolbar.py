# -*- coding: utf-8 -*-

import os
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QAction


class Toolbar():

    def __init__(self, toolbar, output):
        self.toolbar = toolbar
        self.output = output
        self.output.Debug(self, "In nysa toolbar class")
        #include the path to the images
        self.images = os.path.join(os.path.dirname(__file__),
                                  "..",
                                  "images")
        self.actions = []

    def add_toolbar_items(self):
        self.output.Debug(self, "Adding toolbar items")
        for action in self.actions:
            #self.output.Debug(self, "Adding action: %s" % str(action))
            self.toolbar.add_action(action)

    def create_test_icon(self, function):
        #self.output.Debug(self, "Creating test icon")
        tipath = os.path.join(self.images, "test.png")
        action = QAction(QIcon(tipath), 'Test', self.toolbar)
        action.setShortcut('Ctrl+T')
        action.triggered.connect(function)
        self.actions.append(action)

    def create_sim_icon(self, function):
        self.output.Debug(self, "Creating sim icon")
        path = os.path.join(self.images, "sim.png")

        action = QAction(QIcon(path), 'Sim', self.toolbar)
        action.setShortcut('F8')
        action.triggered.connect(function)
        self.actions.append(action)

    def create_wave_icon(self, function):
        self.output.Debug(self, "Creating waveform icon")
        path = os.path.join(self.images, "wave.png")

        action = QAction(QIcon(path), 'Wave', self.toolbar)
        action.setShortcut('Ctrl+F8')
        action.triggered.connect(function)
        self.actions.append(action)

    def create_status_icon(self, function):
        self.output.Debug(self, "Creating status focus icon")
        tipath = os.path.join(self.images, "test.png")
        action = QAction(QIcon(tipath), 'Status', self.toolbar)
        action.setShortcut('Ctrl+T')
        action.triggered.connect(function)
        self.actions.append(action)

    def create_build_view_icon(self, function):
        self.output.Debug(self, "Creating build view")
        bvpath = os.path.join(self.images, "build_view.png")
        action = QAction(QIcon(bvpath), "Build View", self.toolbar)
        action.setShortcut('Ctrl+,')
        action.triggered.connect(function)
        self.actions.append(action)

