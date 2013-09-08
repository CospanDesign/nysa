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
import coregen_utils

def _coregen_emitter(target, source, env):
    config = utils.read_config(env)
    coregen_outfiles = coregen_utils.get_target_files(config)
    target = coregen_outfiles
    return target, source

_coregen_builder = SCons.Builder.Builder(
        action = SCons.Action.Action("$COREGEN_COM", "$COREGEN_COMSTR"),
        suffix = ".ngc",
        src_suffix = ".xco",
        emitter = _coregen_emitter)

class COREGENBuilderWarning(SCons.Warnings.Warning):
    pass

class COREGENBuilderError(COREGENBuilderWarning):
    pass

def _detect(env):
    try:
        return env["COREGEN_COMMAND"]
    except KeyError:
        pass

    coregen_command = env.WhereIs("coregen")
    if coregen_command:
        return coregen_command

    raise SCons.Errors.StopError(
            COREGENBuilderError,
            "could not find coregen command"
            )

    return None

def generate(env):
    env["COREGEN_COMMAND"] = _detect(env)
    config = utils.read_config(env)
    coregen_utils.create_coregen_dir(config)
    coregen_utils.create_coregen_temp_dir(config)
    coregen_utils.create_project_file(config)

    project_path = coregen_utils.get_project_file(config, absolute = True)

    coregen_outfiles = coregen_utils.get_target_files(config)
    #Need to get targets

    env.SetDefault(
            COREGEN_OUTFILES = coregen_outfiles,
            COREGEN_PROJECT = project_path,
            COREGEN_COM = "$COREGEN_COMMAND -b $COREGEN_SCRIPT -p $COREGEN_PROJECT -r"
            )
    env.AddMethod(COREGEN, "coregen")
    return None

def exists(env):
    return _detect(env)


def COREGEN(env, target, source):
    """
    A pseudo-builder wrapper for Xilinx coregen
    """
    config = utils.read_config(env)
    source = coregen_utils.get_new_coregen_file_list(config)
    env["COREGEN_SOURCES"] = source
    env["COREGEN_TARGETS"] = target
    for s in source:
        env["COREGEN_SCRIPT"] = s
        _coregen_builder.__call__(env, target, s)
    return coregen_utils.get_target_files(config)

