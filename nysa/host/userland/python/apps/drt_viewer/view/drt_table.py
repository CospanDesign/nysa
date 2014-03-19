# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os


from PyQt4.QtGui import QTreeView
from PyQt4.Qt import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QColor

p = os.path.join(os.path.dirname(__file__), 
                 os.pardir,
                 os.pardir,
                 "common",
                 "tree_table")

#print "Path: %s" % os.path.abspath(p)
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from tree_table.tree_table import TreeTableModel
from tree_table.tree_table import BranchNode
from tree_table.tree_table import LeafNode

KEY, NODE = range(2)

class DRTValueNode(LeafNode):
    def __init__(self, parent, value):
        fields = [value]
        super (DRTValueNode, self).__init__(fields, parent)

    def field(self, column):
        if column == 3:
            return self.fields[0]



class DRTDescriptionBranch(BranchNode):
    def __init__(self, parent, index, raw, description, dev_type):
        name = "Description Branch"
        super (DRTDescriptionBranch, self).__init__(name, parent)
        self.fields = [index, raw, description, ""]
        self.dev_type = dev_type
        
    def __len__(self):
        return len(self.children)

    def orderKey(self):
        #return self.name.toLower()
        return self.name

    def get_type(self):
        return self.name
    
    def get_dev_type(self):
        return self.dev_type

    def is_first_index(self):
        index = int(self.fields[0], 16)
        if index % 8 == 0:
            return True
        return False


    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]

class Root(BranchNode):
    def __init__(self, name, parent=None):
        super (Root, self).__init__("", parent)
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

    def insertChild(self, child):
        print "Insert Child"
        child.parent = self
        self.children.append(child)

    def removeChild(self, child):
        self.children.remove(child)

class DRTTreeModel(TreeTableModel):

    def __init__(self, parent = None):
        super (DRTTreeModel, self).__init__(parent)
        self.root = Root("")
        headers = ["Index", "Row", "Description", "Value"]
        self.initialize(nesting = 1, headers = headers)
        self.font = QFont("White Rabbit")
        self.font.setBold(True)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def rowCount (self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        if isinstance(node, DRTDescriptionBranch):
            return len(node)
        if isinstance(node, DRTValueNode):
            return 0
        return len(node)
        
    def asRecord(self, index):
        node = self.nodeFromIndex(index)

        #Only return valid records
        if node is None:
            return []
        if isinstance(node, Root):
            return []
        if isinstance(node, DRTDescriptionBranch):
            return [node.asRecord()]
        if isinstance(node, DRTValueNode):
            return node.asRecord()

    def addRecord(self, index, raw, description, dev_type, value_list):
        fields = [raw, description, value_list]
        assert len(fields) > self.nesting
        root = self.root

        #There is no branch with that name
        desc_branch = root.childWithKey(index)

        if desc_branch is None:
            #This thing doesn't exist
            #all type branches are children of root
            desc_branch = DRTDescriptionBranch(root, index, raw, description, dev_type)
            root.insertChild(desc_branch)

        for value in value_list:
            value_node = DRTValueNode(desc_branch, value)
            desc_branch.insertChild(value_node)

        #This may not be needed
        self.reset()

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)

        if role == Qt.FontRole:
            return self.font

        if role == Qt.BackgroundColorRole:
            if index.column() == 0:
                if index.row() != 0:
                    node = self.nodeFromIndex(index)
                    if isinstance(node, DRTDescriptionBranch):
                        if node.is_first_index():
                            return QColor.fromRgb(0xC0C0C0)
            if index.column() == 2:
                if index.row() != 0:
                    node = self.nodeFromIndex(index)
                    if isinstance(node, DRTDescriptionBranch):
                        if node.is_first_index():
                            return QColor.fromRgb(0xC0C0C0)
                   
            if index.column() == 1:
                node = self.nodeFromIndex(index)

                if isinstance(node, DRTValueNode):
                    node = node.parent

                dev_type = node.get_dev_type()
                if isinstance(node, DRTDescriptionBranch):
                    if dev_type == None:
                        return QColor.fromRgb(0xBDFCC9)

                    if dev_type == "memory":
                        return QColor.fromRgb(0xDA70D6)

                    return QColor.fromRgb(0xB0C4DE)


        if role != Qt.DisplayRole:
            return


        node = self.nodeFromIndex(index)
        assert node is not None

        node_value = ""
        if isinstance(node, Root):
            return None
        if isinstance(node, DRTDescriptionBranch):
            return node.field(index.column())
        if isinstance(node, DRTValueNode):
            return node.field(index.column())
        return None

class DRTTree(QTreeView):
    
    def __init__(self, parent = None):
        super (DRTTree, self).__init__(parent)
        self.setUniformRowHeights(True)
        self.m = DRTTreeModel(parent)
        self.setModel(self.m)
        self.expand(self.rootIndex())
        self.setMaximumWidth(1000)
 
    def sizeHint(self):
        size = QSize()
        size.setWidth(1000)
        return size

    def add_entry(self, index, raw, description, dev_type, value_list):
        self.m.addRecord(index, raw, description, dev_type, value_list)

    def clear(self):
        self.m.clear()

    def resize_columns(self):
        count = self.m.columnCount(None)
        for i in range(count):
            self.resizeColumnToContents(i)

        self.expandAll()



