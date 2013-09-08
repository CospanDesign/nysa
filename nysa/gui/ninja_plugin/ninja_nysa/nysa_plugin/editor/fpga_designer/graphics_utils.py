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
  6/17/2013: Initial commit
'''

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


def add_label_to_rect(painter, rect, label):
    painter.save()
    r = QRectF(rect)
    br = painter.fontMetrics().boundingRect(label)
    scale = r.width() / br.width()

    if scale >= 1.0:
        painter.drawText(r, Qt.AlignCenter, label)
    else:
        font_height = br.height()
        box_height = r.height()

        painter.scale(scale, scale)
        br.translate(r.left() - br.left(), r.top() - br.top())
        br.translate(0.0, box_height * (0.5 / scale) - font_height / 2)
        painter.drawText(br, Qt.TextSingleLine, label)

    painter.restore()


