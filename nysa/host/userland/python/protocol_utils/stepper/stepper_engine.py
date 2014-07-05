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
Stepper Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import time
import json

from array import array as Array

from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


STATE_START                     = 0
STATE_READY                     = 1
STATE_BUSY                      = 2


class StepperEngineError(Exception):
    pass

class StepperWorker(QtCore.QThread):
    #write_data = QtCore.pyqtSignal(int, object, name = "stepper_worker_write_data")
    #read_data = QtCore.pyqtSignal(int, int, name = "stepper_worker_read_data")
    #init_worker = QtCore.pyqtSignal(object, object, name="stepper_worker_init")
    stepper_response = QtCore.pyqtSignal(object, name = "stepper_response")
    #move_event = QtCore.pyqtSignal(float, name = "stepper_worker_move_event")

    def __init__(self):
        super(StepperWorker, self).__init__()
        #self.init_worker.connect(self.init_stepper_worker)
        #self.write_data.connect(self.process_write_data)
        #self.read_data.connect(self.process_read_data)
        #self.move_event.connect(self.process_move_event)

    @QtCore.pyqtSlot(object, object)
    def init_stepper_worker(self, stepper, actions):
        print "SDWorker Engine: Initializing worker"
        self.stepper = stepper
        self.actions = actions
        self.stepper.register_interrupt_callback(self.interrupt_callback)
        #Get the divisor for the rotation (Initially set it to 200)
        self.angle_divisor = 360.0 / 200

    def interrupt_callback(self):
        print "Callback from stepper motor"
        print "Getting status"
        status = self.stepper.get_status()

    def process_write_data(self, address, data):
        self.stepper.write(address, data)
        self.stepper_response.emit(None)

    def process_read_data(self, address, length):
        data = self.stepper.read(address, length)
        self.stepper_response.emit(data)

    @QtCore.pyqtSlot(int)
    def update_max_position(self, max_position):
        self.angle_divisor = 360.0 / max_position

    @QtCore.pyqtSlot(float)
    def process_move_event(self, angle):
        print "Process Move event for angle: %f" % angle

        direction = 1
        if angle < 0:
            direction = -1
        num_turns = ((int(abs(angle)) / 360) * direction)
        extra = direction * (abs(angle) - abs((num_turns * 360)))

        if direction == 1:
            self.stepper.set_direction(True)
        else:
            self.stepper.set_direction(False)


        #raw_val = (abs(angle) * 0.03125) << 9
        raw_val = int(((abs(angle) / self.angle_divisor) * 512))
        print "Steps: 0x%08X" % raw_val
        self.stepper.set_steps(raw_val)
        print "Go!"
        self.stepper.go()
        time.sleep(.2)
        while (self.stepper.is_busy()):
            time.sleep(.2)
            #self.actions.stepper_update_register.emit(11, self.stepper.get_current_position)

        #DEBUG!!
        for i in range(13):
            self.actions.stepper_update_register.emit(i, self.stepper.read_register(i))
        #self.actions.stepper_update_register.emit(11, self.stepper.get_current_position)




class StepperEngine (QtCore.QObject):

    def __init__(self, stepper_driver, status, actions):
        super (StepperEngine, self).__init__()

        self.status = status
        self.status.Info(self, "Reset Stepper Interface")
        self.stepper_worker = None
        self.stepper = stepper_driver

        self.actions = actions
        self.status.Verbose(self, "Starting Stepper Engine")
        self.state = STATE_START

        #Create a worker object and move it to it's own thread
        self.stepper_worker = StepperWorker()

        self.stepper_worker.stepper_response.connect(self.state_machine)
        self.worker_thread = QtCore.QThread()
        self.worker_thread.setObjectName("Stepper Worker")
        self.stepper_worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        #self.stepper_worker.init_worker.emit(self.stepper, self.actions)
        QtCore.QMetaObject.invokeMethod(self.stepper_worker,
                                        'init_stepper_worker',
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(object, self.stepper),
                                        QtCore.Q_ARG(object, self.actions))
        #Get all the initialization data
        for i in range(13):
            self.actions.stepper_update_register.emit(i, self.stepper.read_register(i))

        #self.stepper.enable_interrupt(True)
        self.stepper.set_micro_step()

        self.clock_rate = self.stepper.get_clock_rate()
        self.actions.stepper_update_clock_rate.emit(self.clock_rate)
        self.actions.stepper_move_event.connect(self.process_move_event)
        self.actions.stepper_update_configuration.connect(self.update_configuration)
        self.actions.stepper_update_step_type.connect(self.update_step_type)

        self.state_machine(None)

    def state_machine(self, response):
        if self.state == STATE_START:
            print "Starting..."
            pass
        elif self.state == READY:
            print "READY"
        elif self.state == BUSY:
            print "Busy"
        else:
            print "Error in state machine"
            return

    def process_move_event(self, angle):
        #print "Moving the stepper motor by %f degrees" % angle
        QtCore.QMetaObject.invokeMethod(self.stepper_worker,
                                        'process_move_event',
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(float, angle))
        #self.stepper_worker.move_event.emit(angle)

    def update_configuration(self, config_dict):
        print "Updating configuration..."
        if config_dict["stepper_type"].lower() == "bipolar":
            self.stepper.configure_bipolar_stepper()
        else:
            self.stepper.configure_unipolar_stepper()

        print "Clock Rate: %f" % self.clock_rate
        
        walk_period = int(config_dict["walk_period"] * self.clock_rate)
        run_period = int(config_dict["run_period"] * self.clock_rate)
        accelleration = int(config_dict["accelleration"] * self.clock_rate)

        print "Walk Period: %d" % walk_period
        print "Run Period: %d" % run_period
        print "Accelleration: %d" % accelleration
        print "Micro Step Hold: %d" % 0


        self.stepper.set_walk_period(walk_period)
        self.stepper.set_run_period(run_period)
        self.stepper.set_step_accelleration(accelleration)
        self.stepper.set_micro_step_hold(0)
        self.stepper.set_max_position(config_dict["num_steps"])
        QtCore.QMetaObject.invokeMethod(self.stepper_worker,
                                        'update_max_position',
                                        QtCore.Qt.QueuedConnection,
                                        QtCore.Q_ARG(int, config_dict["num_steps"]))
       

        for i in range(13):
            self.actions.stepper_update_register.emit(i, self.stepper.read_register(i))

    def update_step_type(self, index):
        if index == 0:
            self.stepper.set_full_step()
        elif index == 1:
            self.stepper.set_half_step()
        else:
            self.stepper.set_micro_step()


