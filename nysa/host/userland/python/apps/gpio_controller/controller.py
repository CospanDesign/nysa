#! /usr/bin/python

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
app template controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse
import time

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from driver.gpio import GPIO
from apps.common.nysa_base_controller import NysaBaseController
import apps

from view.gpio_widget import GPIOWidget

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from platform_scanner import PlatformScanner
import status
#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"GPIO Controller\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tDebug\n" \
"\t\t%s -d\n"\
"\n" % n

from gpio_actions import GPIOActions

class ReaderThread(QtCore.QThread):
    def __init__(self, gpio, mutex, timeout, gpio_actions):
        super(ReaderThread, self).__init__()

        self.gpio_actions = gpio_actions
        self.timeout = timeout
        self.mutex = mutex
        self.gpio = gpio
        self.term_flag = False
        self.value = 0

        self.gpio_actions.read_rate_change.connect(self.read_rate_change)

    def __del__(self):
        #print "Reader thread terminate"
        self.term_flag = True

    def end_reading(self):
        self.term_flag = True

    def run(self):
        while not self.term_flag:
            time.sleep(self.timeout)
            if self.mutex.tryLock():
                value = self.gpio.get_port_raw()
                if value != self.value:
                    #Only send updates when there really is a change
                    self.value = value
                    self.gpio_actions.gpio_input_changed.emit(value)
                self.mutex.unlock()
            
        
    def read_rate_change(self, rate):
        self.timeout = rate


class Controller(NysaBaseController):

    @staticmethod
    def get_name():
        return "GPIO Controller"

    def __del__(self):
        if self.reader_thread is not None:
            del (self.reader_thread)

    def __init__(self):
        super (Controller, self).__init__()
        self.mutex = QtCore.QMutex()

        self.gpio_actions = GPIOActions()

        self.gpio_actions.get_pressed.connect(self.register_get_pressed)
        self.gpio_actions.set_pressed.connect(self.register_set_pressed)
        self.gpio_actions.gpio_out_changed.connect(self.gpio_out_changed)
        self.gpio_actions.direction_changed.connect(self.direction_changed)
        self.gpio_actions.interrupt_en_changed.connect(self.interrupt_en_changed)
        self.gpio_actions.interrupt_edge_changed.connect(self.interrupt_edge_changed)

        self.gpio_actions.read_start_stop.connect(self.read_start_stop)
        self.gpio_actions.gpio_input_changed.connect(self.gpio_input_changed)
        self.reader_thread = None

    def _initialize(self, platform, device_index):
        self.v = GPIOWidget(count = 32, gpio_actions = self.gpio_actions)
        #self.m.setup_(self, platform[2], device_index)

        self.n = platform[2]

        self.gpio = GPIO(platform[2], device_index)
        self.dev_index = device_index + 1

        #Initialize the thread with a 40mS timeout
        self.reader_thread = ReaderThread(self.gpio, self.mutex, .040, self.gpio_actions)


        self.v.add_register(0, "GPIO Value", initial_value = self.gpio.get_port_raw())
        self.v.add_register(1, "GPIO Direction", initial_value = self.gpio.get_port_direction())
        self.v.add_register(2, "GPIO Interrupts", initial_value = self.gpio.get_interrupts())
        self.v.add_register(3, "GPIO Interrupt Enable", initial_value = self.gpio.get_interrupt_enable())
        self.v.add_register(4, "GPIO Interrupt Edge", initial_value = self.gpio.get_interrupt_edge())

        self.v.set_register(0, self.gpio.get_port_raw())
        self.v.set_register(1, self.gpio.get_port_direction())
        self.v.set_register(2, self.gpio.get_interrupts())
        self.v.set_register(3, self.gpio.get_interrupt_enable())
        self.v.set_register(4, self.gpio.get_interrupt_edge())

    def start_standalone_app(self, platform, device_index):
        #print "Device Index: %d" % device_index
        app = QApplication (sys.argv)
        self._initialize(platform, device_index)
        sys.exit(app.exec_())

    def start_tab_view(self, platform, device_index):
        #print "Device Index: %d" % device_index
        self._initialize(platform, device_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        """
        If this ia controller for an entire image return the associated unique
        image ID here
        """
        return None

    @staticmethod
    def get_device_id():
        return 1

    @staticmethod
    def get_device_sub_id():
        """
        If this is a controller for an individual device with that has a
        specific implementation (Cospan Design's version of a GPIO controller
        as apposed to just a generic GPIO controller) return the sub ID here
        """
        return None

    @staticmethod
    def get_device_unique_id():
        """
        Used to differentiate devices with the same device/sub ids.
        """
        return None

    def read_start_stop(self, start_stop, rate):
        print "Enter Read/startstop"
        if start_stop:
            #Start
            if not self.reader_thread.isRunning():
                self.reader_thread.start()
                self.gpio_actions.read_rate_change.emit(rate)
        else:
            print "Stopping"
            #Stop
            self.reader_thread.end_reading()
            self.reader_thread.wait()
            print "Reader thread is finished"
            del(self.reader_thread)
            #Wait till thread is finished
            self.reader_thread = ReaderThread(self.gpio, self.mutex, rate, self.gpio_actions)

    def gpio_input_changed(self, value):
        print "Input Changed"
        #Input Changed
        self.v.set_register(0, value)

    def register_get_pressed(self, index):
        print "Register Get Pressed: %d" % index
        self.mutex.lock()
        value = self.n.read_register(self.dev_index, index)
        self.mutex.unlock()
        self.v.set_register(index, value)

    def register_set_pressed(self, index, value):
        print "Register Set Pressed: %d: %d" % (index, value)
        self.mutex.lock()
        self.n.write_register(self.dev_index, index, value)
        self.mutex.unlock()

    def gpio_out_changed(self, index, val):
        print "GPIO Out: %d : %s" % (index, str(val))
        self.mutex.lock()
        self.gpio.set_bit_value(index, val)
        self.mutex.unlock()

    def direction_changed(self, index, val):
        print "GPIO Direction: %d : %s" % (index, str(val))
        self.mutex.lock()
        self.n.enable_register_bit(self.dev_index, 1, index, val)
        self.mutex.unlock()

    def interrupt_en_changed(self, index, val):
        print "Interrupt En Changed: %d : %s" % (index, str(val))
        self.mutex.lock()
        self.n.enable_register_bit(self.dev_index, 3, index, val)
        self.mutex.unlock()

    def interrupt_edge_changed(self, index, val):
        print "Interrupt Edge Changed: %d : %s" % (index, str(val))
        self.mutex.lock()
        self.n.enable_register_bit(self.dev_index, 4, index, val)
        self.mutex.unlock()





def main(argv):
    #Parse out the commandline arguments
    s = status.ClStatus()
    s.set_level(status.StatusLevel.INFO)
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")
    parser.add_argument("-l", "--list",
                        action = "store_true",
                        help = "List the available devices from a platform scan")
    parser.add_argument("platform",
                        type = str,
                        nargs='?',
                        default=["first"],
                        help="Specify the platform to use")
                        

    args = parser.parse_args()
    plat = None

    if args.debug:
        s.set_level(status.StatusLevel.VERBOSE)
        s.Debug(None, "Debug Enabled")
        debug = True

    if debug:
        s.Debug(None, "Display a list of platforms found")
    pscanner = PlatformScanner()
    ps = pscanner.get_platforms()
    dev_index = None
    for p in ps:
        s.Verbose(None, p)
        for psi in ps[p]:
            if plat is None:
                s.Verbose(None, "Found a platform: %s" % p)
                n = ps[p][psi]
                n.read_drt()
                dev_index = n.find_device(1)
                if dev_index is not None:
                    print "Dev Index: %d" % dev_index
                    plat = [p, psi, ps[p][psi]]
                    break
                continue
            if p == args.platform and plat[0] != args.platform:
                #Found a match for a platfom to use
                plat = [p, psi, ps[p][psi]]
                continue
            if p == psi:
                #Found a match for a name!
                #See if we can find a GPIO device: 0
                dev_index = n.find_device(1)
                print "Dev Index: %d" % dev_index
                if dev_index is not None:
                    plat = [p, psi, ps[p][psi]]
                    break

            s.Verbose(None, "\t%s" % psi)

    if args.list:
        s.Verbose(None, "Listed all platforms, exiting")
        sys.exit(0)

    if plat is not None:
        s.Important(None, "Using: %s" % plat)
    else:
        s.Fatal(None, "Didn't find a platform to use!")

    c = Controller()
    if dev_index is None:
        sys.exit("Failed to find a GPIO Device")

    c.start_standalone_app(plat, dev_index)

if __name__ == "__main__":
    main(sys.argv)
