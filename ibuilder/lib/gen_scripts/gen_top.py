from gen import Gen

import sys
import os
import string
from string import Template

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import utils
import arbitor

class GenTop(Gen):
    """Generate the top module for a project"""

    def __init__(self):
        #print "in GenTop"
        self.wires=[]
        self.tags = {}
        return

    def add_ports_to_wires(self):
        """add all the ports to wires list so that no item adds wires"""
        for name in self.bindings.keys():
            self.wires.append(self.bindings[name]["loc"])


    def generate_ports(self):
        """create the ports string"""
        port_buf = "module top (\n"
        blist = self.bindings.keys()
        for i in range(len(blist)):
            name = blist[i]
            #print "name: %s" % name
            #for key in self.bindings[name].keys():
            #    print "\t%s" % str(key)

            port_name = self.bindings[name]["loc"]
            eol = ""
            if i < len(blist) - 1:
                eol = ","
            if "[" in port_name and ":" in port_name:
                #port_name = "[" + port_name.partition("[")[2] + "\t" + port_name.partition("[")[0]
                port_name = "[{0:<9}{1}".format(port_name.partition("[")[2], port_name.partition("[")[0])
            else:
                port_name = "{0:<10}{1}".format("", port_name)

            port_buf += "\t{0:10}\t{1}{2}\n".format(self.bindings[name]["direction"], port_name, eol)

        port_buf += ");"
        return string.expandtabs(port_buf, 2)


    def gen_script (self, tags = {}, buf = "", user_paths = [], debug = False):
        """Generate the Top Module"""
        #debug = True
        #if debug: print "Tags: %s" % str(tags)
        self.user_paths = user_paths
        board_dict = utils.get_board_config(tags["board"])
        #if debug: print "Board Dictionary: %s" % str(board_dict)
        invert_reset = board_dict["invert_reset"]
        en_mem_bus = False
        slave_list = tags["SLAVES"]
        self.internal_bindings = {}
        self.bindings = {}
        if "MEMORY" in tags:
            if (len(tags["MEMORY"]) > 0):
                if debug: print "found %d memory devices" % len[tags["MEMORY"]]
                en_mem_bus = True

        num_slaves = len(slave_list) + 1
        self.tags = tags

        #add the internal bindings
        self.internal_bindings = {}
        if "internal_bind" in self.tags.keys():
            self.internal_bindings = self.tags["internal_bind"]
            #print "Internal bindings: %s" % str(self.internal_bindings)

        #add the global tags
        self.bindings = self.tags["bind"]
        #add the interface bindings directly
        if "bind" in self.tags["INTERFACE"]:
            for if_name in self.tags["INTERFACE"]["bind"]:
                self.bindings[if_name] = self.tags["INTERFACE"]["bind"][if_name]

        #add each of the slave items to the binding
          #insert the names
        for slave_name in self.tags["SLAVES"]:
            if "bind" in self.tags["SLAVES"][slave_name]:
                for bind_name in self.tags["SLAVES"][slave_name]["bind"]:
                    bname = "%s_%s" % (slave_name, bind_name)
                    self.bindings[bname] = self.tags["SLAVES"][slave_name]["bind"][bind_name]

        if "MEMORY" in self.tags:
            #add the slave bindings to the list
            for mem_name in self.tags["MEMORY"]:
                if "bind" in self.tags["MEMORY"][mem_name]:
                    for bind_name in self.tags["MEMORY"][mem_name]["bind"]:
                        bname = "%s_%s" % (mem_name, bind_name)
                        self.bindings[bname] = self.tags["MEMORY"][mem_name]["bind"][bind_name]

        if debug:
            print "found " + str(len(slave_list)) + " slaves"
            for slave in slave_list:
                print slave

        #remove all the ports from the possible wires
        self.add_ports_to_wires()

        template = Template(buf)

        #header = ""
        port_buf = self.generate_ports()
        arb_buf = self.generate_arbitor_buffer()
        wr_buf = ""
        wi_buf = ""
        wmi_buf = ""
        wm_buf = ""
        footer = ""

        footer = "endmodule"
        #declare the ports
        #XXX: in the future utilize the constraints to generate the connections

        #declare the wires
        wr_buf +=  "//input handler signals\n"
        #wr_buf +=  "{0:<20}{1};\n".format("wire","clk")
        self.wires.append("clk")
        #wr_buf +=  "{0:<20}{1};\n".format("wire","rst")
        self.wires.append("rst")
        if invert_reset:
            #print "found invert reset!"
            wr_buf +=  "{0:<20}{1};\n".format("wire","rst_n")
            self.wires.append("rst_n")

        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_in_command")
        self.wires.append("w_in_command")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_in_address");
        self.wires.append("w_in_address")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_in_data");
        self.wires.append("w_in_data")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_in_data_count");
        self.wires.append("w_in_data_count")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_ih_ready")
        self.wires.append("w_ih_ready")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_ih_reset")
        self.wires.append("w_ih_reset")
        wr_buf += "\n"

        wr_buf +=  "//output handler signals\n"
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_out_status")
        self.wires.append("w_out_status")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_out_address")
        self.wires.append("w_out_address")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_out_data")
        self.wires.append("w_out_data")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[27:0]","w_out_data_count")
        self.wires.append("w_out_data_count")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_oh_ready")
        self.wires.append("w_oh_ready")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_oh_en")
        wr_buf += "\n"

        wr_buf +=  "//master signals\n"
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_master_ready")
        self.wires.append("w_master_ready")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_wbm_we_o")
        self.wires.append("w_wbm_we_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_wbm_cyc_o")
        self.wires.append("w_wbm_cyc_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_wbm_stb_o")
        self.wires.append("w_wbm_stb_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[3:0]","w_wbm_sel_o")
        self.wires.append("w_wbm_sel_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_wbm_adr_o")
        self.wires.append("w_wbm_adr_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_wbm_dat_i")
        self.wires.append("w_wbm_dat_i")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_wbm_dat_o")
        self.wires.append("w_wbm_dat_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_wbm_ack_i")
        self.wires.append("w_wbm_ack_i")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_wbm_int_i")
        self.wires.append("w_wbm_int_i")

        wr_buf +=  "{0:<20}{1};\n".format("wire","w_mem_we_o")
        self.wires.append("w_mem_we_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_mem_cyc_o")
        self.wires.append("w_mem_cyc_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_mem_stb_o")
        self.wires.append("w_mem_stb_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[3:0]","w_mem_sel_o")
        self.wires.append("w_mem_sel_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_mem_adr_o")
        self.wires.append("w_mem_adr_o")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_mem_dat_i")
        self.wires.append("w_mem_dat_i")
        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_mem_dat_o")
        self.wires.append("w_mem_dat_o")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_mem_ack_i")
        self.wires.append("w_mem_ack_i")
        wr_buf +=  "{0:<20}{1};\n".format("wire","w_mem_int_i")
        self.wires.append("w_mem_int_i")

        wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","w_wbm_debug_out")
        self.wires.append("w_wbm_debug_out");
        wr_buf +=  "\n"


        #put the in clock on the global buffer
        #wr_buf +=  "\t//add a global clock buffer to the input clock\n"
        #wr_buf +=  "\tIBUFG clk_ibuf(.I(clk_in), .O(clk));\n\n"

        wr_buf +=  "//slave signals\n\n"

        for i in range (0, num_slaves):
            wr_buf +=  "//slave " + str(i) + "\n"
            wr_name = "w_s%d_i_wbs_we" % i
            wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_i_wbs_cyc" % i
            wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_i_wbs_dat" % i
            wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_o_wbs_dat" % i
            wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_i_wbs_adr" % i
            wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_i_wbs_stb" % i
            wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_i_wbs_sel" % i
            wr_buf +=  "{0:<19}{1};\n".format("wire\t[3:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_o_wbs_ack" % i
            wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "w_s%d_o_wbs_int" % i
            wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)


        if (en_mem_bus):
            for i in range (0, len(tags["MEMORY"])):
                wr_buf +=  "//mem slave " + str(i) + "\n"
                wr_name = "w_sm%d_i_wbs_we" % i
                wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_i_wbs_cyc" % i
                wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_i_wbs_dat" % i
                wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_o_wbs_dat" % i
                wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_i_wbs_adr" % i
                wr_buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_i_wbs_stb" % i
                wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_i_wbs_sel" % i
                wr_buf +=  "{0:<19}{1};\n".format("wire\t[3:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_o_wbs_ack" % i
                wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "w_sm%d_o_wbs_int" % i
                wr_buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)


        if debug:
            print "wr_buf: \n" + wr_buf


        #generate the IO handler
        io_filename = tags["INTERFACE"]["filename"]
        if debug: print "io_filename: %s" % io_filename
        absfilepath = utils.find_rtl_file_location(io_filename, self.user_paths)
        io_tags = utils.get_module_tags(filename = absfilepath,
                                        bus = "wishbone",
                                        user_paths = self.user_paths)

#XXX: Working on a new version!!
        #io_buf = ""
        #io_buf = self.generate_buffer(name = "io", 
        #                              module_tags = io_tags, 
        #                              io_module = True)

        io_buf = self.generate_host_if_buffer(io_tags)



        #for the FPGA
          #constraints can be a dictionary with the mappings from device
          #to input/output/inout multidimensional values

        #this should just be file with text that I can pull in, it will always be
        #the same!
        #instantiate the connection interface
          #should this be another script that is clled within here?
          #can I extrapolate the required information directly from the
          #file?

        #interconnect
        wi_buf = "wishbone_interconnect wi (\n"

        wi_buf += "\t.clk\t\t\t\t\t\t(clk),\n"
        if invert_reset:
            wi_buf += "\t.rst\t\t\t\t\t\t(rst_n),\n\n"
        else:
            wi_buf += "\t.rst\t\t\t\t\t\t(rst),\n\n"

        wi_buf += "\t//master\n"
        wi_buf += "\t.i_m_we\t\t\t\t\t(w_wbm_we_o),\n"
        wi_buf += "\t.i_m_cyc\t\t\t\t(w_wbm_cyc_o),\n"
        wi_buf += "\t.i_m_stb\t\t\t\t(w_wbm_stb_o),\n"
        wi_buf += "\t.i_m_sel\t\t\t\t(w_wbm_sel_o),\n"
        wi_buf += "\t.o_m_ack\t\t\t\t(w_wbm_ack_i),\n"
        wi_buf += "\t.i_m_dat\t\t\t\t(w_wbm_dat_o),\n"
        wi_buf += "\t.o_m_dat\t\t\t\t(w_wbm_dat_i),\n"
        wi_buf += "\t.i_m_adr\t\t\t\t(w_wbm_adr_o),\n"
        wi_buf += "\t.o_m_int\t\t\t\t(w_wbm_int_i),\n\n"

        for i in range (0, num_slaves):
            wi_buf += "\t//slave %d\n" % i
            wi_buf += "\t.o_s%d_we\t\t\t\t(w_s%d_i_wbs_we),\n" % (i, i)
            wi_buf += "\t.o_s%d_cyc\t\t\t\t(w_s%d_i_wbs_cyc),\n" % (i, i)
            wi_buf += "\t.o_s%d_stb\t\t\t\t(w_s%d_i_wbs_stb),\n" % (i, i)
            wi_buf += "\t.o_s%d_sel\t\t\t\t(w_s%d_i_wbs_sel),\n" % (i, i)
            wi_buf += "\t.i_s%d_ack\t\t\t\t(w_s%d_o_wbs_ack),\n" % (i, i)
            wi_buf += "\t.o_s%d_dat\t\t\t\t(w_s%d_i_wbs_dat),\n" % (i, i)
            wi_buf += "\t.i_s%d_dat\t\t\t\t(w_s%d_o_wbs_dat),\n" % (i, i)
            wi_buf += "\t.o_s%d_adr\t\t\t\t(w_s%d_i_wbs_adr),\n" % (i, i)
            wi_buf += "\t.i_s%d_int\t\t\t\t(w_s%d_o_wbs_int)" % (i, i)


            if (i < num_slaves - 1):
                wi_buf += ",\n"

            wi_buf += "\n"

        wi_buf += ");"

        if debug:
            print "wi_buf: \n" + wi_buf



        #memory interconnect
        if en_mem_bus:
            if debug:
                print "make the membus"
            wmi_buf = "wishbone_mem_interconnect wmi (\n"

            wmi_buf += "\t.clk\t\t\t\t\t\t(clk),\n"

            if invert_reset:
                wmi_buf += "\t.rst\t\t\t\t\t\t(rst_n),\n\n"
            else:
                wmi_buf += "\t.rst\t\t\t\t\t\t(rst),\n\n"

            wmi_buf += "\t//master\n"
            wmi_buf += "\t.i_m_we\t\t\t\t\t(w_mem_we_o),\n"
            wmi_buf += "\t.i_m_cyc\t\t\t\t(w_mem_cyc_o),\n"
            wmi_buf += "\t.i_m_stb\t\t\t\t(w_mem_stb_o),\n"
            wmi_buf += "\t.i_m_sel\t\t\t\t(w_mem_sel_o),\n"
            wmi_buf += "\t.o_m_ack\t\t\t\t(w_mem_ack_i),\n"
            wmi_buf += "\t.i_m_dat\t\t\t\t(w_mem_dat_o),\n"
            wmi_buf += "\t.o_m_dat\t\t\t\t(w_mem_dat_i),\n"
            wmi_buf += "\t.i_m_adr\t\t\t\t(w_mem_adr_o),\n"
            wmi_buf += "\t.o_m_int\t\t\t\t(w_mem_int_i),\n\n"

            num_mems = len(tags["MEMORY"])

            for i in range (0, num_mems):
                wmi_buf += "\t//mem slave %d\n" % i
                wmi_buf += "\t.o_s%d_we\t\t\t\t(w_sm%d_i_wbs_we),\n" % (i, i)
                wmi_buf += "\t.o_s%d_cyc\t\t\t\t(w_sm%d_i_wbs_cyc),\n" % (i, i)
                wmi_buf += "\t.o_s%d_stb\t\t\t\t(w_sm%d_i_wbs_stb),\n" % (i, i)
                wmi_buf += "\t.o_s%d_sel\t\t\t\t(w_sm%d_i_wbs_sel),\n" % (i, i)
                wmi_buf += "\t.i_s%d_ack\t\t\t\t(w_sm%d_o_wbs_ack),\n" % (i, i)
                wmi_buf += "\t.o_s%d_dat\t\t\t\t(w_sm%d_i_wbs_dat),\n" % (i, i)
                wmi_buf += "\t.i_s%d_dat\t\t\t\t(w_sm%d_o_wbs_dat),\n" % (i, i)
                wmi_buf += "\t.o_s%d_adr\t\t\t\t(w_sm%d_i_wbs_adr),\n" % (i, i)
                wmi_buf += "\t.i_s%d_int\t\t\t\t(w_sm%d_o_wbs_int)" % (i, i)


                if ((num_mems > 0) and (i < num_mems - 1)):
                    wmi_buf += ",\n"

                wmi_buf += "\n"

            wmi_buf += ");"

            if debug:
                print "wmi_buf: \n" + wmi_buf



        #instantiate the io handler

        #instantiate the master
        wm_buf += "wishbone_master wm (\n"
        wm_buf += "\t.clk\t\t\t\t\t\t(clk),\n"

        if invert_reset:
            wm_buf += "\t.rst\t\t\t\t\t\t(rst_n),\n\n"
        else:
            wm_buf += "\t.rst\t\t\t\t\t\t(rst),\n\n"

        wm_buf += "\t//input handler signals\n"
        wm_buf += "\t.i_ready\t\t\t\t(w_ih_ready),\n"
        wm_buf += "\t.i_ih_rst\t\t\t\t(w_ih_reset),\n"
        wm_buf += "\t.i_command\t\t\t(w_in_command),\n"
        wm_buf += "\t.i_address\t\t\t(w_in_address),\n"
        wm_buf += "\t.i_data\t\t\t\t\t(w_in_data),\n"
        wm_buf += "\t.i_data_count\t\t(w_in_data_count),\n\n"

        wm_buf += "\t//output handler signals\n"
        wm_buf += "\t.i_out_ready\t\t(w_oh_ready),\n"
        wm_buf += "\t.o_en\t\t\t\t\t\t(w_oh_en),\n"
        wm_buf += "\t.o_status\t\t\t\t(w_out_status),\n"
        wm_buf += "\t.o_address\t\t\t(w_out_address),\n"
        wm_buf += "\t.o_data\t\t\t\t\t(w_out_data),\n"
        wm_buf += "\t.o_data_count\t\t(w_out_data_count),\n"
        wm_buf += "\t.o_master_ready\t(w_master_ready),\n\n"

        wm_buf += "\t//interconnect signals\n"
        wm_buf += "\t.o_per_we\t\t\t\t(w_wbm_we_o),\n"
        wm_buf += "\t.o_per_adr\t\t\t(w_wbm_adr_o),\n"
        wm_buf += "\t.o_per_dat\t\t\t(w_wbm_dat_o),\n"
        wm_buf += "\t.i_per_dat\t\t\t(w_wbm_dat_i),\n"
        wm_buf += "\t.o_per_stb\t\t\t(w_wbm_stb_o),\n"
        wm_buf += "\t.o_per_cyc\t\t\t(w_wbm_cyc_o),\n"
        wm_buf += "\t.o_per_msk\t\t\t(w_wbm_msk_o),\n"
        wm_buf += "\t.o_per_sel\t\t\t(w_wbm_sel_o),\n"
        wm_buf += "\t.i_per_ack\t\t\t(w_wbm_ack_i),\n"
        wm_buf += "\t.i_per_int\t\t\t(w_wbm_int_i),\n\n"

        wm_buf += "\t//memory interconnect signals\n"
        wm_buf += "\t.o_mem_we\t\t\t\t(w_mem_we_o),\n"
        wm_buf += "\t.o_mem_adr\t\t\t(w_mem_adr_o),\n"
        wm_buf += "\t.o_mem_dat\t\t\t(w_mem_dat_o),\n"
        wm_buf += "\t.i_mem_dat\t\t\t(w_mem_dat_i),\n"
        wm_buf += "\t.o_mem_stb\t\t\t(w_mem_stb_o),\n"
        wm_buf += "\t.o_mem_cyc\t\t\t(w_mem_cyc_o),\n"
        wm_buf += "\t.o_mem_msk\t\t\t(w_mem_msk_o),\n"
        wm_buf += "\t.o_mem_sel\t\t\t(w_mem_sel_o),\n"
        wm_buf += "\t.i_mem_ack\t\t\t(w_mem_ack_i),\n"
        wm_buf += "\t.i_mem_int\t\t\t(w_mem_int_i),\n\n"

        wm_buf += "\t.o_debug\t\t\t\t(wbm_debug_out)\n\n";
        wm_buf += ");"

        if debug:
            print "wm_buf: \n" + wm_buf

        #Arbitors


        #Slaves
        slave_index = 0
        slave_buffer_list = []
        absfilename = utils.find_rtl_file_location("device_rom_table.v", self.user_paths)
        slave_tags = utils.get_module_tags(filename = absfilename,
                                           bus="wishbone",
                                           user_paths = self.user_paths)
        slave_buf = self.generate_buffer(name="drt", index=0, module_tags = slave_tags)
        slave_buffer_list.append(slave_buf)

        for i in range (0, len(tags["SLAVES"])):
            slave_name = tags["SLAVES"].keys()[i]
            slave = tags["SLAVES"][slave_name]["filename"]
            if debug:
                print "Slave name: " + slave
            absfilename = utils.find_rtl_file_location(slave, self.user_paths)
            slave_tags = utils.get_module_tags(filename = absfilename,
                                               bus="wishbone",
                                               user_paths = self.user_paths)
            slave_buf = self.generate_buffer(name = slave_name, index = i + 1, module_tags = slave_tags)
            slave_buffer_list.append(slave_buf)


        #Memory devices
        mem_buf = ""
        mem_buffer_list = []
        if en_mem_bus:
            #need to make all the memory devices for the memory bus
            mem_index = 0
            mem_buffer_list = []
            for i in range (0, len(tags["MEMORY"])):
                mem_name = tags["MEMORY"].keys()[i]
                filename = tags["MEMORY"][mem_name]["filename"]
                if debug:
                    print "Mem device: " + mem_name + ", mem file: " + filename
                absfilename = utils.find_rtl_file_location(filename, self.user_paths)
                mem_tags = utils.get_module_tags(filename = absfilename,
                                                 bus="wishbone",
                                                 user_paths = self.user_paths)
                mem_buf = self.generate_buffer(name = mem_name, index = i, module_tags = mem_tags, mem_slave = True)
                mem_buffer_list.append(mem_buf)


        buf_bind = ""
        buf_bind += "\t//assigns\n"
        #Generate the internal bindings
        if (len(self.internal_bindings.keys()) > 0):
            buf_bind += "\t//Internal Bindings\n"
            for key in self.internal_bindings.keys():
                buf_bind += "\tassign\t{0:<20}=\t{1};\n".format(key, self.internal_bindings[key]["signal"])

        #Generate the external bindings
        if (len(self.bindings.keys()) > 0):
            buf_bind += "\t//Bindings to Ports\n"
            for key in self.bindings.keys():
                if (self.bindings[key]["direction"] == "input"):

                    buf_bind += "\tassign\t{0:<20}=\t{1};\n".format(key, self.bindings[key]["loc"])
                    #buf_bind = buf_bind + "\tassign\t" + key + "\t=\t" + self.bindings[key]["port"] + ";\n"
                elif (self.bindings[key]["direction"] == "output"):
                    #buf_bind += "\tassign\t{0:<20}=\t{1};\n".format(key, self.bindings[key]["port"])

                    buf_bind += "\tassign\t{0:<20}=\t{1};\n".format(self.bindings[key]["loc"], key)


        if invert_reset:
            buf_bind += "\tassign\t{0:<20}=\t{1};".format("rst_n", "~rst")




        #top_buffer = header + "\n\n"
        top_buffer = port_buf + "\n\n"
        top_buffer += wr_buf + "\n\n"
        top_buffer += io_buf + "\n\n"
        top_buffer += wi_buf + "\n\n"
        top_buffer += wmi_buf + "\n\n"
        if (len(arb_buf) > 0):
            top_buffer += arb_buf + "\n\n"
        top_buffer += wm_buf + "\n\n"
        for slave_buf in slave_buffer_list:
            top_buffer = top_buffer + "\n\n" + slave_buf

        for mem_buf in mem_buffer_list:
            top_buffer = top_buffer + "\n\n" + mem_buf

        top_buffer = top_buffer + "\n\n" + buf_bind + "\n\n" + footer
        top_buffer = string.expandtabs(top_buffer, 2)
        return top_buffer

    def is_wishbone_port(self, port = ""):
        if port.startswith("i_") and port.endswith("wbs_we"):
            return True
        if port.startswith("i_") and port.endswith("wbs_cyc"):
            return True
        if port.startswith("i_") and port.endswith("wbs_stb"):
            return True
        if port.startswith("i_") and port.endswith("wbs_sel"):
            return True
        if port.startswith("o_") and port.endswith("wbs_ack"):
            return True
        if port.startswith("i_") and port.endswith("wbs_dat"):
            return True
        if port.startswith("o_") and port.endswith("wbs_dat"):
            return True
        if port.startswith("i_") and port.endswith("wbs_adr"):
            return True
        if port.startswith("o_") and port.endswith("wbs_int"):
            return True
        return False

    def generate_buffer(self,
                        name="",
                        index=-1,
                        module_tags={},
                        mem_slave = False,
                        io_module = False,
                        debug = False):
        """Generate a buffer that attaches wishbone signals and
        return a buffer that can be used to generate the top module"""
        slave_name = name

        board_dict = utils.get_board_config(self.tags["board"])
        invert_reset = board_dict["invert_reset"]

        parameter_buffer = ""
        if (io_module == False):
            parameter_buffer = self.generate_parameters(name, module_tags, debug)

        out_buf = ""

        out_buf = "//" + name + "( " + module_tags["module"] + " )\n\n"
        out_buf += "//wires\n"
        #if index == -1 then don't add an index
        #top_name will apply to all signals

        #go through each of hte module tags, and extrapolate the ports

        #generate the wires
        io_types = [
            "input",
            "output",
            "inout"
        ]

        arb_index = -1
        if ("ARBITOR" in self.tags.keys()):
            if (name in self.tags["ARBITOR"].keys()):
                arb_index = self.tags["ARBITOR"].keys().index(name)

        #add a prename to all the slaves
        pre_name = ""
        if (index != -1):
            if (arb_index != -1):
                pre_name = "arb%d_" % arb_index
            else:
                if mem_slave:
                    pre_name += "w_sm%d_" % index
                else:
                    pre_name += "w_s%d_" % index

#XXX: For the slaves, I should just skip all the inout stuff, cause I don't ned wires for inout, they bind directly to the port
    #generate all the wires
        if (name != "io"):
            for io in io_types:
                for port in module_tags["ports"][io].keys():
                    pdict = module_tags["ports"][io][port]
                    if ((len(name) > 0) and (index != -1)):
                        wire = ""
                        if (port == "clk" or port == "rst"):
                            continue
                        else:
                            if (self.is_wishbone_port(port)):
                                wire = pre_name + port
                            else:
                                wire = name + "_" + port
                        if (wire in self.wires):
                            continue
                    self.wires.append(port)
                    out_buf += "wire"
                    #if the size is greater than one add it
                    if (pdict["size"] > 1):
                        size_range = "[%d:%d]" % (pdict["max_val"], pdict["min_val"])
                        out_buf += "\t{0:<12}".format(size_range)
                        #out_buf += "\t[%d:%d]\t\t" % (pdict["max_val"], pdict["min_val"])
                    else:
                        out_buf += "\t{0:<12}".format("")
                        #add name and index if required
                    if (len(name) > 0):
                        if (port == "clk" or port == "rst"):
                            out_buf += port
                        else:
                            if (self.is_wishbone_port(port)):
                                out_buf += pre_name +  port
                            else:
                                out_buf += name + "_" + port
                        out_buf += ";\n"
                out_buf += "\n\n"

        #generate all wires for an IO module
        else:
            for io in io_types:
                for port in module_tags["ports"][io].keys():
                    pdict = module_tags["ports"][io][port]
                    if (port == "clk" or port == "rst"):
                        continue

                    if (port in self.wires):
                        continue

                    self.wires.append(port)
                    out_buf += "wire"
                    if (pdict["size"] > 1):
                        size_range = "[%d:%d]" % (pdict["max_val"], pdict["min_val"])
                        out_buf += "\t{0:<10}".format(size_range)
                    else:
                        out_buf += "\t{0:<10}".format("")

                    out_buf += port + ";\n"

            out_buf += "\n\n"


        #Finished Generating the Wires



        #Generate the instantiation
        out_buf += "%s " % module_tags["module"]

        #check if there are parameters to be added
        out_buf += parameter_buffer
        out_buf += "\t" + name
#   if (index != -1):
#     out_buf += str(index)

        out_buf += "(\n\n"

        pindex = 0
        last =  len(module_tags["ports"]["input"].keys())
        last += len(module_tags["ports"]["output"].keys())
        last += len(module_tags["ports"]["inout"].keys())

        #add the port assignments
        for io in io_types:
            for port in module_tags["ports"][io].keys():
                pdict = module_tags["ports"][io][port]
                out_buf += "\t.{0:<15}(".format(port)

                found_binding = False
                inout_binding = ""

                if (io == "inout"):
                    if debug:
                        print "found inout!: " + port
                    bkeys = self.bindings.keys()
                    for bkey in bkeys:
                        bname = bkey.partition("[")[0]
                        bname = bname.strip()
                        if io_module:
                            if debug:
                                print "comparing %s with %s" % (bname, port)
                            if (bname == port):
                                if debug: print "found: " + bkey


                                out_buf += "{0:<20}".format(self.bindings[bkey]["loc"])
                                found_binding = True

                        else:
                            if debug:
                                print "comparing %s with %s_%s" % (bname, name, port)
                            if (bname == (name + "_" +  port)):
                                if debug: print "found: " + bkey


                                out_buf += "{0:<20}".format(self.bindings[bkey]["loc"])
                                found_binding = True

                if( not found_binding):
                    #add name and index if required
                    if ((len(name) > 0) and (index != -1)):
                        if debug:
                            print "found name and index %s %d" % (name, index)
                        if (port.startswith(name)):
                            out_buf += "{0:<20}".format(name + str(index) + port.partition[name][2])
                            #out_buf += name + str(index) + port.partition(name)[2]
                        else:
                            if (port == "clk" or port == "rst"):
                                if (port == "rst"):
                                    if invert_reset:
                                        out_buf += "{0:<20}".format("rst_n")
                                    else:
                                        out_buf += "{0:<20}".format("rst")
                                else:
                                    out_buf += "{0:<20}".format(port)

                            else:
                                temp_port_name = ""
                                if (self.is_wishbone_port(port)):
                                    temp_port_name = pre_name +  port
                                else:
                                    temp_port_name = name + "_" + port

                                out_buf += "{0:<20}".format(temp_port_name)

                    else:
                        if (port == "clk" or port == "rst"):
                            if (port == "rst"):
                                if invert_reset:
                                    out_buf += "rst_n"
                                else:
                                    out_buf += "rst"
                            else:
                                out_buf += port
                        else:
                            if (self.is_wishbone_port(port)):
                                out_buf += pre_name +  port
                            else:
                                if (not io_module):
                                    out_buf += name + "_" + port
                                else:
                                    out_buf += port

                out_buf += ")"
                pindex = pindex + 1
                if (pindex == last):
                    out_buf += "\n"
                else:
                    out_buf += ",\n"

        out_buf += "\n);"

        return out_buf

    def generate_arbitor_buffer(self, debug = False):
        result = ""
        board_dict = utils.get_board_config(self.tags["board"])
        invert_reset = board_dict["invert_reset"]

        #self.wires
        arbitor_count = 0
        if (not arbitor.is_arbitor_required(self.tags)):
            return ""

        if debug:
            print "arbitration is required"

        result += "//Project Arbitors\n\n"
        arb_tags = arbitor.generate_arbitor_tags(self.tags)

        for i in range (0, len(arb_tags.keys())):
            arb_slave = arb_tags.keys()[i]
            master_count = 1
            arb_name = ""
            if debug:
                print "found arbitrated slave: " + arb_slave
            result += "//" + arb_slave + " arbitor\n\n"
            master_count += len(arb_tags[arb_slave].keys())
            arb_name = "arb" + str(i)
            arb_module = "arbitor_" + str(master_count) + "_masters"
            if debug:
                print "number of masters for this arbitor: " + str(master_count)
                print "using: " + arb_module
                print "arbitor name: " + arb_name

            #generate the wires
            for mi in range (0, master_count):
                wbm_name = ""
                if (mi == 0):
                    #these wires are taken care of by the interconnect
                    continue
                else:

                    master_name = arb_tags[arb_slave].keys()[mi - 1]
                    bus_name = arb_tags[arb_slave][master_name]
                    wbm_name = master_name + "_" + bus_name

                    #strobe

                    wire = "o_%s_stb" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<20}{1};\n".format("wire", wire)
                        self.wires.append(wire)
                    #cycle
                    wire = "o_%s_cyc" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<20}{1};\n".format("wire", wire)
                        self.wires.append(wire)
                    #write enable
                    wire = "o_%s_we" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<20}{1};\n".format("wire", wire)
                        self.wires.append(wire)
                    #select
                    wire = "o_%s_sel" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<19}{1};\n".format("wire\t[3:0]", wire)
                        self.wires.append(wire)
                    #in data
                    wire = "o_%s_dat" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                        self.wires.append(wire)
                    #out data
                    wire = "i_%s_dat" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                        self.wires.append(wire)
                    #address
                    wire = "o_%s_adr" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                        self.wires.append(wire)
                    #acknowledge
                    wire = "i_%s_ack" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<20}{1};\n".format("wire", wire)
                        self.wires.append(wire)
                    #interrupt
                    wire = "i_%s_int" % wbm_name
                    if (not (wire in self.wires)):
                        result += "{0:<20}{1};\n".format("wire", wire)
                        self.wires.append(wire)

            #generate arbitor signals
            #strobe
            wire = "i_%s_wbs_stb" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #cycle
            wire = "i_%s_wbs_cyc" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #write enable
            wire = "i_%s_wbs_we" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #select
            wire = "i_%s_wbs_sel" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<19}{1};\n".format("wire\t[3:0]", wire)
                self.wires.append(wire)
            #in data
            wire = "i_%s_wbs_dat" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #out data
            wire = "o_%s_wbs_dat" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #address
            wire = "i_%s_wbs_adr" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #acknowledge
            wire = "o_%s_wbs_ack" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #interrupt
            wire = "o_%s_wbs_int" % arb_name
            if (not (wire in self.wires)):
                result += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)

            result +="\n\n"





            #finished generating the wires

            result += "" + arb_module + " " + arb_name + "(\n"
            result += "\t.clk\t\t\t\t\t\t\t(clk),\n"
            if invert_reset:
                result += "\t.rst\t\t\t\t\t\t\t(rst_n),\n"
            else:
                result += "\t.rst\t\t\t\t\t\t\t(rst),\n"
            result += "\n"
            result += "\t//masters\n"

            for mi in range (0, master_count):

                wbm_name = ""

                #last master is always from the interconnect
                #XXX: This should really be a parameter, but this will alow slaves to take over a peripheral
                if (mi == master_count - 1):
                    if debug:
                        print "mi: " + str(mi)
                    on_periph_bus = False
                    #in this case I need to use the wishbone interconnect
                    #search for the index of the slave
                    for i in range (0, len(self.tags["SLAVES"].keys())):
                        name = self.tags["SLAVES"].keys()[i]
                        if name == arb_slave:
                            interconnect_index = i + 1 # +1 to account for DRT
                            on_periph_bus = True
                            wbm_name = "s" + str(interconnect_index)
                            if debug:
                                print "arb slave on peripheral bus"
                                print "slave index: " + str(interconnect_index - 1)
                                print "accounting for drt, actual bus index == " + str(interconnect_index)
                            break
                    #check mem bus
                    if (not on_periph_bus):
                        if ("MEMORY" in self.tags.keys()):
                            #There is a memory bus, look in here
                            for i in range (0, len(self.tags["MEMORY"].keys())):
                                name = self.tags["MEMORY"].keys()[i]
                                if name == arb_slave:
                                    mem_inc_index = i
                                    wbm_name = "sm" + str(i)
                                    if debug:
                                        print "arb slave on mem bus"
                                        print "slave index: " + str(mem_inc_index)
                                    break


                    result +="\t.i_m%d_we\t\t\t\t\t(w_%s_wbs_we_i),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_stb\t\t\t\t\t(w_%s_wbs_stb_i),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_cyc\t\t\t\t\t(w_%s_wbs_cyc_i),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_sel\t\t\t\t\t(w_%s_wbs_sel_i),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_dat\t\t\t\t\t(w_%s_wbs_dat_i),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_adr\t\t\t\t\t(w_%s_wbs_adr_i),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_dat\t\t\t\t\t(w_%s_wbs_dat_o),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_ack\t\t\t\t\t(w_%s_wbs_ack_o),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_int\t\t\t\t\t(w_%s_wbs_int_o),\n" % (mi, wbm_name)

                    result +="\n\n"




                #not the last index
                else:
                    if debug:
                        print "mi: " + str(mi)
                    master_name = arb_tags[arb_slave].keys()[mi]
                    bus_name = arb_tags[arb_slave][master_name]
                    wbm_name = master_name + "_" + bus_name


                    result +="\t.i_m%d_we\t\t\t\t\t(w_%s_we_o),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_stb\t\t\t\t\t(w_%s_stb_o),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_cyc\t\t\t\t\t(w_%s_cyc_o),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_sel\t\t\t\t\t(w_%s_sel_o),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_dat\t\t\t\t\t(w_%s_dat_o),\n" % (mi, wbm_name)
                    result +="\t.i_m%d_adr\t\t\t\t\t(w_%s_adr_o),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_dat\t\t\t\t\t(w_%s_dat_i),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_ack\t\t\t\t\t(w_%s_ack_i),\n" % (mi, wbm_name)
                    result +="\t.o_m%d_int\t\t\t\t\t(w_%s_int_i),\n" % (mi, wbm_name)
                    result +="\n\n"

            result += "\t//slave\n"
            result += "\t.o_s_we\t\t\t\t\t\t(w_%s_wbs_we_i),\n" % (arb_name)
            result += "\t.o_s_stb\t\t\t\t\t(w_%s_wbs_stb_i),\n" % (arb_name)
            result += "\t.o_s_cyc\t\t\t\t\t(w_%s_wbs_cyc_i),\n" % (arb_name)
            result += "\t.o_s_sel\t\t\t\t\t(w_%s_wbs_sel_i),\n" % (arb_name)
            result += "\t.o_s_dat\t\t\t\t\t(w_%s_wbs_dat_i),\n" % (arb_name)
            result += "\t.o_s_adr\t\t\t\t\t(w_%s_wbs_adr_i),\n" % (arb_name)
            result += "\t.i_s_dat\t\t\t\t\t(w_%s_wbs_dat_o),\n" % (arb_name)
            result += "\t.i_s_ack\t\t\t\t\t(w_%s_wbs_ack_o),\n" % (arb_name)
            result += "\t.i_s_int\t\t\t\t\t(w_%s_wbs_int_o)\n" % (arb_name)
            result += ");\n"





        return result


    def generate_parameters (self, name = "", module_tags = {}, debug = False):
        buffer = ""


        if (not (name in self.tags["SLAVES"].keys())):
            if debug:
                print "didn't find slave name"
            return ""

        #check to see if the project tags contain a paramter specification
        if debug:
            print "checking to see if " + name + " contains parameters in the configuration file... ",

        if (not ("PARAMETERS" in self.tags["SLAVES"][name])):
            if debug:
                print "no"
            return ""

        if debug:
            print "yes"

        if debug:
            print "checking to see if the module contains any paramters... ",
        if (len(module_tags["parameters"].keys()) == 0):
            if debug:
                print"no"
            return ""

        if debug:
            print "yes"

        module_parameters = module_tags["parameters"]

        #XXX: Unfortunately the parameter finder doesn't discriminate against all parameters within the modules
        #so all the parameters will be exposed here :(
        #
        #   for param in module_parameters.keys():
        #
        #     print param + " : " + module_parameters[param]


        buffer = "#(\n"
        #check to see if the paramter exists within the module's tags

        project_parameters = self.tags["SLAVES"][name]["PARAMETERS"]

        #need a variable for the first one so that we don't inadvertently add a comma

        first_item = True
        for project_param in project_parameters.keys():
            if project_param in module_parameters.keys():
                if (first_item == False):
                    buffer += ",\n"

                first_item = False
                if debug:
                    print "found that " + project_param + " is a match"
                buffer += "\t\t." + project_param + "(" + project_parameters[project_param] + ")"

        #finish off the buffer
        buffer += "\n\t)\n"

        return buffer

    def generate_host_if_buffer(self,
                                module_tags):
        #print "in %s" % "generate_host_if_buffer"
        name = "io"
        board_dict = utils.get_board_config(self.tags["board"])
        invert_reset = board_dict["invert_reset"]
        bkeys = self.bindings.keys()

        out_buf = ""
        out_buf = "// %s ( %s )\n\n" % (name, module_tags["module"])
        out_buf += "//wires\n"

        io_types = [
            "input",
            "output"
        ]

        #Generate the Wires
        #The interface to the master is already defines
        if_wires = [
            "i_master_ready",
            "o_ih_ready",
            "o_ih_reset",
            "o_in_command",
            "o_in_address",
            "o_in_data",
            "o_in_data_count",
            "i_oh_en",
            "o_oh_ready",
            "i_out_status",
            "i_out_address",
            "i_out_data",
            "i_out_data_count"]

        for io in io_types:
            ports = module_tags["ports"][io]
            for port in ports:
                port_dict = ports[port]

                #We have already declared these wires
                if port in if_wires:
                    continue
                #Check to see if any other wire is in here
                if port in self.wires:
                    continue
                line = ""
                if port_dict["size"] > 1:
                    #need to include a range
                    max_val = port_dict["max_val"]
                    min_val = port_dict["min_val"]
                    size_range = "[%d:%d]" % (max_val, min_val)
                    line = "wire\t{0:15}{1};\n".format(size_range, port)
                else:
                    #Single wire
                    line = "wire\t{0:15}{1};\n".format("", port)

                out_buf += line

        out_buf += "\n\n"

        #Declare the module
        module_name = "%s\t%s\t(\n" % (module_tags["module"], name)
        out_buf += module_name
        #Add in the ports

        line = "\t.{0:<20}({1:<20}),\n".format("clk", "clk")
        out_buf += line
        if invert_reset:
            line = "\t.{0:<20}({1:<20}),\n".format("rst", "rst_n")
        else:
            line = "\t.{0:<20}({1:<20}),\n".format("rst", "rst")
        out_buf += line


        # we need to know when we are at the last item
        input_keys = []
        output_keys = []
        inout_keys = []
        
        if "input" in module_tags["ports"].keys():
            input_keys = module_tags["ports"]["input"].keys()
        if "output" in module_tags["ports"].keys():
            output_keys = module_tags["ports"]["output"].keys()
        if "inout" in module_tags["ports"].keys():
            inout_keys = module_tags["ports"]["inout"].keys()

        input_keys_last = True
        output_keys_last = True
        inout_keys_last = True

        if len(output_keys) > 0:
            input_keys_last = False
        if len(inout_keys) > 0:
            output_keys_last = False

        #input signals
        for port in input_keys:
            line = ""
            #We already took care of clock and reset
            if port == "rst":
                continue
            if port == "clk":
                continue
            
            #Check to see if we are one of the pre-defined ports
            wire = ""
            for w in if_wires:
                if w.endswith(port[2:]):
                    wire = "w_%s" % w[2:]
                    break
                
            if len(wire) == 0:
                #No bindings associated with this signal
                wire = port

            line = "\t.{0:<20}({1:<20})".format(port, wire)

            if input_keys_last and port == input_keys[-1]:
                line += "\n"
            else:
                line += ",\n"
            out_buf += line

        #output signals
        for port in output_keys:
            line = ""
            #check to see if we are one of the pre-defined ports
            wire = ""
            for w in if_wires:
                if w.endswith(port[2:]):
                    wire = "w_%s" % w[2:]
                    break
                
            if len(wire) == 0:
                #No bindings associated with this signal
                wire = port

            line = "\t.{0:<20}({1:<20})".format(port, wire)
            if output_keys_last and port == output_keys[-1]:
                line += "\n"
            else:
                line += ",\n"
            out_buf += line



        #Handle the inout case
        for port in inout_keys:
            #port = module_tags["ports"]["inout"][iok]
            #print "port: %s" % port
            for bkey in bkeys:
                bname = bkey.partition("[")[0]
                bname = bname.strip()
                if bname == port:
                    loc = self.bindings[bkey]["loc"]
                    if port == inout_keys[-1]:
                        line = "\t.{0:<20}({1:<20})\n".format(port, loc)
                    else:
                        line = "\t.{0:<20}({1:<20}),\n".format(port, loc)

                    out_buf += line
        out_buf += ");"
        #print "out_buf:\n%s" % out_buf
        return out_buf

    def get_name (self):
        print "generate top!"


