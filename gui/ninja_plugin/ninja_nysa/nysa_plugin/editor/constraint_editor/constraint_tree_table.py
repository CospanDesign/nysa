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
        super(IndexConstraintLeafNode, self).__init__(fields)
        self.signal_name = signal_name
        self.signal_index = signal_index
        self.direction = direction
        self.constraint_name = constraint_name

    def field(self, column):
        #print "ICLN: get column %d" % column
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
            if isinstance(branch, ModuleBranch):
                record.insert(0, branch.toString())
                #record.insert(0, str(branch.color))
            branch = branch.parent
        return record + self.fields

class ConstraintLeafNodeRange(LeafNode):

    def __init__(self, signal_name, direction, parent = None):
        fields = [signal_name, "", direction, ""]
        super (ConstraintLeafNodeRange, self).__init__(fields, parent)
        self.signal_name = signal_name
        self.direction = direction
        self.children = []
        #if there is a range add all the index sigal leaf nodes

    def __len_(self):
        return len([self.signal_name, "index", self.direction, "constraint name"])

    def set_constraint(self, index, constraint_name):
        old_constraint = None
        c = None
        for child in self.children:
            if child.get_index() == index:
                c = child
                break

        if c is None:
            #print "Adding new child"
            c = IndexConstraintLeafNode(self.signal_name, index, self.direction, constraint_name)
            c.parent = self
            i = 0
            if len(self.children) == 0:
                #found an existing child
                self.children.append(c)
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
            c.set_constraint_name(constraint_name)

        return old_constraint

    def remove_signal(self, signal_index):
        print "remove signal index: %d" % index
        c = None
        for child in self.children:
            if child.get_index() == index:
                c = child
                break

        if c is None:
            return False

        self.children.remove(c)
        return True

    def row_count(self):
        return len(self.children)

    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        #print "Getting child"
        #if isinstance(self.children[row], IndexConstraintLeafNode):
        #    print "Instance of index constraint leaf node"
        return self.children[row]

    def has_range(self):
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
            if isinstance(branch, ModuleBranch):
                record.insert(0, branch.toString())
            branch = branch.parent
        return record + [self.signal_name, self.direction]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1




class ConstraintLeafNodeNoRange(LeafNode):

    def __init__(self, signal_name, direction, constraint_name, parent = None):
        fields = [signal_name, direction, constraint_name]
        super (ConstraintLeafNodeNoRange, self).__init__(fields, parent)
        self.signal_name = signal_name
        self.direction = direction
        self.constraint_name = constraint_name

    def __len_(self):
        return len(self.signal_name, self.direction, self.constraint_name)


    def get_constraint(self):
        return self.constraint_name

    def set_constraint(self, constraint_name):
        self.constraint_name = constraint_name

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

    def __len__(self):
        return len(self.children)

    def get_icon(self):
        return self.icon

    def get_pixmap(self):
        return self.pm

    def remove_signal(self, signal_name, signal_index = None):
        c = None
        for child in self.children:
            print "Checking: %s with %s" % (child[NODE].signal_name.lower(), signal_name)
            if child[NODE].signal_name.lower() == signal_name:
                c = child

        if c is None:
            print "didn't find child"
            return False

        if signal_index is not None:
            if c.remove_signal(signal_index):
                if c.row_count() == 0:
                    self.children.remove(c)
        else:
            self.children.remove(c)
        return True

    def childWithKey(self, key):
        if not self.children:
            return None
        print "Getting child with key: %s" % key
        i = bisect.bisect_left(self.children, (key, None))
        if i < 0 or i >= len(self.children):
            return None
        if self.children[i][KEY] == key:
            return self.children[i][NODE]
        return None

    def get_signal(self, signal_name, signal_index = None):
        for child in self.children:
            print "Checking: %s" % child[NODE].signal_name
            if child[NODE].signal_name.lower() == signal_name:
                return child[NODE]
        return None        

class RootBranch(BranchNode):
    def __init__(self, name, parent=None):
        super(RootBranch, self).__init__("", parent)

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

    def remove_module(self, module_name):
        c = None
        for child in self.children:
            if child[NODE].name.lower() == module_name:
                c = child
                break
        self.children.remove(c)

    def removeChild(self, child):
        #assert child in self.children[NODE]:
        self.children.remove(child)


class ConstraintTreeTableModel(QAbstractItemModel):
    def __init__(self, controller, parent=None):
        super(ConstraintTreeTableModel, self).__init__(parent)
        self.columns = 0
        self.root = RootBranch("")
        self.headers = ["Module", "Port", "Index", "Direction", "Constraint Name", "Delete"]
        self.nesting = 2
        self.columns = len(self.headers)
        self.controller = controller

    def flags(self, index):
        node = self.nodeFromIndex(index)
        #need some magic here
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        #Basically only return valid records
        if leaf is None:
            return []
        if isinstance(leaf, ModuleBranch):
            return []
        if isinstance(leaf, RootBranch):
            return []
        if isinstance(leaf, ConstraintLeafNodeNoRange): 
            return leaf.asRecord
        if isinstance(leaf, ConstraintLeafNodeRange):
            return []
        if isinstance(leaf, IndexConstraintLeafNode): 
            return leaf.asRecord

    def addRecord(self, color, module_name, signal_name, signal_index, direction, constraint_name, callReset=True):
        old_constraint = None
        if signal_index is None:
            #Add a node that has no range
            fields = [module_name, signal_name, direction, constraint_name]
        else:
            fields = [module_name, signal_name, signal_index, direction, constraint_name]

        assert len(fields) > self.nesting
        root = self.root
        module_branch = None

        #Look for a module that matches
        module_branch = root.childWithKey(module_name.lower())
        if module_branch is None:
            #didn't find, make reference and add it to the root
            module_branch = ModuleBranch(color, module_name)
            root.insertChild(module_branch)

        #Now we have a module node
        sl = module_branch.get_signal(signal_name.lower())
        if sl is None:
            if signal_index is None:
                #signal with no range
                sl = ConstraintLeafNodeNoRange(signal_name, direction, constraint_name)
            else:
                #signal with range
                sl = ConstraintLeafNodeRange(signal_name, direction)
                sl.set_constraint(signal_index, constraint_name)

            module_branch.insertChild(sl)
        else:
            if signal_index is None:
                old_constraint = sl.get_constraint()
                sl.set_constraint(constraint_name)
            else:
                old_constraint = sl.set_constraint(signal_index, constraint_name)

        if callReset:
            self.reset()

        return old_constraint

    def removeRecord(self, module_name, signal_name, signal_index = None):
        print "Remove record"
        root = self.root
        module_branch = root.childWithKey(module_name.lower())
        if module_branch is None:
            return False
        print "Found Module"
        print "Looking for %s" % signal_name
        sl = module_branch.get_signal(signal_name.lower())
        if sl is None:
            return False
        print "Found Leaf"
        if isinstance(sl, ConstraintLeafNodeNoRange):
            #remove this signal from the
            print "removing %s" % signal_name.lower()
            module_branch.remove_signal(signal_name.lower())
            if len(module_branch) == 0:
                #need to remove this module branch too
                root.removeChild(module_branch)
            return True
        if isinstance(sl, ConstraintLeafNodeRange):
            module_branch.remove_signal(signal_name.lower(), signal_index)

        if len(module_branch) == 0:
            root.remove_module(module_name.lower())

        self.reset()



    def rowCount(self, parent):
        #print "Get Row Count: %s" % str(parent)
        node = self.nodeFromIndex(parent)
        #print "Node %s" % str(node)
        if node is None:
            return 0
        if isinstance(node, RootBranch):
            return len(node)
        if isinstance(node, ModuleBranch):
            return len(node)
        if isinstance(node, ConstraintLeafNodeNoRange):
            return 0
        if isinstance(node, ConstraintLeafNodeRange):
            return node.row_count()
        if isinstance(node, IndexConstraintLeafNode):
            return 0
        if isinstance(node, BranchNode):
            return len(node)
        return 0

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)
        if role == Qt.DecorationRole:
            node = self.nodeFromIndex(index)
            if isinstance(node, ModuleBranch):
                if index.column() == 0:
                    return node.get_pixmap()
        if role != Qt.DisplayRole:
            return

        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, RootBranch):
            return None
        if isinstance(node, ModuleBranch):
            if index.column() != 0:
                return None
            return node.toString()
        if isinstance(node, ConstraintLeafNodeNoRange):
            return node.field(index.column())
        if isinstance(node, ConstraintLeafNodeRange):
            return node.field(index.column())
        if isinstance(node, IndexConstraintLeafNode):
            return node.field(index.column())
        return None

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
        #print "Parent: %s" % str(parent)
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        #print "Brance Node: %s" % str(branch)
        #if isinstance(parent, RootBranch):
        #    print "parent is root"
        #if isinstance(parent, ModuleBranch):
        #    print "Parent is module"
        #    print "row: %d" %row
        #    print "column: %d" %column
        #if isinstance(parent, IndexConstraintLeafNode):
        #    print "Parent is index constraint leaf node"
        #    print "row: %d" %row
        #    print "column: %d" %column
        #if isinstance(parent, ConstraintLeafNodeRange):
        #    print "Parent is constraint leaf not with range"
        #    print "row: %d" %row
        #    print "column: %d" %column
        #if isinstance(parent, ConstraintLeafNodeNoRange):
        #    print "parent is constraint leaf node with NO range"
        #    print "row: %d" %row
        #    print "column: %d" %column
        return self.createIndex(row, column,
                                branch.childAtRow(row))

    def parent(self, child):
        #print "Parent called"
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()

        #if isinstance(child, ModuleBranch):
        #    print "Child is module"
        #if isinstance(child, IndexConstraintLeafNode):
        #    print "Child is Index constraint leaf node"
        #if isinstance(child, ConstraintLeafNodeRange):
        #    print "Child is constraint leaf node range"
        #if isinstance(child, ConstraintLeafNodeNoRange):
        #    print "Child is constraint leaf node no range"


        if isinstance(parent, RootBranch):
            #print "parent is root"
            #print "Child is module"
            return self.createIndex(0, 0, parent)
        if isinstance(parent, ModuleBranch):
            #print "Parent is module"
            row = self.root.rowOfChild(parent)
            return self.createIndex(row, 0, parent)
        #if isinstance(parent, IndexConstraintLeafNode):
        #    print "Parent is index constraint leaf node"
        if isinstance(parent, ConstraintLeafNodeRange):
            #print "Parent is constraint leaf node with range"
            grandparent = parent.parent
            #Get the module
            row = grandparent.rowOfChild(parent)
            return self.createIndex(row, 1, parent)
        #if isinstance(parent, ConstraintLeafNodeNoRange):
        #    print "parent is constraint leaf node with NO range"

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def clear(self):
        self.root = BranchNode("")
        self.reset()

