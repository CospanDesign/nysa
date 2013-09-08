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

  output  reg [31:0]  gpio_out,
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


genvar i;
generate
  for (i = 0; i < 32; i = i + 1) begin : tsbuf
    assign gpio[i] = gpio_direction[i] ? gpio_out[i] : gpio_in[i];
  end
endgenerate

//blocks
always @ (posedge clk) begin

	clear_interrupts 	    <= 0;

	if (rst) begin
		o_wbs_dat	          <= 32'h00000000;
		o_wbs_ack	          <= 0;

		//reset gpio's
		gpio_out			      <= 32'h00000000;
		gpio_direction			<= 32'h00000000;


		//reset interrupts
		interrupt_mask		  <= DEFAULT_INTERRUPT_MASK;
		interrupt_edge		  <= DEFAULT_INTERRUPT_EDGE;
	end

	else begin
		//when the master acks our ack, then put our ack down
		if (o_wbs_ack & ~ i_wbs_stb)begin
			o_wbs_ack <= 0;
		end

		if (i_wbs_stb & i_wbs_cyc) begin
			//master is requesting somethign
			if (i_wbs_we) begin
				//write request
				case (i_wbs_adr) 
					GPIO: begin
						$display("user wrote %h", i_wbs_dat);
						gpio_out	<= i_wbs_dat & gpio_direction;
					end
					GPIO_OUTPUT_ENABLE: begin
						$display("%h ->gpio_direction", i_wbs_dat);
						gpio_direction	<= i_wbs_dat;
					end
					INTERRUPTS: begin
						$display("trying to write %h to interrupts?!", i_wbs_dat);
						//can't write to the interrupt
					end
					INTERRUPT_ENABLE: begin
						$display("%h -> interrupt enable", i_wbs_dat);
						interrupt_mask	<= i_wbs_dat;
					end
					INTERRUPT_EDGE: begin
						$display("%h -> interrupt_edge", i_wbs_dat);
						interrupt_edge	<= i_wbs_dat;
					end
					default: begin
					end
				endcase
			end

			else begin 
				//read request
				case (i_wbs_adr)
					GPIO: begin
						$display("user read %h", i_wbs_adr);
						o_wbs_dat <= gpio;
					end
					GPIO_OUTPUT_ENABLE: begin
						$display("user read %h", i_wbs_adr);
						o_wbs_dat <= gpio_direction;
					end
					INTERRUPTS: begin
						$display("user read %h", i_wbs_adr);
						o_wbs_dat 			<= interrupts;
						clear_interrupts	<= 1;
					end
					INTERRUPT_ENABLE: begin
						$display("user read %h", i_wbs_adr);
						o_wbs_dat			<= interrupt_mask;
					end
					INTERRUPT_EDGE: begin
						$display("user read %h", i_wbs_adr);
						o_wbs_dat			<= interrupt_edge;
					end
					default: begin
					end
				endcase
			end
			o_wbs_ack <= 1;
		end
	end
end

//interrupts
reg	[31:0]	prev_gpio_in;

//this is the change
wire [31:0]	gpio_edge;
assign gpio_edge	= prev_gpio_in ^ gpio_in;

/*
initial begin
	$monitor ("%t, interrupts: %h, mask: %h, edge: %h, gpio_edge: %h", $time, interrupts, interrupt_mask, interrupt_edge, gpio_edge);
end
*/


always @ (posedge clk) begin

	if (rst) begin
		interrupts	<= 32'h00000000;
		o_wbs_int	<= 0;
	end
	else begin
		if (clear_interrupts) begin
			interrupts <= 32'h00000000;
		end
		else begin
			//check to see if there was a negative or postive edge that occured
			interrupts	<= interrupt_mask & (interrupt_edge ^~ gpio_edge);
		end
		if (interrupts != 0) begin
			//tell the master that we have interrupts
//			$display ("found an interrupt in the slave");
			o_wbs_int	<= 1;
		end
		else begin
			o_wbs_int	<= 0;
		end
	end
	prev_gpio_in	<= gpio_in;
end

endmodule
