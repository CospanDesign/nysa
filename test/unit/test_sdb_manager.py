#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.cbuilder.sdb_manager import SDBManager
from nysa.common.status import StatusLevel
from nysa.common.status import Status


class Test (unittest.TestCase):
    """Unit test for arbiter"""

    def setUp(self):
        self.dbg = False
        self.status = Status()
        self.status.set_level(StatusLevel.VERBOSE)
        self.sdb_manager = SDBManager(self.status)
        lines = rom_buffer.splitlines()
        buf = ""
        for n in lines:
            buf += n
        self.buf = Array('B')
        for i in range(0, len(buf), 2):
            self.buf.append(int(buf[i:i + 2], 16))

    def test_parse_top_interconnect(self):
        self.sdb_manager.parse_top_interconnect_buffer(self.buf[0:64])

    def get_number_of_devices_from_top_interconnect(self):
        self.sdb_manager.parse_top_interconnect_buffer(self.buf[0:64])
        num_devices = self.sdb_manager.get_number_of_devices()
        self.assertEqual(num_devices, 3)
        

rom_buffer =   \
        "5344422D" \
        "00030100" \
        "00000000" \
        "00000000" \
        "00000002" \
        "00000000" \
        "80000000" \
        "0000C594" \
        "01000001" \
        "00000001" \
        "140F0105" \
        "6E797361" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000207" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000050" \
        "80000000" \
        "0000C594" \
        "01000001" \
        "00000001" \
        "140F0105" \
        "53444200" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000001" \
        "00000101" \
        "00000207" \
        "00000000" \
        "01000000" \
        "00000000" \
        "01000008" \
        "80000000" \
        "0000C594" \
        "00000000" \
        "00000001" \
        "140F0107" \
        "77625F67" \
        "70696F00" \
        "00000000" \
        "00000000" \
        "00000001" \
        "00000502" \
        "00000207" \
        "00000001" \
        "00000000" \
        "00000001" \
        "00800000" \
        "80000000" \
        "0000C594" \
        "00000000" \
        "00000001" \
        "140F0107" \
        "77625F73" \
        "6472616D" \
        "00000000" \
        "00000000" \
        "00000001" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000" \
        "00000000"

