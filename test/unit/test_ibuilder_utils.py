#! /usr/bin/python

import unittest
import sys
import os
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.ibuilder.lib import utils

import json

GPIO_TAGS = json.load(open( os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            "mock", "gpio_module_tags.txt"), 'r'))
SDRAM_TAGS = json.load(open(os.path.join(os.path.dirname(__file__),
                            os.pardir,
                            "mock", "sdram_module_tags.txt"), 'r'))

class Test (unittest.TestCase):
    """Unit test for utils"""

    def setUp(self):
        base = os.path.join( os.path.dirname(__file__),
                            os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

    def test_get_nysa_base(self):
        """Get the nysa base directory"""
        nysa_base = utils.get_nysa_base()
        assert os.path.exists(nysa_base)

    def test_create_dir(self):
        """use the create_dir to create a local directory"""
        utils.create_dir("test_dir")
        assert os.path.exists("test_dir")
        os.rmdir("test_dir")

    def test_resolve_path(self):
        """given a filename with or without the ~ return a filename with the ~ expanded"""

        filename1 = os.path.join(os.path.sep, "filename1")
        filename = utils.resolve_path(filename1)
        self.assertEqual(filename, filename1)

        filename2 = os.path.join("~", "filename2")
        filename = utils.resolve_path(filename2)
        correct_result = os.path.expanduser("~") + "/filename2"
        self.assertEqual(correct_result, filename)

    def test_remove_comments(self):
        """try and remove all comments from a buffer"""
        bufin = "not comment/*comment\n*/\n//comment\n/*\nabc\n*/something//comment"
        output_buffer = utils.remove_comments(bufin)
        good = "not comment\n\nsomething\n"
        self.assertEqual(output_buffer, good)

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
        loc = os.path.join(os.path.dirname(__file__),
                           os.pardir,
                           "fake")
        search_location = os.path.expanduser(loc)

        result = utils.find_rtl_file_location(  "test.v",
                                            [search_location],
                                            debug=False)
        #print "file location: " + result
        try:
            testfile = open(result)
            result = True
            testfile.close()
        except:
            result = False

        self.assertEqual(result, True)

    def test_get_board_names(self):
        """gets all the board names"""
        boards = utils.get_board_names(debug = False)
        self.assertIn("dionysus", boards)

    def test_get_board_names_user_loc(self):
        """get all the board names adding custom locations"""
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake")
        boards = utils.get_board_names([loc])
        self.assertIn("test_board", boards)

    def test_get_constraint_filenames(self):
        cfiles = utils.get_constraint_filenames("dionysus")
        self.assertIn("dionysus.ucf", cfiles)

    def test_get_constraint_filenames_user_loc(self):
        """Set the current directory to a search location""" 
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake")

        cfiles = utils.get_constraint_filenames("test_board", [loc])
        self.assertIn("test.ucf", cfiles)

    def test_get_board_config(self):
        """gets the board configuration dictionary given the board name"""
        boardname = "dionysus"
        board_dict = utils.get_board_config(boardname)
        self.assertEqual(board_dict["board_name"], "Dionysus")

    def test_get_board_config_usr_loc(self):
        """gets the board configuration dictionary given the board name"""
        boardname = "test_board"
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake")

        board_dict = utils.get_board_config(boardname, [loc])
        self.assertEqual(board_dict["board_name"], "Test Board")

    def test_get_net_names(self):
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake",
                           "test_board",
                           "test.ucf")
        netnames = utils.get_net_names(loc, debug = self.dbg)
        if self.dbg:
            print "net names: "
            for name in netnames:
                print "\t%s" % name
        self.assertIn("clk", netnames)

    def test_get_constraint_file_path(self):
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake")
        filename = "test.ucf"
        fp = utils.get_constraint_file_path(filename, [loc])
        assert os.path.exists(fp)

    def test_read_clk_with_period(self):
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake",
                           "test_board",
                           "test.ucf")
        clock_rate = utils.read_clock_rate(loc, debug = self.dbg)
        self.assertEqual(int(clock_rate), 50000000)

    def test_read_clk_with_timespec(self):
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake",
                           "lx9.ucf")
        clock_rate = utils.read_clock_rate(loc, debug = self.dbg)
        self.assertEqual(int(clock_rate), 100000000)

    def test_get_slave_list(self):
        slave_list = utils.get_slave_list(debug = self.dbg)
        #print "slave list: %s" % str(slave_list)
        p = False
        for slave in slave_list:
            if "wb_gpio.v" in slave:
                p = True
        assert p

    def test_get_slave_list_usr_loc(self):
        loc = os.path.join(os.path.dirname(__file__),
                           os.path.pardir,
                           "fake")

        slave_list = utils.get_slave_list(user_paths = [loc], debug = self.dbg)
        #print "slave list: %s" % str(slave_list)
        p = False
        for slave in slave_list:
            if "test_wb_slave.v" in slave:
                p = True
        assert p

    def test_is_module_in_file_fail(self):
        module_name = "uart"
        filepath = os.path.join(os.path.dirname(__file__),
                                os.path.pardir,
                                "fake",
                                "test_wb_slave.v")
        result = utils.is_module_in_file(filepath, module_name, debug = self.dbg)
        self.assertEqual(result, False)

    def test_is_module_in_file_pass(self):
        module_name = "wb_test"
        filepath = os.path.join(os.path.dirname(__file__),
                                os.path.pardir,
                                "fake",
                                "test_wb_slave.v")
        result = utils.is_module_in_file(filepath, module_name, debug = self.dbg)
        self.assertEqual(result, True)

    def test_find_module_filename(self):
        module_name = "wb_spi"
        result = utils.find_module_filename(module_name, debug = self.dbg)
        self.assertEqual(len(result) > 0, True)

    def test_find_module_filename_usr_paths(self):
        module_name = "wb_test"
        loc = os.path.join( os.path.dirname(__file__),
                            os.path.pardir,
                            "fake")
        result = utils.find_module_filename(module_name, user_paths = [loc], debug = self.dbg)
        self.assertEqual(len(result) > 0, True)

    def test_recursive_dict_name_fix(self):
        d = {
        "dir":"${NYSA}/path/number/one"
        }
        utils.recursive_dict_name_fix(d)
        self.assertNotIn("${NYSA}", d["dir"])
    
    def test_create_native_path(self):
        non_native_path = "./."
        native_path = utils.create_native_path(non_native_path)
        native_path = os.path.abspath(native_path)
        assert os.path.exists(native_path)

    def test_board_exists(self):
        assert not utils.board_exists("bad")
        assert utils.board_exists("dionysus")

if __name__ == "__main__":
    unittest.main()

