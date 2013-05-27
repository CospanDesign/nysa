import os
import sys
import string
import glob
import json
from ibuilder_error import XilinxToolchainError


"""
Xilinx specific utilities
"""

"""
Changes:
5/21/2012
  -Initial commit

"""

LINUX_DEFAULT_SEARCH_PATHS = ["/opt"]
WINDOWS_DEFAULT_SEARCH_PATHS = ["C:\\xilnix", "D:\\xilinx"]

DEFAULT_SEARCH_PATHS = LINUX_DEFAULT_SEARCH_PATHS

if os.name == "nt":
  DEFAULT_SEARCH_PATHS = WINDOWS_DEFAULT_SEARCH_PATHS

elif os.name == "posix":
  DEFAULT_SEARCH_PATHS = LINUX_DEFAULT_SEARCH_PATHS


def get_version_list(base_directory = None, debug=False):
  """
  Returns a list of version of the Xilinx toolchain

  if the user does not specify the base_directory
  the default /opt will be used
  """
  versions = []
  base_dirs = []

  if base_directory is None:
    base_directory = DEFAULT_SEARCH_PATHS
  else:
    base_dirs = [base_directory]

  for bd in base_dirs:
    if debug:
      print "searching in %s..." % (bd)
    dir_list = glob.glob(os.path.join(bd, "*"))
    dirs = []
    for d in dir_list:
      if "Xilinx" in d:
        dirs = glob.glob(os.path.join(d,"*"))
        for v in dirs:
          versions.append(float(v.rpartition(os.path.sep)[2]))
          break

    if debug:
      print "versions: " + str(versions)

  return versions

def locate_xilinx_base(base_directory=None, version=None, debug=False):
  base_dirs = []
  versions = []
  path_dict = {}
  if debug: print "Find Path"
  if base_directory is None or len(base_directory) == 0:
    if debug: print "Using Default search path"
    base_dirs = DEFAULT_SEARCH_PATHS
  else:
    base_dirs = [base_directory]

  for bd in base_dirs:
    if debug:
      print "searching in %s..." % (bd)
    dir_list = glob.glob(os.path.join(bd, "*"))
    dirs = []
    for d in dir_list:
      if "Xilinx" in d:
        dirs = glob.glob(os.path.join(d,"*"))
        for v in dirs:
          ver_string = v.rpartition(os.path.sep)[2]
          ver = float(ver_string)
          versions.append(float(v.rpartition(os.path.sep)[2]))
          # map the version number to the path
          path_dict[v.rpartition(os.path.sep)[2]] = v
          break

    if debug:
      print "versions: " + str(versions)
      for v in path_dict.keys():
        print "%s: %s" % (v, path_dict[v])

  if version is None:
    if debug: "Version was not specified, select the most recent version"
    if len(path_dict.keys()) == 0:
      raise XilinxToolchainError("Xilinx toolchain was not found looked in %s" % str(base_dirs))
      return None
    version = max(path_dict.keys())

  if version not in path_dict.keys():
    raise XilinxToolchainError("Xilinx toolchain version: %s doesn't exists" % version)

  return path_dict[version]


def locate_xilinx_sim_files(xilinx_base=None, debug=False):
  """
  Locate the simulation files for Xilinx

  Args:
    xilinx_base:
      base directory of the Xilinx toolchain, if left blank
      the function will attempt to locate the most recent Xilnx toolchain and
      use it as the base

  Returns:
    (string) A directory of the simulation base to search for sim files
  """
  debug = True
  if xilinx_base is None:
    xilinx_base = locate_xilinx_base()

  sim_base = os.path.join(xilinx_base, "ISE_DS", "ISE", "verilog", "src", "unisims")
  if debug: print "Simulation Base: %s" % sim_base

  return sim_base


def get_supported_version(fpga_part_number, versions, debug = False):
  """
  using an FPGA number, determine if the FPGA is a
  Spartan 3 or a Spartan 6

  based off of the fpga_part_number determine what version
  should be used to build the design

  Spartan 3 < 14.0
  Spartan 6 >= 12.0
  """

  pn = fpga_part_number
  #strip off the first two characters
  pn = pn[2:]
  num = 0
  length = len(pn)
  i = 0
  for i in range (0, length):
    if pn[i].isdigit():
      i += 1
    else:
      break

  num = int(pn[0:i])
  if debug:
    print "FPGA number: %d" % num

  versions.sort()
  if len(versions) == 0:
    raise Exception("no Versions of Xilinx Toolchain")

  if num == 6:
    #return the largest version
    return versions[-1]

  if num == 3:
    for i in range (0, len(versions)):
      if versions[-1 - i] < 14.0:
        return versions[-1 - i]

  raise Exception("FPGA Number %d not supported yet!" % num)




