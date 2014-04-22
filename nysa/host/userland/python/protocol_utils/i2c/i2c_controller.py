# Copyright (c) 2014 name (dave.mccoy@cospandesign.com)

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


"""
I2C Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys


from i2c_token import I2CToken
from i2c_token import I2CException

from PyQt4.QtCore import *

from i2c_config_controller import I2CConfigParseError
from i2c_config_controller import I2CConfigController

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir))

from driver.i2c import I2C


CONFIG_KEY = "host/i2c_configs"

class I2CTransaction(object):

    def __init__(self):
        self.tokens = []

        t = I2CToken("Start")
        t.set_address(address = 0x00)
        self.tokens.append(t)
        t = I2CToken("Stop")
        self.tokens.append(t)
        #Initialize all transactions as writing
        self.set_reading(False)

    def set_address(self, address):
        if address > 255:
            raise I2CException("I2C Slave Address > 255")
        start = self.tokens[0]
        start.set_address(address)

    def set_reading(self, reading_enable):
        #print "Set Reading: %s" % str(reading_enable)
        start = self.tokens[0]
        if reading_enable:
            start.set_reading()
        else:
            start.set_writing()

        #Update all tokens to reflect a read/write
        for t in self.tokens:
            if start.is_reading():
                #print "Reading"
                if t.get_type() == "Write":
                    t.set_type("Read")
                    t.set_read_data(0x00)
            else:
                #print "Writing"
                if t.get_type() == "Read":
                    t.set_type("Write")

    def set_restart(self):
        self.tokens[-1].set_type("Repeat Start")

    def set_stop(self):
        self.tokens[-1].set_type("Stop")

    def is_reading(self):
        t = self.tokens[0]
        return t.is_reading()

    def set_type(self, index, token_type):
        if index == 0:
            raise I2CException("Cannot Change Start Token Type")
        if len(self.tokens) < index + 1:
            raise I2CException("Token Length out of range, add more tokens")

        #Check if the user is trying to add a read to a write sequence
        if (token_type == "Read") and self.is_reading():
            raise I2CException("Attempting to add a read to a write transaction")

        t = self.tokens[index]
        t.set_type(token_type)

    def set_write_data(self, index, data):
        if len(self.tokens) < index + 1:
            raise I2CException("Token Length out of range, add more tokens")
        t = self.tokens[index]
        if t.get_type() != "Write":
            raise I2CException("Cannot set Write Data on type: %s" % t.get_type())

        t.set_write_data(data)

    def set_read_data(self, index, data):
        if len(self.tokens) < index + 1:
            raise I2CException("Token Length out of range, add more tokens")
        t = self.tokens[index]
        if t.get_type() != "Read":
            raise I2CException("Cannot set Read Data on type: %s" % t.get_type())
        t.set_read_data(data)

    def set_require_ack(self, index, data):
        if len(self.tokens) < index + 1:
            raise I2CException("Token Length out of range, add more tokens")
        t = self.tokens[index]
        t.data_require_ack(data)

    def as_record(self):
        dict_list = []
        for t in self.tokens:
            d = {}
            token_type = t.get_type()
            d["type"] = token_type

            if token_type == "Start":
                d["address"] = t.get_address()
                d["reading"] = t.is_reading()
            
            elif token_type == "Stop":
                pass
            
            elif token_type == "Repeat Start":
                pass
            
            elif token_type == "Write":
                d["data"] = t.get_write_data()
                #print "Require Ack: %s" % str(t.is_ack_required())
                d["require_ack"] = t.is_ack_required()

            elif token_type == "Read":
                d["data"] = t.get_read_data()
                #print "Require Ack: %s" % str(t.is_ack_required())
                d["require_ack"] = t.is_ack_required()

            dict_list.append(d)
        return dict_list

    def insert_token(self, index, token):
        self.tokens.insert(index, token)

    def add_token(self, index = None):
        last_token = self.tokens[-1]
        if last_token.get_type() == "Repeat Start":
            self.tokens.append(I2CToken("Repeat Start"))
        else:
            self.tokens.append(I2CToken("End"))

        if self.is_reading():
            last_token.set_type("Read")
        else:
            last_token.set_type("Write")
        return last_token

    def remove_token(self, index):
        if len(self.tokens) < index + 1:
            raise I2CException("Token Length out of range")
        del (self.tokens[index])
        last_token = self.tokens[-1]
        if last_token.get_type() != "Stop" and last_token.get_type() != "Repeat Start":
            last_token.set_type("Stop")
        
class I2CController(object):

    def __init__(self, status, actions):
        super (I2CController, self).__init__()
        self.status = status
        self.actions = actions
        self.init_tokens = []
        self.add_init_transaction()
        self.loop_tokens = []
        self.actions.i2c_reading_row_changed.connect(self.row_reading_changed)
        self.actions.i2c_token_changed.connect(self.token_changed)
        self.actions.i2c_default_i2c_address.connect(self.address_changed)
        self.actions.i2c_token_add.connect(self.add_token)
        self.actions.i2c_token_remove.connect(self.remove_token)
        self.actions.i2c_update_write.connect(self.update_write_data)
        self.actions.i2c_row_add.connect(self.add_transaction)
        self.actions.i2c_row_delete.connect(self.remove_transaction)
        self.actions.i2c_ack_changed.connect(self.set_token_require_ack)

        usr = os.path.expanduser("~")
        self.file_location = os.path.join(usr, "Projects", "nysa_projects", "i2c_configs")
        settings = QSettings("Cospan Design", "nysa")

        if settings.contains(CONFIG_KEY):
            self.file_location = settings.value(CONFIG_KEY)
            self.status.Info(self,
                            "Found Default Config Location for I2C Base location: %s at %s" %
                                (CONFIG_KEY, self.file_location))
        else:
            #Set a default location for next time
            settings.setValue(CONFIG_KEY, self.file_location)
        settings.sync()

        self.config = I2CConfigController()

    def __del__(self):
        default = None
        
    def save_i2c_commands(self, file_location):
        init_data = self.get_all_init_transactions()
        loop_data = self.get_all_loop_transactions()
        self.config.save_data(file_location, init_data, loop_data)

    def load_i2c_commands(self, file_location):
        init_data, loop_data = self.config.load_data(file_location)
        self.init_tokens = []
        for transaction in init_data:
            t = I2CTransaction()
            reading = False
            for token in transaction:
                #print "token: %s" % token
                if "type" in token:
                    if token["type"].lower() == "start":
                        t.set_address(token["address"])
                        t.set_reading(token["reading"])
                        reading = token["reading"]
                    elif token["type"].lower() == "stop":
                        t.set_stop()
                    elif token["type"].lower() == "repeat start":
                        t.set_restart()
                else:
                    if reading:
                        nt = t.add_token()
                        #nt.data_require_ack(token["require_ack"])
                    else:
                        nt = t.add_token()
                        #nt.data_require_ack(token["require_ack"])
                        nt.set_write_data(token["data"])
            self.init_tokens.append(t)

        self.loop_tokens = []

        for transaction in loop_data:
            t = I2CTransaction()
            reading = False
            for token in transaction:
                #print "token: %s" % token
                if "type" in token:
                    if token["type"].lower() == "start":
                        t.set_address(token["address"])
                        t.set_reading(token["reading"])
                        reading = token["reading"]
                    elif token["type"].lower() == "stop":
                        t.set_stop()
                    elif token["type"].lower() == "repeat start":
                        t.set_restart()
                else:
                    if reading:
                        nt = t.add_token()
                        #nt.data_require_ack(token["require_ack"])
                    else:
                        nt = t.add_token()
                        #nt.data_require_ack(token["require_ack"])
                        nt.set_write_data(token["data"])

            self.loop_tokens.append(t)
        d = self.get_all_init_transactions()
        #print "Dict: %s" % str(d)
        self.actions.i2c_update_view.emit(False, d)
        d = self.get_all_loop_transactions()
        #print "Dict: %s" % str(d)
        self.actions.i2c_update_view.emit(True, d)



    def add_transaction(self, loop):
        self.status.Important(self, "Adding a transaction")
        if not loop:
            self.add_init_transaction()
            d = self.get_all_init_transactions()
            self.actions.i2c_update_view.emit(False, d)
        else:
            self.add_loop_transaction()
            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)

    def remove_transaction(self, loop):
        self.status.Important(self, "Removing a transaction")
        if not loop:
            d = self.get_all_init_transactions()
            self.actions.i2c_update_view.emit(False, d)
        else:
            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)

    def update_write_data(self, loop, row, column, data):
        if not loop:
            transaction = self.init_tokens[row]
        else:
            transaction = self.loop_tokens[row]
        transaction.set_write_data(column, data)

    def add_token(self, loop, row, column):
        transaction = None

        if not loop:
            self.status.Debug(self, "Init: Adding a token after: %d, %d" % (row, column))
            transaction = self.init_tokens[row]
            #Got the transaction
            #print "Add token before: %d" % (column + 1)
            if transaction.is_reading():
                #Reading
                self.init_tokens[row].insert_token(column + 1, I2CToken("Read"))
            else:
                #Writing
                self.init_tokens[row].insert_token(column + 1, I2CToken("Write"))

            d = self.get_all_init_transactions()

        else:
            self.status.Debug(self, "Loop: Adding a token after: %d, %d" % (row, column))
            transaction = self.loop_tokens[row]
            if transaction.is_reading():
                #Reading
                self.loop_tokens[row].insert_token(column + 1, I2CToken("Read"))
            else:
                #Writing
                self.loop_tokens[row].insert_token(column + 1, I2CToken("Write"))


            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)

        self.actions.i2c_update_view.emit(False, d)

    def remove_token(self, loop, row, column):
        transaction = None
        if not loop:
            self.status.Debug(self, "Loop: Removing a token after: %d, %d" % (row, column))
            transaction = self.init_tokens[row]
        else:
            self.status.Debug(self, "Init: Removing a token after: %d, %d" % (row, column))
            transaction = self.loop_tokens[row]

        #Got the transaction
        transaction.remove_token(column)

        if not loop:
            d = self.get_all_init_transactions()
            self.actions.i2c_update_view.emit(False, d)
        else:
            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)

    def address_changed(self, address):
        for tokens in self.init_tokens:
            tokens.set_address(address)

        d = self.get_all_init_transactions()
        self.actions.i2c_update_view.emit(False, d)
        for tokens in self.loop_tokens:
            tokens.set_address(address)

        d = self.get_all_loop_transactions()
        self.actions.i2c_update_view.emit(True, d)


    def token_changed(self, loop, row, column, d):
        tokens = None
        if not loop:
            tokens = self.init_tokens[row].set_type(column, d["type"])
            d = self.get_all_init_transactions()
            self.actions.i2c_update_view.emit(False, d)
        else:
            tokens = self.loop_tokens[row].set_type(column, d["type"])
            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)
        #XXX: update 

    def row_reading_changed(self, row, enable, loop):
        self.status.Debug(self, "RW Changed: %d" % row)
        if not loop:
            self.init_tokens[row].set_reading(enable)
            d = self.get_all_init_transactions()
            self.actions.i2c_update_view.emit(False, d)
        else:
            self.loop_tokens[row].set_reading(enable)
            d = self.get_all_loop_transactions()
            self.actions.i2c_update_view.emit(True, d)

    #Transaction Add/Remove
    def add_init_transaction(self):
        self.init_tokens.append(I2CTransaction())

    def add_loop_transaction(self):
        self.loop_tokens.append(I2CTransaction())

    def set_init_token_data(self, row, column, data):
        self._set_token_data(self.init_tokens, row, column, data)

    def set_token_require_ack(self, loop, row, column, require_ack):
        if loop:
            self.set_loop_token_require_ack(row, column, require_ack)
        else:
            self.set_init_token_require_ack(row, column, require_ack)

    def set_init_token_require_ack(self, row, column, require_ack):
        self._set_token_require_ack(self.init_tokens, row, column, require_ack)

    def set_loop_token_require_ack(self, row, column, require_ack):
        self._set_token_require_ack(self.loop_tokens, row, column, require_ack)

    def set_loop_token_data(self, row, column, data):
        self._set_token_data(self.loop_tokens, row, column, data)

    def _set_token_data(self, tokens, row, column, data):
        if len(tokens) < row + 1:
            raise I2CException("Attempting to access an out of range index: %d, size is: %d" % row, len(tokens))
        if tokens[row].is_reading():
            tokens[row].set_read_data(column, data)
        else:
            tokens[row].set_write_data(column, data)

    def _set_token_require_ack(self, tokens, row, column, require_ack):
        if len(tokens) < row + 1:
            raise I2CException("Attempting to access an out of range index: %d, size is: %d" % row, len(self.tokens))
        tokens[row].set_require_ack(column, require_ack)


    #Token Add/Remove/Change
    def add_init_token(self):
        self.init_tokens.add_token()

    def remove_init_token(self, row, column):
        if len(self.init_tokens) < row + 1:
            raise I2CException("Attempting to access an out of range index: %d, size is: %d" % row, len(self.init_tokens))
        self.init_tokens[row].remove_token(column)

    def add_loop_token(self):
        self.loop_tokens.add_token()

    def remove_loop_token(self, index):
        if len(self.loop_tokens) < row + 1:
            raise I2CException("Attempting to access an out of range index: %d, size is: %d" % row, len(self.loop_tokens))
        self.loop_tokens.remove_token(index)

    #Get transactions
    def get_all_init_transactions(self):
        init_list = []
        for index in range(len(self.init_tokens)):
            init_list.append(self.get_init_transaction(index))

        return init_list

    def get_all_loop_transactions(self):
        loop_list = []
        for index in range(len(self.loop_tokens)):
            loop_list.append(self.get_loop_transaction(index))

        return loop_list

    def get_init_transaction(self, index):
        #print "get init transaction: %d" % index
        #return self.init_tokens[index].as_record()
        return self.init_tokens[index].as_record()

    def get_loop_transaction(self, index):
        return self.loop_tokens[index].as_record()


