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

from nysa.host.driver.sd_host_driver import SDHostDriver
from nysa.host.driver.sd_host_driver import SDHostException
from nysa.host.driver.sdio_device_driver import SDIODeviceDriver

from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

DRIVER = SDHostDriver
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
            self.sd = None
            return
        n = plat[2]
        self.n = n
        sdio_urn = n.find_device(DRIVER)[0]
        self.sd = DRIVER(n, sdio_urn)
        sdio_urn = n.find_device(SDIODeviceDriver)[0]
        self.sdio = SDIODeviceDriver(n, sdio_urn)
        self.s.set_level("verbose")

        self.s.Info("Using Platform: %s" % plat[0])

    def test_sd_host_sdio(self):
        #self.s.Info("Host Control:\t\t0x%08X" % self.sd.get_control())
        self.sd.display_control()
        self.s.Info("Device Control:\t\t0x%08X" % self.sdio.get_control())
        self.s.Info("Delay: 0x%02X" % self.sd.get_input_delay())
        sd_host_input_delay_value = 63
        self.s.Info("Set Output delay to %d ( 0x%02X )" % (sd_host_input_delay_value, sd_host_input_delay_value))
        self.sd.set_input_delay(sd_host_input_delay_value)
        self.s.Info("Delay: 0x%02X" % self.sd.get_input_delay())

        self.sdio.enable_sdio_device(False)
        self.sdio.reset_core()

        sdio_input_delay_value = 20
        self.s.Info("Delay: 0x%02X" % self.sdio.get_input_delay())
        self.s.Info("Set Output delay to %d ( 0x%02X )" % (sdio_input_delay_value, sdio_input_delay_value))
        self.sdio.set_input_delay(sdio_input_delay_value)
        self.s.Info("Delay: 0x%02X" % self.sdio.get_input_delay())

        self.sdio.enable_sdio_device(True)
        #self.s.Info("Host Status:\t\t0x%08X" % self.sd.get_status())
        self.sd.display_status()
        self.s.Info("Device Control:\t\t0x%08X" % self.sdio.get_control())
        self.s.Info("Device Status:\t\t0x%08X" % self.sdio.get_status())
        self.s.Info("Host Attempting to set voltage range")
        self.sd.set_voltage_range(2.0, 3.6)
        self.s.Info("Host Enable SD Host")
        self.sd.enable_sd_host(True)

        self.s.Verbose("Setting Phy Select... should be no response")
        self.sdio.display_control()
        self.sdio.display_status()
        self.sd.cmd_phy_sel()
        self.sd.display_crcs()
        self.sdio.display_crcs()

        self.s.Verbose("Phy State should be 0x00")
        self.s.Info("SD Command:\t\t0x%08X" % self.sdio.get_sd_cmd())
        self.s.Info("Host Control:\t\t0x%08X" % self.sd.get_control())

        try:
            self.s.Verbose("Send Command 5")
            self.sd.cmd_io_send_op_cond(enable_1p8v = True)
            self.sd.display_crcs()
            self.sdio.display_crcs()
            self.s.Info("SD Command:\t\t0x%08X" % self.sdio.get_sd_cmd())
            self.s.Info("SD Command Arg:\t\t0x%08X" % self.sdio.get_sd_cmd_arg())
            self.s.Info("Response Value:\t\t0x%0X" % self.sd.read_response())

            self.s.Verbose("Get Relative Address")
            self.sd.cmd_get_relative_card_address()
            self.sd.display_crcs()
            self.sdio.display_crcs()
            self.s.Info("SD Command:\t\t0x%08X" % self.sdio.get_sd_cmd())
            self.s.Info("SD Command Arg:\t\t0x%08X" % self.sdio.get_sd_cmd_arg())
            self.s.Info("Response Value:\t\t0x%0X" % self.sd.read_response())


            '''

            self.s.Verbose("Enable Card")
            self.sd.cmd_enable_card(True)
            self.sd.display_crcs()
            self.sdio.display_crcs()

            self.s.Verbose("Read a configuration byte")
            value = self.sd.read_config_byte(0x00)
            self.sd.display_crcs()
            self.sdio.display_crcs()

            self.s.Important("Read Value: 0x%02X" % value)
            '''
        except SDHostException as e:
            self.s.Error("Failed data transfer!: %s" % str(e))

        self.sd.display_control()
        #self.s.Info("Host Control:\t\t0x%08X" % self.sd.get_control())
        #self.s.Info("Host Status:\t\t0x%08X" % self.sd.get_status())
        self.sd.display_status()
        #self.s.Warning("Device Status:\t\t0x%08X" % self.sdio.get_status())
        self.sdio.display_status()
        '''
        self.s.Info("Clock Count:\t\t0x%08X" % self.sdio.get_clock_count())
        self.s.Info("SD Command:\t\t0x%08X" % self.sdio.get_sd_cmd())
        self.s.Info("SD Command Arg:\t\t0x%08X" % self.sdio.get_sd_cmd_arg())

        #data_out = [0x0F, 0x0E, 0x0D, 0x0C, 0x0B, 0x0A, 0x09, 0x08]
        #data_out = [0x08]
        #self.sd.write_sd_data(function_id = 1, address = 0x00, data = data_out)

        self.s.Info("Attempt to read a byte of data")

        data_out = [0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]
        #data_out = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        #data_out = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.sdio.write_local_buffer(0, data_out)
        data = self.sdio.read_local_buffer(0, 2)
        print "Data: %s" % print_hex_array(data)

        #value = self.sd.read_sd_data(function_id = 1, address = 0x00, byte_count = len(data_out), fifo_mode = False)
        #value = self.sd.read_sd_data(function_id = 1, address = 0x00, byte_count = 0x20, fifo_mode = False)
        value = self.sd.read_sd_data(function_id = 0, address = 0x00, byte_count = 0x20, fifo_mode = False)
        self.s.Info("SD Command:\t\t0x%08X" % self.sdio.get_sd_cmd())
        self.s.Info("SD Command Arg:\t\t0x%08X" % self.sdio.get_sd_cmd_arg())

        print "Value: %s" % print_hex_array(value)
        #data = self.sdio.read_local_buffer(0, 2)
        #print "Data: %s" % print_hex_array(data)

        #value = self.sd.read_sd_data(function_id = 1, address = 0x00, byte_count = 8, fifo_mode = False)
        #print "Value: %s" % str(value)
        '''

def print_hex_array(a):
    s = None
    for i in a:
        if s is None:
            s = "["
        else:
            s += ", "

        s += "0x%02X" % i

    s += "]"

    return s

if __name__ == "__main__":
    unittest.main()

