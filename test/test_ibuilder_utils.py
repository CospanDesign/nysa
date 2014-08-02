#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from nysa.ibuilder.lib import utils

import json

GPIO_TAGS = json.load(open(os.path.join(os.path.dirname(__file__), "mock", "gpio_module_tags.txt"), 'r'))
SDRAM_TAGS = json.load(open(os.path.join(os.path.dirname(__file__), "mock", "sdram_module_tags.txt"), 'r'))

class Test (unittest.TestCase):
    """Unit test for utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                            os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_create_dir(self):
        pass

    def test_get_nysa_base(self):
        pass

    def test_remove_comments(self):
        """try and remove all comments from a buffer"""
        bufin = "not comment/*comment\n*/\n//comment\n/*\nabc\n*/something//comment"
        output_buffer = utils.remove_comments(bufin)
        good = "not comment\n\nsomething\n"
        self.assertEqual(output_buffer, good)

    def test_get_constraint_filenames(self):
        cfiles = utils.get_constraint_filenames("dionysus")
        self.assertIn("dionysus.ucf", cfiles)

    def test_get_board_config(self):
        """
        gets the board configuration dictionary given the board
        name
        """
        boardname = "dionysus"
        board_dict = utils.get_board_config(boardname)
        self.assertEqual(board_dict["board_name"], "Dionysus")

    def test_get_board_names(self):
        """
        gets all the board names
        """
        boards = utils.get_board_names(False)
        self.assertIn("dionysus", boards)

    def test_find_rtl_file_location(self):
        """give a filename that should be in the RTL"""
        result = utils.find_rtl_file_location("wb_gpio.v", debug=False)
        #print "file location: " + result
        try:
            testfile = open(result)
            result = True
            testfile.close()
        except:
            result = False

        self.assertEqual(result, True)

    def test_find_rtl_file_location_user_cbuilder(self):
        """give a filename that should be in the RTL"""
        utils.create_dir(os.path.join(os.path.expanduser("~"), "sandbox", "temp"))
        try:
            fname = os.path.expanduser("~/sandbox/temp/temp.v")
            f = open(fname, 'w')
            f.write("module m ()\n\nendmodule")
            f.close()
        except IOError, err:
            print "Failed to write file" + str(err)
            return

        result = utils.find_rtl_file_location(  "temp.v",
                                            [os.path.expanduser("~/sandbox")],
                                            debug=False)
        #print "file location: " + result
        try:
            testfile = open(result)
            result = True
            testfile.close()
        except:
            result = False

        self.assertEqual(result, True)



    def test_resolve_path(self):
        """given a filename with or without the ~ return a filename with the ~ expanded"""

        filename1 = "/filename1"
        filename = utils.resolve_path(filename1)
        self.assertEqual(filename, "/filename1")

        filename2 = "~/filename2"
        filename = utils.resolve_path(filename2)
        correct_result = os.path.expanduser("~") + "/filename2"
        self.assertEqual(correct_result, filename)
        filename = filename.strip()


    def test_read_user_parameters(self):
        print "Read Parameters"
        filename = utils.find_rtl_file_location("wb_gpio.v")
        #tags = vutils.get_module_tags(filename, debug=self.dbg)
        tags = GPIO_TAGS
        #print "GPIO TAGS: %s" % str(GPIO_TAGS)

        #f = open("gpio_module_tags.txt", 'w')
        #print "Tags: %s" % str(tags)
        #f.write(json.dumps(tags))
        #f.close()


        keys = tags["parameters"].keys()
        if self.dbg:
            print "reading the parameters specified by the user"
        self.assertIn("DEFAULT_INTERRUPT_MASK", keys)
        if self.dbg:
            print "make sure other parameters don't get read"
        self.assertNotIn("ADDR_GPIO", keys)

    def test_read_hard_slave_tags(self):
        """try and extrapolate all info from the slave file"""
        filename = os.path.join(  self.nysa_base,
                                  "nysa",
                                  "cbuilder",
                                  "verilog",
                                  "wishbone",
                                  "slave",
                                  "wb_sdram",
                                  "rtl",
                                  "wb_sdram.v")
        drt_keywords = [
          "DRT_ID",
          "DRT_FLAGS",
          "DRT_SIZE"
        ]


        tags = SDRAM_TAGS
        #print "Tags: %s" % str(tags)

        io_types = [
          "input",
          "output",
          "inout"
        ]

        self.assertEqual(True, True)

    def test_get_net_names(self):
        filename = "lx9.ucf"
        netnames = utils.get_net_names(filename, debug = self.dbg)
        if self.dbg:
            print "net names: "
            for name in netnames:
                print "\t%s" % name
        self.assertIn("clk", netnames)


    def test_read_clk_with_period(self):
        filename = "dionysus.ucf"
        clock_rate = utils.read_clock_rate(filename, debug = self.dbg)
        self.assertEqual(int(clock_rate), 50000000)

    def test_read_clk_with_timespec(self):
        filename = "lx9.ucf"
        clock_rate = utils.read_clock_rate(filename, debug = self.dbg)
        self.assertEqual(int(clock_rate), 100000000)


    def test_is_module_in_file(self):
        module_name = "uart"
        filename = "wb_gpio.v"
        result = utils.is_module_in_file(filename, module_name, debug = self.dbg)
        self.assertEqual(result, False)

        module_name = "wb_gpio"
        filename = "wb_gpio.v"
        result = utils.is_module_in_file(filename, module_name, debug = self.dbg)
        self.assertEqual(result, True)

    def test_get_slave_list(self):
        slave_list = utils.get_slave_list(debug = self.dbg)

    def test_find_module_filename(self):
        module_name = "wb_spi"
        result = utils.find_module_filename(module_name, debug = self.dbg)
        self.assertEqual(len(result) > 0, True)

    def test_recursive_dict_name_fix(self):
        d = {
        "dir":"${NYSA}/path/number/one"
        }
        utils.recursive_dict_name_fix(d)
        self.assertNotIn("${NYSA}", d["dir"])


if __name__ == "__main__":
    unittest.main()

