import sys
import os
from gen import Gen

sys.path.append(os.path.join(os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "cbuilder",
                "scripts"))

import wishbone_interconnect_cbuilder as wic

class GenInterconnect(Gen):


  def __init__(self):
    #print "in GenInterconnect"
    return

  def gen_script (self, tags = {}, buf = "", user_paths = [], debug=False):
    num_slaves = len(tags["SLAVES"].keys())
    buf = wic.generate_wb_interconnect(num_slaves = num_slaves)
    return buf

  def get_name (self):
    print "wishbone_interconnect.py"
