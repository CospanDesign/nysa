# -*- coding: utf-8 *-*

#import re

from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QRadioButton
#from PyQt4.QtGui import QMessageBox


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


SLAVE_TYPE = enum('WISHBONE', 'AXI')


class PagePluginProperties(QWizardPage):

    def __init__(self, locator, output):
        QWizardPage.__init__(self)
        # service locator
        self.locator = locator
        self.output = output
        # grid
        grid = QGridLayout(self)
        grid.addWidget(QLabel('Core Name:'), 0, 0)
        self.txtCore = QLineEdit()
        grid.addWidget(self.txtCore, 0, 1)
        self.registerField('coreName*', self.txtCore)

        grid.addWidget(QLabel("Bus Type"), 1, 0)
        self.axi_radio = QRadioButton("Axi")
        self.wishbone_radio = QRadioButton("Wishbone")
        self.wishbone_radio.setChecked(True)
        #grid.addWidget(QLabel('Wishbone'), 1, 1)
        grid.addWidget(self.wishbone_radio, 1, 1)
        #grid.addWidget(QLabel('Axi'), 2, 1)
        grid.addWidget(self.axi_radio, 2, 1)

        grid.addWidget(QLabel('Author(s):'), 3, 0)
        self.txtAuthors = QLineEdit()
        grid.addWidget(self.txtAuthors, 3, 1)
        self.registerField('txtAuthors*', self.txtAuthors)

        #grid.addWidget(QLabel('Url:'), 4, 0)
        #self.txtUrl = QLineEdit()
        #grid.addWidget(self.txtUrl, 4, 1)

        grid.addWidget(QLabel('Version:'), 5, 0)
        self.txtVersion = QLineEdit("0.1")
        grid.addWidget(self.txtVersion, 5, 1)
        self.func = None

        #Add a second page that is specific to either Axi or wishbone

        #Axi/Wishbone
        #   Add the capability to be a master (arbitrator) Axi/Wisbhone

        #Axi Page:
        #   Add the option to be a simple Axi extension
    def set_slave_type_func(self, func):
        self.func = func

    def validatePage(self):
        if self.axi_radio.isChecked():
            self.func(SLAVE_TYPE.AXI)
        else:
            self.func(SLAVE_TYPE.WISHBONE)

        """
        pat_core_name = re.compile("^[a-z_]+$")
        pat_class_name = re.compile(r"([a-zA-Z_]+[0-9]*)+$")
        if not pat_core_name.match(self.txtModule.text()):
            QMessageBox.information(self, 'Validation error',
                'The core name is invalid')
            return False
        if not pat_class_name.match(self.txtClass.text()):
            QMessageBox.information(self, 'Validation error',
                'The class name is invalid')
            return False
        """
        return True


class CoreCustomize(QWizardPage):
    def __init__(self, locator, output):
        QWizardPage.__init__(self)
        self.locator = locator
        self.output = output
        self.grid = QGridLayout(self)
        self.slave_type = SLAVE_TYPE.WISHBONE
        self.cb_wb_memory_master = None
        self.rb_axi_simple = None
        self.rb_axi_normal = None

    def set_slave_type(self, slave_type):
        if slave_type is SLAVE_TYPE.AXI:
            self.output.Info(self, "AXI Selected")
            self.rb_axi_simple = QRadioButton("Simple Slave")
            self.rb_axi_normal = QRadioButton("Normal Slave")
            self.rb_axi_simple.setChecked(True)
            self.grid.addWidget(self.rb_axi_simple, 1, 0)
            self.grid.addWidget(self.rb_axi_normal, 2, 0)

        elif slave_type is SLAVE_TYPE.WISHBONE:
            self.output.Info(self, "Wishbone Selected")
            self.cb_wb_memory_master = QCheckBox('Master')
            self.grid.addWidget(self.cb_wb_memory_master, 1, 0)

    def validate_page(self):
        return True
