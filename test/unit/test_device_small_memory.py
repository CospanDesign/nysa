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

from nysa.host.driver.memory import Memory
from nysa.common.status import Status

from nysa.host.platform_scanner import PlatformScanner

MAX_LONG_SIZE = 0x0800000

class Test (unittest.TestCase):

    def setUp(self):
        self.s = Status()
        self.s.set_level("fatal")
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
                    if n.is_device_in_platform(Memory):
                        plat = [platform_name, name, n]
                        break
                    continue

                #self.s.Verbose("\t%s" % psi)

        if plat[1] is None:
            self.camera = None
            return
        self.n = plat[2]
        self.urn = self.n.find_device(Memory)[0]
        self.s.set_level("verbose")
        self.s.Important("Using Platform: %s" % plat[0])
        self.s.Important("Instantiated a Memory Device: %s" % self.urn)
        self.memory = Memory(self.n, self.urn)

    def _test_small_memory_rw_at_beginning(self):
        if self.single_rw_start() == "Failed":
            print "Failed memory write and read at beginning"

    def _test_small_memory_rw_at_end(self):
        if self.single_rw_end() == "Failed":
            print "Failed memory write and read at end"

    def single_rw_start(self):
        status = "Passed"
        #self.clear_memory()
        size = self.n.get_device_size(self.urn)
        print "size: 0x%08X" % size
        print ( "Test Single Read/Write at Beginning")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory(0, data_out)
        print "Wrote second part!"
        data_in = self.n.read_memory(0, len(data_out)/4)
        print "length: data_out: %d, data_in: %d" % (len(data_out), len(data_in))
        print "data out: %s" % str(data_out)
        print "data_in: %s" % str(data_in)
        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                status = "Failed"
                print "Error at: 0x%02X OUT: 0x%02X IN: 0x%02X" % (i, data_out[i], data_in[i])
                #print "ERROR at: [{0:>2}] OUT: {1:>8} IN: {2:>8}".format(str(i), hex(data_out[i]), hex(data_in[i]))
        return status

    def single_rw_end(self):
        status = "Passed"
        #self.clear_memory()
        size = self.n.get_device_size(self.urn)
        print ( "Test Single Read/Write at End")
        data_out = Array('B', [0xAA, 0xBB, 0xCC, 0xDD, 0x55, 0x66, 0x77, 0x88])
        self.n.write_memory((size - 16), data_out)
        print "Reading from location: 0x%08X" % (size - 16)
        data_in = self.n.read_memory((size - 16), 2)
        print "data out: %s" % str(data_out)
        print "data_in: %s" % str(data_in)

        for i in range (len(data_out)):
            if data_in[i] != data_out[i]:
                print "Error at: 0x%02X OUT: 0x%02X IN: 0x%02X" % (i, data_out[i], data_in[i])
                status = "Failed"

        return status

    def test_long_burst(self):
        status = "Passed"
        fail = False
        fail_count = 0
        position = 0
        #self.clear_memory()
        total_size = self.n.get_device_size(self.urn)

        size = 0
        if total_size > MAX_LONG_SIZE:
            print("Memory Size: 0x%08X is larger than read/write size" % total_size)
            print("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
            size = MAX_LONG_SIZE
        else:
            size = total_size

        #Write Data Out
        while position < total_size:
            data_out = Array('B')

            data_out = Array('B')
            for i in range (0, size):
                data_out.append((i % 0x100))

            self.n.write_memory(position, data_out)

            #Increment the position
            prev_pos = position

            if position + size > total_size:
                size = total_size - position
            position += size
            print("Wrote: 0x%08X - 0x%08X" % (prev_pos, position))


        position = 0
        size = total_size

        if total_size > MAX_LONG_SIZE:
            print("Memory Size: 0x%08X is larger than read/write size" % total_size)
            print("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)

            size = MAX_LONG_SIZE
 
        while (position < total_size) and fail_count < 257:

            data_in = self.n.read_memory(position, size / 4)
            if size != len(data_in):
                print( "Data in length not equal to data_out length")
                print( "\toutgoing: %d" % size)
                print( "\tincomming: %d" % len(data_in))

            dout = data_out.tolist()
            din = data_in.tolist()

            for i in range(len(data_out)):
                out_val = dout[i]
                in_val = din[i]
                if out_val != in_val:
                    fail = True
                    status = "Failed"
                    print("Mismatch @ 0x%08X: Write: (Hex): 0x%08X Read (Hex): 0x%08X" % (position + i, data_out[i], data_in[i]))
                    if fail_count >= 16:
                        break
                    fail_count += 1

            prev_pos = position
            if (position + size) > total_size:
                size = total_size - position
            position += size

            print("Read: 0x%08X - 0x%08X" % (prev_pos, position))

        return status



    def clear_memory(self):
        total_size = self.n.get_device_size(self.urn)
        position = 0
        size = 0
        print ( "Clearing Memory")
        print ( "Memory Size: 0x%08X" % size)

        if total_size > MAX_LONG_SIZE:
            print("Memory Size: 0x%08X is larger than read/write size" % total_size)
            print("\tBreaking transaction into 0x%08X chunks" % MAX_LONG_SIZE)
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

            print ("Cleared: 0x%08X - 0x%08X" % (prev_pos, position))



