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
import par_utils

def _par_emitter(target, source, env):
    return target, source

_par_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$PAR_COM", "$PAR_COMSTR"),
        suffix = "_par.ncd",
        src_suffix = ".ncd",
        emitter = _par_emitter)

class PARBuilderWarning(SCons.Warnings.Warning):
    pass

class PARBuilderError(PARBuilderWarning):
    pass

def _detect(env):
    try:
        return env["PAR_COMMAND"]
    except KeyError:
        pass

    par_cmd = env.WhereIs("par")
    if par_cmd:
        return par_cmd

    raise SCons.Errors.StopError(
            PARBuilderError,
            "could not find par command")
    return None

def generate(env):
    env["PAR_COMMAND"] = _detect(env)

    config = utils.read_config(env)
    par_utils.create_par_dir(config)
    par_file = par_utils.get_par_filename(config)
    flag_string = par_utils.get_build_flags_string(config)

    env.SetDefault(
        PAR_OUTFILE = par_file,
        PAR_FLAGSTRING = flag_string,
        PAR_COM = "$PAR_COMMAND $PAR_FLAGSTRING $PAR_SOURCES $PAR_TARGETS"
    )
    env.AddMethod(PAR, 'par')
    return None


def exists(env):
    return _detect(env)

def PAR(env, target, source):
    """
    A pseudo-builder wrapper for the Xilinx par
    """
    config = utils.read_config(env)
    env["PAR_SOURCES"] = source
    env["PAR_TARGETS"] = target

    _par_builder.__call__(env, target, source)

    return par_utils.get_par_filename(config)
