import sys
import os
from gen import Gen
import string
from string import Template

from nysa.ibuilder import utils

class GenInterconnect(Gen):

  def __init__(self):
    #print "in GenInterconnect"
    return

  def gen_script (self, tags = {}, buf = "", user_paths = [], debug=False):
    num_slaves = len(tags["SLAVES"].keys())
    buf = generate_wb_interconnect(num_slaves = num_slaves)
    return buf

  def get_name (self):
    print "wishbone_interconnect.py"



def generate_wb_interconnect(num_slaves = 1, add_sdb = True, debug=False):
  if debug: print "Generating wishbone slave interconnect"

  buf = ""

  #Allow errors to pass up to the calling class
  directory = utils.get_local_verilog_path("nysa-verilog")
  wb_i_loc = os.path.join(  directory, 
                            "verilog", 
                            "wishbone", 
                            "interconnect",
                            "wishbone_interconnect.v")


  f = open(wb_i_loc, "r")
  buf = f.read()
  f.close()

  #print "Buffer: %s" % buf

  template = Template(buf)
  port_buf = ""
  assign_buf = ""
  data_block_buf = ""
  ack_block_buf = ""
  int_block_buf = ""
  address_param_buf = ""


  if add_sdb:
    num_slaves += 1


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

  #addresss
  for i in range(0, num_slaves):
    address_param_buf += "parameter ADDR_%d = %d;\n"  % (i, i)
  
  #assign defines
  for i in range (0, num_slaves):
    assign_buf +="assign o_s%d_we   =\t(slave_select == ADDR_%d) ? i_m_we: 1\'b0;\n"  % (i, i)
    assign_buf +="assign o_s%d_stb  =\t(slave_select == ADDR_%d) ? i_m_stb: 1\'b0;\n" % (i, i)
    assign_buf +="assign o_s%d_sel  =\t(slave_select == ADDR_%d) ? i_m_sel: 4\'h0;\n" % (i, i)
    assign_buf +="assign o_s%d_cyc  =\t(slave_select == ADDR_%d) ? i_m_cyc: 1\'b0;\n" % (i, i)
    assign_buf +="assign o_s%d_adr  =\t(slave_select == ADDR_%d) ? {8\'h0, i_m_adr[23:0]}: 32\'h0;\n"  % (i, i)
    assign_buf +="assign o_s%d_dat  =\t(slave_select == ADDR_%d) ? i_m_dat: 32\'h0;\n" % (i, i)
    assign_buf +="\n"

  #data in block
  data_block_buf = "//data in from slave\n" 
  data_block_buf += "always @ (slave_select"
  for i in range (0, num_slaves):
    data_block_buf += " or i_s%d_dat" % i

  data_block_buf += " or interrupts) begin\n\tcase (slave_select)\n"
  for i in range (0, num_slaves):
    data_block_buf += "\t\tADDR_%d: begin\n\t\t\to_m_dat <= i_s%d_dat;\n\t\tend\n" % (i, i)
  data_block_buf += "\t\tdefault: begin\n\t\t\to_m_dat <= interrupts;\n\t\tend\n\tendcase\nend\n\n"

  #ack in block
  ack_block_buf =  "//ack in from slave\n\n" 
  ack_block_buf += "always @ (slave_select"
  for i in range (0, num_slaves):
    ack_block_buf += " or i_s%d_ack" % (i)
  ack_block_buf += ") begin\n\tcase (slave_select)\n"
  for i in range (0, num_slaves):
    ack_block_buf += "\t\tADDR_%d: begin\n\t\t\to_m_ack <= i_s%d_ack;\n\t\tend\n" % (i, i)
  ack_block_buf += "\t\tdefault: begin\n\t\t\to_m_ack <= 1\'h0;\n\t\tend\n\tendcase\nend\n\n"

  #int in block
  int_block_buf = "//int in from slave\n" 
  int_num_slaves = num_slaves

#X: right now were only handling 32 interrupts
  if (int_num_slaves > 32):
    int_num_slaves = 32
  for i in range (0, int_num_slaves):
    int_block_buf += "assign interrupts[%d]\t\t=\ti_s%d_int;\n" % (i, i)

  if (num_slaves < 31):
    int_block_buf += "assign interrupts[31:" + str(num_slaves) + "]\t\t=\t0;\n\n"
 
  buf = template.substitute(  PORTS=port_buf, 
                ASSIGN=assign_buf, 
                DATA=data_block_buf, 
                ACK=ack_block_buf, 
                INT=int_block_buf, 
                ADDRESSES=address_param_buf)
  buf = string.expandtabs(buf, 2)

  return buf


