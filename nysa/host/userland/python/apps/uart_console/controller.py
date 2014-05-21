#! /usr/bin/python

# Copyright (c) 2014 Cospan Design LLC (dave.mccoy@cospandesign.com)

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
UART Console
"""

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

from driver.uart import UART
from uart_actions import UARTActions

from apps.common.nysa_base_controller import NysaBaseController
import apps

from view.uart_widget import UARTWidget

#Module Defines
n = str(os.path.split(__file__)[1])


#Platform Scanner
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from platform_scanner import PlatformScanner
import status

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "protocol_utils",
                             "uart"))


from uart_engine import UARTEngine



DESCRIPTION = "\n" \
"\n"\
"A template app\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.uart = None
        self.actions = UARTActions()
        self.actions.uart_baudrate_change.connect(self.baudrate_change)
        self.actions.uart_flowcontrol_change.connect(self.flowcontrol_change)
        self.actions.uart_data_out.connect(self.uart_data_out)
        self.actions.uart_read_data.connect(self.uart_read_data)

    @staticmethod
    def get_name():
        return "UART Console"

    def _initialize(self, platform, device_index):
        self.uart = UART(platform[2], device_index)
        self.v = UARTWidget(self.status, self.actions)

        #Setup the UART
        self.uart.set_baudrate(self.v.get_baudrate())
        self.flowcontrol_change(self.v.get_flowcontrol())
        data = self.uart.read_all_data()
        #self.v.append_text(data.tostring())
        self.v.append_text(data.tostring())
        self.uart.disable_interrupts()

        self.engine = UARTEngine(self.uart, self.actions, self.status)

        self.actions.uart_data_in.connect(self.uart_data_in)
        self.uart.enable_read_interrupt()

    def start_standalone_app(self, platform, device_index, debug = False):
        app = QApplication (sys.argv)
        self.status = status.ClStatus()
        if debug:
            self.status.set_level(status.StatusLevel.VERBOSE)
        else:
            self.status.set_level(status.StatusLevel.INFO)

        self._initialize(platform, device_index)
        self.status.Verbose(self, "Starting I2C Application")
        sys.exit(app.exec_())

    def start_tab_view(self, platform, device_index):
        self.status = status.Status()
        self._initialize(platform, device_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        return None

    @staticmethod
    def get_device_id():
        return UART.get_core_id()

    @staticmethod
    def get_device_sub_id():
        #return UART.get_core_sub_id()
        return None

    @staticmethod
    def get_device_unique_id():
        return None

    def uart_data_out(self, data):
        if self.uart is None:
            return
        d = Array('B')
        d.fromstring(data)
        #print "data: %s" % str(d)
        if len(data) > 0:
            self.uart.write_string(data)
            if d[0] == 13:
                self.uart.write_byte(10)

    def uart_read_data(self):
        data = self.uart.read_all_data()
        if len(data) > 0:
            self.uart_data_in(data.tostring())

    def uart_data_in(self, data):
        #print "data in: %s" % data
        self.v.append_text(data)
        self.uart.get_status()

    def baudrate_change(self, baudrate):
        self.uart.set_baudrate(baudrate)

    def flowcontrol_change(self, flowcontrol):
        flowcontrol = str(flowcontrol)
        if flowcontrol.lower() == "none":
            self.uart.disable_flowcontrol()

        elif flowcontrol.lower() == "soft":
            self.uart.enable_soft_flowcontrol()

        elif flowcontrol.lower() == "hardware":
            self.uart.enable_hard_flowcontrol()

        self.uart.enable_hard_flowcontrol()

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
                dev_index = n.find_device(UART.get_core_id())
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
                dev_index = n.find_device(UART.get_core_id())
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
        sys.exit("Failed to find an I2C Device")

    c.start_standalone_app(plat, dev_index, debug)

if __name__ == "__main__":
    main(sys.argv)

