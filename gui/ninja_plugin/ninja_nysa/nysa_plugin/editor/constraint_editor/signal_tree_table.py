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
import bisect
import codecs
from PyQt4.QtCore import *
from PyQt4.QtGui import *

KEY, NODE = range(2)

from tree_table import TreeTableModel
from tree_table import BranchNode
from tree_table import LeafNode

class IndexSignalLeafNode(LeafNode):
    def __init__(self, signal_name, signal_index, direction):
        fields = [signal_name, str(signal_index), direction]
        super(IndexSignalLeafNode, self).__init__(fields)
        self.signal_name = signal_name
        self.signal_index = signal_index
        self.direction = direction


    def field(self, column):
        if column == 0:
            #print "Get column 0"
            return ""
        if column == 1:
            #print "Get column 1"
            return self.signal_name
        if column == 2:
            #print "Get column 2"
            return str(self.signal_index)
        if column == 3:
            #print "Get column 3"
            return self.direction

class SignalLeafNode(LeafNode):

    def __init__(self, signal_name, signal_range, direction, parent = None):
        fields = [signal_name, str(signal_range), direction]
        super (SignalLeafNode, self).__init__(fields, parent)
        self.signal_name = signal_name
        self.signal_range = signal_range
        self.direction = direction
        self.children = []
        #if there is a range add all the index sigal leaf nodes
        if self.has_range():
            for i in range (min(signal_range), max(signal_range) + 1):
                isln = IndexSignalLeafNode(self.signal_name, i, self.direction)
                isln.parent = self
                self.children.insert(0, isln)

    def __len_(self):
        return len(self.signal_name, self.signal_range, self.direction)

    def row_count(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row]

    def has_range(self):
        if self.signal_range is None:
            return False
        if type(self.signal_range) is tuple and self.signal_range[0] != self.signal_range[1]:
            return True

    def hasLeaves(self):
        if self.has_range():
            return True
        return False

    def field(self, column):
        if column == 0:
            #print "Get column 0"
            return ""
        if column == 1:
            #print "Get column 1"
            return self.signal_name
        if column == 2:
            if self.has_range():
                #print "Get column 2 with range"
                return "[%d:%d]" % (max(self.signal_range), min(self.signal_range))
            else:
                #print "Get column 2"
                return ""
        if column == 3:
            #print "Get column 3"
            return self.direction


class ModuleBranchNode(BranchNode):
    def __init__(self, color, name, parent=None):
        super(ModuleBranchNode, self).__init__(name, parent)
        self.color = color
        self.icon = QIcon(name)
        pm = self.icon.pixmap(22, 15)
        pm.fill(QColor(self.color))
        self.pm = QPixmap(22, 15)
        self.pm.fill(QColor(color))

    def get_icon(self):
        return self.icon

    def get_pixmap(self):
        return self.pm

class RootBranchNode(BranchNode):
    def __init__(self, name, parent=None):
        super(RootBranchNode, self).__init__(name, parent)

    def __len__(self):
        return len(self.children)

    def childWithKey(self, key):
        if not self.children:
            return None
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        #print "self.children[i][KEY]: %s ? key: %s" % (self.children[i][KEY], key)
        
        if self.children[i][KEY] == key:
            #print "\tFound it"
            return self.children[i][NODE]
        return None

    def hasLeaves(self):
        return False


class SignalTreeTableModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(SignalTreeTableModel, self).__init__(parent)
        self.columns = 0
        #Empty Branch Node is the root
        self.root = RootBranchNode("")
        self.headers = ["Module", "Port", "index", "Direction"]
        self.nesting = 2
        self.columns = len(self.headers)

    def addRecord(self, color, module_name, signal_name, signal_range, direction, callReset=True):
        #print "TT: add record"
        fields = [module_name, signal_name, signal_range, direction]
        assert len(fields) > self.nesting
        root = self.root
        module_branch = None

        #See if we can find the module name
        key = module_name.lower()
        #print "Looking for: %s" % key
        module_branch = root.childWithKey(module_name.lower())

        if module_branch is None:
            #print "\tDidn't find it, creating"
            #Need to create this new branch
            module_branch = ModuleBranchNode(color, module_name)
            root.insertChild(module_branch)

        #Add the signal
        key = signal_name.lower()
        sl = module_branch.childWithKey(key)
        if sl is None:
            sl = SignalLeafNode(signal_name, signal_range, direction)
            module_branch.insertChild(sl)
        if callReset:
            self.reset()


    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, IndexSignalLeafNode):
            return leaf.asRecord()
        return []

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:             
            return 0
        if isinstance(node, IndexSignalLeafNode):
            return 0
        if isinstance(node, SignalLeafNode):
            return node.row_count()

        return len(node)


    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop|Qt.AlignLeft)
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            
            #print "TT: Decoration role at %d, %d: %s" % (index.row(), index.column(), node.toString())
            if isinstance(node, ModuleBranchNode) and index.column() == 0:
                return node.get_pixmap()
        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, ModuleBranchNode):
            if index.column() == 0:
                #return node.get_icon()
                #return node.get_pixmap()
                return node.toString()

        elif isinstance(node, BranchNode):
            if index.column() == 0:
                node_value = node.toString()
            #print "TT: Get Module Node at %d, %d: %s" % (index.row(), index.column(), node_value)
            return node.toString() \
                if index.column() == 0 else ""
        elif isinstance(node, SignalLeafNode):
            #Found a Signal Leaf Node
            node_value = node.field(index.column())
            #print "TT: Get signal leaf node at: %d, %d: %s" % (index.row(), index.column(), node_value)

        elif isinstance(node, IndexSignalLeafNode):
            #Found index signal leaf node
            node_value = node.field(index.column())
            #print "TT: Get the indexed signal at: %d, %d: %s" % (index.row(), index.column(), node_value)
        return node_value


    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
           role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            #return QVariant(self.headers[section])
            return self.headers[section]
        #return QVariant()


    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)


    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root


