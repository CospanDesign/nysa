#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))



from nysa.ibuilder.lib import xilinx_utils
from nysa.ibuilder.lib.ibuilder_error import XilinxToolchainError

class Test (unittest.TestCase):
    """Unit test for saputils"""

    def setUp(self):
        self.dbg = True
        pass
    ''' 
    def test_get_version_list(self):
        """
        returns a list of the version on this computer
        """
        #get a list of the version on this computer
        self.dbg = True
        versions = xilinx_utils.get_version_list(base_directory = None, 
                            debug = self.dbg)
        if self.dbg: print "List: %s" % str(versions)
        self.dbg = False
        self.assertIsNotNone(versions)  
    '''
 
 
    def test_locate_xilinx_default(self, debug = False):
        """
        Locats the Xilinx Base directory
        """
        base = xilinx_utils.find_xilinx_path()

        self.dbg = True
        if self.dbg: print "Base: %s" % base
        self.dbg = False
        self.assertIsNotNone(base)


if __name__ == "__main__":
      sys.path.append (sys.path[0] + "/../")
      unittest.main()
