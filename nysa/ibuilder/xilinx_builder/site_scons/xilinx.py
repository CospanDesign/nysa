#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

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

import os
import shutil
import string
try:
    import getpass
except:
    pass

import utils

import xst_utils
import ngd_utils
import map_utils
import par_utils
import trace_utils
import bitgen_utils
import coregen_utils

class XilinxNotImplimented(Exception):
    """XilinxNotImplemented

    Errors associated with not implementing stuff
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def test_xst():
    print "Hello"


def initialize_environment(env, xilinx_path = "", build_tool = "ISE", version_number = ""):
    """
    Initialized an environment to contain all the xilinx build tools

    Args:
        env (Scons.Environment): An environment to add all the xilinx tools too
        xilinx_path (string): A user defined path to the xilinx base directory
            (leave empty to use the default system location)
        build_type (string): to use, valid build types are found with
            utils.get_xilinx_tool_types
            (leave empty to use "ISE")
        version_number (string): specify a version number to use for one of the
            tool chains: e.g.
                build_tool = ISE -> version number = 13.2
                build_tool = Vivado -> version number = 2013.1
            (leave empty for the latest version)

    Returns:
        SCons.Environment): with the xilinx tools added

    Raises:
        Configuration Error
    """
    xpath = utils.find_xilinx_path(xilinx_path, build_tool, version_number)

    #print "path to xilinx build tool: %s " % xpath
    env['XIL_SCRIPT_LOC'] = xpath
    env['XILINX_DSP'] = xpath
    env['XILINX_PLANAHEAD'] = os.path.join(xpath, "PlanAhead")
    env['XILINX'] = xpath

    if "USER" not in os.environ:
        os.environ["USER"] = getpass.getuser()
	if "XILINXD_LICENSE_FILE" in os.environ:
		#print "Found License File Location: %s" % os.environ["XILINXD_LICENSE_FILE"]
		env['ENV']['XILINXD_LICENSE_FILE'] = os.environ["XILINXD_LICENSE_FILE"]
	if "LM_LICENSE_FILE" in os.environ:
		env['ENV']['LM_LICENSE_FILE'] = os.environ["LM_LICENSE_FILE"]
    env['ENV']['USER'] = os.environ["USER"]
    env['ENV']['HOME'] = os.environ["HOME"]

    if 'LD_LIBRARY_PATH' not in env:
        env['LD_LIBRARY_PATH'] = ''
    #print "xilinx path: %s" % xilinx_path
    #print "build tool: %s" % build_tool
    #print "version number: %s" % version_number
    #print "xpath: %s" % xpath
    #This is used for the license file
	if os.name == "nt":
		env["ENV"]["USERNAME"] = env['ENV']["USER"]

    if build_tool.lower() == "ise" or build_tool.lower() == "planahead":
        env.AppendENVPath("PATH", os.path.join(xpath, "PlanAhead", "bin"))
        env.AppendENVPath("PATH", os.path.join(xpath, "ISE", "sysgen", "util"))
        if utils.is_64_bit():
            #64 bit machine
            if os.name == "nt":
                env.AppendENVPath("PATH", os.path.join(xpath, "common", "bin", "nt64"))
                env.AppendENVPath("PATH", os.path.join(xpath, "ISE", "bin", "nt64"))
                lib_path = os.path.join(xpath, "ISE", "lib", "nt64")
                env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
                lib_path = os.path.join(xpath, "common", "lib", "nt64")
                env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
                #print "LD_LIBRARY_PATH: %s" % str(env['LD_LIBRARY_PATH'])
            else:
                env.AppendENVPath("PATH", os.path.join(xpath, "common", "bin", "lin64"))
                env.AppendENVPath("PATH", os.path.join(xpath, "ISE", "bin", "lin64"))
                lib_path = os.path.join(xpath, "ISE", "lib", "lin64")
                env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
                lib_path = os.path.join(xpath, "common", "lib", "lin64")
                env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
                #print "LD_LIBRARY_PATH: %s" % str(env['LD_LIBRARY_PATH'])
        else:
            #32 bit machine
            env.AppendENVPath("PATH", os.path.join(xpath, "common", "bin", "lin"))
            env.AppendENVPath("PATH", os.path.join(xpath, "ISE", "bin", "lin"))
            lib_path = os.path.join(xpath, "ISE", "lib", "lin")
            env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
            lib_path = os.path.join(xpath, "common", "lib", "lin")
            env['LD_LIBRARY_PATH'] = string.join([lib_path, env['LD_LIBRARY_PATH']], os.pathsep)
            #print "LD_LIBRARY_PATH: %s" % str(env['LD_LIBRARY_PATH'])
    else:

        raise XilinxNotImplemented("Vivado is not implemented yet")

    return env

def get_xst_targets(env):
    """
    Returns a list of build target for the XST
    """
    config = utils.read_config(env)
    return xst_utils.get_ngc_filename(config, absolute = True)

def get_ngd_targets(env):
    config = utils.read_config(env)
    return ngd_utils.get_ngd_filename(config, absolute = True)

def get_map_targets(env):
    config = utils.read_config(env)
    return map_utils.get_map_filename(config, absolute = True)

def get_par_targets(env):
    config = utils.read_config(env)
    return par_utils.get_par_filename(config, absolute = True)

def get_trace_targets(env):
    config = utils.read_config(env)
    return trace_utils.get_trace_filename(config, absolute = True)

def get_bitgen_targets(env):
    config = utils.read_config(env)
    return bitgen_utils.get_bitgen_filename(config, absolute = True)

def get_coregen_targets(env):
    config = utils.read_config(env)
    return coregen_utils.get_target_files(config)

def clean_cores(env):
    """
    Cores take a terribly long time to build so unless the user obliterates
    everything with a 'clean_build' don't remove the generated cores unless
    the user explicitly asks for it

    Args:
        env (SCons Environment): Current environment

    Returns:
        Empty promises

    Raises:
        Hopes and Dreams
    """
    core_targets = get_coregen_targets(env)
    for core in core_targets:
        if os.path.exists(core):
            os.remove(core)
    return None

def clean_build(env):
    config = utils.read_config(env)
    base_dir = utils.get_project_base()
    build_dir = utils.get_build_directory(config, absolute = True)
    xmsgs_dir = os.path.join(base_dir, "_xmsgs")
    xlnx_auto = os.path.join(base_dir, "xlnx_auto_0_xdb")
    config_log = os.path.join(base_dir, "config.log")
    xdevice_details = os.path.join(base_dir, "xilinx_device_details.xml")
    map_report = "%s_map.xrpt" % config["top_module"]
    map_report = os.path.join(base_dir, map_report)

    par_usage = os.path.join(base_dir, "par_usage_statistics.html")
    par_report = "%s_par.xrpt" % config["top_module"]
    par_report = os.path.join(base_dir, par_report)

    #Coregen
    coregen_log = os.path.join(base_dir, "coregen.log")


    print "Removing Directories/Files:"

    if os.path.exists(build_dir):
        print "\t%s" % build_dir
        shutil.rmtree(build_dir)
    if os.path.exists(xmsgs_dir):
        print "\t%s" % xmsgs_dir
        shutil.rmtree(xmsgs_dir)
    if os.path.exists(xlnx_auto):
        print "\t%s" % xlnx_auto
        shutil.rmtree(xlnx_auto)
    if os.path.exists(config_log):
        print "\t%s" % config_log
        os.remove(config_log)
    if os.path.exists(xdevice_details):
        print "\t%s" % xdevice_details
        os.remove(xdevice_details)
    if os.path.exists(map_report):
        print "\t%s" % map_report
        os.remove(map_report)
    if os.path.exists(par_usage):
        print "\t%s" % par_usage
        os.remove(par_usage)
    if os.path.exists(par_report):
        print "\t%s" % par_report
        os.remove(par_report)
    if os.path.exists(coregen_log):
        print "\t%s" % coregen_log
        os.remove(coregen_log)



