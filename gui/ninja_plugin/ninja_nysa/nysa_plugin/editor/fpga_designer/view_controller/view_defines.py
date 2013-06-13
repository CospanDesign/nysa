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

"""
Add all view controller defines here
"""
from PyQt4.QtGui import *

WISHBONE_LINK_COLOR = QColor("blue")
AXI_LINK_COLOR = QColor("blue")
HOST_INTERFACE_LINK_COLOR = QColor("green")
ARBITOR_LINK_COLOR = QColor("black")


HOST_INTERFACE_SIZE = (100, 200)
HOST_INTERFACE_POS = (-200, 0)
HOST_INTERFACE_COLOR = QColor("yellow")

MASTER_SIZE = (100, 200)
MASTER_POS = (0, 0)
MASTER_COLOR = QColor("orange")

PBUS_SIZE = (100, 200)
PBUS_POS = (200, 150)
PBUS_COLOR = QColor("blue")


MBUS_SIZE = (100, 200)
MBUS_POS = (200, -150)
MBUS_COLOR = QColor("purple")

