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
memory controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse
import time
from array import array as Array

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from apps.common.nysa_base_controller import NysaBaseController
import apps

from view.view import View
from model.model import AppModel

from memory_actions import MemoryActions

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

import status
from platform_scanner import PlatformScanner

#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"Memory Controller\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n

class ReaderThread(QtCore.QThread):
    def __init__(self, mutex, func):
        super(ReaderThread, self).__init__()

        self.memory_actions = MemoryActions()
        self.mutex = mutex
        self.func = func

    def run(self):
        #Perform Memory Test
        self.mutex.lock()
        result = "Error"
        try:
            result = self.func()
        except:
            print "Error while executing memory test"
        finally:
            self.mutex.unlock()
        self.memory_actions.memory_read_finished.emit(result)
        print "Finished with thread"

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.status = None
        self.actions = None
        self.memory_actions = MemoryActions()
        self.mutex = QtCore.QMutex()
        self.m = AppModel()
        self.reader_thread = None
        self.memory_actions.memory_test_start.connect(self.start_tests)
        self.memory_actions.memory_read_finished.connect(self.run_test)

    @staticmethod
    def get_name():
        return "Memory Controller"

    def __del__(self):
        if self.reader_thread is not None:

            self.status.Important(self, "Waiting for reader thread to finish")
            self.reader_thread.join()

    def _initialize(self, platform, dev_index):
        self.n = platform[2]
        print "Index: %d" % dev_index
        self.dev_index = dev_index
        self.v = View(self.status, self.memory_actions)
        self.v.setup_view()
        self.v.add_test("Single Read/Write at Start", True, self.test_single_rw_start)
        self.v.add_test("Single Read/Write at End", True, self.test_single_rw_end)
        self.v.add_test("Long Read/Write Test", True, self.test_long_burst)
        self.v.set_memory_size(self.n.get_device_size(dev_index))


    def start_standalone_app(self, plat, dev_index):
        app = QApplication (sys.argv)
        self.status = status.ClStatus()
        self._initialize(plat, dev_index)
        sys.exit(app.exec_())

    def start_tab_view(self, platform, dev_index):
        self.status = status.Status()
        self._initialize(platform, dev_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        return None

    @staticmethod
    def get_device_id():
        #Return Memory Device ID
        return 5

    @staticmethod
    def get_device_sub_id():
        return None

    @staticmethod
    def get_device_unique_id():
        return None

    def start_tests(self):
        print "Start Tests!"
        self.gen = test_iterator(self.v.get_num_tests())
        self.run_test()

    def get_test(self):
        index = self.gen.next()
        if self.v.is_test_enabled(index):
            return self.v.get_test_function(index)
        return None

    def run_test(self, status = None):
        finished = False
        if status is not None:
            print "Finished test, Result: %s" % status
        try:
            while not finished:
                t = self.get_test()
                if t is not None:
                    print "Running Test: %s" % str(t)
                    self.reader_thread = ReaderThread(self.mutex, t)
                    self.reader_thread.start()
                    return
                else:
                    continue
        except StopIteration:
            print "Done!"


    def test_single_rw_start(self):
        status = "Passed"
        size = self.n.get_device_size(self.dev_index)
        if self.status.is_command_line():
            print "Command Line %s" % str(type(self.status))
            self.status.Verbose(self, "Clearing Memory")
            self.status.Verbose(self, "Memory Size: 0x%08X" % size)
        data_out = Array('B')
        for i in range(0, ((size / 4) - 1)):
            num = 0x00
            data_out.append(num)

        self.n.write_memory(0, data_out)

        if self.status.is_command_line():
            self.status.Verbose(self, "Test Single Read/Write at Beginning")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory(0, data_out)
        data_in = self.n.read_memory(0, 2)
        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                status = "Failed"
                print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))
        return status

    def test_single_rw_end(self):
        status = "Passed"
        size = self.n.get_device_size(self.dev_index)
        if self.status.is_command_line():
            self.status.Verbose(self, "Clearing Memory")
            self.status.Verbose(self, "Memory Size: 0x%08X" % size)
        data_out = Array('B')
        for i in range(0, ((size / 4) - 1)):
            num = 0x00
            data_out.append(num)
        self.n.write_memory(0, data_out)


        if self.status.is_command_line():
            self.status.Verbose(self, "Test Single Read/Write at End")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory((size - 16), data_out)
        print "Reading from location: 0x%08X" % (size - 16)
        data_in = self.n.read_memory((size - 16), 2)

        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))
                status = "Failed"

        return status

    def test_long_burst(self):
        status = "Passed"
        size = self.n.get_device_size(self.dev_index)
        if self.status.is_command_line():
            self.status.Verbose(self, "Clearing Memory")
            self.status.Verbose(self, "Memory Size: 0x%08X" % size)
        data_out = Array('B')
        for i in range(0, ((size / 4) - 1)):
            num = 0x00
            data_out.append(num)

        self.n.write_memory(0, data_out)


        if self.status.is_command_line():
            self.status.Verbose(self, "long rw")
        data_out = Array('B')
        for i in range (0, size):
            data_out.append((i % 255))

        if self.status.is_command_line():
            self.status.Verbose(self, "Writing 0x%08X bytes of data" % (len(data_out)))
        start = time.time()
        self.n.write_memory(0, data_out)
        end = time.time()
        if self.status.is_command_line(): 
            self.status.Verbose(self, "Write Time : %f" % (end - start))
            self.status.Verbose(self, "Reading 0x%08X bytes of data" % (len(data_out)))
        start = time.time()
        data_in = self.n.read_memory(0, len(data_out) / 4)
        end = time.time()
        if self.status.is_command_line():
            self.status.Verbose(self, "Read Time: %f" % (end - start))
            self.status.Verbose(self, "Comparing Values")
        fail = False
        fail_count = 0
        if len(data_out) != len(data_in):
            if self.status.is_command_line():
                self.status.Error(self, "Data in lenght not equal to data_out length")
                self.status.Error(self, "\toutgoing: %d" % len(data_out))
                self.status.Error(self, "\tincomming: %d" % len(data_in))

        
        dout = data_out.tolist()
        din = data_in.tolist()


        for i in range(len(data_out)):
            out_val = dout[i]
            in_val = din[i]
            if out_val != in_val:
                print "%d and %d not equal" % (out_val, in_val)
                fail = True
                status = "Failed"
                if self.status.is_command_line(): 
                    self.status.Error(self,
                        "Mismatch at: {0:>8}: WRITE (Hex):[{0:>8}] Read (Hex): [{0:>8}]".format(
                        hex(i),
                        hex(data_out[i]),
                        hex(data_in[i])))
                if fail_count >= 16:
                    break
                fail_count += 1


        return status


def test_iterator(count):
    index = 0
    while index < count:
        yield index
        index += 1


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
                dev_index = n.find_device(5)
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
                #See if we can find a Memory device: 0
                dev_index = n.find_device(5)
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
        sys.exit("Failed to find a Memory")

    c.start_standalone_app(plat, dev_index)

if __name__ == "__main__":
    main(sys.argv)
