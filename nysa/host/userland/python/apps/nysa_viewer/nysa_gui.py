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


""" nysa interface
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'


import argparse
import sys
import os
from inspect import isclass
from inspect import ismodule

from PyQt4.Qt import *
from PyQt4.QtCore import *

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir,
                             os.pardir))

from view.main_view import MainForm
from status import Status
from actions import Actions
from nysa_control import NysaControl

from phy.phy import Phy
import phy

DESCRIPTION = "\n" \
"\n"\
"usage: nysa.py [options]\n"

EPILOG = "\n" \
"\n"\
"Examples:\n"\
"\tSomething\n" \
"\t\ttest_dionysus.py\n"\
"\n"

debug = False

class NysaGui(QObject):

    def __init__(self):
        super (NysaGui, self).__init__()

        app = QApplication(sys.argv)
        mf = MainForm()
        self.actions = Actions()
        self.status = Status()
        self.status.Debug(self, "Created main form!")

        #Connect the action signal to a local function
        self.actions.refresh_signal.connect(self.refresh_phy_tree)
        self.nysa_control = NysaControl(mf.get_fpga_view())
        self.refresh_phy_tree()
        sys.exit(app.exec_())

    def refresh_phy_tree(self):
        self.actions.clear_phy_tree_signal.emit()
        phy_dir = os.path.join(os.path.dirname(__file__), "phy")
        #print "Phy: %s" % str(os.listdir(phy_dir))
        phy_files = os.listdir(phy_dir)
        phy_classes = []
        for f in phy_files:
            if f.endswith("pyc"):
                continue

            if f.startswith("__init__"):
                continue

            f = f.split(".")[0]
            m = __import__("phy.%s" % f)
            for name in dir(m):
                item = getattr(m, name)
                if not ismodule(item):
                    continue
                
                for mname in dir(item):
                    #print "Name: %s" % mname
                    #print "Type: %s" % str(type(mname))
                    obj = getattr(item, mname)

                    if not isclass(obj):
                        #print "Type: %s" % str(type(obj))
                        continue
                    if issubclass(obj, Phy) and obj is not Phy:
                        unique = True
                        for phy_class in phy_classes:
                            if type(phy_class) == type(obj):
                                unique = False
                        if unique:
                            #print "Adding Class: %s" % str(obj)
                            phy_classes.append(obj)

        phy_instances = []
        for pc in phy_classes:
            phy_instances.append(pc())

        for pi in phy_instances:
            dev_dict = pi.scan()
            for d in dev_dict:
                self.status.Info(self, "Refresh The Physical Tree")
                self.actions.add_device_signal.emit(pi.get_type(), d, dev_dict[d])

        self.actions.phy_tree_get_first_dev.emit()

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
            formatter_class = argparse.RawDescriptionHelpFormatter,
            description = DESCRIPTION,
            epilog = EPILOG
    )
    debug = False

    parser.add_argument("-d", "--debug",
                        action = "store_true",
                        help = "Enable Debug Messages")

    args = parser.parse_args()

    if args.debug:
        print ("Debug Enable")
        debug = True

    n = NysaGui()

if __name__ == "__main__":
    main(sys.argv)

