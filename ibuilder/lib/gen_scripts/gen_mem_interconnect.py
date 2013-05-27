import gen
import os
import sys
from string import Template
from gen import Gen

sys.path.append(os.path.join(os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "cbuilder",
                "scripts"))

import wishbone_mem_interconnect_cbuilder as wic

class GenMemInterconnect(Gen):


  def __init__(self):
    #print "in GenInterconnect"
    return

  def gen_script (self, tags = {}, buf = "", debug=False):
    buf = wic.generate_wb_mem_interconnect(tags = tags, debug = debug)
    return buf

  def get_name (self):
    print "wishbone_mem_interconnect.py"
