//wb_console.v
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
	11/02/2011
		-changed the DRT ID to 6
*/

/*
	Use this to tell sycamore how to populate the Device ROM table
	so that users can interact with your slave

	META DATA

	identification of your device 0 - 65536
	DRT_ID:6

	flags (read drt.txt in the slave/device_rom_table directory 1 means
	a standard device
	DRT_FLAGS:1

	number of registers this should be equal to the nubmer of ADDR_???
	parameters
	DRT_SIZE:3

*/

`define CONTROL_ENABLE          0 
`define CONTROL_ENABLE_TIMEOUT  1

module wb_console (
	input               clk,
	input               rst,

	//Add signals to control your device here

  //wishbone slave signals
  input 				      i_wbs_we,
  input 				      i_wbs_stb,
  input 				      i_wbs_cyc,
  input		    [3:0]	  i_wbs_sel,
  input		    [31:0]	i_wbs_adr,
  input  		  [31:0]	i_wbs_dat,
  output reg  [31:0]	o_wbs_dat,
  output reg			    o_wbs_ack,
  output reg			    o_wbs_int,

  //master control signal for memory arbitration
	output reg			    o_fb_we,
	output reg			    o_fb_stb,
	output reg			    o_fb_cyc,
	output reg	[3:0]	  o_fb_sel,
	output reg	[31:0]	o_fb_adr,
	output reg	[31:0]	o_fb_dat,
	input		    [31:0]	i_fb_dat,
	input				        i_fb_ack,
	input				        i_fb_int,

  //master control signal for lcd arbitration
	output reg			    o_lcd_we,
	output reg			    o_lcd_stb,
	output reg			    o_lcd_cyc,
	output reg	[3:0]	  o_lcd_sel,
	output reg	[31:0]	o_lcd_adr,
	output reg	[31:0]	o_lcd_dat,
	input		    [31:0]	i_lcd_dat,
	input				        i_lcd_ack,
	input				        i_lcd_int
);


parameter			TIMEOUT				      =	32'd10;
//30 times a second
//parameter			TIMEOUT				    =	32'd1666666;
//60 times a second
//parameter			TIMEOUT				    =	32'd833333;

parameter			ADDR_CONTROL		    =	32'h00000000;
parameter			ADDR_TIMEOUT		    =	32'h00000001;
parameter			ADDR_UPDATE_RATE	  =	32'h00000002;
parameter			ADDR_SCREEN_WIDTH	  =	32'h00000003;
parameter			ADDR_SCREEN_HEIGHT	=	32'h00000004;
parameter			ADDR_FONT_ADDRESS	  =	32'h00000005;
parameter			ADDR_FRONT			    =	32'h00000006;
parameter			ADDR_BACK			      =	32'h00000007;


reg			    [31:0]	local_data;
reg			    [31:0]	timeout;

reg			    [31:0]	screen_width;
reg			    [31:0]	screen_height;

reg			    [31:0]	buffer_pointer;
reg			    [31:0]	front;
reg			    [31:0]	back;
reg			    [31:0]	font_address;

reg         [31:0]  control;

reg					        timeout_elapsed;

//flags
reg					        console_ready;

wire                enable_console;
wire                enable_timeout;

assign  enable_console  = control[`CONTROL_ENABLE];
assign  enable_timeout  = control[`CONTROL_ENABLE_TIMEOUT];

reg                 oneshot;



//blocks
always @ (posedge clk) begin
	if (rst) begin
		o_wbs_dat			      <= 32'h0;
		o_wbs_ack			      <= 0;
		o_wbs_int			      <= 0;

		local_data			    <= 32'h00000000;
		console_ready		    <= 0;
		timeout				      <= TIMEOUT;
    control             <=  0;

	end

	else begin
    control[`CONTROL_ENABLE]  <=  0;
		//when the master acks our ack, then put our ack down
		if (o_wbs_ack & ~ i_wbs_stb)begin
			o_wbs_ack <= 0;
		end

		if (i_wbs_stb & i_wbs_cyc) begin
			//master is requesting somethign
			if (i_wbs_we) begin
				//write request
				case (i_wbs_adr) 
					ADDR_CONTROL: begin
						//writing something to address 0
						//do something
	
						//NOTE THE FOLLOWING LINE IS AN EXAMPLE
						//	THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
            control   <=  i_wbs_dat;
						local_data <= i_wbs_dat;
					end
					ADDR_TIMEOUT: begin
						//writing something to address 1
						//do something
	
						//NOTE THE FOLLOWING LINE IS AN EXAMPLE
						//	THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
						$display("user wrote %h", i_wbs_dat);
						timeout			<= i_wbs_dat;
					end
					ADDR_UPDATE_RATE: begin
						//writing something to address 3
						//do something
	
						//NOTE THE FOLLOWING LINE IS AN EXAMPLE
						//	THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
						$display("user wrote %h", i_wbs_dat);
					end
					//add as many ADDR_X you need here
					default: begin
					end
				endcase
			end

			else begin 
				//read request
				case (i_wbs_adr)
					ADDR_CONTROL: begin
						//read the control and status flags
						$display("user read %h", ADDR_CONTROL);
            o_wbs_dat <=  control;
					end
					ADDR_TIMEOUT: begin
						//read the timeout value
						$display("user read %h", ADDR_TIMEOUT);
						o_wbs_dat <= timeout;
					end
					ADDR_UPDATE_RATE: begin
						//read the update rate
						$display("user read %h", ADDR_UPDATE_RATE);
						o_wbs_dat <= ADDR_UPDATE_RATE;
					end
					//add as many ADDR_X you need here
					default: begin
					end
				endcase
			end
			o_wbs_ack <= 1;
		end
	end
end


//wishbone master module
always @ (posedge clk) begin
	if (rst) begin
		o_fb_we		<= 0;
		o_fb_stb 	<= 0;
		o_fb_cyc 	<= 0;
		o_fb_sel 	<= 4'h0;
		o_fb_adr	<= 32'h00000000;
		o_fb_dat	<= 32'h00000000;
	end
	else begin
		if (timeout_elapsed) begin
			$display ("write to the memory");
		end
		if (fb_ack_i) begin
			$display ("got an ack!");
			o_fb_stb	<=  0;
			o_fb_cyc	<=  0;
      o_fb_we   <=  0;
		  o_fb_sel 	<=  4'h0;
		end
		if (enable_console) begin
			$display("enable a host write! of %h", local_data);
			o_fb_stb  <= 1;
			o_fb_cyc  <= 1;
			o_fb_sel  <= 4'b1111;
			o_fb_we	  <= 1;
			o_fb_adr  <= 0;
			o_fb_dat  <= 32'h1234567;  
		end
	end
end


//timeout
reg		[31:0]	timeout_count;
always @ (posedge clk) begin
	timeout_elapsed	<= 0;
	if (rst) begin
		timeout_count	<= 32'h00000000;
	end
	else begin
		if (enable_timeout) begin
			if (timeout_count > timeout) begin
				//reached the max, reset everything
				timeout_count 	<= 32'h00000000;
				timeout_elapsed	<= 1;
				$display ("timeout!");
			end
			else begin
				timeout_count <= timeout_count + 1;
			end
		end
		else begin
			timeout_count <= 32'h00000000;
		end
	end
end

endmodule
