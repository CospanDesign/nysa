//wishbone_arbitor.v
/*
Distributed under the MIT licesnse.
Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do 
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE.
*/


`timescale 1 ns/1 ps

module ${ARBITOR_NAME} (
  clk,
  rst,

  //master ports
${PORTS}

  //slave port
    s_we_o,
    s_cyc_o,
    s_stb_o,
    s_sel_o,
    s_ack_i,
    s_dat_o,
    s_dat_i,
    s_adr_o,
    s_int_i

);


//control signals
input               clk;
input               rst;

//wishbone slave signals
output              s_we_o;
output              s_stb_o;
output              s_cyc_o;
output  [3:0]       s_sel_o;
output  [31:0]      s_adr_o;
output  [31:0]      s_dat_o;

input   [31:0]      s_dat_i;
input               s_ack_i;
input               s_int_i;

parameter           MASTER_COUNT = ${NUM_MASTERS};
//wishbone master signals
${PORT_DEFINES}

//registers/wires
//this should be parameterized
reg [7:0]           master_select;
reg [7:0]           priority_select;


wire                master_we_o  [MASTER_COUNT:0];
wire                master_stb_o [MASTER_COUNT:0];
wire                master_cyc_o [MASTER_COUNT:0];
wire  [3:0]         master_sel_o [MASTER_COUNT:0];
wire  [31:0]        master_adr_o [MASTER_COUNT:0];
wire  [31:0]        master_dat_o [MASTER_COUNT:0];


${MASTER_SELECT}

//priority select
${PRIORITY_SELECT}



//slave assignments
assign  s_we_o  = (master_select != MASTER_NO_SEL) ? master_we_o[master_select]  : 0;
assign  s_stb_o = (master_select != MASTER_NO_SEL) ? master_stb_o[master_select] : 0;
assign  s_cyc_o = (master_select != MASTER_NO_SEL) ? master_cyc_o[master_select] : 0;
assign  s_sel_o = (master_select != MASTER_NO_SEL) ? master_sel_o[master_select] : 0;
assign  s_adr_o = (master_select != MASTER_NO_SEL) ? master_adr_o[master_select] : 0;
assign  s_dat_o = (master_select != MASTER_NO_SEL) ? master_dat_o[master_select] : 0;


${WRITE}

${STROBE}

${CYCLE}

${SELECT}

${ADDRESS}

${DATA}

${ASSIGN}

endmodule
