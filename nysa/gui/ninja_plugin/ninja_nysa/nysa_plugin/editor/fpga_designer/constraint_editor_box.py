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


#A huge thanks to 'Rapid GUI Programming with Python and Qt' by Mark Summerfield

'''
Log
  6/24/2013: Initial commit
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *


from visual_graph.box import Box

from defines import CONSTRAINT_EDITOR_NAME
from defines import CONSTRAINT_EDITOR_COLOR
from defines import CONSTRAINT_EDITOR_RECT
from defines import CONSTRAINT_EDITOR_POS
from defines import CONSTRAINT_EDITOR_ID


class ConstraintEditorBox(Box):

    def __init__(self, scene):
        super(ConstraintEditorBox, self).__init__(position = CONSTRAINT_EDITOR_POS,
                                                  scene = scene,
                                                  name = CONSTRAINT_EDITOR_NAME,
                                                  color = CONSTRAINT_EDITOR_COLOR,
                                                  rect = CONSTRAINT_EDITOR_RECT,
                                                  user_data = CONSTRAINT_EDITOR_ID)
        self.movable(False)
        self.selectable(False)
        self.s = scene


    def mousePressEvent(self, event):
        self.s.constraint_item_selected()
        super(ConstraintEditorBox, self).mousePressEvent(event)

    def itemChange(self, a, b):
        #if self.isSelected():
        #    self.s.constraint_item_selected()
        #Bypass the box, we don't want this selected
        return QGraphicsItem.itemChange(self, a, b)

