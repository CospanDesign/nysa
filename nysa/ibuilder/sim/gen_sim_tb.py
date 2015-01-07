import sys
import os
import string
import copy
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import sim_utils as sutils

import gen_sim_top

from gen import Gen

class GenSimTop(Gen):

    def __init__(self):
        return

    def get_name (self):
        print "generate sim tb!"

    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        #Copy the interface so we don't modify the original
        gs = gen_sim_top.GenSimTop()
        buf = gs.gen_script(tags, buf, user_paths)
        return sutils.generate_tb_module(tags, buf, user_paths)
