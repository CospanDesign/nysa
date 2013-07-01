#! /usr/bin/python
import unittest
import os
import sys
import json
import mock

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.gui import wishbone_model
from ibuilder.gui import graph_manager as gm
from ibuilder.gui.graph_manager import SlaveType as st
from ibuilder.gui.graph_manager import NodeType as nt

from ibuilder.lib.ibuilder_error import SlaveError
from ibuilder.lib import utils

from ibuilder.gui.gui_error import WishboneModelError

class WishboneModelTest (unittest.TestCase):


    EXAMPLE_CONFIG = {
      "BASE_DIR": "~/projects/sycamore_projects",
      "board": "xilinx-s3esk",
      "PROJECT_NAME": "example_project",
      "TEMPLATE": "wishbone_template.json",
      "INTERFACE": {
        "filename": "uart_io_handler.v",
        "bind": {
          "i_phy_uart_in": {
            "port": "RX",
            "direction": "input"
          },
          "o_phy_uart_out": {
            "port": "TX",
            "direction": "output"
          }
        }
      },
      "SLAVES": {
        "gpio1": {
          "filename":"wb_gpio.v",
          "bind": {
            "gpio_out[7:0]": {
              "port":"led[7:0]",
              "direction":"output"
            },
            "gpio_in[3:0]": {
              "port":"switch[3:0]",
              "direction":"input"
            }
          }
        }
      },
      "bind": {},
      "constraint_files": []
    }


    BOARD_CONFIG = {
      "board_name": "Spartan 3 Starter Board",
      "vendor": "Digilent",
      "fpga_part_number": "xc3s500efg320",
      "host_interface":"uart_io_handler",
      "build_tool": "xilinx",
      "default_constraint_files": [
        "s3esk_sycamore.ucf"
      ],
      "default_project":"xilnx-xilinx-s3esk_default.json",
      "invert_reset": False
    }

    dbg = False



    def setUp(self):
        """Creates a WishboneModel for each test"""
        #print "Graph WishboneModel Test"
        self.c = wishbone_model.WishboneModel()
        base = os.path.join( os.path.dirname(__file__),
                             os.pardir)
        self.nysa_base = os.path.abspath(base)

    def test_start_with_project_config_file(self):
        fname = os.path.join(os.path.dirname(__file__), os.pardir, "ibuilder",
          "example_projects", "xilinx-s3esk_default.json")

        self.c = wishbone_model.WishboneModel(config_file=fname)

        self.assertEqual(self.c.project_tags, self.EXAMPLE_CONFIG)
        self.assertEqual(self.c.filename, fname)
        self.assertEqual(self.c.build_tool, {})
        self.assertEqual(self.c.board_dict["board_name"], self.BOARD_CONFIG["board_name"])

    def test_start_with_board_name(self):
        self.c = wishbone_model.WishboneModel(board_name="xilinx-s3esk")
        self.assertEqual(self.c.board_dict["board_name"], self.BOARD_CONFIG["board_name"])
    
    def test_load_config_file(self):
        """Loads the config file and compares it to EXAMPLE_CONFIG"""
        self.c.get_board_config = (lambda x: self.BOARD_CONFIG)
        self.c.get_project_constraint_files = (
          lambda: self.BOARD_CONFIG['default_constraint_files'])
       
        # Load the example file from the example dir
        fname = os.path.join(os.path.dirname(__file__), os.pardir, "ibuilder",
          "example_projects", "xilinx-s3esk_default.json")
        self.assertTrue(self.c.load_config_file(fname),
          'Could not get file %s. Please ensure that is exists\n' +
          '(re-checkout from the git repos if necessary)')
       
        #cfilename = os.path.join(self.nysa_base, "ibuilder", "example_projects", "dionysus_gpio_mem.json")
        #f = open(cfilename, "r")
        #board_dict = json.load(f)
        #f.close()
       
        #Check that the state of the wishbone_model is as it should be.
        self.assertEqual(self.c.project_tags, self.EXAMPLE_CONFIG)
        self.assertEqual(self.c.filename, fname)
        self.assertEqual(self.c.build_tool, {})
        self.assertEqual(self.c.board_dict, self.BOARD_CONFIG)

    def test_set_config_file_location(self):
        path = os.path.join(os.path.expanduser("~"), "sandbox")
        self.c.set_config_file_location(path)
        #Interrogate the class directly
        self.assertEqual(path, self.c.filename)

    def test_initialize_graph(self):
        try:
            self.c.initialize_graph(debug = False)
        except WishboneModelError, err:
            self.fail("Failed Graph Initialization: %s" % err)

    def test_get_number_of_memory_slaves(self):
        fn = utils.find_module_filename("wb_sdram")
        fn = utils.find_rtl_file_location(fn)
       
        self.assertEqual(self.c.get_number_of_memory_slaves(), 0)
        self.c.add_slave("SM0", fn, st.MEMORY)
        self.assertEqual(self.c.get_number_of_memory_slaves(), 1)



    def test_get_number_of_peripheral_slaves(self):
        fn = utils.find_module_filename("wb_i2c")
        fn = utils.find_rtl_file_location(fn)
       
        retval = self.c.get_number_of_peripheral_slaves()
        print "Number of slaves %d" % retval
        self.assertEqual(retval, 1)
        self.c.add_slave("S0", fn, st.PERIPHERAL)
        retval = self.c.get_number_of_peripheral_slaves()
        print "Number of slaves after adding one: %d" % retval
        self.assertEqual(retval, 2)

    def test_save_config_file(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        path = os.path.join(  os.path.expanduser("~"), 
                              "sandbox", 
                              "out_config.json")
        try:
            self.c.save_config_file(path)
        except WishboneModelError, err:
            self.fail("Failed saving config file: %s" % err)
       
        f = open(fname, 'r')
        orig = json.load(f)
        f.close()
       
        f = open(path, 'r')
        out = json.load(f)
        f.close()
       
        if self.dbg: print "orig: %s" % str(orig)
        if self.dbg: print "Compare with:"
        if self.dbg: print "out: %s" % str(out)
        self.assertEqual(orig, out)

    def test_apply_slave_tags_to_project(self):
        from ibuilder.gui.graph_manager import SlaveType
        from ibuilder.lib import utils
       
        fn = utils.find_module_filename("wb_i2c")
        fn = utils.find_rtl_file_location(fn)
        self.c.add_slave("S0", fn, SlaveType.PERIPHERAL)
       
        fn = utils.find_module_filename("wb_sdram")
        fn = utils.find_rtl_file_location(fn)
        self.c.add_slave("SM0", fn, SlaveType.MEMORY)
       
        try:
            self.c.apply_slave_tags_to_project(debug = self.dbg)
        except:
            self.fail("Failed applying slave tags to project")

    def test_set_project_location(self):
        path = os.path.join(os.path.expanduser("~"), "sandbox")
        self.c.set_project_location(path)
        self.assertEqual(self.c.project_tags["BASE_DIR"], path)

    def test_set_project_name(self):
        name = "bob"
        self.c.set_project_name(name)
        self.assertEqual(self.c.project_tags["PROJECT_NAME"], name)

    def test_get_project_name(self):
        name = "bob"
        self.c.set_project_name(name)
        rb_name = self.c.get_project_name()
        self.assertEqual(name, rb_name)

    def test_get_vendor_tools(self):
        fname = os.path.join(os.path.dirname(__file__), os.pardir, "ibuilder",
            "example_projects", "xilinx-s3esk_default.json")
        self.c.load_config_file(fname)
        vt = self.c.get_vendor_tools()
        self.assertEqual("xilinx", vt)

    def test_set_board_name(self):
        self.c.set_board_name("dionysus")
        self.assertEqual(self.c.board_dict["default_constraint_files"], ["dionysus.ucf"])

    def test_get_board_name(self):
        self.c.set_board_name("dionysus")
        bn = self.c.get_board_name()
        self.assertEqual(bn, "dionysus")

    def test_get_constraint_filenames(self):
        self.c.set_board_name("dionysus")
        cfn = self.c.get_constraint_filenames()
        self.assertEqual(cfn, ["dionysus.ucf"])

    def test_add_project_constraint_file(self):
        self.c.set_board_name("dionysus")
        self.c.add_project_constraint_file("constraint.ucf")
        cfn = self.c.get_constraint_filenames()
        self.assertEqual(cfn, ["dionysus.ucf", "constraint.ucf"])

    def test_remove_project_constraint_file(self):
        self.c.set_board_name("dionysus")
        #Add an item to the project constraint files
        self.c.add_project_constraint_file("constraint.ucf")
        #Get a list of constraint files
        cfn = self.c.get_constraint_filenames()
        #Compare
        self.assertEqual(cfn, ["dionysus.ucf", "constraint.ucf"])
        #Remove the list of constraint files
        self.c.remove_project_constraint_file("constraint.ucf")
        #Get a list of constraint files
        cfn = self.c.get_constraint_filenames()
        self.assertEqual(cfn, ["dionysus.ucf"])

    def test_set_project_constraint_files(self):
        self.c.set_board_name("dionysus")
        self.c.set_project_constraint_files(["constraint.ucf"])
        #Get a list of constraint files
        cfn = self.c.get_constraint_filenames()
        #Compare
        self.assertEqual(cfn, ["dionysus.ucf", "constraint.ucf"])

    def test_get_fpga_part_number(self):
        self.c.set_board_name("dionysus")
        pn = self.c.get_fpga_part_number()
        self.assertEqual("xc6slx9tqg144-3", pn)

    def test_set_bus_type(self):
        bt = "axi"
        self.c.set_bus_type(bt)
        self.assertEqual(self.c.bus_type, bt)

    def test_get_bus_type(self):
        bt = "axi"
        self.c.set_bus_type(bt)
        obt = self.c.get_bus_type()
        self.assertEqual(obt, bt)

    def test_set_host_interface(self):
        self.c.set_host_interface("ft_master_interface")
        hi = self.c.project_tags["INTERFACE"]["filename"]
        self.assertEqual(hi, "ft_master_interface.v")

    def test_get_master_bind_dict(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        mbd = self.c.get_master_bind_dict()
        #XXX: This is wrong, it should be from the ft_master_interface!!!!!
        self.assertIn("i_ftdi_clk", mbd.keys())

    def test_get_node_ports(self):
        #self.c.unbind_all()
        self.c.set_board_name("dionysus")
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "xilinx-s3esk_default.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        self.c.set_host_interface("ft_master_interface", debug=False)
       
       
        ps = self.c.get_number_of_peripheral_slaves()
        name = ""
        mbd = self.c.get_master_bind_dict()
       
        name = self.c.get_slave_name(st.PERIPHERAL, 1)
       
        uname = self.c.get_unique_name(name, nt.SLAVE, st.PERIPHERAL, slave_index = 1)
        ports = self.c.get_node_ports(uname)
        self.assertNotEqual(len(ports), 0)

    def test_unbind_all(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        mbd = self.c.get_master_bind_dict()
        self.assertNotEqual(len(mbd.keys()), 0)
        self.c.unbind_all()
        mbd = self.c.get_master_bind_dict()
        self.assertEqual(len(mbd.keys()), 0)
      

    def test_set_binding(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        self.c.set_host_interface("ft_master_interface", debug=False)
       
       
        ps = self.c.get_number_of_peripheral_slaves()
        mbd = self.c.get_master_bind_dict()
        name = self.c.get_slave_name(st.PERIPHERAL, 1)
        uname = self.c.get_unique_name(name, nt.SLAVE, st.PERIPHERAL, slave_index = 1)
        ports = self.c.get_node_ports(uname)
       
        '''
        try:
          self.c.set_binding(uname, 'gpio_in[8]', 'led0')
        except SlaveError, err:
          self.fail("Failed Set Binding: %s" % err)
        '''
        #print "Ports for %s: %s" % (uname, ports)


    def test_unbind_port(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        mbd = self.c.get_master_bind_dict()
        self.assertNotEqual(len(mbd.keys()), 0)
        node_names = self.c.gm.get_node_names()
        for nn in node_names:
            nb = self.c.gm.get_node_bindings(nn)
            for b in nb.keys():
                self.c.unbind_port(nn, b)
       
        mbd = self.c.get_master_bind_dict()
        self.assertEqual(len(mbd.keys()), 0)


    def test_get_host_interface_name(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        hi_name = self.c.get_host_interface_name()
        if self.dbg: print "Host Interface Name: %s" % hi_name
        self.assertEqual(hi_name, "ft_master_interface")

    def test_get_slave_name(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        slave_count = self.c.get_number_of_peripheral_slaves()
        if slave_count == 0:
            self.fail("Failed while attempting to test get_slave_name, slave_count == 0")
       
        name = self.c.get_slave_name(st.PERIPHERAL, 0)
        self.assertEqual(name, "DRT")

    def test_is_arb_master_connected(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        #mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)

    def test_add_arbitor_by_name(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
       
        self.c.remove_arbitor(  host_type = st.PERIPHERAL,
                                host_index = 1,
                                slave_type = st.MEMORY,
                                slave_index = 0)
       
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, False)
       
        #Add an arbitor back in the same place
        self.c.add_arbitor_by_name(arb_master_uname,
                            arbitor_name = "fb",
                            slave_name = mem_uname)
       
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)

    def test_add_arbitor(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
       
        self.c.remove_arbitor(  host_type = st.PERIPHERAL,
                                host_index = 1,
                                slave_type = st.MEMORY,
                                slave_index = 0)
       
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, False)
       
        #Add an arbitor back in the same place
        self.c.add_arbitor( host_type = st.PERIPHERAL, host_index = 1,
                            arbitor_name = "fb",
                            slave_type = st.MEMORY, slave_index = 0)
       
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)

    def test_get_connected_arbitor_slave(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        sn = self.c.get_connected_arbitor_slave(arb_master_uname, "fb")
        self.assertEqual(sn, mem_uname)


    def test_get_connected_arbitor_name(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        name = self.c.get_connected_arbitor_name( st.PERIPHERAL, 1,
                                                  st.MEMORY, 0)
        self.assertEqual(name, arb_name)




    def test_remove_arbitor_by_arb_master(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        #mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
        self.c.remove_arbitor_by_arb_master(arb_master_uname, arb_name)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, False)

    def test_remove_arbitor_by_name(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
       
        self.c.remove_arbitor_by_name(arb_master_uname, mem_uname)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, False)

    def test_remove_arbitor(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
       
        self.c.remove_arbitor(  host_type = st.PERIPHERAL,
                                host_index = 1,
                                slave_type = st.MEMORY,
                                slave_index = 0)
       
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, False)


    def test_is_active_arbitor_host(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_arb_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
        arb_name = "fb"
        mem_name = "mem1"
        arb_master_name = self.c.get_slave_name(st.PERIPHERAL, 1)
        arb_master_uname = self.c.get_unique_name(arb_master_name, nt.SLAVE, st.PERIPHERAL, 1)
        mem_uname = self.c.get_unique_name(mem_name, nt.SLAVE, st.MEMORY, 0)
        result = self.c.is_arb_master_connected(arb_master_uname, arb_name)
        self.assertEqual(result, True)
       
        result = self.c.is_active_arbitor_host(st.PERIPHERAL, 1)
        self.assertEqual(result, True)
       
        self.c.remove_arbitor(  host_type = st.PERIPHERAL,
                                host_index = 1,
                                slave_type = st.MEMORY,
                                slave_index = 0)
       
        result = self.c.is_active_arbitor_host(st.PERIPHERAL, 1)
       
        self.assertEqual(result, False)



    def test_rename_slave(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        name = "debug_lax"
        self.c.rename_slave(st.PERIPHERAL, 1, name)
        uname = self.c.get_unique_name(name, nt.SLAVE, st.PERIPHERAL, 1)
        new_name = self.c.get_slave_name_by_unique(uname)
        self.assertEqual(name, new_name)

    def test_get_slave_name_by_unique(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
       
       
        name = self.c.get_slave_name(st.PERIPHERAL, 1)
        uname = self.c.get_unique_name(name, nt.SLAVE, st.PERIPHERAL, 1)
        new_name = self.c.get_slave_name_by_unique(uname)
        self.assertEqual(name, new_name)

    def test_add_slave(self):
        fn = utils.find_module_filename("wb_sdram")
        fn = utils.find_rtl_file_location(fn)
       
        self.assertEqual(self.c.get_number_of_memory_slaves(), 0)
        self.c.add_slave("SM0", fn, st.MEMORY)
        self.assertEqual(self.c.get_number_of_memory_slaves(), 1)

    def test_remove_slave(self):
        fn = utils.find_module_filename("wb_sdram")
        fn = utils.find_rtl_file_location(fn)
       
        self.assertEqual(self.c.get_number_of_memory_slaves(), 0)
        self.c.add_slave("SM0", fn, st.MEMORY)
        self.assertEqual(self.c.get_number_of_memory_slaves(), 1)
        self.c.remove_slave(st.MEMORY, slave_index = 0)
        self.assertEqual(self.c.get_number_of_memory_slaves(), 0)


    def test_move_slave(self):
        fn = utils.find_module_filename("wb_sdram")
        fn = utils.find_rtl_file_location(fn)
       
        self.assertEqual(self.c.get_number_of_memory_slaves(), 0)
        self.c.add_slave("SM0", fn, st.MEMORY)
        self.assertEqual(self.c.get_number_of_memory_slaves(), 1)
       
        self.c.move_slave("SM0",
                          from_slave_type = st.MEMORY,
                          from_slave_index = 0,
                          to_slave_type = st.PERIPHERAL,
                          to_slave_index = -1)
        #Need to account for the DRT
        self.assertEqual(self.c.get_number_of_peripheral_slaves(), 2)


    def test_generate_project(self):
        fname = os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              "ibuilder",
                              "example_projects",
                              "dionysus_internal_lax_example.json")
        self.c.load_config_file(fname)
        self.c.initialize_graph(debug = False)
        self.c.generate_project()



if __name__ == "__main__":
  unittest.main()

