#!/usr/bin/python

import unittest
import json
import sys
import os
import collections
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.host.driver import logic_analyzer

class Test (unittest.TestCase):
    """Unit test SDB Tree"""

    def setUp(self):
        pass

    def test_generate_vcd_waveform(self):
        data = Array('L')
        SIZE = 1024
        CLOCK_COUNT = 62500000
        home = os.path.expanduser("~")
        FILENAME = os.path.join(home, "sandbox", "temp.vcd")
        for i in range(SIZE):
            data.append(i)

        buf = logic_analyzer.create_vcd_buffer(data, clock_count = CLOCK_COUNT, debug = True)
        f = open(FILENAME, "w")
        f.write(buf)
        f.close()


if __name__ == "__main__":
    unittest.main()


