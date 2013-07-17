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

Tool-specific initialization of the Xilinx Place and Router

"""
import SCons.Action
import SCons.Builder
import SCons.Util
import SCons.Tool

import os

import utils
import trace_utils

def _trace_emitter(target, source, env):
    return target, source

_trace_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$TRACE_COM", "$TRACE_COMSTR"),
        suffix = ".twr",
        src_suffix = "_par.ncd",
        emitter = _trace_emitter)

class TRACEBuilderWarning(SCons.Warnings.Warning):
    pass

class TRACEBuilderError(TRACEBuilderWarning):
    pass

def _detect(env):
    try:
        return env["TRACE_COMMAND"]
    except KeyError:
        pass

    trace_cmd = env.WhereIs("trce")
    if trace_cmd:
        return trace_cmd

    raise SCons.Errors.StopError(
            TRACEBuilderError,
            "could not find trce command"
    )
    return None

def generate(env):
    env["TRACE_COMMAND"] = _detect(env)
    config = utils.read_config(env)
    trace_utils.create_trace_dir(config)
    trace_file = trace_utils.get_trace_filename(config)
    flag_string = trace_utils.get_build_flags_string(config)

    env.SetDefault(
            TRACE_OUTFILE = trace_file,
            TRACE_FLAGSTRING = flag_string,
            TRACE_COM = "$TRACE_COMMAND $TRACE_FLAGSTRING $TRACE_SOURCES",
            TRACE_COMSTR = ""
    )
    env.AddMethod(TRACE, 'trace')
    return None

def exists(env):
    return _detect(env)

def TRACE(env, target, source):
    """
    A pseudo-builder wrapper for Xilinx trace
    """
    config = utils.read_config(env)
    env["TRACE_SOURCES"] = source
    env["TRACE_TARGETS"] = target

    _trace_builder.__call__(env, target, source)
    return trace_utils.get_trace_filename(config)

