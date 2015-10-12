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

from nysa.host.driver.sdio_device_driver import SDIODeviceDriver

from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

DRIVER = SDIODeviceDriver
MAX_LONG_SIZE = 0x0800000
TIMEOUT = 1.0



class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
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
            self.sdio_drv = None
            return
        n = plat[2]
        self.n = n
        sdio_urn = n.find_device(DRIVER)[0]
        self.sdio = DRIVER(n, sdio_urn)
        self.s.set_level("verbose")

        self.s.Info("Using Platform: %s" % plat[0])
        self.s.Info("Instantiated a SDIO Device Device: %s" % sdio_urn)

    def test_sdio_device(self):
        self.s.Info("Hello!")
        self.s.Info("Control: 0x%08X" % self.sdio.get_control())
        self.s.Info("Enable Interrupt: %s" % self.sdio.is_interrupt_enable())
        self.sdio.enable_interrupt(True)
        self.s.Info("Enable Interrupt: %s" % self.sdio.is_interrupt_enable())
        self.s.Info("Control: 0x%08X" % self.sdio.get_control())
        self.sdio.enable_sdio_device(True)
        self.s.Info("Control: 0x%08X" % self.sdio.get_control())
        self.sdio.set_control(0x01)
        self.s.Info("Control: 0x%08X" % self.sdio.get_control())
        self.sdio.write_local_buffer(0, [0, 1, 2, 3, 4, 5, 6, 7, 8])
        data = self.sdio.read_local_buffer(0, 2)
        self.s.Info("Buffer Out: %s" % str(data))

if __name__ == "__main__":
    unittest.main()

