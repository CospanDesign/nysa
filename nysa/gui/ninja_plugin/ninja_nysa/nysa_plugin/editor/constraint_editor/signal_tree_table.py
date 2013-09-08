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

import bisect
from PyQt4.QtCore import *
from PyQt4.QtGui import *

KEY, NODE = range(2)

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common",
                             "tree_table"))

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

    def asRecord(self):
        record = []
        branch = self.parent.parent
        while branch is not None:
            if isinstance(branch, ModuleBranch):
                record.insert(0, branch.toString())
                #record.insert(0, str(branch.color))
            branch = branch.parent
        return record + self.fields



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


    def orderKey(self):
        if self.has_range():
            out_string = u""
            out_string += self.signal_name
            out_string += "\t[%d:%d]" % (max(self.signal_range), min(self.signal_range))
            out_string += "\t%s" % self.direction
            return out_string.lower()
        return u"\t".join(self.fields).lower()


    def toString(self, separator="\t"):
        if self.has_range():
            out_string = ""
            out_string += self.signal_name
            out_string += "%s[%d:%d]" % (separator, max(self.signal_range), min(self.signal_range))
            out_string += "%s%s" % (separator, self.direction)
            return out_string

        return separator.join(self.fields)

    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            if isinstance(branch, ModuleBranch):
                record.insert(0, branch.toString())
                #record.insert(0, str(branch.color))
            branch = branch.parent
        return record + self.fields

class ModuleBranch(BranchNode):
    def __init__(self, color, name, parent=None):
        super(ModuleBranch, self).__init__(name, parent)
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

    def remove_signal(self, signal_name):
        c = None
        for child in self.children:
            if child[NODE].signal_name.lower() == signal_name.lower():
                c = child

        if c is None:
            print "Didn't find child"
            return False
        self.children.remove(c)

class RootBranch(BranchNode):
    def __init__(self, name, parent=None):
        super(RootBranch, self).__init__(name, parent)

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

    def __init__(self, controller, parent=None):
        super(SignalTreeTableModel, self).__init__(parent)
        self.columns = 0
        #Empty Branch Node is the root
        self.root = RootBranch("")
        self.headers = ["Module", "Port", "index", "Direction"]
        self.nesting = 2
        self.columns = len(self.headers)
        self.controller = controller

    def flags(self, index):
        node = self.nodeFromIndex(index)
        if isinstance (node, ModuleBranch):
            return Qt.ItemIsEnabled
        if isinstance (node, BranchNode):
            return Qt.ItemIsEnabled
        if isinstance(node, SignalLeafNode):
            if node.has_range():
                return Qt.NoItemFlags

        if self.controller.item_is_enabled(node.asRecord()):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.NoItemFlags

    def addRecord(self, color, module_name, signal_name, signal_range, direction, callReset=True):
        #print "TT: add record"
        fields = [module_name, signal_name, signal_range, direction]
        assert len(fields) > self.nesting
        root = self.root
        module_branch = None

        #See if we can find the module name
        module_branch = root.childWithKey(module_name.lower())

        if module_branch is None:
            #print "\tDidn't find it, creating"
            #Need to create this new branch
            module_branch = ModuleBranch(color, module_name)
            root.insertChild(module_branch)

        #Add the signal
        key = signal_name.lower()
        sl = module_branch.childWithKey(key)
        if sl is None:
            sl = SignalLeafNode(signal_name, signal_range, direction)
            module_branch.insertChild(sl)
        if callReset:
            self.reset()

    def removeRecord(self, module_name, signal_name):
        module_branch = self.root.childWithKey(module_name.lower())
        module_branch.remove_signal(signal_name.lower())
        self.reset()


    def asRecord(self, index):
        #print "Getting slected index at %d, %d" % (index.row(), index.column())
        leaf = self.nodeFromIndex(index)
        
        if leaf is not None:
            if isinstance(leaf, IndexSignalLeafNode):
                return leaf.asRecord()
            if isinstance(leaf, SignalLeafNode):
                #print "Signal Name: %s" % leaf.signal_name
                if leaf.has_range():
                    #print "Not connecting up vectors yet"
                    return []
                else:
                    return leaf.asRecord()

        #print "Location returned None"
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
            if isinstance(node, ModuleBranch) and index.column() == 0:
                return node.get_pixmap()
        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, ModuleBranch):
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
        #print "Getting index: %d, %d" % (row, column)
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        #print "Finding Parent:"
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            #print "\tParent is none"
            return QModelIndex()

        if isinstance(parent, RootBranch):
            #print "\tParent is root"
            return QModelIndex()

        if isinstance(parent, ModuleBranch):
            #print "\tFinding (Module) for: %s" % str(node.asRecord())
            row = self.root.rowOfChild(parent)
            #print "\t\trow: %s" % row
            assert row != -1
            return self.createIndex(row, 0, parent)


        #print "\tParent type: %s" % str(parent)

        grandparent = parent.parent
        if grandparent is None:
            #print "\tGrandparent is none"
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root

    def clear(self):
        self.root = RootBranch("")
        self.reset()

