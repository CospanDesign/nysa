# -*- coding: utf-8 *-*

import re

from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
#from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QMessageBox

class PagePluginProperties(QWizardPage):

    def __init__(self, locator):
        QWizardPage.__init__(self)
        # service locator
        self.locator = locator
        # grid
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Core Name:'), 0, 0)
        self.txtModule = QLineEdit()
        grid.addWidget(self.txtModule, 0, 1)
        self.registerField('moduleName*', self.txtModule)

        grid.addWidget(QLabel("Bus Type"), 1, 0)
        self.axi_radio = QRadioButton("Axi")
        self.wishbone_radio = QRadioButton("Wishbone")
        self.wishbone_radio.setChecked(True)
        #grid.addWidget(QLabel('Wishbone'), 1, 1)
        grid.addWidget(self.wishbone_radio, 1, 1)
        #grid.addWidget(QLabel('Axi'), 2, 1)
        grid.addWidget(self.axi_radio, 2, 1)

        grid.addWidget(QLabel('Author(s):'), 2, 0)
        self.txtAuthors = QLineEdit()
        grid.addWidget(self.txtAuthors, 2, 1)
        self.registerField('txtAuthors*', self.txtAuthors)

        grid.addWidget(QLabel('Url:'), 3, 0)
        self.txtUrl = QLineEdit()
        grid.addWidget(self.txtUrl, 3, 1)

        grid.addWidget(QLabel('Version:'), 4, 0)
        self.txtVersion = QLineEdit("0.1")
        grid.addWidget(self.txtVersion, 4, 1)

        '''
        # Plugin services
        grid.addWidget(QLabel('Services:'), 5, 0)

        self.checkEditorS = QCheckBox('Editor')
        grid.addWidget(self.checkEditorS, 6, 0)

        self.checkToolbarS = QCheckBox('Toolbar')
        grid.addWidget(self.checkToolbarS, 6, 1)

        self.checkMenuPluginS = QCheckBox('Menu Plugin')
        grid.addWidget(self.checkMenuPluginS, 6, 2)

        self.checkMiscS = QCheckBox('Misc Container')
        grid.addWidget(self.checkMiscS, 7, 0)

        self.checkExplorerS = QCheckBox('Explorer')
        grid.addWidget(self.checkExplorerS, 7, 1)
        '''

    def validatePage(self):
        pat_module_name = re.compile("^[a-z_]+$")
        #pat_class_name = re.compile(r"([a-zA-Z_]+[0-9]*)+$")
        if not pat_module_name.match(self.txtModule.text()):
            QMessageBox.information(self, 'Validation error',
                'The module name is invalid')
            return False
        """
        if not pat_class_name.match(self.txtClass.text()):
            QMessageBox.information(self, 'Validation error',
                'The class name is invalid')
            return False
        """
        return True
