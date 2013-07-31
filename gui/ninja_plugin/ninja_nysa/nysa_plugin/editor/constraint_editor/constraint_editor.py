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
  6/24/2013:
    -Initial commit
  6/30/2013:
    -Added Icons
    -Changed view from table to tree view
'''

import os
import sys
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ninja_ide.gui import actions
from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.editor.editor import Editor

from signal_tree_table import SignalTreeTableModel
from constraint_tree_table import ConstraintTreeTableModel

class ConstraintEditor (QWidget, itab_item.ITabItem):

    output = None

    def __init__(self, parent, nactions, output, controller, filename, project_name):
        QWidget.__init__(self, parent)
        itab_item.ITabItem.__init__(self)

        self.actions = actions.Actions()
        self.nactions = nactions
        self.ID = filename
        self.lang = "Constraint Editor"
        self.output = output
        self.project_name = project_name
        self.controller = controller
        self.connect_callback = None
        self.disconnect_callback = None

        self.signal_table = None
        self.pin_table = None
        self.connection_table = None

        #self.initialize_view()
        #self.show()
        mc = self.actions.ide.mainContainer
        self.connect(mc,
                     SIGNAL("currentTabChanged(QString)"),
                     self.tab_changed)

    def tab_changed(self, tab_name):
        print "Tab Changed to %s" % tab_name
        if tab_name == self.ID:
            self.refresh_tables()

    def get_project(self):
        return project

    def clear_all(self):
        self.signal_table.clear()

        row_count = self.pin_model.rowCount()
        for i in range(row_count):
            self.pin_model.removeRow(0)
        self.connection_table.clear()

    def refresh_tables(self):
        #Refresh all the tables
        self.controller.refresh_constraint_editor()

    def set_connect_callback(self, connect):
        self.connect_callback = connect

    def set_disconnect_callback(self, disconnect):
        self.disconnect_callback = disconnect

    def initialize_view(self):
        layout = QVBoxLayout()

        unconnected_layout = QVBoxLayout()
        pin_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Horizontal)
        connect = QPushButton("Connect")
        connect.clicked.connect(self.signal_connect)

        unconnected_panel = QWidget(self)
        pin_panel = QWidget(self)

        #Add the signal table to the unconnected layout
        self.create_signal_table()
        self.create_pin_table()
        self.create_connection_table()

        unconnected_layout.addWidget(self.signal_table)
        unconnected_panel.setLayout(unconnected_layout)

        pin_layout.addWidget(self.pin_table)
        pin_panel.setLayout(pin_layout)

        splitter.addWidget(unconnected_panel)
        splitter.addWidget(connect)
        splitter.addWidget(pin_panel)


        layout.addWidget(splitter)
        layout.addWidget(self.connection_table)
        self.setLayout(layout)
        self.show()


    def create_signal_table(self):
        #Setup the Signal Table
        self.signal_table = SignalTable(self.controller)

    def create_pin_table(self):
        self.pin_table = QTableView()
        self.pin_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pin_table.setShowGrid(True)

        header = ["Pin Name"]

        self.pin_model = ConstraintModel([[]], header_data = header, parent = self)
        self.pin_table.setModel(self.pin_model)

        #Show the grids
        self.pin_table.setShowGrid(True)

        #Vertical tab settings
        vh = self.pin_table.verticalHeader()
        vh.setVisible(True)

        #Set horizontal header properties
        hh = self.pin_table.horizontalHeader()
        hh.setStretchLastSection(True)

    def create_connection_table(self):
        self.connection_table = ConnectionTable(self.controller)

    def add_signal(self, color, module_name, name, signal_range, direction):
        self.signal_table.add_signal(color, module_name, name, signal_range, direction)

    def remove_signal(self, module_name, port):
        self.signal_table.remove_signal(module_name, port)
        
    def add_pin(self, pin_name):
        pos = self.pin_model.rowCount()
        self.output.Debug(self, "Adding Pin")
        self.pin_model.insertRows(pos, 1)
        self.pin_model.set_line_data([pin_name])

    def remove_pin(self, pin_name):
        pos = self.pin_model.find_pos([pin_name])
        if pos != -1:
            self.output.Debug(self, "Pin Table: Remove Position: %d" % pos)
            success = self.pin_model.removeRow(pos)
            if success:
                self.output.Debug(self, "Removed Signal")
            
    def add_connection(self, color, module_name, port, direction, pin_name, index = None):
        #print "Adding Connection: %s.%s" % (module_name, port)
        self.connection_table.add_connection(color, module_name, port, index, direction, pin_name)

    def remove_connection(self, module_name, port, index=None):
        self.connection_table.remove_connection(module_name, port, index)

    def set_controller(self, controller):
        self.controller = controller

    def notify_connection_delete(self, row_data):
        print "Disconnect Row Data: %s" % str(row_data)
        self.add_signal(row_data[0], row_data[1], row_data[2])
        self.add_pin(row_data[3])
        self.remove_connection(row_data[0], row_data[1])
        if self.disconnect_callback is not None:
            self.disconnect_callback(row_data[0], row_data[1], row_data[2], row_data[3])

    def signal_connect(self):
        print "Connect"
        signal_index_list = self.signal_table.selectedIndexes()
        pin_index_list = self.pin_table.selectedIndexes()
        if len(signal_index_list) == 0:
            self.output.Info(self, "No signal is selected")
            return

        if len(pin_index_list) == 0:
            self.output.Info(self, "No pin is selected")
            return

        #XXX: Only grab the first row
        signal_index = signal_index_list[-1]
        for signal in signal_index_list:
            print "Signal Location: %d, %d" % (signal.row(), signal.column())

        #print "signal location: %d, %d" % (signal_index.row(), signal_index.column())
        pin_row = pin_index_list[0].row()
        signal = self.signal_table.get_signal(signal_index)
        pin_data = self.pin_model.get_row_data(pin_row)

        #print "signal: %s" % str(signal)
        #print "pin_data: %s" % str(pin_data)

        module_name = signal[0]
        signal_name = signal[1]
        index = None
        if signal[2] != "None":
            index = int(signal[2])
        direction = signal[3]
        loc = pin_data[0]
        self.controller.connect_signal(module_name, signal_name, direction, index, loc)

        #print "Connection: %s" % str(connection)
        #self.output.Info(self, "Connect: %s" % str(connection))
               

class ConstraintModel(QAbstractTableModel):
    def __init__(self, data_in = [[]], header_data=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.array_data = []
        self.header_data = header_data

    def rowCount(self, parent=None):
        return len(self.array_data)

    def columnCount(self, parent):
        return len(self.header_data)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self.array_data[index.row()][index.column()]

    def find_pos(self, data):
        for i in range (len(self.array_data)):
            match = True
            for j in range (len(data)):
                #print "Comparing: %s - %s" % (self.array_data[i][j], data[j])
                if self.array_data[i][j] != data[j]:
                    match = False
                    break
            if match == True:
                #print "Found at %d!" % i
                return i
        return -1

    def get_row_data(self, row):
        return self.array_data[row]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header_data[col]

    def set_line_data(self, data):
        self.array_data.append(data)

    def removeRow(self, pos, parent = QModelIndex()):
        if pos > len(self.array_data):
            return False
        self.beginRemoveRows(parent, pos, pos)
        val = self.array_data[pos]
        self.array_data.remove(val)
        self.endRemoveRows()
        return True

    def insertRows(self, pos, rows, parent = QModelIndex()):
        self.beginInsertRows(parent, pos, pos + rows - 1) 
        self.endInsertRows()
        return True


class SignalTable(QTreeView):

    def __init__(self, controller, parent=None):
        super(SignalTable, self).__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows |
                                  QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.m = SignalTreeTableModel(controller, self)
        #A tree of two depth to allow users to select isolate modules
        self.setModel(self.m)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)

        self.expand(self.rootIndex())

    def add_signal(self, color, module_name, name, signal_range, direction):
        #fields = [module_name, name, signal_range, direction]
        self.m.addRecord(color, module_name, name, signal_range, direction)

    def remove_signal(self, module_name, name, index=-1):
        self.m.removeRecord(module_name, name)

    def get_signal(self, index):
        return self.m.asRecord(index)

    def activated(self, index):
        print "Actived: %d, %d" % (index.row(), index.column())
        self.emit(SIGNAL("activated"), self.model().asRecord(index))

    def clear(self):
        self.m.clear()

    def selectionChanged(self, a, b):
        print "Selection Changed"
        super (SignalTable, self).selectionChanged(a, b)


class ConnectionTable(QTreeView):

    def __init__(self, controller, parent = None):
        super(ConnectionTable, self).__init__(parent)
        #self.setSelectionBehavior(QAbstractItemView.SelectRows | 
        #                          QAbstractItemView.SingleSelection)
        #self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.m = ConstraintTreeTableModel(controller, self)
        self.setModel(self.m)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)
        self.connect(self, SIGNAL("pressed(QModelIndex)"), self.pressed)

    def add_connection(self, color, module_name, name, index, direction, constraint_name):
        return self.m.addRecord(color, module_name, name, index, direction, constraint_name)

    def remove_connection(self, module_name, name, index = None):
        return self.m.removeRecord(module_name, name, index)

    def activated(self, index):
        print "Actived: %d, %d" % (index.row(), index.column())
        self.emit(SIGNAL("activated"), self.model().asRecord(index))

    def pressed(self, index):
        print "Pressed: %d, %d" % (index.row(), index.column())
        self.m.check_pressed(index)

    def clear(self):
        self.m.clear()

