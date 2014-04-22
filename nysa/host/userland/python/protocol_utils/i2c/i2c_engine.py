# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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
import time

from array import array as Array

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))
from driver.i2c import I2CError



class I2CEngineError(Exception):
    pass

class I2CEngineThread(QtCore.QThread):
    def __init__(self, engine, i2c, mutex, delay, actions, init_commands, loop_commands):
        super(I2CEngineThread, self).__init__()

        self.i2c = i2c
        self.engine = engine
        self.mutex = mutex
        self.delay = int(delay * 1000)
        self.actions = actions
        self.term_flag = False
        self.init_commands = init_commands
        self.loop_commands = loop_commands
        self.init_pos = 0
        self.loop_pos = 0
        self.pause = False
        self.step = False
        self.step_loop = False

        self.actions.i2c_run.connect(self.continue_flow)
        self.actions.i2c_reset.connect(self.reset_flow)
        self.actions.i2c_pause.connect(self.pause_flow)
        self.actions.i2c_step.connect(self.step_flow)
        self.actions.i2c_loop_step.connect(self.step_loop_flow)
        self.actions.i2c_pause.connect(self.pause_flow)
        self.actions.i2c_execute_delay_change.connect(self.set_delay)

    def load_commands(self, init_commands, loop_commands):
        print "Loading commands"
        self.init_commands = init_commands
        self.loop_commands = loop_commands
        self.init_pos = 0
        self.loop_pos = 0

    def __del__(self):
        self.term_flag = True

    def stop_flow(self):
        self.term_flag = True

    def set_delay(self, delay):
        #Delays cannot be shorter than 1 ms
        self.actions.i2c_execute_status_update.emit("Update Delay to: %d" % delay)
        self.delay = delay
        if self.delay < 1:
            self.delay = 1
        self.delay = delay

    def step_flow(self):
        self.actions.i2c_execute_status_update.emit("Single step")
        self.step = True

    def step_loop_flow(self):
        self.actions.i2c_execute_status_update.emit("Step through loop")
        self.step_loop = True

    def pause_flow(self):
        self.actions.i2c_execute_status_update.emit("Pause")
        self.pause = True

    def continue_flow(self):
        self.pause = False

    def reset_flow(self):
        self.actions.i2c_execute_status_update.emit("Reset")
        self.init_pos = 0
        self.loop_pos = 0

    def run(self):
        while not self.term_flag:
            self.yieldCurrentThread()
            time.sleep(self.delay * 0.001)
            if not self.pause or self.step or self.step_loop:
                if self.mutex.tryLock():
                    if len(self.init_commands) > 0 and (self.init_pos < len(self.init_commands)):
                        self.engine.process_transaction(self.init_commands[self.init_pos])
                        self.actions.i2c_execute_status_update.emit("Init Pos: %d" % (self.init_pos))
                        self.init_pos += 1
                        if self.init_pos == len(self.init_commands):
                            self.actions.i2c_execute_status_update.emit("Init Pos: %d (Finished)" % (self.init_pos - 1))
                    else:
                        if len(self.loop_commands) > 0:
                            #print "loop pos: %d" % self.loop_pos
                            if self.loop_pos < len(self.loop_commands):
                                self.engine.process_transaction(self.loop_commands[self.loop_pos])
                                self.loop_pos += 1

                            self.actions.i2c_execute_status_update.emit("Loop Pos: %d" % (self.loop_pos))
                            if self.loop_pos >= len(self.loop_commands):
                                self.actions.i2c_execute_status_update.emit("Loop Pos: %d (Finished)" % self.loop_pos)
                                self.loop_pos = 0
                                self.step_loop = False

                    self.step = False
                    self.mutex.unlock()


class I2CEngine (QtCore.QObject):

    def __init__(self, i2c_driver, status, actions):
        super (I2CEngine, self).__init__()

        self.i2c = i2c_driver
        self.status = status
        self.actions = actions
        self.mutex = QtCore.QMutex()
        self.status.Verbose(self, "Starting I2C Engine")
        self.engine_thread = None
        self.actions.i2c_stop.connect(self.stop_flow)

    def stop_flow(self):
        if self.engine_thread is not None:
            if self.engine_thread.isRunning():
                self.engine_thread.stop_flow()
                self.engine_thread.wait()
                del(self.engine_thread)
                self.engine_thread = None

    def __del__(self):
        if self.engine_thread is not None:
            self.engine_thread.stop()
            self.engine_thread.wait()
            del (self.engine_thread)

    def load_commands(self, init_commands, loop_commands):
        self.mutex.lock()
        self.engine_thread.load_commands(init_commands, loop_commands)
        self.mutex.unlock()

    def start_engine(self, init_commands, loop_commands, delay = 0.1, pause = False):
        if self.engine_thread is None:
            self.engine_thread = I2CEngineThread(self,
                                                 self.i2c,
                                                 self.mutex,
                                                 delay,
                                                 self.actions,
                                                 init_commands,
                                                 loop_commands)

        if pause:
            self.engine_thread.pause_flow()

        if not self.engine_thread.isRunning():
            self.engine_thread.start()

    def pause_flow(self):
        self.engine_thread.pause_flow()

    def step_flow(self):
        self.engine_thread.step_flow()

    def step_loop_flow(self):
        self.engine_thread.step_loop_flow()

    def is_running(self):
        if self.engine_thread is None:
            return False
        return self.engine_thread.isRunning()

    def process_transaction(self, transaction):
        #Transaction is a list of tokens to send to the I2C device
        #index 0 of the transaction is the start transaction, this will dictate
        #Whether this is a read or a write
        #print "i2c type: %s" % str(self.i2c)
        if not self.i2c.is_i2c_enabled():
            self.i2c.enable_i2c()

        i2c_address = transaction[0]["address"]
        read_data = Array('B')

        if transaction[0]["reading"]:
            count = len(transaction) - 2
            if count <= 0:
                #Reading from I2C
                raise I2CEngineError("Read Count = %d, read count must be greater than 0" % count)
            try:
                read_data = self.i2c.read_from_i2c(i2c_id = i2c_address,
                                                   i2c_write_data = None,
                                                   read_length = count)
            except I2CError as e:
                self.status.Error(self, "I2C Driver Error: %s" % str(e))

        else:
            #Writing to I2C
            write_data = Array('B')
            repeat_start = False
            if transaction[-1]["type"].lower() == "repeat start":
                repeat_start = True
            for token in transaction:
                if token["type"] == "Write":
                    write_data.append(token["data"])

            #Propagate I2C Errors to the above
            try:
                self.i2c.write_to_i2c(i2c_id = i2c_address,
                                      i2c_data = write_data,
                                      repeat_start = repeat_start)
            except I2CError as e:
                self.status.Error(self, "I2C Driver Error: %s" % str(e))

        self.status.Debug(self, "Transaction complete")
        return read_data

    def reset_i2c(self):
        self.status.Debug(self, "Reset I2C Core")
        self.i2c.reset_i2c_core()

    def set_speed_to_100khz(self):
        self.status.Debug(self, "Set I2C Rate to 100Khz")
        self.i2c.set_speed_to_100khz()

    def set_speed_to_400khz(self):
        self.status.Debug(self, "Set I2C Rate to 400Khz")
        self.i2c.set_speed_to_400khz()

    def set_custom_speed(self, rate):
        self.status.Debug(self, "Set I2C Rate to a custom rate: %dkHz" % rate)
        self.i2c.set_custom_speed(rate)
