//wb_dma_reader.v
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
  DRT_ID:100

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:1

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:6

*/

`include "dma_reader_defines.v"

module wb_dma_reader #(
  parameter           BUFFER_SIZE = 8
)(
  input               clk,
  input               rst,

  //Add signals to control your device here
  output      [31:0]  debug,

  //Wishbone Bus Signals
  input               i_wbs_we,
  input               i_wbs_cyc,
  input       [3:0]   i_wbs_sel,
  input       [31:0]  i_wbs_dat,
  input               i_wbs_stb,
  output  reg         o_wbs_ack,
  output  reg [31:0]  o_wbs_dat,
  input       [31:0]  i_wbs_adr,
  output  reg         o_wbs_int,

  //master control signal for memory arbitration
  output              mem_o_we,
  output              mem_o_stb,
  output              mem_o_cyc,
  output      [3:0]   mem_o_sel,
  output      [31:0]  mem_o_adr,
  output      [31:0]  mem_o_dat,
  input       [31:0]  mem_i_dat,
  input               mem_i_ack,
  input               mem_i_int
);

//Local Parameters
localparam           REG_CONTROL        = 32'h00000000;
localparam           REG_STATUS         = 32'h00000001;
localparam           REG_MEM_0_BASE     = 32'h00000002;
localparam           REG_MEM_0_SIZE     = 32'h00000003;
localparam           REG_MEM_1_BASE     = 32'h00000004;
localparam           REG_MEM_1_SIZE     = 32'h00000005;

//Wires/Registers
reg         [31:0]  r_control;
wire        [31:0]  w_status;

wire                w_enable;
wire                w_enable_interrupt;
wire                w_control_reset;

reg         [31:0]  r_clock_divisor = 0;
reg         [31:0]  r_clock_count;
reg                 dclock;
reg                 r_dclock;

//Submodules

//Asynchronous Logic
//Synchronous Logic
reg                 r_flush_memory;
reg         [31:0]  r_memory_0_base;
reg         [31:0]  r_memory_0_size;
wire        [31:0]  w_memory_0_count;
reg                 r_memory_0_ready;
wire                w_memory_0_finished;
wire                w_memory_0_empty;

wire        [31:0]  w_default_mem_0_base;

reg         [31:0]  r_memory_1_base;
reg         [31:0]  r_memory_1_size;
wire        [31:0]  w_memory_1_count;
reg                 r_memory_1_ready;
wire                w_memory_1_finished;
wire                w_memory_1_empty;

wire        [31:0]  w_default_mem_1_base;

wire                w_write_finished;

//Ping Pong FIFO Write Side
wire        [23:0]  w_wfifo_size;
wire        [1:0]   w_wfifo_ready;
wire        [1:0]   w_wfifo_activate;
wire                w_wfifo_strobe;
wire        [31:0]  w_wfifo_data;

wire        [23:0]  w_rfifo_size;
wire                w_rfifo_ready;
wire                w_rfifo_activate;
wire                w_rfifo_strobe;
wire        [31:0]  w_rfifo_data;

//Submodules

/*--------------------------------------------------------------------------*/
//For testing purposes this will generate data, replace this interface
//with your interface
ppfifo_data_generator dg(
  .clk                  (clk                      ),
  .rst                  (rst |  w_control_reset   ),

  .i_enable             (w_enable                 ),

  .i_wr_rdy             (w_wfifo_ready            ),
  .o_wr_act             (w_wfifo_activate         ),
  .i_wr_size            (w_wfifo_size             ),
  .o_wr_stb             (w_wfifo_strobe           ),
  .o_wr_data            (w_wfifo_data             )
);
/*--------------------------------------------------------------------------*/

wb_ppfifo_2_mem p2m(

  .clk                  (clk                      ),
  .rst                  (rst |  w_control_reset   ),

  //Control
  .i_enable             (w_enable                 ),
  .i_flush              (r_flush_memory           ),

  .i_memory_0_base      (r_memory_0_base          ),
  .i_memory_0_size      (r_memory_0_size          ),
  .o_memory_0_count     (w_memory_0_count         ),
  .i_memory_0_ready     (r_memory_0_ready         ),
  .o_memory_0_finished  (w_memory_0_finished      ),
  .o_memory_0_empty     (w_memory_0_empty         ),

  .o_default_mem_0_base (w_default_mem_0_base     ),

  .i_memory_1_base      (r_memory_1_base          ),
  .i_memory_1_size      (r_memory_1_size          ),
  .o_memory_1_count     (w_memory_1_count         ),
  .i_memory_1_ready     (r_memory_1_ready         ),
  .o_memory_1_finished  (w_memory_1_finished      ),
  .o_memory_1_empty     (w_memory_1_empty         ),

  .o_default_mem_1_base (w_default_mem_1_base     ),

  .o_write_finished     (w_write_finished         ),

  //master control signal for memory arbitration
  .o_mem_we             (mem_o_we                 ),
  .o_mem_stb            (mem_o_stb                ),
  .o_mem_cyc            (mem_o_cyc                ),
  .o_mem_sel            (mem_o_sel                ),
  .o_mem_adr            (mem_o_adr                ),
  .o_mem_dat            (mem_o_dat                ),
  .i_mem_dat            (mem_i_dat                ),
  .i_mem_ack            (mem_i_ack                ),
  .i_mem_int            (mem_i_int                ),

  //Ping Pong FIFO Interface (Read)
  .i_ppfifo_rdy         (w_rfifo_ready            ),
  .o_ppfifo_act         (w_rfifo_activate         ),
  .i_ppfifo_size        (w_rfifo_size             ),
  .o_ppfifo_stb         (w_rfifo_strobe           ),
  .i_ppfifo_data        (w_rfifo_data             )
);

/*
* It might make sense to move the PPFIFO into a sub core. This is useful if
* thecore will be operating at a different frequency than other parts
*/

ppfifo #(
  .DATA_WIDTH           (32                       ),
                        //Size will always be 32 bits for mem
  .ADDRESS_WIDTH        (BUFFER_SIZE              )
                        //Parameterize the depth of the PPFIFO
) ping_pong (
  .reset                (rst |  w_control_reset   ),

  //write
  .write_clock          (clk                      ),
  .write_ready          (w_wfifo_ready            ),
  .write_activate       (w_wfifo_activate         ),
  .write_fifo_size      (w_wfifo_size             ),
  .write_strobe         (w_wfifo_strobe           ),
  .write_data           (w_wfifo_data             ),

  //read
  .read_clock           (clk                      ),
  .read_strobe          (w_rfifo_strobe           ),
  .read_ready           (w_rfifo_ready            ),
  .read_activate        (w_rfifo_activate         ),
  .read_count           (w_rfifo_size             ),
  .read_data            (w_rfifo_data             )
);

//Asynchronous Logic
assign  w_enable            = r_control[`CONTROL_ENABLE];
assign  w_enable_interrupt  = r_control[`CONTROL_ENABLE_INTERRUPT];
assign  w_control_reset     = r_control[`CONTROL_RESET];

//Verilogs default behavior will pad the upper bits with '0's
assign  w_status            = { 28'h00,
                                w_memory_1_empty,
                                w_memory_0_empty,
                                w_memory_1_finished,
                                w_memory_0_finished
                              };
assign  debug               = {
                                14'h0,
                                r_memory_1_ready,       //  16
                                r_memory_0_ready,       //  15
                                w_rfifo_strobe,         //  14
                                w_rfifo_activate,       //  13
                                w_rfifo_ready,          //  12
                                w_wfifo_strobe,         //  11
                                w_wfifo_activate,       //  10:9
                                w_wfifo_ready,          //  8:7
                                w_control_reset,        //  6
                                w_enable_interrupt,     //  5
                                w_enable,               //  4
                                w_memory_1_empty,       //  3
                                w_memory_0_empty,       //  2
                                w_memory_1_finished,    //  1
                                w_memory_0_finished     //  0
                              };
//Synchronous Logic
always @ (posedge clk) begin
  if (rst) begin
    o_wbs_dat             <=  32'h0;
    o_wbs_ack             <=  0;
    r_control             <=  0;

    //Default base, user can change this from the API
    r_memory_0_base       <=  w_default_mem_0_base;
    r_memory_1_base       <=  w_default_mem_1_base;

    //Nothing in the memory initially
    r_memory_0_size       <=  0;
    r_memory_1_size       <=  0;

    r_memory_0_ready      <=  0;
    r_memory_1_ready      <=  0;

  end
  else begin
    r_memory_0_ready      <=  0;
    r_memory_1_ready      <=  0;

    //when the master acks our ack, then put our ack down
    if (o_wbs_ack & ~i_wbs_stb)begin
      o_wbs_ack <= 0;
    end
    if (i_wbs_stb & i_wbs_cyc) begin
      //master is requesting something
      if (i_wbs_we) begin
        //write request
        case (i_wbs_adr)
          REG_CONTROL: begin
            r_control             <=  i_wbs_dat;
          end
          REG_STATUS: begin
            //Do nothing for a write to status
          end
          REG_MEM_0_BASE: begin
            r_memory_0_base       <=  i_wbs_dat;
          end
          REG_MEM_0_SIZE: begin
            r_memory_0_size       <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              r_memory_0_ready    <=  1;
            end
          end
          REG_MEM_1_BASE: begin
            r_memory_1_base       <=  i_wbs_dat;
          end
          REG_MEM_1_SIZE: begin
            r_memory_1_size       <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              r_memory_1_ready    <=  1;
            end
          end
          default: begin
          end
        endcase
      end
      else begin
        //Reading
        case (i_wbs_adr)
          REG_CONTROL: begin
            o_wbs_dat <=  r_control;
          end
          REG_STATUS: begin
            o_wbs_dat <=  w_status;
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
      o_wbs_ack <= 1;
    end
  end
end

//Interrupt control
always @ (posedge clk) begin
  if (rst) begin
    o_wbs_int           <=  0;
  end
  else if (w_enable) begin
    if (i_wbs_stb) begin
      o_wbs_int         <=  0;
    end
    else if (w_memory_0_finished || w_memory_1_finished) begin
      o_wbs_int         <=  1;
    end
    else if (!w_memory_0_finished && !w_memory_1_finished) begin
      o_wbs_int         <=  0;
    end
  end
  else begin
    o_wbs_int           <=  0;
  end
end

always @ (posedge clk) begin
  if (rst) begin
    r_flush_memory      <=  0;
  end
  else begin
  end
end


endmodule
