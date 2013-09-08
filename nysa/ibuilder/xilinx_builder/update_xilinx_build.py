#! /usr/bin/python

import sys
import os
import argparse
import shutil

DESCRIPTION = "\n" \
"Update the xilinx_builder with the most recent version from a local dir\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"update_xilinx_build.py\n" + \
"\tupdates the xilinx build with the files in ~/Projects/xilinx_build\n" + \
"\n" + \
"update_xilinx_build.py <your path here>\n" + \
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
    default_path = os.path.join(home, "Projects", "xilinx_builder")
    parser.add_argument("path",
                        type = str,
                        nargs='?',
                        default=default_path,
                        help="Specify the path to xilinx_builder (leave blank for %s" % default_path)
    parser.parse_args()
    arg = parser.parse_args()

    if not os.path.exists(arg.path):
        print "Path: %s Doesn't exists!" % arg.path
        sys.exit(1)

    out_dir = os.path.dirname(__file__)


    local_site_scons = os.path.join(out_dir, "site_scons")
    remote_site_scons = os.path.join(arg.path, "site_scons")

    local_config = os.path.join(out_dir, "config.json")
    remote_config = os.path.join(arg.path, "config.json")

    local_sconstruct = os.path.join(out_dir, "SConstruct")
    remote_sconstruct = os.path.join(arg.path, "SConstruct")

    local_readme = os.path.join(out_dir, "README.md")
    remote_readme = os.path.join(arg.path, "README.md")


    #Verify all the remote items to copy exists
    if not os.path.exists(remote_site_scons):
        print "Path: %s Doesn't exists!" % remote_site_scons
        sys.exit(1)

    if not os.path.exists(remote_config):
        print "Path: %s Doesn't exists!" % remote_config
        sys.exit(1)

    if not os.path.exists(remote_sconstruct):
        print "Path: %s Doesn't exists!" % remote_sconstruct
        sys.exit(1)

    if not os.path.exists(remote_readme):
        print "Path: %s Doesn't exists!" % remote_readme
        sys.exit(1)

    #Remove any local version of the files
    if os.path.exists(local_site_scons):
        shutil.rmtree(local_site_scons)

    if os.path.exists(local_config):
        os.remove(local_config)

    if os.path.exists(local_sconstruct):
        os.remove(local_sconstruct)

    if os.path.exists(local_readme):
        os.remove(local_readme)

    #Copy over site_scons
    shutil.copytree(remote_site_scons, local_site_scons)

    #Copy over default config
    shutil.copy2(remote_config, local_config)

    #Copy over default sconstruct
    shutil.copy2(remote_sconstruct, local_sconstruct)

    shutil.copy2(remote_readme, local_readme)

