from gen import Gen

import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import arbiter
from wishbone_utils import WishboneTopGenerator

class GenTop(Gen):
    """Generate the top module for a project"""

    def __init__(self):
        return

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        """Generate the Top Module"""
        wtg = WishboneTopGenerator()
        buf = wtg.generate_simple_top(tags, user_paths, debug)
        return buf

    def get_name (self):
        print "generate top!"


