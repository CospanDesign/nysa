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
  6/12/2013: Initial commit
'''

from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Note this cannot have a QColor for these two because the values are passed
#through MIME types
PERIPHERAL_COLOR="blue"
MEMORY_COLOR="purple"

LINK_ARBITOR_COLOR = QColor("black")
LINK_BUS_COLOR = QColor("black")
LINK_HOST_INTERFACE_COLOR = QColor("black")
LINK_PORT_COLOR = QColor("black")
LINK_MASTER_COLOR = QColor("black")
LINK_SLAVE_COLOR = QColor("black")
LINK_ARBITOR_MASTER_COLOR = QColor("blue")

HI_COLOR = "yellow"
HOST_INTERFACE_RECT = QRectF(0, 0, 100, 200)
HOST_INTERFACE_POS = QPointF(-200, 0)
HOST_INTERFACE_COLOR = QColor(HI_COLOR)
HOST_INTERFACE_ID = "host_interface"

MASTER_RECT = QRectF(0, 0, 100, 200)
MASTER_POS = QPointF(0, 0)
MASTER_COLOR = QColor("orange")
MASTER_ID = "master"

PERIPHERAL_BUS_RECT = QRectF(0, 0, 100, 200)
PERIPHERAL_BUS_POS = QPointF(200, -150)
PERIPHERAL_BUS_COLOR = QColor("blue")
PERIPHERAL_BUS_ID = "peripheral_bus"

MEMORY_BUS_RECT = QRectF(0, 0, 100, 200)
MEMORY_BUS_POS = QPointF(200, 150)
MEMORY_BUS_COLOR = QColor("purple")
MEMORY_BUS_ID = "memory_bus"

ARB_MASTER_RECT = QRectF(0, 0, 100, 25)
ARB_MASTER_HORIZONTAL_SPACING = 50
ARB_MASTER_VERTICAL_SPACING = 25
ARB_MASTER_COLOR = QColor("white")

ARB_MASTER_ACT_RECT = QRectF(0, 0, 100, 50)
ARB_MASTER_ACT_COLOR = QColor("green")

ARB_MASTER_EXPAND_OFFSET = 300

SLAVE_RECT = QRectF(0, 0, 100, 50)
SLAVE_VERTICAL_SPACING = 50
SLAVE_HORIZONTAL_SPACING = 50

PS_COLOR = "blue"
PERIPHERAL_SLAVE_COLOR = QColor(PS_COLOR)

MS_COLOR = "purple"
MEMORY_SLAVE_COLOR = QColor(MS_COLOR)
BEZIER_CONNECTION = False

