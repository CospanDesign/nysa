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
I2C Controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

#I2C Driver
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from driver.i2c import I2C

from apps.common.nysa_base_controller import NysaBaseController
import apps

#I2C Protocol Utility
from view.i2c_widget import I2CWidget
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "protocol_utils"))


from i2c.i2c_controller import I2CController
from i2c.i2c_engine import I2CEngine
from i2c.i2c_engine import I2CEngineError

#Platform Scanner
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
"A template app\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n

from i2c_actions import I2CActions

from apps.common.udp_server import UDPServer
I2C_PORT = 0xC594

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = I2CActions()
        self.i2c = None
    
    def __del__(self):
        if self.i2c is not None:
            self.i2c.enable_i2c(False)

    @staticmethod
    def get_name():
        return "I2C Controller"

    def _initialize(self, platform, device_index):
        self.i2c = I2C(platform[2], device_index)
        self.m = I2CController(self.status, self.actions)
        self.server = UDPServer(self.status, self.actions, I2C_PORT)

        self.engine = I2CEngine(self.i2c, self.status, self.actions, self.server)
        init_transactions = self.m.get_all_init_transactions()
        #print "Transactions: %s" % str(test)
        self.v = I2CWidget(self.status, self.actions)
        self.v.update_i2c_init_transactions(init_transactions)
        self.v.set_save_callback(self.save_callback)
        self.v.set_load_callback(self.load_callback)
        self.v.set_load_default_callback(self.load_default_callback)
        #print "Files: %s" % str(files)
        self.v.load_default_scripts()

        self.actions.i2c_run.connect(self.i2c_run)
        self.actions.i2c_step.connect(self.i2c_step)
        self.actions.i2c_loop_step.connect(self.i2c_loop_step)

    def start_standalone_app(self, platform, device_index, debug = False):
        app = QApplication (sys.argv)
        self.status = status.ClStatus()
        if debug:
            self.status.set_level(status.StatusLevel.VERBOSE)
        else:
            self.status.set_level(status.StatusLevel.INFO)
        self.status.Verbose(self, "Starting Standalone Application")
        self._initialize(platform, device_index)
        sys.exit(app.exec_())

    def start_tab_view(self, platform, device_index):
        self.status = status.Status()
        self.status.Verbose(self, "Starting I2C Application")
        self._initialize(platform, device_index)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        return None

    @staticmethod
    def get_device_id():
        return 3

    @staticmethod
    def get_device_sub_id():
        return None

    @staticmethod
    def get_device_unique_id():
        return None

    def i2c_run(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions)
        else:
            self.engine.load_commands(init_transactions, loop_transactions)

    def i2c_step(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions, pause = True)

        self.engine.pause_flow()
        self.engine.step_flow()

    def i2c_loop_step(self):
        init_transactions = self.m.get_all_init_transactions()
        loop_transactions = self.m.get_all_loop_transactions()

        if not self.engine.is_running():
            self.engine.start_engine(init_transactions, loop_transactions, pause = True)

        self.engine.pause_flow()
        self.engine.step_loop_flow()

    def save_callback(self):
        filename = self.v.get_filename()
        name = self.v.get_config_name()
        description = self.v.get_config_description()
        self.status.Important(self, "Saving I2C Config File: %s" % filename)
        self.m.save_i2c_commands(filename, name, description)
        
    def load_default_callback(self, filename):
        self.status.Important(self, "Loading Default I2C Config File: %s" % filename)
        self.m.load_i2c_commands(filename)
        self.v.set_config_name(self.m.get_config_name())
        self.v.set_config_description(self.m.get_config_description())

    def load_callback(self):
        filename = self.v.get_filename()
        self.status.Important(self, "Loading I2C Config File: %s" % filename)
        self.m.load_i2c_commands(filename)

        self.v.set_config_name(self.m.get_config_name())
        self.v.set_config_description(self.m.get_config_description())



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
                dev_index = n.find_device(I2C.get_core_id())
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
                dev_index = n.find_device(I2C.get_core_id())
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

