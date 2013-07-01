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
  6/24/2013: Initial commit
'''

import os
import sys
import json

from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.editor.editor import Editor

from signal_tree_table import SignalTreeTableModel

class ConstraintEditor (QWidget, itab_item.ITabItem):

    output = None

    def __init__(self, parent, actions, output, project_name):
        QWidget.__init__(self, parent)
        itab_item.ITabItem.__init__(self)

        self.actions = actions
        self.ID = project_name + "_constraints"
        self.lang = "Constraint Editor"
        self.output = output
        self.connect_callback = None
        self.disconnect_callback = None

        self.signal_table = None
        self.pin_table = None
        self.connection_table = None

        #self.initialize_view()
        #self.show()

    def clear_all(self):
        row_count = self.signal_model.rowCount()
        for i in range(row_count):
            self.signal_model.removeRow(0)

        row_count = self.pin_model.rowCount()
        for i in range(row_count):
            self.pin_model.removeRow(0)
        self.connection_table.clear()


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
        connect.clicked.connect(self.connect)

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
        self.signal_table = SignalTable()

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
        header = ["Module", "Port", "Direction", "Pin Name", "Disconnect"]
        self.connection_table = ConnectionTable()
        self.connection_table.set_delete_callback(self.notify_connection_delete)
        self.connection_table.setColumnCount(len(header))
        self.connection_table.setHorizontalHeaderLabels(header)
        #self.connection_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        #self.connection_model = ConnectionModel([[]], header_data = header, parent = self)
        #self.connection_table.setModel(self.connection_model)

        #Show the grids
        self.connection_table.setShowGrid(True)

        #Vertical tab settings
        vh = self.connection_table.verticalHeader()
        vh.setVisible(True)

        #Set horizontal header properties
        hh = self.pin_table.horizontalHeader()
        hh = self.connection_table.horizontalHeader()
        hh.setStretchLastSection(True)

    def add_signal(self, color, module_name, name, signal_range, direction):
        print "Adding Signal"
        #pos = self.signal_model.rowCount()
        #self.output.Debug(self, "Adding signal")
        #self.signal_model.insertRows(pos, 1)
        #self.signal_model.set_line_data([module_name, port, direction])
        self.signal_table.add_signal(color, module_name, name, signal_range, direction)

    def remove_signal(self, module_name, port):
        print "Removing Signal"
        return
        #get data from the model
        #search each entry for a module name
        #print "Remove signal"
        pos = self.signal_model.find_pos([module_name, port])
        if pos != -1:
            #print "Remove position: %d" % pos
            self.output.Debug(self, "Signal Table: Remove Position: %d" % pos)

            success = self.signal_model.removeRow(pos)
            self.output.Debug(self, "%s: Removing: %s %s" % (str(success), module_name, port))

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
            
    def add_connection(self, module_name, port, direction, pin_name):
        pos = self.connection_table.rowCount()
        self.output.Debug(self, "Adding Connection")

        self.connection_table.insertRow(pos)
        self.connection_table.set_row_data(pos, [module_name, port, direction, pin_name])

    def remove_connection(self, module_name, port):
        pos = self.connection_table.find_pos(module_name, port)

        if pos != -1:
            self.output.Debug(self, "Connection Table: Remove Position: %d" % pos)
            success = self.connection_table.removeRow(pos)
            if success:
                self.output.Debug(self, "Removed Signal")

    def set_controller(self, controller):
        self.controller = controller

    def notify_connection_delete(self, row_data):
        print "Disconnect Row Data: %s" % str(row_data)
        self.add_signal(row_data[0], row_data[1], row_data[2])
        self.add_pin(row_data[3])
        self.remove_connection(row_data[0], row_data[1])
        if self.disconnect_callback is not None:
            self.disconnect_callback(row_data[0], row_data[1], row_data[2], row_data[3])

    def connect(self):
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
        signal_row = signal_index_list[0].row()
        pin_row = pin_index_list[0].row()
        connection = []
        signal_data = self.signal_model.get_row_data(signal_row)
        pin_data = self.pin_model.get_row_data(pin_row)
        connection.extend(signal_data)
        connection.extend(pin_data)
        self.signal_model.removeRow(signal_row)
        self.pin_model.removeRow(pin_row)
        self.add_connection(connection[0], connection[1], connection[2], connection[3])
        if self.connect_callback is not None:
            self.connect_callback(connection[0], connection[1], conneciton[2], connection[3])


        #print "Connection: %s" % str(connection)
        self.output.Info(self, "Connect: %s" % str(connection))
               


class ConnectionTable(QTableWidget):
    def __init__(self, parent = None):
        super(ConnectionTable, self).__init__(parent)
        self.delete_callback = None

    def set_delete_callback(self, callback):
        self.delete_callback = callback


    def set_row_data(self, row, data):
        for i in range(len(data)):
            #print "Adding: %s to the cell" % data[i]
            self.setItem(row, i, QTableWidgetItem(data[i]))


        btn = QPushButton("Disconnect")
        #btn.clicked.connect(self.disconnect_clicked)
        cb = lambda who=row: self.disconnect_clicked(who)
        self.connect(btn, SIGNAL("clicked()"), cb)
        self.setCellWidget(row, self.columnCount() - 1, btn)

    def find_pos(self, module_name, port):
        print "Number of rows: %d" % self.rowCount()
        for i in range(self.rowCount()):
            #print "Row pos: %d" % i
            mname = self.item(i, 0)
            pname = self.item(i, 1)
            if mname is None:
                print "Module name in table is None"
                return -1
            if pname is None:
                print "Port name in table is none"
                return -1


            if module_name == mname.text() and port == pname.text():
                return i

        return -1

    def disconnect_clicked(self, row):
        #print "Disconnect clicked on Row: %d" % row
        if self.rowCount() == 1:
            row = 0
        row_data = []
        print "Row: %d" % row
        for i in range (self.columnCount() - 1):
            row_data.append(self.item(row, i).text())

        self.delete_callback(row_data)


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
            #if role == Qt.DecorationRole:
            #    node = self.nodeFromIndex(index)
            #    if node is None:
            #        return QVariant()
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

    def __init__(self, parent=None):
        super(SignalTable, self).__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows |
                                  QAbstractItemView.SingleSelection)
        self.setUniformRowHeights(True)
        self.m = SignalTreeTableModel(self)
        #A tree of two depth to allow users to select isolate modules
        self.setModel(self.m)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)

        self.expand(self.rootIndex())

    def add_signal(self, color, module_name, name, signal_range, direction):
        #fields = [module_name, name, signal_range, direction]
        self.m.addRecord(color, module_name, name, signal_range, direction)

    def remove_signal(self, module_name, name, index=-1):
        print "Impliment me!!"

    def activated(self, index):
        print "Actived: %d, %d" % (index.row(), index.column())
        self.emit(SIGNAL("activated"), self.model().asRecord(index))


    def selectionChanged(self, a, b):
        print "Selection Changed"
        super (SignalTable, self).selectionChanged(a, b)
