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
        self.s.set_level("verbose")
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a DRIVER Device: %s" % urn)

    def test_sata(self):
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
        #self.s.Info("Is reset in progress: %s" % self.drv.is_sata_reset_active())
        #self.s.Info("Command Layer Reset: %s" % self.drv.is_sata_command_layer_reset())
        self.s.Info("Is platform ready: %s" % self.drv.is_platform_ready())
        #self.s.Info("Is platform error: %s" % self.drv.is_platform_error())
        self.s.Important("linkup: %s" % self.drv.is_linkup())
        #self.s.Info("phy layer ready: %s" % self.drv.is_phy_ready())
        #self.s.Info("link layer ready: %s" % self.drv.is_link_layer_ready())
        #self.s.Info("sata busy: %s" % self.drv.is_sata_busy())
        #self.s.Info("is hard drive error: %s" % self.drv.is_hard_drive_error())
        #self.s.Info("PIO data ready: %s" % self.drv.is_pio_data_ready())
        #self.s.Info("RX COMM Init Detect: %s" % self.drv.get_rx_comm_init_detect())
        #self.s.Info("RX COMM Wake Detect: %s" % self.drv.get_rx_comm_wake_detect())
        #self.s.Info("TX OOB Complete: %s" % self.drv.get_tx_oob_complete())

        #self.s.Info("TX Comm Reset Detect: %s" % self.drv.get_tx_comm_reset())
        #self.s.Info("TX Comm Wake Detect: %s" % self.drv.get_tx_comm_wake())
        #self.s.Debug("OOB State: 0x%04X" % self.drv.get_oob_state())
        #self.s.Debug("Reset Count: 0x%08X" % self.drv.get_reset_count())
        #self.s.Debug("Debug Linkup Data: 0x%08X" % self.drv.get_debug_linkup_data())

        #self.s.Debug("Write to local buffer")
        self.s.Info("Local Buffer Test")
        values = Array('B')
        for i in range (2048 * 4):
            values.append(i % 256)

        self.drv.write_local_buffer(values)
        buf = self.drv.read_local_buffer()
        length_error = False
        if len(values) != len(buf):
            length_error = True
            self.s.Error("Length of write does not match length of read! %d != %d" % (len(values), len(buf)))

        error_count = 0
        for i in range(len(values)):
            if error_count > 16:
                break
            if values[i] != buf[i]:
                error_count += 1
                self.s.Error("Error at Address 0x%04X: 0x%02X != 0x%02X" % (i, values[i], buf[i]))

        if error_count > 0 or length_error:
            self.s.Error("Failed local buffer test")
        else:
            self.s.Important("Passed local buffer test!")

        #self.drv.get_hard_drive_size()
        ''' 
        rok_count = self.drv.get_r_ok_count()
        rok_count_before = rok_count
        rerr_count = self.drv.get_r_err_count()
        rerr_count_before = rerr_count

        print "ROK Test"
        self.s.Warning("ROK Count Before: %d" % rok_count)
        self.s.Warning("RERR Count Before: %d" % rerr_count)
        self.drv.hard_drive_idle()
        
        rok_count = self.drv.get_r_ok_count()
        rerr_count = self.drv.get_r_err_count()
        self.s.Warning("ROK Count After: %d" % rok_count)
        self.s.Warning("ROK Count Delta: %d" % (rok_count - rok_count_before))
        self.s.Warning("RERR Count After: %d" % rerr_count)
        self.s.Warning("RERR Count Delta: %d" % (rerr_count - rerr_count_before))
        '''
        self.s.Info("\tInitial Status of hard drive (Status): 0x%02X" % self.drv.get_d2h_status())

        if (self.drv.get_d2h_status() & 0x0004) == 0:
            self.s.Info("\tReceived 0 for status of hard drive, sending reset!")
            self.s.Info ("Sending reset command to hard drive")
            self.drv.send_hard_drive_command(0x08)

            self.s.Info("\tInitial (Status): 0x%02X" % self.drv.get_d2h_status())
            for i in range (32):
                self.drv.send_hard_drive_command(0xEC)
                if (self.drv.get_d2h_status() & 0x040) == 0:
                    print "Not Found..."
                else:
                    print "Found!"
            if (self.drv.get_d2h_status() & 0x040) == 0:
                self.s.Warning("Did not get a normal status response from the hard drive attempting soft reset")
                time.sleep(0.1)
                self.drv.enable_sata_command_layer_reset(True) 
                time.sleep(0.1)
                self.drv.enable_sata_command_layer_reset(False) 


        self.s.Info("Put Hard Drive in IDLE state")
        self.drv.hard_drive_idle()
        #self.s.Info("\tIdle Result (Status): 0x%02X" % self.drv.get_d2h_status())
        if (self.drv.get_d2h_status() & 0x040) == 0:
            self.s.Error("Did not get a normal status response from the hard drive")
            return

       

        native_size = self.drv.get_hard_drive_native_size()
        max_lba = self.drv.get_hard_drive_max_native_lba()
        print "Max Native LBA: %d" % max_lba
        self.s.Important("Native Size in gigabytes: %f" % ((native_size * 1.0) * 0.000000001))

        print "Identify Device:"
        data = self.drv.identify_hard_drive()[0:512]
        #print "\tLength of read: %d" % len(data)
        #print "\tdata from hard drive: %s" % str(data)

        config = self.drv.get_config()
        print "Serial Number: %s" % config.serial_number()
        print "Max User Sectors: %d" % config.max_user_sectors()
        print "Max User Size (GB): %f" % ((config.max_user_sectors() * 512.0) * 0.000000001)
        #print "Max Sector Capacity: %d" % config.capacity_in_sectors()
        #print "Max Sector Capacity (GB): %f" % ((config.capacity_in_sectors() * 512.0) * 0.000000001)
        #print "Buffer size (bytes): %d" % config.hard_drive_buffer_size()
        #print "DMA Transfer Mode..."
        #config.dma_transfer_mode()
        #config.sata_enabled_features()


        values = Array('B')
        clear_values = Array('B')
        for i in range (2048 * 4):
            values.append(i % 256)
            clear_values.append(0)

        self.drv.set_local_buffer_write_size(128)
        self.drv.write_local_buffer(values)
        #self.drv.write_local_buffer(clear_values)
        #print "Ready Status (Before):0x%02X" % self.drv.get_din_fifo_status()
        #print "Sata Ready: %s" % self.drv.is_command_layer_ready()
        #print "Sata Busy: %s" % self.drv.is_sata_busy()


        self.drv.load_local_buffer()
        self.drv.load_local_buffer()
        self.s.Important("Before Write Start DMA Activate: %s" % self.drv.is_dma_activate_en())
        #self.drv.hard_drive_write(0x0101, 16)
        #self.drv.hard_drive_write(0x0101, 1)
        self.drv.hard_drive_write(0x0000, 2)
        time.sleep(0.5)
        self.s.Important("After Write Start DMA Activate: %s" % self.drv.is_dma_activate_en())
        #self.drv.load_local_buffer()
        #self.drv.load_local_buffer()
        self.drv.set_local_buffer_write_size(2048)
        #self.drv.load_local_buffer()

        #print "Ready Status (Before):0x%02X" % self.drv.get_din_fifo_status()
        #print "command state: %d" % self.drv.get_cmd_wr_state()
        #print "transport state: %d" % self.drv.get_transport_state()
        #print "link layer write state: %d" % self.drv.get_link_layer_write_state()

        #print ""
        #print "Ready Status (Before Read):0x%02X" % self.drv.get_din_fifo_status()
        #print "Sata Ready: %s" % self.drv.is_command_layer_ready()
        #print "Sata Busy: %s" % self.drv.is_sata_busy()
        #print "phy layer ready: %s" % self.drv.is_phy_ready()
        #print ""

        #if self.drv.is_command_layer_ready():
        #print "*** CAN READ NOW! ***"
        self.s.Info("Reading from Hard Drive...")
        self.drv.write_local_buffer(clear_values)
        
        #self.drv.hard_drive_read(0x0101, 2)
        self.drv.hard_drive_read(0x0400, 2)
        
        print "Read Result:"
        print "\tstatus: 0x%02X" % self.drv.get_d2h_status()
        print "\terror : 0x%02X" % self.drv.get_d2h_error()
        print "\tLBA: 0x%012X" % self.drv.get_hard_drive_lba()
        print "\tSector Count: 0x%04X" % self.drv.get_sector_count()
        
        
        data = self.drv.read_local_buffer()
        #print "\tdata from hard drive: %s" % str(data[0:1024])
        print "\tLength of read: %d" % len(data)
        print "\tdata from hard drive: %s" % str(data[0:1024])
        print "\tReady Status :0x%02X" % self.drv.get_din_fifo_status()

        self.drv.hard_drive_sleep()

if __name__ == "__main__":
    unittest.main()

