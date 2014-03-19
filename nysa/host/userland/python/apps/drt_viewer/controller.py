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
DRT (Device Rom Table Viewer)
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import argparse

from PyQt4.Qt import QApplication

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from apps.common.nysa_base_controller import NysaBaseController
import apps

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             "common"))

from platform_scanner import PlatformScanner
import status

from view.view import View
from model.model import AppModel


#Module Defines
n = str(os.path.split(__file__)[1])

DESCRIPTION = "\n" \
"\n"\
"A DRT Viewer\n"

EPILOG = "\n"

DRT_DESC_LOC = os.path.join(os.pardir,
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            os.pardir,
                            "docs",
                            "drt.txt")

print "DLOC: %s" % os.path.abspath(DRT_DESC_LOC)


class Controller(NysaBaseController):

    def __init__(self):
        super (Controller, self).__init__()
        f = open(DRT_DESC_LOC, 'r')
        s = f.read()
        f.close()
        s = s.split("DESCRIPTION START")[1]
        s = s.split("DESCRIPTION END")[0]
        #print "s: %s" % s
        self.drt_desc = s
        self.m = AppModel()


    def _initialize(self, platform):
        self.m.setup_model(self, platform[2])
        self.v = View(self.status, self.actions)
        self.v.setup_simple_text_output_view()
        self.v.clear_text()
        self.v.append_text(self.drt_desc)

        for i in range(self.m.get_row_count()):
            row_data = self.m.get_row_data(i)
            #print "%s" % row_data[0]
            index = "0x%02X" % i
            self.v.add_drt_entry(index, row_data[0], row_data[1], row_data[2], row_data[3])

            #for j in range(len(row_data[1])):
            #    print "\t%s" % row_data[1][j]

        self.v.resize_columns()
        self.v.collapse_all()

    def start_standalone_app(self, platform):
        app = QApplication (sys.argv)
        self._initialize(platform)
        sys.exit(app.exec_())

    def start_tab_view(self, platform):
        self._initialize(platform)

    def get_view(self):
        return self.v

    @staticmethod
    def get_name():
        return "DRT Viewer"

    @staticmethod
    def get_unique_image_id():
        return None

    @staticmethod
    def get_device_id():
        #ID of DRT
        return 0

    @staticmethod
    def get_device_sub_id():
        return None

    @staticmethod
    def get_device_unique_id():
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

    if debug:
        s.Debug(None, "Display a list of platforms found")
    pscanner = PlatformScanner()
    ps = pscanner.get_platforms()
    for p in ps:
        s.Verbose(None, p)
        for psi in ps[p]:
            if plat is None:
                s.Verbose(None, "Found a platform: %s" % p)
                plat = [p, psi, ps[p][psi]]
                continue
            if p == args.platform and plat[0] != args.platform:
                #Found a match for a platfom to use
                plat = [p, psi, ps[p][psi]]
                continue
            if p == psi:
                #Found a match for a name!
                plat = [p, psi, ps[p][psi]]

            s.Verbose(None, "\t%s" % psi)

    if args.list:
        s.Verbose(None, "Listed all platforms, exiting")
        sys.exit(0)

    if plat is not None:
        s.Important(None, "Using: %s" % plat)
    else:
        s.Fatal(None, "Didn't find a platform to use!")

    c = Controller()
    c.start_standalone_app(plat)

if __name__ == "__main__":
    main(sys.argv)
