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


""" nysa controller
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os

from PyQt4.Qt import *
from PyQt4.QtCore import *

from status import Status
from actions import Actions

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir))


class NysaControl(QObject):
    def __init__(self, fpga_image):
        super(NysaControl, self).__init__()
        self.status = Status()
        self.actions = Actions()
        self.n = None
        self.uid = None
        self.dev_type = None
        self.actions.phy_tree_changed_signal.connect(self.nysa_device_changed)
        self.fpga_image = fpga_image
        self.fpga_image.clear()


    def nysa_device_changed(self, uid, dev_type, nysa_device):
        #if uid == uid:
        #    #Don't change anything if it's the same UID
        #    self.status.Verbose(self, "Same UID, no change")
        #    return

        self.status.Debug(self, "Device Changed")
        if dev_type is None:
            self.n = None
            self.status.Info(self, "No Device Selected")
            self.fpga_image.clear()
            return

        self.uid = uid
        self.dev_type = dev_type
        self.n = nysa_device

        self.n.read_drt()
        print "Memory Size: 0x%08X" % self.n.get_total_memory_size()

        
