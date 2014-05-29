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

from PyQt4.Qt import QApplication
from PyQt4 import QtCore

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from apps.common.nysa_base_controller import NysaBaseController
import apps

#View Interface
from view.view import View

#Platform Scanner
sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))


from platform_scanner import PlatformScanner
import status


from driver.spi import SPI

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "protocol_utils"))


from spi.sdcard_engine import SDCARDEngine

#Module Defines
n = str(os.path.split(__file__)[1])

from sdcard_actions import SDCARDActions

DESCRIPTION = "\n" \
"\n"\
"A template app\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\t%s Something\n"\
"\n" % n

SEEED_SDCARD_SHIELD_IMAGE_ID = 261

class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        self.actions = SDCARDActions()
        self.spi = None
        self.actions.sdcard_reset.connect(self.sdcard_reset_complete)

    @staticmethod
    def get_name():
        #Change this for your app
        return "Seeed Studio SDcard Shield"

    def _initialize(self, platform):
        self.v = View(self.status, self.actions)
        self.v.setup_simple_text_output_view()
        self.spi = SPI(platform[2], dev_id = 1)
        self.engine = SDCARDEngine(self.spi, self.status, self.actions)

    def start_standalone_app(self, platform, debug = False):
        app = QApplication (sys.argv)
        self.status = status.ClStatus()
        if debug:
            self.status.set_level(status.StatusLevel.VERBOSE)
        else:
            self.status.set_level(status.StatusLevel.INFO)
        self._initialize(platform)
        sys.exit(app.exec_())

    def start_tab_view(self, platform, debug = False):
        self.status = status.Status()
        self._initialize(platform)

    def get_view(self):
        return self.v

    @staticmethod
    def get_unique_image_id():
        return SEEED_SDCARD_SHIELD_IMAGE_ID

    @staticmethod
    def get_device_id():
        return None

    @staticmethod
    def get_device_sub_id():
        return None

    @staticmethod
    def get_device_unique_id():
        return None


    def sdcard_reset_complete(self):
        self.v.append_text("Reset Complete")

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
    image_id = None
    for p in ps:
        s.Verbose(None, p)
        for psi in ps[p]:
            if plat is None:
                s.Verbose(None, "Found a platform: %s" % p)
                n = ps[p][psi]
                n.read_drt()
                #n.drt_manager.pretty_print_drt()
                image_id = n.get_image_id()
                #print "image id: %s" % str(image_id)
                if image_id is not None and image_id == SEEED_SDCARD_SHIELD_IMAGE_ID:
                    print "Found an image ID that matches: %d" % image_id
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
    c.start_standalone_app(plat, debug)

if __name__ == "__main__":
    main(sys.argv)

