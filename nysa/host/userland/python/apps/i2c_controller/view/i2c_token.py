#! /usr/bin/python

import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *


ss = os.path.join(os.path.dirname(__file__), "stylesheet.css")
STYLE = open(ss, "r").read()

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from hex_validator import HexValidator


BAD_VAL = "QLineEdit {                  "\
          " background-color : red      "\
          "}                            "
GOOD_VAL ="QLineEdit {                  "\
          " background-color : white    "\
          "}                            "


class I2CToken(QWidget):

    def __init__(self, parent, status, actions, row, column, loop):
        super (I2CToken, self).__init__()
        self.row = row
        self.loop = loop
        self.status =  status
        self.actions = actions
        self.table = parent
        self.data = None
        self.rw_toggle = QPushButton("Write")
        self.slave_address_line = QLineEdit("0x10")
        self.slave_address_line.setAlignment(Qt.AlignRight)
        self.rw_toggle.setObjectName("rw_check")
        self.rw_toggle.clicked.connect(self.rw_clicked)

        #self.status.Debug(self, "Inserting token")

        #Writing Line Edit
        self.write_value_line_hex = QLineEdit("0x00")
        self.write_value_line_hex.setAlignment(Qt.AlignRight)
        hv = HexValidator()
        hv.setRange(0, 0xFF)
        self.write_value_line_hex.setValidator(hv)

        #XXX: This should be handled by the model
        self.write_value_line_hex.textEdited.connect(self.hex_text_changed)

        self.write_value_line_dec = QLineEdit("0")
        self.write_value_line_dec.setAlignment(Qt.AlignRight)
        v = QIntValidator()
        v.setRange(0, 255)
        self.write_value_line_dec.setValidator(v)
        #XXX: This should be handled by the model
        self.write_value_line_dec.textEdited.connect(self.dec_text_changed)

        #Reading Line Edit
        self.read_value_line_hex = QLineEdit("0x??")
        self.read_value_line_hex.setAlignment(Qt.AlignRight)
        self.read_value_line_hex.setReadOnly(True)

        self.read_value_line_dec = QLineEdit("???")
        self.read_value_line_dec.setAlignment(Qt.AlignRight)
        self.read_value_line_dec.setReadOnly(True)

        layout = QGridLayout()
        self.type_sel = QComboBox()

        #XXX: This should be handled by the model
        self.type_sel_no_change = True
        self.type_sel.currentIndexChanged.connect(self.token_type_changed)
        self.type_sel_no_change = False
        #layout.addWidget(self.type_sel, 0, 0, 1, 3)
        self.type_label = QLabel("Start")
        self.setLayout(layout)
        self.setFixedWidth(200)

        self.add_token_button = QPushButton("+")
        self.add_token_button.setObjectName("add_button")
        self.add_token_button.setStyleSheet(STYLE)
        self.add_token_button.clicked.connect(self.add_clicked)
        self.remove_token_button = QPushButton("-")
        self.remove_token_button.setObjectName("remove_button")
        self.remove_token_button.setStyleSheet(STYLE)
        self.remove_token_button.clicked.connect(self.remove_clicked)

        #self.require_ack_cb = QCheckBox("Ack")
        #self.require_ack_cb.setChecked(True)
        #self.require_ack_cb.setVisible(False)
        #self.require_ack_cb.clicked.connect(self.ack_checked)

    def sizeHint(self):
        size = QSize()
        size.setHeight(100)
        return size

    def ack_checked(self):
        print "Checked"
        #ack = self.require_ack_cb.isChecked()
        self.actions.i2c_ack_changed.emit(self.loop, self.row, self.column, ack)

    def set_column(self, column):
        self.column = column

    def set_default_i2c_slave_address(self, i2c_address):
        self.slave_address_line.setText("0x%0X" % i2c_address)

    def get_token_type(self):
        return self.type_sel.currentText()

    def process_token_type(self):
        #print "Process Token Type: %s" % str(QThread.currentThread().objectName())
        self.clear_layout()
        t = self.token_type
        if t == "Start":
            self.setup_start()
        elif t == "Stop":
            self.setup_stop()
        elif t == "Repeat Start":
            self.setup_repeat_start()
        elif t == "Write":
            self.setup_write()
        elif t == "Read":
            self.setup_read()

    def get_color(self):
        t = self.type_sel.currentText()
        if t == "Start":
            return QColor("blue")
        elif t == "Stop":
            return QColor("purple")
        elif t == "Repeat Start":
            return QColor("blue")
        elif t == "Write":
            return QColor("orange")
        elif t == "Read":
            return QColor("yellow")
        return QColor("white")

    def is_reading_transaction(self):
        if self.rw_toggle.isChecked():
            return True
        return False

    def setup_start(self):
        self.layout().addWidget(self.type_label, 0, 0, 1, 1)
        self.type_label.setVisible(True)
        self.status.Debug(self, "Setup Start")
        self.layout().addWidget(QLabel("Start Address:"), 1, 0)
        self.layout().addWidget(self.slave_address_line, 2, 0)
        self.rw_toggle.setCheckable(True)
        self.rw_toggle.setStyleSheet(STYLE)

        self.layout().addWidget(self.rw_toggle, 2, 1, 1, 1)
        self.slave_address_line.setVisible(True)
        self.rw_toggle.setVisible(True)
        self.layout().addWidget(self.add_token_button, 0, 1, 1, 1)
        self.add_token_button.setVisible(True)

    def setup_stop(self):
        self.layout().addWidget(self.type_sel, 0, 0, 1, 3)
        self.type_sel_no_change = True
        self.type_sel.clear()
        self.type_sel.addItems(["Stop", "Repeat Start"])
        self.type_sel_no_change = False
        self.type_sel.setVisible(True)
        self.status.Debug(self, "Setup Stop")
        l = QLabel("Add a new Row with 'Add Row'")
        l.setWordWrap(True)
        self.layout().addWidget(l, 1, 0, 1, 3)

    def setup_repeat_start(self):
        self.layout().addWidget(self.type_sel, 0, 0, 1, 3)
        self.type_sel_no_change = True
        self.type_sel.clear()
        self.type_sel.addItems(["Stop", "Repeat Start"])
        self.type_sel.setCurrentIndex(1)
        self.type_sel_no_change = False
        self.type_sel.setVisible(True)
        self.status.Debug(self, "Setup Start/Start")
        l = QLabel("Add a new Row with 'Add Row', end transaction on next")
        l.setWordWrap(True)
        self.layout().addWidget(l, 1, 0, 1, 3)

    def setup_write(self):
        self.status.Debug(self, "Setup Write")

        self.layout().addWidget(self.add_token_button, 0, 3, 1, 1)
        self.add_token_button.setVisible(True)
        self.layout().addWidget(self.remove_token_button, 2, 3, 1, 1)
        self.remove_token_button.setVisible(True)

        self.layout().addWidget(QLabel("Write"), 0, 0, 1, 1)
        #self.layout().addWidget(self.require_ack_cb, 0, 1, 1, 1)
        self.layout().addWidget(QLabel("Hex"), 1, 0)
        self.layout().addWidget(QLabel("Dec"), 1, 1)
        self.layout().addWidget(self.write_value_line_hex, 2, 0)
        self.layout().addWidget(self.write_value_line_dec, 2, 1)


        #self.require_ack_cb.setVisible(True)
        self.write_value_line_hex.setVisible(True)
        self.write_value_line_dec.setVisible(True)

    def setup_read(self):
        self.status.Debug(self, "Setup Read")

        self.layout().addWidget(self.add_token_button, 0, 3, 1, 1)
        self.add_token_button.setVisible(True)
        self.layout().addWidget(self.remove_token_button, 2, 3, 1, 1)
        self.remove_token_button.setVisible(True)


        self.layout().addWidget(QLabel("Read"), 0, 0, 1, 1)
        #self.layout().addWidget(self.require_ack_cb, 0, 1, 1, 1)
        self.layout().addWidget(QLabel("Hex"), 1, 0)
        self.layout().addWidget(QLabel("Dec"), 1, 1)
        self.layout().addWidget(self.read_value_line_hex, 2, 0)
        self.layout().addWidget(self.read_value_line_dec, 2, 1)
        #self.require_ack_cb.setVisible(True)
        self.read_value_line_hex.setVisible(True)
        self.read_value_line_dec.setVisible(True)

    def set_rw(self, enable):
        self.rw_toggle.setChecked(enable)
        if self.rw_toggle.isChecked():
            self.rw_toggle.setText("Read")
        else:
            self.rw_toggle.setText("Write")

    def rw_clicked(self):
        self.status.Debug(self, "RW Changed for row: %d" % self.row)
        self.actions.i2c_reading_row_changed.emit(self.row, self.rw_toggle.isChecked(), self.loop)

        #self.table.setSelection(QRect(self.row, self.column, self.row + 1, self.column + 1), QItemSelectionModel.Clear)
        self.table.clearSelection

    def set_ack_required(self, ack_required):
        self.require_ack_cb.setChecked(ack_required)

    def token_type_changed(self):
        if not self.type_sel_no_change:
            d = {}
            d["type"] = self.type_sel.currentText()
            self.actions.i2c_token_changed.emit(self.loop, self.row, self.column, d)

    def set_token_type(self, token_type):
        self.token_type = token_type
        self.process_token_type()

    def get_slave_address(self):
        self.status.Info(self, "Slave Address: %s" % self.slave_address_line.text())
        return int(str(self.slave_address_line.text()), 16)

    def clear_layout(self):
        #print "clear layout: in thread: %s" % str(QThread.currentThread().objectName())
        #self.status.Debug(self, "Clear the layout")
        for i in range(self.layout().count(), -1, -1):
            #print "Working on %d" % i
            #self.status.Debug(self, "Working on: %d" % i)
            item = self.layout().itemAt(i)
            #print "Type: %s" % type(item)
            if item is None:
                continue
            if item.widget() is not None:
                item.widget().setVisible(False)
            #print "Type: %s" % type(item.widget())
            self.layout().removeItem(item)

        self.layout().invalidate()

    def set_read_data(self, read_data):
        self.read_value_line_dec.setText(str(read_data))
        self.read_value_line_hex.setText("0x%02X" % read_data)

    def set_write_data(self, write_data):
        self.write_value_line_hex.setText("0x%02X" % write_data)
        self.write_value_line_dec.setText("%d" % write_data)

    def is_write_value_good(self, value):
        if value < 0:
            return False
        if value > 255:
            return False
        return True

    def dec_text_changed(self, s):
        try:
            v = int(str(s), 10)
            self.write_value_line_hex.setText("0x%02X" % v)
            self.actions.i2c_update_write.emit(self.loop, self.row, self.column, v)
        except ValueError:
            return
        return

    def hex_text_changed(self, s):
        try:
            v = int(str(s), 16)
            self.write_value_line_dec.setText("%d" % v)
            self.actions.i2c_update_write.emit(self.loop, self.row, self.column, v)
        except ValueError:
            return
        return

    def write_validator(self):
        try:
            value = int(str(self.write_value_line_hex.text(), 16))
            if not self.is_write_value_good(value):
                self.write_value_line_hex.setStyleSheet(BAD_VAL)
        except:
            self.write_value_line_hex.setStyleSheet(BAD_VAL)

        self.write_value_line_hex.setStyleSheet(GOOD_VAL)

    def add_clicked(self):
        #print "Add Button Clicked Loop: %s" % self.loop
        self.actions.i2c_token_add.emit(self.loop, self.row, self.column)

    def remove_clicked(self):
        #print "Remove Button Clicked"
        self.actions.i2c_token_remove.emit(self.loop, self.row, self.column)

    def get_write_data(self):
        return int (str(self.write_value_line_hex.text()), 16)

