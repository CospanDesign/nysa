# Copyright (c) 2010-2011, Emmanuel Blot <emmanuel.blot@free.fr>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Neotion nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL NEOTION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import json
from array import array as Array

from pyftdi.pyftdi.spi import SpiController

#Get all types of the SPI Flash
import numonyx_flash



CMD_JEDEC_ID = 0x9F

#Exceptions
class SerialFlashNotSupported(Exception):
    """Exception thrown when a non-existing feature is invoked"""

class SerialFlashUnknownJedec(SerialFlashNotSupported):
    """Exception thrown when a JEDEC identifier is not recognized"""
    def __init__(self, jedec):
        from binascii import hexlify
        SerialFlashNotSupported.__init__(self, "Unknown Flash Device: %s" % \
                                         hexlify(jedec))

class SerialFlashTimeout(Exception):
    """Exception thrown when a flash command cannot be completed in a timely
    manner"""

class SerialFlashValueError(ValueError):
    """Exception thrown when a parameter is out of range"""


class SerialFlashManager(object):
    """ Serial Flash Manager

    Automatically detects and instantiates the proper flash device class
    based on the JEDEC identifier which is read out from the device.
    """


    def __init__(self,
                 vendor,
                 product,
                 interface = 2,
                 prom_config_file = "proms.json",
                 debug = False):

        self._ctrl = SpiController(silent_clock = False)
        self._ctrl.configure(vendor, product, interface)
        #Load the configuration file
        name = prom_config_file
        if not os.path.exists(prom_config_file):
            name = os.path.join(os.path.dirname(__file__), prom_config_file)

        f = open(name, "r")
        self.devices = {}
        proms = {}
        proms = json.load(f)
        if debug:
            print "Loaded: %s" % name
            print "Proms: %s" % str(proms)


        for man in proms:
            #change the string representation of hex to a real hex
            man_hex = int(man, 16)
            if debug:
                print "man: 0x%02X" % man_hex
                print "Manufacturer: %s" % proms[man]["Manufacturer"]
                print "\tDevices:"

            self.devices[man_hex] = {}
            #Copy over the manufacturer's name
            self.devices[man_hex]["Manufacturer"] = proms[man]["Manufacturer"]
            self.devices[man_hex]["Devices"] = {}

            for device in proms[man]["Devices"]: 
                dev_hex = int(device, 16)
                if debug:
                    print "\t\tFound: 0x%02X" % dev_hex

                self.devices[man_hex]["Devices"][dev_hex] = {}
                self.devices[man_hex]["Devices"][dev_hex]["Description"] = proms[man]["Devices"][device]["Description"]
                self.devices[man_hex]["Devices"][dev_hex]["capacity"] = int(proms[man]["Devices"][device]["capacity"], 16)


    def get_flash_device(self, cs = 0, debug = False):
        """Obtain an instance of the detected flash device"""
        spi = self._ctrl.get_port(cs)
        jedec = SerialFlashManager.read_jedec_id(spi)
        if debug:
            print "Jedec: %s" % str(jedec)
        if not jedec:
            #It's likely the latency setting is too low if this conditio is
            #Encountered
            raise SerialFlashUnknownJedec("Unable to read JEDEC ID")

        #Go through the PROM to find the identification of this device
        maxlength = 3
        ids = tuple([ord(x) for x in jedec[:maxlength]])
        if debug:
            print "SPI Values: 0x%02X 0x%02X 0x%02X" % (ids[0], ids[1], ids[2])
            #print "Manufacturer: %s" % self.devices[ids[1]]["Manufacturer"]
            #print "Values: %s" % str(self.devices[ids[1]]["Devices"])
            print "Device: %s" % self.devices[ids[1]]["Devices"][ids[2]]["Description"]
        if ids[1] == numonyx_flash.NumonyxFlashDevice.ID:
            #print "Found Numonyx Device"
            return numonyx_flash.NumonyxFlashDevice(spi, ids[2])
        
        raise SerialFlashUnknownJedec(ids[1])


    @staticmethod
    def read_jedec_id(spi):
        """Read the flash device JEDEC Identifier (3 bytes)"""
        jedec_cmd = Array('B', [CMD_JEDEC_ID])
        spi_values = spi.exchange(jedec_cmd, 3)
        #print "SPI Values: %s" % str(spi_values)

        return spi.exchange(jedec_cmd, 3).tostring()

