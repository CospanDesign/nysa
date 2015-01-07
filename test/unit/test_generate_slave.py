#!/usr/bin/python

import unittest
import json
import sys
import os
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.tools import generate_slave
from nysa.common.status import Status

#Mock object
class MOCK_ARGS(object):
    
    def __init__(self):
        self.name = "test_name"
        self.major = "0"
        self.minor = "0"
        self.output = ""
        self.debug = False
        self.axi = False

class Test (unittest.TestCase):
    """Unit test for arbiter"""

    def setUp(self):
        self.status = Status()

    def test_generate_peripheral_slave(self):
        args = MOCK_ARGS()
        args.name = "test_core"
        args.major = "1"
        args.minor = "0"
        args.output = os.path.join(os.path.expanduser("~"),
                                   "sandbox")
        args.debug = True
        
        #args.output = tempfile.mkdtemp()
        generate_slave.generate_slave(args, self.status)

        #Clean up the generated files
        #shutil.rmtree(tempdir)


