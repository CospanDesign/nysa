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



"""SConst.Tool.xst

Tool-specific initialization of the Xilinx XST synthesizer

"""
import SCons.Action
import SCons.Builder
import SCons.Util
import SCons.Tool

import os

import utils
import xst_utils
import coregen_utils




def _xst_emitter(target, source, env):
    #Sources are okay but I need to tell SCons all the stuff this thing
    #makes
    config = utils.read_config(env)
    coregen_outfiles = coregen_utils.get_target_files(config)
    if not SCons.Util.is_List(source):
        source = [source]

    if len(coregen_outfiles) > 0:
        source.append(coregen_outfiles)
    #print "source: %s" % source

    #Targets:
    #   .lso file
    #   .prj file
    #   .ngr file
    #   .ngc file (This may already be there)
    #   .xrpt file
    #   .xst file
    #target.append(xst_utils.get_xst_dir(config))



    return target, source

_xst_builder = SCons.Builder.Builder(
        action = SCons.Action.Action('$XST_COM', '$XST_COMSTR'),
        suffix = ".ngc",
        src_suffix = ".xst",
        #single_source = 1,
        emitter = _xst_emitter)

class XSTBuilderWarning(SCons.Warnings.Warning):
    pass

class XSTBuilderError(XSTBuilderWarning):
    pass

def _detect(env):
    try:
        return env["XST_COMMAND"]
    except KeyError:
        pass

    xst = env.WhereIs("xst")
    if xst:
        return xst

    raise SCons.Errors.StopError(
            XSTBuilderError,
            "Could not find XST")
    return None

def generate(env):
    """add the correct xst builder to the environement"""
    #Everything I need should be within the env
    #print "In generate function"
    env["XST_COMMAND"] = _detect(env)
    #get the configuration file name
    #fn = env["CONFIG_FILE"]
    #if os.path.exists(fn):
    #    #if the configuration file name doesn't exists then
    #    #maybe it is at the base directory of the project
    #    fn = os.path.join(utils.get_project_base(), fn)

    config = utils.read_config(env)
    xst_utils.create_xst_project_file(config)
    script_filename = xst_utils.create_xst_script(config)
    report_filename = xst_utils.get_report_filename(config)
    ngc_filename = xst_utils.get_ngc_filename(config)

    env.SetDefault(
        XST_REPORT_FILE = report_filename,
        XST_SCRIPT_FILE = script_filename,
        XST_NGC_FILE  = ngc_filename,

        #XST_COM = '$XST_COMMAND -intstyle ise -ifn "$XST_SCRIPT_FILE" -ofn "$XST_REPORT_FILE"',
        XST_COM = '$XST_COMMAND -ifn "$XST_SCRIPT_FILE" -ofn "$XST_REPORT_FILE"',
        XST_COMSTR = ""
    )

    #print "Script Filename: %s" % script_filename
    #print "Report Filename: %s" % report_filename
    #print "NGC Filename: %s" % ngc_filename



    env.AddMethod(XST, 'xst')
    return None

def exists(env):
    """Make sure xst exists in the environment"""
    return _detect(env)


def XST(env, target, source):
    """
    A pseudo-Builder wrapper for the XST synthesizer

    Reads the config file
    Creates the XST Project file (containing all the verilog)
    Creates the XST Script file (containing all of the commands)
    Executes the build

    Args:
        env (SCons Environment)
        target (list of strings)
        source (list of strings) 

    Returns:
        The output file list

    Raises:
        XSTBuilderWarning
        XSTBuilderError
    """
    #OKAY MAYBE I DIDN'T NEED A PSUEDO-BUILDER
    config = utils.read_config(env)
    _xst_builder.__call__(env, env["XST_NGC_FILE"], config["verilog"])
    return [xst_utils.get_ngc_filename(config)]

    


