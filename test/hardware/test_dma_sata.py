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
import nysa.host.driver.dma as dmam
from nysa.host.driver.dma import DMA
from nysa.host.driver.memory import Memory

from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

DRIVER = SATADriver
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
            self.sata_drv = None
            return
        n = plat[2]
        self.n = n
        sata_urn = n.find_device(DRIVER)[0]
        dma_urn = n.find_device(DMA)[0]
        self.memory_urn = self.n.find_device(Memory)[0]

        self.sata_drv = DRIVER(n, sata_urn)
        self.dma = DMA(n, dma_urn)
        self.s.set_level("verbose")

        self.s.Info("Using Platform: %s" % plat[0])
        self.s.Info("Instantiated a SATA Device: %s" % sata_urn)
        self.s.Info("Instantiated a DMA Device: %s" % dma_urn)

    def test_dma_sata(self):
        if self.sata_drv is None:
            self.s.Fatal("Cannot Run Test when no device is found!")
            return

        self.s.Info("Reseting Hard Drive...")
        self.sata_drv.enable_sata_reset(True)
        time.sleep(0.5)
        self.sata_drv.enable_sata_reset(False)
        time.sleep(0.75)
        self.s.Info("Reset Complete")

        if self.sata_drv.is_linkup():
            self.s.Important("Linked up with Hard Drive!")

        self.s.Info("\tInitial Status of hard drive (Status): 0x%02X" % self.sata_drv.get_d2h_status())

        if (self.sata_drv.get_d2h_status() & 0x040) == 0:
            self.s.Warning("\tReceived 0 for status of hard drive, sending reset!")
            self.s.Warning ("Sending reset command to hard drive")
            self.sata_drv.send_hard_drive_command(0x08)

            if (self.sata_drv.get_d2h_status() & 0x040) == 0:
                self.s.Warning("Still Received 0x00 after reset, send a sequence of identify commands to get hard drive into known state")
                for i in range (32):
                    self.sata_drv.send_hard_drive_command(0xEC)
                    if (self.sata_drv.get_d2h_status() & 0x040) > 0:
                        print "Found!"
                        break

                if (self.sata_drv.get_d2h_status() & 0x040) == 0:
                    self.s.Warning("Did not get a normal status response from the hard drive attempting soft reset")
                    time.sleep(0.1)
                    self.sata_drv.enable_sata_command_layer_reset(True)
                    time.sleep(0.1)
                    self.sata_drv.enable_sata_command_layer_reset(False)
                    self.sata_drv.send_hard_drive_command(0x00)
                    if (self.sata_drv.get_d2h_status() & 0x040) == 0:
                        self.s.Error("After Soft Reset Still Did not get a good response")
                        sys.exit(1)



        self.sata_drv.identify_hard_drive()
        config = self.sata_drv.get_config()
        self.s.Verbose("Hard Drive Serial Number: %s" % config.serial_number())
        max_user_lba = config.max_user_sectors()
        self.s.Verbose("Max User Sectors: %d" % config.max_user_sectors())
        self.s.Verbose("Max User Size (GB): %f" % ((config.max_user_sectors() * 512.0) * 0.000000001))

        #Clear out a block of memory
        values = Array('B')
        clear_values = Array('B')
        for i in range (2048 * 4):
            values.append(i % 256)
            clear_values.append(0)

        self.sata_drv.set_local_buffer_write_size(128)
        self.sata_drv.write_local_buffer(clear_values)
        self.sata_drv.load_local_buffer()
        self.sata_drv.hard_drive_write(0x0000, 1)

        self.sata_drv.hard_drive_read(0x0000, 1)
        data = self.sata_drv.read_local_buffer()
        self.s.Verbose("Data from Hard Drive Before DMA Transfer (Should be all zeros):")
        print str(data[0:128])

        self.sata_drv.enable_dma_control(True)

        self.s.Info("Setup DMA")
        self.dma.setup()
        self.dma.enable_dma(True)

        #DMA Configuration
        CHANNEL_ADDR        = 2
        SINK_ADDR           = 0
        INST_ADDR           = 0
        DDR3_ADDRESS        = 0x0000000000000000
        SATA_ADDRESS        = 0x0000000000000000
        #WORD_TRANSFER_COUNT = 0x1000
        #WORD_TRANSFER_COUNT = 0x800
        #WORD_TRANSFER_COUNT = 2048

        #Rarely Failed:
        #WORD_TRANSFER_COUNT = 0x2000
        #WORD_TRANSFER_COUNT = 0x16000
        WORD_TRANSFER_COUNT = 0x700000
        MEGABYTES = (WORD_TRANSFER_COUNT * 4.0) / 1000000.0
        self.s.Info ("Transfer Size: 0x%08X" % WORD_TRANSFER_COUNT)

        #Fill Memory With Data
        self.s.Important("Fill memory with pattern")
        self.s.Important("Configure DMA to transfer %f MB from DDR3 to Hard Drive" % MEGABYTES)
        self.fill_memory_with_pattern()

        #Configure DMA to transfer 100MB of data from DDR3 to hard drive
        self.dma.set_channel_sink_addr              (CHANNEL_ADDR, SINK_ADDR            )
        self.dma.set_channel_instruction_pointer    (CHANNEL_ADDR, INST_ADDR            )
        self.dma.enable_source_address_increment    (CHANNEL_ADDR, True                 )

        self.dma.enable_dest_address_increment      (SINK_ADDR,    True                 )
        self.dma.enable_dest_respect_quantum        (SINK_ADDR,    True                 )

        self.dma.set_instruction_source_address     (INST_ADDR,    DDR3_ADDRESS         )
        self.dma.set_instruction_dest_address       (INST_ADDR,    SATA_ADDRESS         )
        self.dma.set_instruction_data_count         (INST_ADDR,    WORD_TRANSFER_COUNT  )
        #This is only needed if we are going to another instruction after this
        self.dma.set_instruction_next_instruction   (INST_ADDR,    INST_ADDR            )
        self.dma.enable_instruction_continue        (INST_ADDR,    False                )

        #Initate DMA Transaction
        self.s.Important("Intiate a DMA Transaction")
        self.dma.enable_interrupt_when_command_finished(True)
        self.dma.enable_channel                     (CHANNEL_ADDR, True                 )

        #Transaction Complete
        self.s.Important("DMA Transaction is complete")
        #self.dma.wait_for_interrupts(wait_time = 10)
        self.s.Info ("Wait for transaction to finish")
        fail = False
        timeout = time.time() + TIMEOUT
        while not self.dma.is_channel_finished(CHANNEL_ADDR):
            print ".",
            if time.time() > timeout:
                print ""
                self.s.Error("Timeout Occured!")
                fail = True
                break
        if fail:
            self.fail_analysis(CHANNEL_ADDR, SINK_ADDR, INST_ADDR)
            return

        self.s.Info ("Transaction Finished!")
        #print "\tSATA Current Address:              0x%08X" % self.sata_drv.get_hard_drive_lba()

        self.dma.enable_channel                     (CHANNEL_ADDR, False                )
        self.sata_drv.enable_dma_control(False)


        self.sata_drv.hard_drive_read(0x0000, 1)
        data = self.sata_drv.read_local_buffer()
        self.s.Verbose("Data from Hard Drive (Should be incrementing number patter):")
        print str(data[0:128])
        self.sata_drv.enable_dma_control(True)


        #Clear DDR3 Memory
        self.s.Important("Clear DDR3 Memory")
        self.clear_memory()
        data = self.n.read_memory(0x00, 128)
        self.s.Verbose("Data read from memory after clear (Should be all zeros):")
        print str(data[0:128])

        #Configure DMA to transfer 100MB of data from hard drive to DDR3
        CHANNEL_ADDR        = 0
        SINK_ADDR           = 2
        self.s.Important("Transfer 100MB of data from hard drive to DDR3")
        self.dma.set_channel_sink_addr              (CHANNEL_ADDR, SINK_ADDR            )
        self.dma.set_channel_instruction_pointer    (CHANNEL_ADDR, INST_ADDR            )
        self.dma.enable_source_address_increment    (CHANNEL_ADDR, True                 )

        self.dma.enable_dest_address_increment      (SINK_ADDR,    True                 )
        #self.dma.enable_dest_respect_quantum        (SINK_ADDR,    True                 )
        self.dma.enable_dest_respect_quantum        (SINK_ADDR,    False                )

        self.dma.set_instruction_source_address     (INST_ADDR,    SATA_ADDRESS         )
        self.dma.set_instruction_dest_address       (INST_ADDR,    SATA_ADDRESS         )
        self.dma.set_instruction_data_count         (INST_ADDR,    WORD_TRANSFER_COUNT  )
        #This is only needed if we are going to another instruction after this
        self.dma.set_instruction_next_instruction   (INST_ADDR,    INST_ADDR            )
        self.dma.enable_instruction_continue        (INST_ADDR,    False                )

        #Initate DMA Transaction
        self.s.Important("Intiate a DMA Transaction")
        self.dma.enable_interrupt_when_command_finished(True)
        self.dma.enable_channel                     (CHANNEL_ADDR, True                 )

        #Transaction Complete
        self.s.Important("DMA Transaction is complete")
        #self.dma.wait_for_interrupts(wait_time = 10)
        self.s.Info ("Wait for transaction to finish (Timeout: %d)" % TIMEOUT)
        timeout = time.time() + TIMEOUT
        fail = False
        while not self.dma.is_channel_finished(CHANNEL_ADDR):
            print ".",
            if time.time() > timeout:
                print ""
                self.s.Error("Timeout Occured!")
                fail = True
                break

        if fail:
            self.fail_analysis(CHANNEL_ADDR, SINK_ADDR, INST_ADDR)
            return

        self.s.Info ("Transaction Finished!")


        #Transaction Complete
        self.s.Important("DMA Transaction is complete")

        #Verify values of memory are correct
        self.s.Important("Verify values of DDR3 are correct")
        data = self.n.read_memory(0x00, 128)
        self.s.Verbose("Data read from memory after clear (Should be all incrementing number pattern):")
        print str(data[0:128])
        #self.verify_memory_pattern()

        self.s.Verbose("Put Hard Drive to Sleep")
        self.sata_drv.hard_drive_sleep()

    def fail_analysis(self, channel, sink, instruction_addr):
        status          = self.dma.get_channel_status(channel)
        source_ready    = ((status & 0x200) >> 9)
        source_activate = ((status & 0x100) >> 8)
        sink_ready      = ((status & 0xC0) >> 6)
        sink_activate   = ((status & 0x30) >> 4)

        if channel == 0:
            self.s.Warning("Hard Drive -> DDR3")
            if ((source_ready == 0) and (source_activate == 0)):
                self.s.Error("*** HARD DRIVE STALL! ****")
            elif ((sink_ready == 0) and (sink_activate == 0)):
                self.s.Error("***DMA STALL! *****")

        elif channel == 2:
            self.s.Warning("DDR3 -> Hard Drive")
            if ((source_ready == 0) and (source_activate == 0)):
                self.s.Error("***DMA STALL! *****")
            elif ((sink_ready == 0) and (sink_activate == 0)):
                self.s.Error("*** HARD DRIVE STALL! ****")



        print "Channel Status: 0x%08X" % status
        print "\tDMA Enabled:           %s" % str(((status & 0x01) > 0))
        print "\tBusy:                  %s" % str(((status & 0x02) > 0))
        print "\tFinished:              %s" % str(((status & 0x04) > 0))
        print "\tSink Error Conflict:   %s" % str(((status & 0x08) > 0))
        print "\tSink Activate:         0x%02X" % sink_activate
        print "\tSink Ready:            0x%02X" % sink_ready
        print "\tSource Activate:       0x%02X" % source_activate
        print "\tSource Ready:          0x%02X" % source_ready
        print""
        print "\tDMA Request Ingress Address:       0x%08X" % self.dma.get_channel_sink_addr(channel)
        print "\tSATA Current Address:              0x%08X" % self.sata_drv.get_hard_drive_lba()
        print "\tDMA Request Egress Address:        0x%08X" % self.dma.get_instruction_dest_address(instruction_addr)
        print ""
        print "\tSATA Command Layer Write State: %d" % self.sata_drv.get_cmd_wr_state()
        print "\tSATA Transport State: %d" % self.sata_drv.get_transport_state()
        print "\tSATA Link Layer State: %d" % self.sata_drv.get_link_layer_write_state()
        print ""
        print "\tSATA Status: 0x%08X" % self.sata_drv.get_d2h_status()
        print "\tDMA Channel State:     %s" % self.dma.get_debug_channel_state(channel)


    def fill_memory_with_pattern(self):
        position = 0
        #self.clear_memory()
        total_size = self.n.get_device_size(self.memory_urn)

        size = 0
        if total_size > MAX_LONG_SIZE:
            self.s.Verbose("Memory Size: 0x%08X is larger than write size" % total_size)
            self.s.Verbose("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        #Write Data Out
        data_out = Array('B')
        for i in range (0, size):
            data_out.append((i % 0x100))


        while position < total_size:
            self.n.write_memory(position, data_out)

            #Increment the position
            prev_pos = position

            if position + size > total_size:
                size = total_size - position
            position += size
            self.s.Verbose("Wrote: 0x%08X - 0x%08X" % (prev_pos, position))

    def verify_memory_pattern(self):
        #Read
        status = "Passed"
        fail = False
        fail_count = 0
        total_size = self.n.get_device_size(self.memory_urn)
        position = 0
        size = 0

        data_out = Array('B')
        for i in range (0, size):
            data_out.append((i % 0x100))

        if total_size > MAX_LONG_SIZE:
            self.s.Verbose("Memory Size: 0x%08X is larger than write size" % total_size)
            self.s.Verbose("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        while (position < total_size) and fail_count < 257:

            data_in = self.n.read_memory(position, size / 4)
            if size != len(data_in):
                self.s.Error("Data in length not equal to data_out length")
                self.s.Error("\toutgoing: %d" % size)
                self.s.Error("\tincomming: %d" % len(data_in))

            dout = data_out.tolist()
            din = data_in.tolist()

            for i in range(len(data_out)):
                out_val = dout[i]
                in_val = din[i]
                if out_val != in_val:
                    fail = True
                    status = "Failed"
                    self.s.Error("Mismatch @ 0x%08X: Write: (Hex): 0x%08X Read (Hex): 0x%08X" % (position + i, data_out[i], data_in[i]))
                    if fail_count >= 16:
                        break
                    fail_count += 1

            prev_pos = position
            if (position + size) > total_size:
                size = total_size - position
            position += size

            self.s.Verbose("Read: 0x%08X - 0x%08X" % (prev_pos, position))

        return status

    def clear_memory(self):
        total_size = self.n.get_device_size(self.memory_urn)
        position = 0
        size = 0
        self.s.Verbose("Clearing Memory")
        self.s.Verbose("Memory Size: 0x%08X" % size)

        if total_size > MAX_LONG_SIZE:
            self.s.Verbose("Memory Size: 0x%08X is larger than read/write size" % total_size)
            self.s.Verbose("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        while position < total_size:
            data_out = Array('B')
            for i in range(0, ((size / 4) - 1)):
                num = 0x00
                data_out.append(num)

            self.n.write_memory(position, data_out)

            #Increment the position
            prev_pos = position

            if position + size > total_size:
                size = total_size - position
            position += size

            self.s.Verbose ("Cleared: 0x%08X - 0x%08X" % (prev_pos, position))





if __name__ == "__main__":
    unittest.main()

