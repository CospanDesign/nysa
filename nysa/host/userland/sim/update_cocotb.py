#! /usr/bin/python

import sys
import os
import argparse
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__)))
default_path = "~/Projects/cocotb"
debug = False

DESCRIPTION = "\n" \
"Update the cocotb makefiles with the most recent version from a local dir\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"update_cocotb.py\n" + \
"\tupdates the cocotb makefiles with the files in %s\n" % default_path + \
"\n" + \
"update_cocotb.py <path to base of cocotb> (Not the base of cocotb/makefiles)\n" + \
"\tupdates the cocotb makefiles with the path specified"




if __name__ == "__main__":
    print "update cocotb"
    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
      description=DESCRIPTION,
      epilog=EPILOG
    )

    #Add an argument to the parser
    home = os.path.expanduser("~")
    default_path = os.path.expanduser(default_path)
    parser.add_argument("path",
                        type = str,
                        nargs='?',
                        default=default_path,
                        help="Specify the path to cocotb base (leave blank for %s" % default_path)
    parser.parse_args()
    arg = parser.parse_args()

    if not os.path.exists(arg.path):
        print "Path: %s Doesn't exists!" % arg.path
        sys.exit(1)

    path = arg.path
    if not os.path.exists(path):
        print "Path: %s Doesn't exists!" % arg.path
        sys.exit(1)

    out_dir = os.path.dirname(__file__)
    

    #Verify all the cocotb makefiles exists
    remote_makefiles = os.path.join(path, "makefiles")
    local_makefiles = os.path.join(out_dir, "makefiles")

    remote_lib = os.path.join(path, "lib")
    local_lib = os.path.join(out_dir, "lib")

    #Remove any local version

    if os.path.exists(local_makefiles):
        shutil.rmtree(local_makefiles)

    if os.path.exists(local_lib):
        shutil.rmtree(local_lib)

    #Copy over the makefils
    shutil.copytree(remote_makefiles, local_makefiles)
    shutil.copytree(remote_lib, local_lib)


