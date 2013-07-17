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

Tool-specific initialization of the Xilinx NGD Translator

"""
import SCons.Action
import SCons.Builder
import SCons.Util
import SCons.Tool

import os

import utils
import ngd_utils

def _ngd_emitter(target, source, env):
    return target, source


_ngd_builder = SCons.Builder.Builder(
        action = SCons.Action.Action('$NGD_COM', '$NGD_COMSTR'),
        suffix = ".ngd",
        src_suffix = ".xst",
        emitter = _ngd_emitter)

class NGDBuilderWarning(SCons.Warnings.Warning):
    pass

class NGDBuilderError(NGDBuilderWarning):
    pass

def _detect(env):
    try:
        return env["NGD_COMMAND"]
    except KeyError:
        pass

    ngd = env.WhereIs("ngdbuild")
    if ngd:
        return ngd

    raise SCons.Errors.StopError(
            NGDBuilderError,
            "Could not find ngdbuild command")
    return None

def generate(env):
    """Add the ngdbuild builder to the environment"""
    env["NGD_COMMAND"] = _detect(env)

    config = utils.read_config(env)
    ngd_utils.create_ngd_dir(config)
    ngd_file = ngd_utils.get_ngd_filename(config)
    flag_string = ngd_utils.get_build_flags_string(config)
    #print "Command string:"
    #print "\t%s %s %s %s" % (str(_detect(env)), flag_string, "in_file", ngd_file)
    env.SetDefault(
        NGD_OUTFILE = ngd_utils.get_ngd_filename(config),
        NGD_FLAGSTRING = ngd_utils.get_build_flags_string(config),
        NGD_COM = '$NGD_COMMAND $NGD_FLAGSTRING $NGD_SOURCES $NGD_TARGETS'
    )
    #env['BUILDER']['NGD'] = _ngd_builder
    env.AddMethod(NGD, 'ngd')
    return None

def exists(env):
    return _detect(env)

def NGD(env, target, source):
    """
    A pseudo-Builder wrapper for the NGD translate

    Args
        env (SCons Environment)
        target (list of strings) target files to build
        source (list of strings) source files to read in
    """
    #print "in NGD method"
    config = utils.read_config(env)
    #print "NGC File: %s" % str(source)
    env["NGD_SOURCES"] = source
    env["NGD_TARGETS"] = target
    _ngd_builder.__call__(env, target, source)
    return ngd_utils.get_ngd_filename(config)

