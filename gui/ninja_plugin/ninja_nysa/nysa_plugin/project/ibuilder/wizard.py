# -*- coding: utf-8 -*-

import inspect
from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRadioButton
#from PyQt4.QtGui import QMessageBox

class PageBoardSelection(QWizardPage):
    def __init__(self, locator, output):
        QWizardPage.__init__(self)
        self.locator = locator
        self.output = output
        # grid
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Select a target board from the following list'), 0, 0)

    def validatePage(self):
        self.output.Debug(self, "Validate board selection page")
        return True

