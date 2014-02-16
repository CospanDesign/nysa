#! /usr/bin/python

import sys
import os
import argparse
import shutil

DESCRIPTION = "\n" \
"Update pyqt4-visual-graph with the most recent version of the library\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"update_visual_graph.py\n" + \
"\tupdates the xilinx build with the files in ~/Projects/visual_graph\n" + \
"\n" + \
"update_visual_graph.py <your path here>\n" + \
"\tupdates the xilinx build with the path specified"


debug = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
      description=DESCRIPTION,
      epilog=EPILOG
    )

    #Add an argument to the parser
    home = os.path.expanduser("~")
    default_path = os.path.join(home, "Projects", "pyqt4-visual-graph", "visual_graph")
    parser.add_argument("path",
                        type = str,
                        nargs='?',
                        default=default_path,
                        help="Specify the path to visual_grapher (leave blank for %s" % default_path)
    parser.parse_args()
    arg = parser.parse_args()

    if not os.path.exists(arg.path):
        print "Path: %s Doesn't exists!" % arg.path
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(__file__), "visual_graph")

    arg.path

    #Remove any local version of the files
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    #Copy over site_scons
    shutil.copytree(arg.path, out_dir)

