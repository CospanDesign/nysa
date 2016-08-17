//${SDB_NAME}.v
/*
Distributed under the MIT license.
Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)

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
  Set the Vendor ID (Hexidecimal 64-bit Number)
  SDB_VENDOR_ID:${SDB_VENDOR_ID}

  Set the Device ID (Hexcidecimal 32-bit Number)
  SDB_DEVICE_ID:${SDB_DEVICE_ID}

  Set the version of the Core XX.XXX.XXX Example: 01.000.000
  SDB_CORE_VERSION:${SDB_CORE_VERSION}

  Set the Device Name: 19 UNICODE characters
  SDB_NAME:${SDB_NAME}

  Set the class of the device (16 bits) Set as 0
  SDB_ABI_CLASS:${SDB_ABI_CLASS}

  Set the ABI Major Version: (8-bits)
  SDB_ABI_VERSION_MAJOR:${SDB_ABI_VERSION_MAJOR}

  Set the ABI Minor Version (8-bits)
  SDB_ABI_VERSION_MINOR:${SDB_ABI_VERSION_MINOR}

  Set the Module URL (63 Unicode Characters)
  SDB_MODULE_URL:${SDB_MODULE_URL}

  Set the date of module YYYY/MM/DD
  SDB_DATE:${SDB_DATE}

  Device is executable (True/False)
  SDB_EXECUTABLE:${SDB_EXECUTABLE}

  Device is readable (True/False)
  SDB_READABLE:${SDB_READABLE}

  Device is writeable (True/False)
  SDB_WRITEABLE:${SDB_WRITEABLE}

  Device Size: Number of Registers
  SDB_SIZE:${SDB_SIZE}
*/


module ${SDB_NAME} (
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
reg           [31:0]   r_test_data;
//Submodules
//Asynchronous Logic
//Synchronous Logic

always @ (posedge clk) begin
  if (rst) begin
    o_wbs_dat   <=  32'h0;
    o_wbs_ack   <=  0;
    o_wbs_int   <=  0;
    r_test_data <=  0;
  end

  else begin
    //when the master acks our ack, then put our ack down
    if (o_wbs_ack && ~i_wbs_stb)begin
      o_wbs_ack <= 0;
    end

    if (i_wbs_stb && i_wbs_cyc) begin
      //master is requesting somethign
      if (!o_wbs_ack) begin
        if (i_wbs_we) begin
          //write request
          case (i_wbs_adr)
            ADDR_0: begin
              //writing something to address 0
              //do something

              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
              r_test_data       <=  0;
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
        else begin
          //read request
          case (i_wbs_adr)
            ADDR_0: begin
              //reading something from address 0
              //NOTE THE FOLLOWING LINE IS AN EXAMPLE
              //  THIS IS WHAT THE USER WILL READ FROM ADDRESS 0
              $display("user read %h", ADDR_0);
              //o_wbs_dat <= ADDR_0;
              o_wbs_dat <=  r_test_data;
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
      o_wbs_ack <= 1;
    end
    end
  end
end

endmodule
