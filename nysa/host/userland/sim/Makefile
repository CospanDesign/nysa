###############################################################################
# Copyright (c) 2013 Potential Ventures Ltd
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Potential Ventures Ltd nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL POTENTIAL VENTURES LTD BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################


#Change this to location of Cocotb
COCOTB_PATH=${COCOTB}
XILINX_PATH=${XILINX}
NYSA_PATH=${NYSA}



TOPLEVEL=top

PWD=$(shell pwd)
COMPILE_ARGS=-y$(XILINX_PATH)/ISE/verilog/src/unisims
COMPILE_ARGS+=-I$(PWD)/../rtl/dependencies -I$(PWD)/../rtl
COMPILE_ARGS+=-I$(PWD)/../rtl/bus/slave


VERILOG_SOURCES = $(XILINX_PATH)/ISE/verilog/src/glbl.v
VERILOG_SOURCES += $(shell find $(PWD)/../rtl/dependencies/ -name '*.v')
VERILOG_SOURCES += $(shell find $(PWD)/../rtl/bus/ -name '*.v')
VERILOG_SOURCES += ./top.v ./sim_interface.v

MODULE=test

include $(COCOTB_PATH)/makefiles/Makefile.inc
include $(COCOTB_PATH)/makefiles/Makefile.sim

clean_design:
	rm -rf obj
	rm *.pyc
	rm results.xml
	rm waveform.vcd

wave:
	gtkwave waveform.vcd &

