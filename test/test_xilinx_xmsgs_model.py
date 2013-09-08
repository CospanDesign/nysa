#! /usr/bin/python

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             "nysa",
                             "gui",
                             "ninja_plugin",
                             "ninja_nysa",
                             "nysa_plugin",
                             "common",
                             "xmsgs_tree_model"))

import xilinx_builder
import xilinx_xmsgs_parser


full_message = "<messages>"\
               "<msg type=\"warning\" file=\"HDLCompiler\" num=\"1127\" delta=\"old\" >\"ft.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">out_d</arg> ignored, since the identifier is never used\n"\
               "</msg>" \
               "<msg type=\"info\" file=\"HDLCompiler\" num=\"123\" delta=\"old\" >\"file.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">thing</arg> ignored, since the identifier is never used\n"\
               "</msg>" \
               "<msg type=\"error\" file=\"HDLCompiler\" num=\"123\" delta=\"new\" >\"file.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">thing</arg> ignored, since the identifier is never used\n"\
               "</msg>"\
               "</messages>"

partial_message_with_start = "<messages>" \
               "<msg type=\"warning\" file=\"HDLCompiler\" num=\"1127\" delta=\"old\" >\"file.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">out_d</arg> ignored, since the identifier is never used\n"\
               "</msg>"
partial_message = "<msg type=\"info\" file=\"HDLCompiler\" num=\"123\" delta=\"old\" >\"file.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">thing</arg> ignored, since the identifier is never used\n</msg>"

partial_message_with_end = "<msg type=\"error\" file=\"HDLCompiler\" num=\"123\" delta=\"old\" >\"file.v\" Line 142: Assignment to <arg fmt=\"%s\" index=\"1\">thing</arg> ignored, since the identifier is never used \n</msg>"\
               "</messages>"

active_path = "/home/cospan/Projects/ibuilder_projects/image_builder_test/output/_xmsgs"

class Test (unittest.TestCase):
    """Unit test for xilinx xmsgs model"""

    def setUp(self):
        base = os.path.join(os.path.dirname(__file__),
                            os.pardir)
        self.nysa_base = os.path.abspath(base)
        self.dbg = False

        #Test only a builder
    def test_full_messages(self):
        xb = xilinx_builder.XilinxBuilder("test")
        ftime = os.path.getctime("gotest.py")
        #print "ftime: %s" % str(ftime)
        xb.new_xmsgs_data(full_message, ftime)
        #print "result: %s" % str(result)
        result = xb.finished()
        self.assertTrue(result)

    def test_partial_message(self):
        xb = xilinx_builder.XilinxBuilder("test")
        ftime = os.path.getctime("gotest.py")
        xb.new_xmsgs_data(partial_message_with_start, ftime)
        result = xb.finished()
        self.assertFalse(result)
        xb.new_xmsgs_data(partial_message, ftime)
        result = xb.finished()
        self.assertFalse(result)
        xb.new_xmsgs_data(partial_message_with_end, ftime)
        result = xb.finished()
        self.assertTrue(result)
        
        #Test the message parser

    def test_xmsg_parser_start(self):
        xmp = xilinx_xmsgs_parser.XilinxXmsgsParser()
        xmp.watch_path(active_path)


#    def test_message_info(self):
#        xb = xilinx_builder.XilinxBuilder()
#        ftime = os.path.getctime("gotest.py")
#        xb.new_xmsgs_data(full_message, ftime)
#        result = xb.finished()
#        messages = xb.infos()
#        self.assertEqual(len(messages), 1)
#
#    def test_message_warnings(self):
#        xb = xilinx_builder.XilinxBuilder()
#        ftime = os.path.getctime("gotest.py")
#        xb.new_xmsgs_data(full_message, ftime)
#        result = xb.finished()
#        messages = xb.warnings()
#        self.assertEqual(len(messages), 1)
#
#    def test_message_errors(self):
#        xb = xilinx_builder.XilinxBuilder()
#        ftime = os.path.getctime("gotest.py")
#        xb.new_xmsgs_data(full_message, ftime)
#        result = xb.finished()
#        messages = xb.errors()
#        self.assertEqual(len(messages), 1)
#
#    def test_message_errors(self):
#        xb = xilinx_builder.XilinxBuilder()
#        ftime = os.path.getctime("gotest.py")
#        xb.new_xmsgs_data(full_message, ftime)
#        result = xb.finished()
#        messages = xb.new_messages()
#        self.assertEqual(len(messages), 1)
#
#    def test_message_timestamp(self):
#        xb = xilinx_builder.XilinxBuilder()
#        ftime = os.path.getctime("gotest.py")
#        xb.new_xmsgs_data(full_message, ftime)
#        result = xb.finished()
#        messages = xb.new_messages()
#        self.assertEqual(len(messages), 1)
#        ts = xb.message_timestamp()
#        self.assertEqual(ts, ftime)
#


