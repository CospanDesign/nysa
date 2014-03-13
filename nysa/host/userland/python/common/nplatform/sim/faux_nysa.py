# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

""" dionysus

Concrete interface for Nysa on the Dionysus platform
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

""" Changelog:
10/18/2013
    -Pep8ing the module and some cleanup
09/21/2012
    -added core dump function to retrieve the state of the master when a crash
    occurs
08/30/2012
    -Initial Commit
"""
import sys
import os
import time
from array import array as Array


p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir)
#print "Path: %s" % os.path.abspath(p)
sys.path.append(p)
from nysa import Nysa

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "ibuilder",
                 "lib")
#print "Path: %s" % os.path.abspath(p)
sys.path.append(p)

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "ibuilder",
                 "lib",
                 "gen_scripts")

#print "Path: %s" % os.path.abspath(p)
sys.path.append(p)
from gen_drt import GenDRT

p = os.path.join(os.path.dirname(__file__),
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 os.pardir,
                 "cbuilder",
                 "drt")
sys.path.append(p)
import drt as drt_controller
from drt import DRTError
from drt import DRTManager




class FauxNysa(Nysa):

    def __init__(self, dev_dict, debug = False):
        Nysa.__init__(self, debug)
        self.dev_dict = dev_dict

    def read(self, device_id, address, length = 1, mem_device = False):
        read_array = Array('B')
        for i in range(length):
            read_array.append(i)
        return read_array

    def write(self, device_id, address, data=None, mem_device=False):
        return

    def ping(self):
        return

    def reset(self):
        return

    def read_drt(self):
        """read_drt

        Read the contents of the DRT

        Args:
          Nothing

        Returns (Array of bytes):
          the raw DRT data, this can be ignored for normal operation 

        Raises:
          Nothing
        """

        gd = GenDRT()
        #d = gd.gen_script(self.dev_dict, debug = True)
        d = gd.gen_script(self.dev_dict, debug = False)
        drt_array = Array('B')
        dl = d.splitlines()
        print "DL Lenght: %d" % len(dl)
        for l in dl:
            #print "l: %s" % l
            i = int(l, 16)
            drt_array.append((i >> 24) & 0xFF)
            drt_array.append((i >> 16) & 0xFF)
            drt_array.append((i >>  8) & 0xFF)
            drt_array.append((i      ) & 0xFF)
       
        #print "d: %s" % str(d)
        num_of_devices  = drt_controller.get_number_of_devices(drt_array)
        #print "Num Devices: %d" % num_of_devices

        len_to_read = num_of_devices * 8
        self.drt_manager.set_drt(drt_array)
        return drt_array


    def wait_for_interrupts(self, wait_time = 1):
        time.sleep(0.1)
        return
