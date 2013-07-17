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
import bitgen_utils

def _bitgen_emitter(target, source, env):
    return target, source

_bitgen_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$BITGEN_COM", "$BITGEN_COMSTR"),
        suffix = ".bit",
        src_suffix = "_par.ncd",
        emitter = _bitgen_emitter)

class BITGENBuilderWarning(SCons.Warnings.Warning):
    pass

class BITGENBuilderError(BITGENBuilderWarning):
    pass

def _detect(env):
    try:
        return env["BITGEN_COMMAND"]
    except KeyError:
        pass

    bitgen_command = env.WhereIs("bitgen")
    if bitgen_command:
        return bitgen_command

    raise SCons.Errors.StopError(
            BITGENBuilderError,
            "could not find bitgen command")
    return None

def generate(env):
    env["BITGEN_COMMAND"] = _detect(env)
    config = utils.read_config(env)
    bitgen_utils.create_bitgen_dir(config)
    bitgen_file = bitgen_utils.get_bitgen_filename(config)
    script_file = bitgen_utils.create_script(config)

    env.SetDefault(
            BITGEN_OUTFILE = bitgen_file,
            BITGEN_SCRIPT_NAME = script_file,
            BITGEN_COM = "$BITGEN_COMMAND -f $BITGEN_SCRIPT_NAME $BITGEN_SOURCES $BITGEN_OUTFILE",
            BITGEN_COMSTR = ""
    )
    env.AddMethod(BITGEN, "bitgen")
    return None

def exists(env):
    return _detect(env)

def BITGEN(env, target, source):
    """
    A pseudo-builder wrapper for Xilinx Bitgen
    """
    config = utils.read_config(env)
    env["BITGEN_SOURCES"] = source
    env["BITGEN_TARGETS"] = target
    _bitgen_builder.__call__(env, target, source)
    return bitgen_utils.get_bitgen_filename(config)

