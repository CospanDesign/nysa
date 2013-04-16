//wishbone_interconnect.v
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

/*
	11/08/2011
		fixed the wb_ack_o to be 0 when nothing is selected
*/

/* 
    Thanks Rudolf Usselmann yours was a better implementation than mine

    Copyright (C) 2000-2002
    Rudolf Usselmann
    www.asics.ws
    rudi@asics.ws
*/
`timescale 1ns/1ps

module wishbone_interconnect (
	clk,
	rst,

    m_we_i,
    m_cyc_i,
	m_sel_i,
    m_stb_i,
    m_ack_o,
    m_dat_i,
    m_dat_o,
    m_adr_i,
    m_int_o,

    //virtual slave master 0
    s0_we_o,
    s0_cyc_o,
	s0_sel_o,
    s0_stb_o,
    s0_ack_i,
    s0_dat_o,
    s0_dat_i,
    s0_adr_o,
    s0_int_i,

    //virtual slave master 0
    s1_we_o,
    s1_cyc_o,
	s1_sel_o,
    s1_stb_o,
    s1_ack_i,
    s1_dat_o,
    s1_dat_i,
    s1_adr_o,
    s1_int_i
);


parameter ADDR_0    =   8'h00;
parameter ADDR_1    =   8'h01;

parameter ADDR_FF	=	8'hFF;

//state

//control signals
input 				clk;
input 				rst;

//wishbone slave signals
input 				m_we_i;
input 				m_stb_i;
input 				m_cyc_i;
input		[3:0]	m_sel_i;
input		[31:0]	m_adr_i;
input  		[31:0]	m_dat_i;
output reg  [31:0]	m_dat_o = 32'h0;
output reg      	m_ack_o = 1'h0;
output	 			m_int_o;

output              s0_we_o;
output              s0_stb_o;
output              s0_cyc_o;
output		[3:0]	s0_sel_o;
output      [31:0]  s0_adr_o;
output      [31:0]  s0_dat_o;
input       [31:0]  s0_dat_i;
input               s0_ack_i;
input               s0_int_i;

output              s1_we_o;
output              s1_stb_o;
output              s1_cyc_o;
output		[3:0]	s1_sel_o;
output      [31:0]  s1_adr_o;
output      [31:0]  s1_dat_o;
input       [31:0]  s1_dat_i;
input               s1_ack_i;
input               s1_int_i;

/*
initial begin
    $monitor ("%t adr: %h, stb: %h, ack: %h", $time, m_adr_i, m_stb_i, m_ack_o);
end
*/

//this should be parameterized
wire [7:0]slave_select;
assign slave_select =   m_adr_i[31:24];


wire [31:0]	interrupts;


/*initial begin
    $monitor("%t, int: %h, s0_int_i: %h, s1_int_i: %h", $time, interrupts, s0_int_i, s1_int_i);
end
*/


//data
always @ (slave_select or s0_dat_i or s1_dat_i or interrupts) begin
    case (slave_select)
        ADDR_0: begin
            m_dat_o <= s0_dat_i;
        end
        ADDR_1: begin
            m_dat_o <= s1_dat_i;
        end
        default: begin
			  //$display("WBI: interrupt address selected");
            m_dat_o <= interrupts;
        end
    endcase
end

//ack
always @ (slave_select or s0_ack_i or s1_ack_i) begin
    case (slave_select)
        ADDR_0: begin
            m_ack_o <= s0_ack_i;
        end
        ADDR_1: begin
            m_ack_o <= s1_ack_i;
        end
		default: begin
            m_ack_o <= 1'h0;
        end
    endcase
end

//int
//set up the interrupts flags
assign interrupts[0]	= s0_int_i;
assign interrupts[1]	= s1_int_i;
//set all other interrupts to zero
assign interrupts[31:2]	= 0;

assign m_int_o	= (interrupts != 0);



assign s0_we_o    =  (slave_select == ADDR_0) ? m_we_i: 0;
assign s0_stb_o   =  (slave_select == ADDR_0) ? m_stb_i: 0;
assign s0_sel_o	  =  (slave_select == ADDR_0) ? m_sel_i: 0;
assign s0_cyc_o   =  (slave_select == ADDR_0) ? m_cyc_i: 0;
assign s0_adr_o   =  (slave_select == ADDR_0) ? {8'h0 , m_adr_i[23:0]}: 0;
assign s0_dat_o   =  (slave_select == ADDR_0) ? m_dat_i: 0;

assign s1_we_o    = (slave_select == ADDR_1) ? m_we_i: 0;
assign s1_stb_o   = (slave_select == ADDR_1) ? m_stb_i: 0;
assign s1_sel_o	  = (slave_select == ADDR_1) ? m_sel_i: 0;
assign s1_cyc_o   = (slave_select == ADDR_1) ? m_cyc_i: 0;
assign s1_adr_o   = (slave_select == ADDR_1) ? {8'h0 , m_adr_i[23:0]}: 0;
assign s1_dat_o   = (slave_select == ADDR_1) ? m_dat_i: 0;


endmodule
