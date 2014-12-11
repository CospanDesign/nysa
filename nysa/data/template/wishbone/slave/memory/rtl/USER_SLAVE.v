//${NAME}.v
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

/* Log
  5/08/2013:
    -Added a test for ack on the read section so that there is no double reads
  4/16/2011:
    -implemented style i_: input, o_: output, r_: register, w_: wire
    -moved the entire port declaration within the module declaration
    -changed Parameters to localparams so the address cannot be inadvertently
      changed with a parameter statement outside the module
    -refactored the logs so they don't take up as much space
  10/29/2011:
    -added 'else' statement for reset
  10/23/2011:
    -fixed the wbs_ack_i to wbs_ack
    -added the default entires for read and write to illustrate different
      communication
    -added license
  9/10/2011:
    -removed duplicate wbs_dat_i
    -added the wbs_sel_i port
*/
/*
  Use this to tell Nysa how to populate the Device ROM table
  so that users can interact with your slave

  META DATA

  identification of your device 0 - 65536
  DRT_ID:${DRT_ID}

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:${DRT_FLAGS}

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:${DRT_SIZE}

*/


module ${NAME} (
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
  output  reg         o_wbs_int
  //output              o_wbs_int
);


//Local Parameters
localparam     ADDR_0  = 32'h00000000;
localparam     ADDR_1  = 32'h00000001;
localparam     ADDR_2  = 32'h00000002;

//Local Registers/Wires

//Submodules

//Asynchronous Logic
//Synchronous Logic

always @ (posedge clk) begin
  if (rst) begin
    o_wbs_dat <= 32'h0;
    o_wbs_ack <= 0;
    o_wbs_int <= 0;
  end

  else begin
    //when the master acks our ack, then put our ack down
    if (o_wbs_ack && ~i_wbs_stb)begin
      o_wbs_ack <= 0;
    end

    if (i_wbs_stb && i_wbs_cyc) begin
      //master is requesting somethign
      if (i_wbs_we) begin
        if (!o_wbs_ack) begin
          //write request
          case (i_wbs_adr)
            ADDR_0: begin
              //writing something to address 0
              //do something

              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
            end
            ADDR_1: begin
              //writing something to address 1
              //do something

              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
            end
            ADDR_2: begin
              //writing something to address 3
              //do something

              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
            end
            //add as many ADDR_X you need here
            default: begin
            end
          endcase
        end
      end

      else begin
        if (!o_wbs_ack) begin //Fix double reads
          //read request
          case (i_wbs_adr)
            ADDR_0: begin
              //reading something from address 0
              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("user read %h", ADDR_0);
              o_wbs_dat <= ADDR_0;
            end
            ADDR_1: begin
              //reading something from address 1
              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("user read %h", ADDR_1);
              o_wbs_dat <= ADDR_1;
            end
            ADDR_2: begin
              //reading soething from address 2
              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("user read %h", ADDR_2);
              o_wbs_dat <= ADDR_2;
            end
            //add as many ADDR_X you need here
            default: begin
            end
          endcase
        end
      end
      o_wbs_ack <= 1;
    end
  end
end

endmodule
