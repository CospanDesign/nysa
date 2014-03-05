#!/usr/bin/env python
# Copyright (c) 2007-8 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.


"""
This code was mostly taken from the Rapid Gui Development with Python and Qt

as such this file uses the GNU copyright

by: Mark Summerfield

"""

import sys
import os
import hashlib

import bisect
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


KEY, NODE = range(2)

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common",
                             "tree_table"))


sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from status import Status
from actions import Actions

from tree_table import TreeTableModel
from tree_table import BranchNode
from tree_table import LeafNode


class DeviceNode(LeafNode):
    def __init__(self, unique_id, data):
        fields = ["", unique_id]
        self.data = data
        m = hashlib.md5()
        m.update(unique_id)
        h = int(m.hexdigest(), 16)
        #print "Hex: 0x%08X" % h
        #Boost the light level, it would be very difficult to see if the
        #Background Color is too dark

        red = ((h >> 16) & 0xFF) | 0x40
        green = ((h >> 8) & 0xFF) | 0x40
        blue = (h & 0xFF) | 0x40
        self.color = QColor(red, green, blue)
        super (DeviceNode, self).__init__(fields)

    def field(self, column):
        '''
        Override the fields function so we only show the unique_id and
        not the type
        '''
        return self.fields[column]

    def get_id(self):
        return self.fields[1]

    def orderKey(self):
        return self.fields[1].toLower()

    def get_data(self):
        return self.data

    def get_color(self):
        return self.color

class TypeBranch(BranchNode):
    def __init__(self, name, parent = None):
        super (TypeBranch, self).__init__(name, parent)

    def __len__(self):
        return len(self.children)

    def remove_device(self, unique_id):
        c = None
        node = None
        for child in self.children:
            if child[NODE].get_id() == unique_id:
                c = child
                node = c[NODE]

        if node is None:
            return False

        self.children.remove(c)
        return True

    def childWidthKey(self, key):
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None

    def get_device(self, unique_id):
        for child in self.children:
            if child[NODE].get_id() == unique_id:
                return child[NODE]

    def get_type(self):
        return self.name


class RootBranch(BranchNode):
    def __init__(self, name, parent=None):
        super (RootBranch, self).__init__("", parent)
        self.parent = None

    def __len__(self):
        return len(self.children)

    def childWithKey(self, key):
        key = key.toLower()
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if self.children[i][KEY] == key:
            return self.children[i][NODE]

        if i < 0 or i >= len(self.children):
            return None

    def remove_type(self, type_name):
        c = None
        for child in self.children:
            if child[NODE].name.toLower() == type_name:
                c = child
                break
        self.children.remove(c)

    def removeChild(self, child):
        self.children.remove(child)


class PhyTreeTableModel(QAbstractItemModel):
    def __init__(self, parent = None):
        super (PhyTreeTableModel, self).__init__(parent)
        self.root = RootBranch("")
        self.headers = ["Type", "UID"]
        self.nested = 1
        self.columns = len(self.headers)

        self.font = QFont("White Rabbit")
        self.font.setBold(True)
        self.status = Status()


    def flags (self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount (self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, DeviceNode):
            return 0
        return len(node)

    def asRecord(self, index):
        node = self.nodeFromIndex(index)
        self.status.Debug(self, "node: %s" % str(node))

        #Only return valid records
        if node is None:
            return []
        if isinstance(node, RootBranch):
            return []
        if isinstance(node, TypeBranch):
            return []
        if isinstance(node, DeviceNode):
            return node.asRecord()

    def get_nysa_device(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return node.get_data()
        return None

    def get_nysa_type(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return node.parent.get_type()
        return None

    def addRecord(self, dev_type, unique_id, data):
        fields = [dev_type, unique_id]
        assert len(fields) > self.nested
        root = self.root

        #There is no branch with that name
        type_branch = root.childWithKey(dev_type)

        if type_branch is None:
            #This thing doesn't exist
            #all type branches are children of root
            type_branch = TypeBranch(dev_type, root)
            root.insertChild(type_branch)

        device_node = type_branch.get_device(unique_id = unique_id)
        if device_node is None:
            device_node = DeviceNode(unique_id, data)
            type_branch.insertChild(device_node)

        #This may not be needed
        self.reset()

    def removeRecord(self, unique_id):
        root = self.root
        dev_node = None
        type_branch = None
        for branch_index in range (len(root)):
            branch = root.childAtRow(branch_index)
            for dev_index in range(len(branch)):
                child = branch.childAtRow(dev_index)
                if child.get_id() == unique_id:
                    dev_node = child
                    break
                
            if dev_node is not None:
                type_branch = branch
                break

        if dev_node is not None:
            type_branch.removeChild(dev_node)
            dev_node = None

        if len(type_branch) == 0:
            root.removeChild(type_branch)
            type_branch = None

        #This may not be needed
        self.reet()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return self.headers[section]

    def columnCount(self, parent):
        return len(self.headers)

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.root

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column, branch.childAtRow(row))
        
    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        if isinstance(node, tuple):
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()


        if isinstance (parent, RootBranch):
            return self.createIndex(0, 0, parent)

        if isinstance (parent, TypeBranch):
            row = self.root.rowOfChild(parent)
            return self.createIndex(row, 0, parent)

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def clear (self):
        self.root = RootBranch("")
        self.reset()

    def is_nysa_device(self, index):
        node = self.nodeFromIndex(index)
        if isinstance(node, DeviceNode):
            return True
        return False

    def first_device_index(self):
        for r in range(len(self.root)):
            type_branch = self.root.childAtRow(r)
            for cr in range(len(type_branch)):

                dev_node = type_branch.childAtRow(cr)
                if dev_node is None: 
                    continue
                grandparent = self.root
                roc = grandparent.rowOfChild(type_branch)
                #print "Found Row of child: %d" % roc
                #print "Type: %s" % dev_node.parent.get_type()
                return self.createIndex(roc, 0, dev_node)

        return None

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)
        '''
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if isinstance(node, TypeBranch)
                if index.column() == 0:
                    return node.get_pixmap()
        '''
        if role == Qt.BackgroundColorRole:
            node = self.nodeFromIndex(index)
            if not isinstance(node, DeviceNode):
                return

            if index.column() == 1:
                return QBrush(node.get_color())

        

        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, RootBranch):
            return None
        if isinstance(node, TypeBranch):
            if index.column() == 0:
                return node.toString()
            return None
        if isinstance(node, DeviceNode):
            return node.field(index.column())
        return None

class PhyTree(QTreeView):
    def __init__(self, parent = None):
        super (PhyTree, self).__init__(parent)
        self.setUniformRowHeights(True)
        self.m = PhyTreeTableModel()
        self.setModel(self.m)
        self.expand(self.rootIndex())
        self.status = Status()
        self.actions = Actions()
        self.actions.add_device_signal.connect(self.add_device)
        self.actions.clear_phy_tree_signal.connect(self.clear)
        self.actions.phy_tree_get_first_dev.connect(self.select_first_item)
        self.status.Debug(self, "Phy Tree View Started!")
        self.setMaximumWidth(300)
        
        hdr = self.header()
        #hdr.setStretchLastSection (False)
        hdr.setDefaultSectionSize(90)
        self.connect(self, SIGNAL("activated(QModelIndex)"), self.activated)
        self.connect(self, SIGNAL("pressed(QModelIndex)"), self.item_pressed)
        #self.connect(self, SIGNAL("SelectionChanged(QModelIndex)"), self.item_pressed)
        self.sm = QItemSelectionModel(self.m)
        self.setSelectionModel(self.sm)

    def sizeHint (self):
        size = QSize()
        size.setWidth(300)
        return size

    def add_device(self, dev_type, unique_id, data):
        print "Adding: %s" % dev_type
        self.m.addRecord(dev_type, unique_id, data)
        self.expandAll()

    def remove_device(self, unique_id):
        self.m.removeRecord(unique_id)

    def get_unique_id(self, index):
        self.m.asRecord(index)

    def activated(self, index):
        self.status.Debug(self, "Activated: %d, %d" % (index.row(), index.column()))
        #super(PhyTree, self).activated(index)

    def clear(self):
        self.m.clear()

    def select_first_item(self):
        self.status.Debug(self, "Selecting first device in phy tree")
        index = self.m.first_device_index()
        if index is not None:
            nysa_dev = self.m.get_nysa_device(index)
            nysa_type = self.m.get_nysa_type(index)
            uid = self.m.nodeFromIndex(index).get_id()
            #print "Type: %s" % nysa_type
            #print "Device: %s" % str(type(nysa_dev))
            #print "ID: %s" % uid
            self.actions.phy_tree_changed_signal.emit(uid, nysa_type, nysa_dev)
            self.sm.select(index, QItemSelectionModel.Rows | QItemSelectionModel.Select)

    def item_pressed(self, index):
        self.status.Debug(self, "Pressed: %d, %d" % (index.row(), index.column()))
        if not self.m.is_nysa_device(index):
            return

        nysa_dev = self.m.get_nysa_device(index)
        nysa_type = self.m.get_nysa_type(index)
        uid = self.m.nodeFromIndex(index).get_id()
        self.actions.phy_tree_changed_signal.emit(uid, nysa_type, nysa_dev)
