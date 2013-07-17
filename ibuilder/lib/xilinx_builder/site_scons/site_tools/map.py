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

Tool-specific initialization of the Xilinx MAP

"""
import SCons.Action
import SCons.Builder
import SCons.Util
import SCons.Tool

import os

import utils
import map_utils

def _map_emitter (target, source, env):
    return target, source

_map_builder = SCons.Builder.Builder(
    action = SCons.Action.Action("$MAP_COM", "$MAP_COMSTR"),
    suffix = ".ncd",
    src_suffix = ".ngd",
    emitter = _map_emitter)

class MAPBuilderWarning(SCons.Warnings.Warning):
    pass

class MAPBuilderError(MAPBuilderWarning):
    pass

def _detect(env):
    try:
        return env["MAP_COMMAND"]
    except KeyError:
        pass

    map_cmd = env.WhereIs("map")
    if map_cmd:
        return map_cmd

    raise SCons.Errors.StopError(
            MAPBuilderError,
            "Could not find map command")
    return None

def generate(env):
    """Add the map builder to the environment"""
    env["MAP_COMMAND"] = _detect(env)

    config = utils.read_config(env)
    map_utils.create_map_dir(config)
    map_file = map_utils.get_map_filename(config, absolute = True)
    flag_string = map_utils.get_build_flags_string(config)

    env.SetDefault(
        MAP_OUTFILE = map_file,
        MAP_FLAGSTRING = flag_string,
        MAP_COM = "$MAP_COMMAND $MAP_FLAGSTRING $MAP_SOURCES"
    )
    env.AddMethod(MAP, 'map')
    return None

def exists(env):
    return _detect(env)

def MAP(env, target, source):
    """
    A pseudo-builder wrapper for the Xilinx map
    """
    config = utils.read_config(env)

    env["MAP_SOURCES"] = source
    env["MAP_TARGETS"] = target

    _map_builder.__call__(env, target, source)

    return map_utils.get_map_filename(config)

