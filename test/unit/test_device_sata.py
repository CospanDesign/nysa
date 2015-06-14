#!/usr/bin/python

import unittest
import json
import sys
import os
import time
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver.sata_driver import SATADriver
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

DRIVER = SATADriver

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("verbose")
        plat = ["", None, None]
        pscanner = PlatformScanner()
        platform_dict = pscanner.get_platforms()
        platform_names = platform_dict.keys()

        if "sim" in platform_names:
            #If sim is in the platforms, move it to the end
            platform_names.remove("sim")
            platform_names.append("sim")
        urn = None
        for platform_name in platform_names:
            if plat[1] is not None:
                break

            self.s.Debug("Platform: %s" % str(platform_name))

            platform_instance = platform_dict[platform_name](self.s)
            #self.s.Verbose("Platform Instance: %s" % str(platform_instance))

            instances_dict = platform_instance.scan()

            for name in instances_dict:

                #s.Verbose("Found Platform Item: %s" % str(platform_item))
                n = instances_dict[name]
                plat = ["", None, None]

                if n is not None:
                    self.s.Important("Found a nysa instance: %s" % name)
                    n.read_sdb()
                    #import pdb; pdb.set_trace()
                    if n.is_device_in_platform(DRIVER):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.drv = None
            return
        n = plat[2]
        urn = n.find_device(DRIVER)[0]
        self.drv = DRIVER(n, urn)
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a DRIVER Device: %s" % urn)

    def test_all_base_values(self):
        if self.drv is None:
            self.s.Fatal("Cannot Run Test when no device is found!")
            return
        self.drv.enable_sata_reset(True)
        self.s.Info("Reseting Hard Drive, sleeping for a half second...")
        time.sleep(0.5)
        self.drv.enable_sata_reset(False)
        self.s.Info("Hard Drive Reset, sleeping for a half second...")
        time.sleep(0.75)

        self.s.Info("Sata in reset: %s" % self.drv.is_sata_reset())
        self.s.Info("Is reset in progress: %s" % self.drv.is_sata_reset_active())
        self.s.Info("Command Layer Reset: %s" % self.drv.is_sata_command_layer_reset())
        self.s.Info("Is platform ready: %s" % self.drv.is_platform_ready())
        self.s.Info("Is platform error: %s" % self.drv.is_platform_error())
        self.s.Important("linkup: %s" % self.drv.is_linkup())
        self.s.Info("phy layer ready: %s" % self.drv.is_phy_ready())
        self.s.Info("link layer ready: %s" % self.drv.is_link_layer_ready())
        self.s.Info("sata busy: %s" % self.drv.is_sata_busy())
        self.s.Info("is hard drive error: %s" % self.drv.is_hard_drive_error())
        self.s.Info("PIO data ready: %s" % self.drv.is_pio_data_ready())
        self.s.Info("RX COMM Init Detect: %s" % self.drv.get_rx_comm_init_detect())
        self.s.Info("RX COMM Wake Detect: %s" % self.drv.get_rx_comm_wake_detect())
        self.s.Info("TX OOB Complete: %s" % self.drv.get_tx_oob_complete())

        self.s.Info("TX Comm Reset Detect: %s" % self.drv.get_tx_comm_reset())
        self.s.Info("TX Comm Wake Detect: %s" % self.drv.get_tx_comm_wake())
        self.s.Debug("OOB State: 0x%04X" % self.drv.get_oob_state())
        self.s.Debug("Reset Count: 0x%08X" % self.drv.get_reset_count())
        self.s.Debug("Debug Linkup Data: 0x%08X" % self.drv.get_debug_linkup_data())

        self.s.Debug("Write to local buffer")
        values = Array('B')
        for i in range (512 * 4):
            values.append(i % 256)

        self.drv.write_local_buffer(values)
        buf = self.drv.read_local_buffer()
        if len(values) != len(buf):
            self.s.Error("Length of write does not match length of read! %d != %d" % (len(values), len(buf)))
        else:
            self.s.Important("Lengths of test write and test read match!")

        error_count = 0
        for i in range(len(values)):
            if error_count > 16:
                break
            if values[i] != buf[i]:
                error_count += 1
                self.s.Error("Error at Address 0x%04X: 0x%02X != 0x%02X" % (i, values[i], buf[i]))

