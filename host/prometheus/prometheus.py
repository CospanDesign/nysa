#! /usr/bin/python

# -*- coding: UTF-8 -*-

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import argparse

from PyQt4.QtCore import *

from gui.prometheus_gui import PrometheusGui 

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "\n"\
    "Prometheus controller and programmer: Standalone or Subsystem of the\n"\
    "Nysa Plugin\n"\
    "\n"\
    "Sends and receives data between the host and Prometheus\n"\
    "\n"\
    "Starts a server on the local host that can be used to program using sockets\n"

EPILOG = "\n"\
    "Examples:\n"\
    "\n"\
    "prometheus.py]n"\
    "\tStarts the visual prometheus interface\n"\
    "prometheus.py --daemon\n"\
    "\tStart the GUI in background mode the socket server is the only thing\n"\
    "\tthat will be visible\n"\

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )
 
    global debug
    debug = False
    #Make debug global to the all modules

    #Add arguments to the parser
    parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")
    parser.add_argument("--daemon", action="store_true", help="Start Prometheus comm as a daemon")
    parser.parse_args()
    args = parser.parse_args()



    if args.debug:
        print "Debug Enabled"
        debug = True

    if args.daemon:
        print "Run the system as a deamon"

