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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

KEY, NODE = range(2)

from tree_table import TreeTableModel
from tree_table import BranchNode
from tree_table import LeafNode

class IndexConstraintLeafNode(LeafNode):
    def __init__(self, signal_name, signal_index, direction, constraint_name):
        fields = [signal_name, str(signal_index), direction, constraint_name]
        super(IndexSignalLeafNode, self).__init__(fields)
        self.signal_name = signal_name
        self.signal_index = signal_index
        self.direction = direction
        self.constraint_name = constraint_name

    def field(self, column):
        if column == 0:
            return ""
        if column == 1:
            return self.signal_name
        if column == 2:
            return str(self.signal_index)
        if column == 3:
            return self.direction
        if column == 4:
            return self.constraint_name

    def get_index(self):
        return self.signal_index

    def get_constraint_name(self):
        return self.constraint_name

    def set_constraint_name(self, constraint_name):
        self.constraint_name = constraint_name

    def asRecord(self):
        record = []
        branch = self.parent.parent
        while branch is not None:
            if isinstance(branch, ModuleBranchNode):
                record.insert(0, branch.toString())
                #record.insert(0, str(branch.color))
            branch = branch.parent
        return record + self.fields

class ConstraintLeafNodeRange(LeafNode):
    def __init__(self, signal_name, signal_range, direction, parent = None):
        fields = [signal_name, str(signal_range), direction]
        super (SignalLeafNode, self).__init__(fields, parent)
        self.signal_name = signal_name
        self.signal_range = signal_range
        self.direction = direction
        self.children = []
        #if there is a range add all the index sigal leaf nodes

    def __len_(self):
        return len(self.signal_name, self.signal_range, self.direction)

    def set_constraint(self, index, constraint_name):
        old_constraint = None
        assert min(self.signal_range) <= index < max(self.signal_range)
        c = None
        for child in self.children:
            if child.get_index() == index:
                c = child
                break

        if c is None:
            c = IndexConstraintLeafNode(self.signal_name, index, direction, constraint_name)
            i = 0
            if len(self.children) == 0:
                #found an existing child
            else:
                #Create a new child and put them into the children
                pos = 0
                for child in self.children:
                    compare_index = child.get_index()
                    #this is no the last one
                    if index < compare_index:
                        self.children.insert(pos, c)
                        break

                    #Check if this is the last one
                    if child == self.children[-1]:
                        #This is the last one
                        #put the new child after the last
                        self.children.append(c)
                        break
                    pos = pos + 1

        else:
            old_constraint = c.get_constraint_name()
            c.set_constraint_name(constraint_name):

        return old_constraint


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
            return ""
        if column == 1:
            return self.signal_name
        if column == 2:
            #Don't display the range here, let the children leaf do this
            return ""
        if column == 3:
            return self.direction
        if column == 4:
            return ""


    def orderKey(self):
        if self.has_range():
            out_string = u""
            out_string += self.signal_name
            out_string += "\t%s" % self.direction
            out_string += "\t%s" % self.direction
            return out_string.lower()
        return u"\t".join(self.fields).lower()


    def toString(self, separator="\t"):
        if self.has_range():
            out_string = ""
            out_string += self.signal_name
            out_string += "%s%s" % (separator, self.direction)
            return out_string

        return separator.join(self.fields)

    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            if isinstance(branch, ModuleBranchNode):
                record.insert(0, branch.toString())
            branch = branch.parent
        return record + [self.signal_name, self.direction]


class ConstraintLeafNodeNoRange(LeafNode):

    def __init__(self, signal_name, direction, constraint_name, parent = None):
        fields = [signal_name, direction, constraint_name]
        super (SignalLeafNode, self).__init__(fields, parent)
        self.signal_name = signal_name
        self.direction = direction
        self.constraint_name = constraint_name

    def __len_(self):
        return len(self.signal_name, self.direction, self.constraint_name)

    def row_count(self):
        return 1

    def has_range(self):
        return False

    def hasLeaves(self):
        return False

    def field(self, column):
        if column == 0:
            return ""
        if column == 1:
            return self.signal_name
        if column == 2:
            return ""
        if column == 3:
            return self.direction
        if column == 4:
            return self.constraint_name


    def orderKey(self):
        if self.has_range():
            out_string = u""
            out_string += self.signal_name
            out_string += "\t%s" % self.direction
            out_string += "\t%s" % self.constraint_name
            return out_string.lower()
        return u"\t".join(self.fields).lower()


    def toString(self, separator="\t"):
        if self.has_range():
            out_string = ""
            out_string += self.signal_name
            out_string += "%s%s" % (separator, self.direction)
            out_string += "%s%s" % (separator, self.constraint_name)
            return out_string

        return separator.join(self.fields)

    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            if isinstance(branch, ModuleBranchNode):
                record.insert(0, branch.toString())
                #record.insert(0, str(branch.color))
            branch = branch.parent
        return record + self.fields

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


class ConstraintTreeTableModel(QAbstractItemModel):
    def __init__(self, controller, parent=None):
        super(ConstraintTreeTableModel, self).__init__(parent)
        self.columns = 0
        self.root = RootBranchNode("")
        self.headers = ["Module", "Port", "Index", "Direction", "Constraint Name", "Delete"]
        self.nesting = 2
        self.columns = len(self.headers)
        self.controller = controller

    def flags(self, index):
        node = self.nodeFromIndex(index)
        #need some magic here
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def asRecord(self, index):
        #TODO
        pass

    def addRecord(self, color, module_name, signal_name, index = None, direction, constraint_name, callReset=True):
        if callReset:
            self.reset()


        #TODO
        pass

    def rowCount(self, parent):
        #TODO
        pass


    def data(self, index, role):
        #TODO
        pass

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and \
           role == Qt.DisplayRole:
            assert 0 <= section <= len(self.headers)
            return self.headers[section]

    def columnCount(self, parent):
        return self.columns



    def nodeFromIndex(self, index):
        return index.internalPointer() \
            if index.isValid() else self.root

    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        #TODO
        pass

    def clear(self):
        self.root = BranchNode("")
        self.reset()


