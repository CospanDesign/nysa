#! /usr/bin/python

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class HexValidator(QValidator):
    
    def __init__(self):
        super (HexValidator, self).__init__()
        self.bottom = 0
        self.top = 255

    def fixup(self, s):
        pass

    def setRange(self, bottom, top):
        self.bottom = bottom
        self.top = top

    def _check_range(self, v):
        if v < self.bottom:
            return False
        if v > self.top:
            return False
        return True


    def validate(self, s, i):
        value = 0
        try:
            value = int(str(s), 16)
            if not self._check_range(value):
                return QValidator.Invalid, i
        except:
            return QValidator.Invalid, i

        return QValidator.Acceptable, i
