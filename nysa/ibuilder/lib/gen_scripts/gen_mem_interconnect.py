import gen
import os
import sys
import string
from string import Template
from gen import Gen

from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import verilog_utils as vutils

class GenMemInterconnect(Gen):

  def __init__(self):
    return

  def gen_script (self, tags = {}, buf = "", user_paths = [], debug=False):
    buf = generate_wb_mem_interconnect(tags = tags, user_paths = user_paths, debug = debug)
    return buf

  def get_name (self):
    print "wishbone_mem_interconnect.py"



def generate_wb_mem_interconnect(tags = {}, user_paths = [], debug = False):

  if "MEMORY" not in tags:
    return ""

  num_slaves = len(tags["MEMORY"].keys())
  if debug: print "Number of slaves: %d" % num_slaves


  buf = ""

  #Allow errors to pass up to the calling class
  directory = utils.get_local_verilog_path("nysa-verilog")
  wb_i_loc = os.path.join(  directory,
                            "verilog",
                            "wishbone",
                            "interconnect",
                            "wishbone_mem_interconnect.v")

  f = open(wb_i_loc, "r")
  buf = f.read()
  f.close()

  template = Template(buf)

  port_buf = ""
  port_def_buf = ""
  mem_select_buf = ""
  assign_buf = ""
  data_block_buf = ""
  ack_block_buf = ""
  int_block_buf = ""
  param_buf = ""

  #start with 1 to account for SDB
  num_mems = 0
  if (tags.has_key("MEMORY")):
    #got a list of all the slaves to add to make room for
    mem_list = tags["MEMORY"]
    num_mems = num_mems + len(mem_list)

  if num_mems == 0:
    return ""

  if debug:
    "Memory Keys\n\n"
    for key in tags["MEMORY"]:
      print key + ":" + str(tags["MEMORY"][key])
      print "\n\n"

  slave_keywords = [
      "SDB_ABI_VERSION_MAJOR",
      "SDB_ABI_VERSION_MINOR",
      "SDB_SIZE"
  ]

  mem_offset = 0
  #generate the parameters
  for i in range(0, num_mems):
    key = tags["MEMORY"].keys()[i]
    absfilename = utils.find_rtl_file_location(tags["MEMORY"][key]["filename"], user_paths)
    #print "filename: %s" % absfilename
    slave_tags = vutils.get_module_tags(filename = absfilename, bus = "wishbone", keywords = slave_keywords)
    if debug:
        print "slave tags: " + str(slave_tags)

    mem_size = int(slave_tags["keywords"]["SDB_SIZE"].strip(), 0)

    param_buf = param_buf + "parameter MEM_SEL_%d\t=\t%d;\n" % (i, i)
    param_buf = param_buf + "parameter MEM_OFFSET_%d\t=\t %d;\n" % (i, mem_offset)
    param_buf = param_buf + "parameter MEM_SIZE_%d\t=\t 32'h%02X;\n" % (i, mem_size)
    mem_offset += mem_size

  #generate the memory select logic
  mem_select_buf =  "reg [31:0] mem_select;\n"

  mem_select_buf += "\n"
  mem_select_buf += "always @(rst or i_m_adr or mem_select) begin\n"
  mem_select_buf += "\tif (rst) begin\n"
  mem_select_buf += "\t\t//nothing selected\n"
  mem_select_buf += "\t\tmem_select <= 32'hFFFFFFFF;\n"
  mem_select_buf += "\tend\n"
  mem_select_buf += "\telse begin\n"
  for i in range (num_mems):
    if (i == 0):
      mem_select_buf += "\t\tif "
    else:
      mem_select_buf += "\t\telse if "

    mem_select_buf += "((i_m_adr >= MEM_OFFSET_%d) && (i_m_adr < (MEM_OFFSET_%d + MEM_SIZE_%d))) begin\n" % (i, i, i)
    mem_select_buf += "\t\t\tmem_select <= MEM_SEL_%d;\n" % i
    mem_select_buf += "\t\tend\n"

  mem_select_buf += "\t\telse begin\n"
  mem_select_buf += "\t\t\tmem_select <= 32'hFFFFFFFF;\n"
  mem_select_buf += "\t\tend\n"
  mem_select_buf += "\tend\n"
  mem_select_buf += "end\n"

  #Ports
  for i in range (0, num_slaves):
    port_buf += "\t//Slave %d\n" % i
    port_buf += "\toutput\t\t\t\t\t\t\to_s%d_we,\n" % i
    port_buf += "\toutput\t\t\t\t\t\t\to_s%d_cyc,\n" % i
    port_buf += "\toutput\t\t\t\t\t\t\to_s%d_stb,\n" % i
    port_buf += "\toutput\t\t[3:0]\t\t\to_s%d_sel,\n" % i
    port_buf += "\tinput\t\t\t\t\t\t\t\ti_s%d_ack,\n" % i
    port_buf += "\toutput\t\t[31:0]\t\to_s%d_dat,\n" % i
    port_buf += "\tinput\t\t\t[31:0]\t\ti_s%d_dat,\n" % i
    port_buf += "\toutput\t\t[31:0]\t\to_s%d_adr,\n" % i
    port_buf += "\tinput\t\t\t\t\t\t\t\ti_s%d_int" % i

    #if this isn't the last slave add a comma
    if (i < num_slaves - 1):
      port_buf += ",\n"

    port_buf += "\n"

  #assign defines
  for i in range (0, num_mems):
    assign_buf += "assign o_s%d_we   =\t(mem_select == MEM_SEL_%d) ? i_m_we: 1'b0;\n" % (i, i)
    assign_buf += "assign o_s%d_stb  =\t(mem_select == MEM_SEL_%d) ? i_m_stb: 1'b0;\n" % (i, i)
    assign_buf += "assign o_s%d_sel  =\t(mem_select == MEM_SEL_%d) ? i_m_sel: 4'b0;\n" % (i, i)
    assign_buf += "assign o_s%d_cyc  =\t(mem_select == MEM_SEL_%d) ? i_m_cyc: 1'b0;\n" % (i, i)
    assign_buf += "assign o_s%d_adr  =\t(mem_select == MEM_SEL_%d) ? i_m_adr: 32'h0;\n" % (i, i)
    assign_buf += "assign o_s%d_dat  =\t(mem_select == MEM_SEL_%d) ? i_m_dat: 32'h0;\n" % (i, i)
    assign_buf +="\n"

  #data in block
  data_block_buf = "//data in from slave\n"
  data_block_buf += "always @ (mem_select"
  for i in range (0, num_mems):
    data_block_buf += " or i_s%d_dat" % i

  data_block_buf += ") begin\n\tcase (mem_select)\n"
  for i in range (0, num_mems):
    data_block_buf += "\t\tMEM_SEL_%d: begin\n\t\t\to_m_dat <= i_s%d_dat;\n\t\tend\n" % (i, i)
  data_block_buf += "\t\tdefault: begin\n\t\t\to_m_dat <= 32\'h0000;\n\t\tend\n\tendcase\nend\n\n"

  #ack in block
  ack_block_buf = "//ack in from mem slave\n"
  ack_block_buf += "always @ (mem_select"
  for i in range (0, num_mems):
    ack_block_buf += " or i_s%d_ack" % i
  ack_block_buf += ") begin\n\tcase (mem_select)\n"
  for i in range (0, num_mems):
    ack_block_buf += "\t\tMEM_SEL_%d: begin\n\t\t\to_m_ack <= i_s%d_ack;\n\t\tend\n" % (i, i)
  ack_block_buf += "\t\tdefault: begin\n\t\t\to_m_ack <= 1\'h0;\n\t\tend\n\tendcase\nend\n\n"

  #int in block
  int_block_buf = "//int in from slave\n"
  int_block_buf += "always @ (mem_select"
  for i in range (0, num_mems):
    int_block_buf += " or i_s%d_int" % (i)
  int_block_buf += ") begin\n\tcase (mem_select)\n"
  for i in range (0, num_mems):
    int_block_buf += "\t\tMEM_SEL_%d: begin\n\t\t\to_m_int <= i_s%d_int;\n\t\tend\n" % (i, i)
  int_block_buf += "\t\tdefault: begin\n\t\t\to_m_int <= 1\'h0;\n\t\tend\n\tendcase\nend\n\n"

  buf = template.substitute(  PORTS=port_buf,
                MEM_SELECT=mem_select_buf,
                ASSIGN=assign_buf,
                DATA=data_block_buf,
                ACK=ack_block_buf,
                INT=int_block_buf,
                MEM_PARAMS=param_buf)
  buf = string.expandtabs(buf, 2)

  return buf


