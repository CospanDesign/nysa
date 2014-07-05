#! /usr/bin/python

# Copyright (c) 2014 name (email@example.com)

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

__author__ = 'email@example.com (name)'

import os
import sys
import argparse

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

#from driver import ???

from apps.common.nysa_base_controller import NysaBaseController
import apps

from view.view import View

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


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        pass

    @staticmethod
    def get_name():
        #Change this for your app
        return "app_template"

    def _initialize(self, platform, device_index):
        self.v = View(self.status, self.actions)
        self.v.setup_simple_text_output_view()

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
        self.status.Verbose(self, "Starting Template Application")
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
        """
        If this is a controller for an individual device (GPIO, I2C, UART,
        etc...) return the associted device ID here (notes for the device are in
        /nysa/cbuilder/drt/drt.json
        """
        return None

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
                dev_index = None
                #dev_index = n.find_device(I2C.get_core_id())
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
                #See if we can find a device

                dev_index = None
                #dev_index = n.find_device(I2C.get_core_id())
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
        sys.exit("Failed to find an Device")

    c.start_standalone_app(plat, dev_index, debug)

if __name__ == "__main__":
    main(sys.argv)

