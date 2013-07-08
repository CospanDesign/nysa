//wb_gpio.v
/*
Distributed under the MIT license.
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
  8/31/2012
    -Changed some of the naming for clarity
	10/29/2011
		-added an 'else' statement that so either the
		reset HDL will be executed or the actual code
		not both
	10/23/2011
		-fixed the wbs_ack_i to o_wbs_ack
		-added the default entries for read and write
			to illustrate the method of communication
		-added license
	9/10/2011
		-removed the duplicate wbs_dat_i
		-added the wbs_sel_i port
*/

/*
	Use this to tell sycamore how to populate the Device ROM table
	so that users can interact with your slave

	META DATA

	identification of your device 0 - 65536
	DRT_ID:  1

	flags (read drt.txt in the slave/device_rom_table directory 1 means
	a standard device
	DRT_FLAGS:  1

	number of registers this should be equal to the nubmer of ???
	parameters
	DRT_SIZE:  5

	USER_PARAMETER: DEFAULT_INTERRUPT_MASK
	USER_PARAMETER: DEFAULT_INTERRUPT_EDGE

*/

module wb_gpio#(
  parameter DEFAULT_INTERRUPT_MASK = 0,
  parameter DEFAULT_INTERRUPT_EDGE = 0
  )(
  input               clk,
  input               rst,

  //Add signals to control your device here

  //Wishbone Bus Signals
  input               i_wbs_we,
  input               i_wbs_cyc,
  input       [3:0]   i_wbs_sel,
  input       [31:0]  i_wbs_dat,
  input               i_wbs_stb,
  output  reg         o_wbs_ack,
  output  reg [31:0]  o_wbs_dat,
  input       [31:0]  i_wbs_adr,

  //This interrupt can be controlled from this module or a submodule
  output  reg         o_wbs_int,

  input       [31:0]  gpio_in

);



localparam			GPIO			            =	32'h00000000;
localparam			GPIO_OUTPUT_ENABLE		=	32'h00000001;
localparam			INTERRUPTS		        =	32'h00000002;
localparam			INTERRUPT_ENABLE	    =	32'h00000003;
localparam			INTERRUPT_EDGE        =	32'h00000004;


//gpio registers
reg			[31:0]	gpio_direction;
wire    [31:0]  gpio;

//interrupt registers
reg			[31:0]	interrupts;
reg			[31:0]	interrupt_mask;
reg			[31:0]	interrupt_edge;
reg					    clear_interrupts;


endmodule
