//wb_sf_camera.v
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
  DRT_ID:(1,)

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:(1,)

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:(3,)

*/

`include "sf_camera_defines.v"

module wb_sf_camera (
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
  //output              o_wbs_int

  //master control signal for memory arbitration
  output              o_mem_we,
  output              o_mem_stb,
  output              o_mem_cyc,
  output      [3:0]   o_mem_sel,
  output      [31:0]  o_mem_adr,
  output      [31:0]  o_mem_dat,
  input       [31:0]  i_mem_dat,
  input               i_mem_ack,
  input               i_mem_int
);


//Local Parameters
localparam           CONTROL            = 32'h00000000;
localparam           STATUS             = 32'h00000001;

localparam           REG_MEM_0_BASE     = 32'h00000004;
localparam           REG_MEM_0_SIZE     = 32'h00000005;
localparam           REG_MEM_1_BASE     = 32'h00000006;
localparam           REG_MEM_1_SIZE     = 32'h00000007;



//Local Registers/Wires

//Control
reg         [31:0]  control;
wire        [31:0]  status;
reg         [31:0]  clock_divider = 1;

wire                w_enable_dma;

//Get the Memory write controller
//nysa/cbuilder/verilog/wishbone/wb_ppfifo_2_mem/sim/test_wb_ppfifo_2_mem.v

reg         [31:0]  r_memory_0_base;
reg         [31:0]  r_memory_0_size;
wire        [31:0]  w_memory_0_count;
reg                 r_memory_0_new_data;
wire                w_memory_0_empty;

wire        [31:0]  w_default_mem_0_base;

reg         [31:0]  r_memory_1_base;
reg         [31:0]  r_memory_1_size;
wire        [31:0]  w_memory_1_count;
reg                 r_memory_1_new_data;
wire                w_memory_1_empty;

wire        [31:0]  w_default_mem_1_base;

wire                w_write_finished;

wire                w_rfifo_ready;
wire                w_rfifo_activate;
wire                w_rfifo_strobe;
wire        [31:0]  w_rfifo_data;
wire        [23:0]  w_rfifo_size;


//Submodules
wb_ppfifo_2_mem p2m(

  .clk                  (clk                      ),
  .rst                  (rst                      ),

  //Control
  .i_enable             (w_enable_dma             ),

  .i_memory_0_base      (r_memory_0_base          ),
  .i_memory_0_size      (r_memory_0_size          ),
  .o_memory_0_count     (w_memory_0_count         ),
  .i_memory_0_new_data  (r_memory_0_new_data      ),
  .o_memory_0_empty     (w_memory_0_empty         ),

  .o_default_mem_0_base (w_default_mem_0_base     ),

  .i_memory_1_base      (r_memory_1_base          ),
  .i_memory_1_size      (r_memory_1_size          ),
  .o_memory_1_count     (w_memory_1_count         ),
  .i_memory_1_new_data  (r_memory_1_new_data      ),
  .o_memory_1_empty     (w_memory_1_empty         ),

  .o_default_mem_1_base (w_default_mem_1_base     ),

  .o_write_finished     (w_write_finished         ),

  //master control signal for memory arbitration
  .o_mem_we             (o_mem_we                 ),
  .o_mem_stb            (o_mem_stb                ),
  .o_mem_cyc            (o_mem_cyc                ),
  .o_mem_sel            (o_mem_sel                ),
  .o_mem_adr            (o_mem_adr                ),
  .o_mem_dat            (o_mem_dat                ),
  .i_mem_dat            (i_mem_dat                ),
  .i_mem_ack            (i_mem_ack                ),
  .i_mem_int            (i_mem_int                ),

  //Ping Pong FIFO Interface (Read)
  .i_ppfifo_rdy         (w_rfifo_ready            ),
  .o_ppfifo_act         (w_rfifo_activate         ),
  .i_ppfifo_size        (w_rfifo_size             ),
  .o_ppfifo_stb         (w_rfifo_strobe           ),
  .i_ppfifo_data        (w_rfifo_data             )
);

sf_camera camera(
  .clk                  (clk                      ),
  .rst                  (rst                      ),

  //Memory Enable
  .o_enable_dma         (w_enable_dma             ),
  //Ping Pong FIFO Signals
  .o_rfifo_ready        (w_rfifo_ready            ),
  .i_rfifo_activate     (w_rfifo_activate         ),
  .i_rfifo_strobe       (w_rfifo_strobe           ),
  .o_rfifo_data         (w_rfifo_data             ),
  .o_rfifo_size         (w_rfifo_size             )
);




//Submodules

//Asynchronous Logic
//Synchronous Logic

always @ (posedge clk) begin
  if (rst) begin
    o_wbs_dat <= 32'h0;
    o_wbs_ack <= 0;
    o_wbs_int <= 0;

    r_memory_0_base <=  w_default_mem_0_base;
    r_memory_1_base <=  w_default_mem_1_base;

    //Nothing in the memory initially
    r_memory_0_size <=  0;
    r_memory_1_size <=  0;

    r_memory_0_new_data <=  0;
    r_memory_1_new_data <=  0;

  end

  else begin
    //when the master acks our ack, then put our ack down
    if (o_wbs_ack && ~i_wbs_stb)begin
      o_wbs_ack <= 0;
    end

    if (i_wbs_stb && i_wbs_cyc) begin
      //master is requesting somethign
      if (i_wbs_we) begin
        //write request
        case (i_wbs_adr)
          CONTROL: begin
            $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
          end
          STATUS: begin
            $display("ADDR: %h user wrote %h", i_wbs_adr, i_wbs_dat);
          end


          REG_MEM_0_BASE: begin
            r_memory_0_base       <=  i_wbs_dat;
          end
          REG_MEM_0_SIZE: begin
            r_memory_0_size       <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              r_memory_0_new_data <=  1;
            end
          end
          REG_MEM_1_BASE: begin
            r_memory_1_base       <=  i_wbs_dat;
          end
          REG_MEM_1_SIZE: begin
            r_memory_1_size       <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              r_memory_1_new_data <=  1;
            end
          end

          default: begin
          end
        endcase
      end

      else begin
        if (!o_wbs_ack) begin //Fix double reads
          //read request
          case (i_wbs_adr)
            CONTROL: begin
              $display("user read %h", CONTROL);
              o_wbs_dat <= CONTROL;
            end
            STATUS: begin
              $display("user read %h", STATUS);
              o_wbs_dat <=  {30'h00000000, w_memory_1_empty, w_memory_0_empty};
            end

            REG_MEM_0_BASE: begin
              o_wbs_dat <=  r_memory_0_base;
            end
            REG_MEM_0_SIZE: begin
              o_wbs_dat <=  w_memory_0_count;
            end
            REG_MEM_1_BASE: begin
              o_wbs_dat <=  r_memory_1_base;
            end
            REG_MEM_1_SIZE: begin
              o_wbs_dat <=  w_memory_1_count;
            end
            default: begin
              o_wbs_dat <=  32'h00;
            end
          endcase
        end
      end
      o_wbs_ack <= 1;
    end
  end
end

//Wishbone Memory Master
endmodule
