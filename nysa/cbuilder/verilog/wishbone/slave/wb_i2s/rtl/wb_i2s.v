//wb_i2s.v
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
  Use this to tell Nysa how to populate the Device ROM table
  so that users can interact with your slave

  META DATA

  identification of your device 0 - 65536
  DRT_ID:  11

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:  1

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:  8

*/

`define DEFAULT_MEMORY_TIMEOUT  300

`include "project_defines.v"
`include "i2s_defines.v"
`timescale 1 ns/1 ps

`define DEFAULT_CLOCK_DIVISOR (`CLOCK_RATE / (`AUDIO_RATE * `AUDIO_BITS * `AUDIO_CHANNELS)) / 2

module wb_i2s (

  input               clk,
  input               rst,

  //wishbone slave signals
  input               i_wbs_we,
  input               i_wbs_stb,
  input               i_wbs_cyc,
  input       [3:0]   i_wbs_sel,
  input       [31:0]  i_wbs_adr,
  input       [31:0]  i_wbs_dat,
  output reg  [31:0]  o_wbs_dat,
  output reg          o_wbs_ack,
  output reg          o_wbs_int,

  //master control signal for memory arbitration
  output              mem_o_we,
  output              mem_o_stb,
  output              mem_o_cyc,
  output      [3:0]   mem_o_sel,
  output      [31:0]  mem_o_adr,
  output      [31:0]  mem_o_dat,
  input       [31:0]  mem_i_dat,
  input               mem_i_ack,
  input               mem_i_int,

  //status
  output              writer_starved,

  //i2s signals
  output              phy_mclock,
  output              phy_clock,
  output              phy_data,
  output              phy_lr,

  output      [31:0]  debug

);


localparam           REG_CONTROL        = 32'h00000000;
localparam           REG_STATUS         = 32'h00000001;
localparam           REG_CLOCK_RATE     = 32'h00000002;
localparam           REG_CLOCK_DIVIDER  = 32'h00000003;
localparam           REG_MEM_0_BASE     = 32'h00000004;
localparam           REG_MEM_0_SIZE     = 32'h00000005;
localparam           REG_MEM_1_BASE     = 32'h00000006;
localparam           REG_MEM_1_SIZE     = 32'h00000007;

//Reg/Wire
wire                timeout_elapsed;
reg                 timeout_enable;
reg         [31:0]  timeout_count;
reg         [31:0]  timeout_value;

reg                 enable_mem_read;

reg                 memory_data_strobe;
reg                 enable_strobe;


reg         [31:0]  control;
wire        [31:0]  status;
reg         [31:0]  clock_divider = 1;


reg         [23:0]  request_count;

reg                 memory_ready;
reg                 active_bank;

//Mem 2 PPFIFO
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

wire                w_read_finished;

//control
wire                enable;
wire                enable_interrupt;
wire                post_fifo_wave_en;
wire                pre_fifo_wave_en;

//status

wire        [23:0]  wfifo_size;
reg         [23:0]  write_count;
reg         [23:0]  memory_write_count;
reg         [23:0]  memory_write_size;

wire        [1:0]   wfifo_ready;
wire        [1:0]   wfifo_activate;
wire                wfifo_strobe;
wire        [31:0]  wfifo_data;

reg         [3:0]   state;


i2s_controller controller (
  .rst               (rst               ),
  .clk               (clk               ),

  .enable            (enable            ),
  .post_fifo_wave_en (post_fifo_wave_en ),

  .clock_divider     (clock_divider     ),

  .wfifo_size        (wfifo_size        ),
  .wfifo_ready       (wfifo_ready       ),
  .wfifo_activate    (wfifo_activate    ),
  .wfifo_strobe      (wfifo_strobe      ),
  .wfifo_data        (wfifo_data        ),


  .i2s_mclock        (phy_mclock        ),
  .i2s_clock         (phy_clock         ),
  .i2s_data          (phy_data          ),
  .i2s_lr            (phy_lr            )
);

wb_mem_2_ppfifo m2p(

  .clk                  (clk                      ),
  .rst                  (rst                      ),
  .debug                (debug                    ),

  //Control
  .i_enable             (enable                   ),

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

  .o_read_finished      (w_read_finished          ),

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

  //Ping Pong FIFO Interface
  .i_ppfifo_rdy         (wfifo_ready              ),
  .o_ppfifo_act         (wfifo_activate           ),
  .i_ppfifo_size        (wfifo_size               ),
  .o_ppfifo_stb         (wfifo_strobe             ),
  .o_ppfifo_data        (wfifo_data               )
);




//Asynchronous Logic
assign        enable                = control[`CONTROL_ENABLE];
assign        enable_interrupt      = control[`CONTROL_ENABLE_INTERRUPT];
assign        post_fifo_wave_en     = control[`CONTROL_POST_FIFO_WAVE];
assign        pre_fifo_wave_en      = control[`CONTROL_PRE_FIFO_WAVE];

assign        status[`STATUS_MEMORY_0_EMPTY]  = w_memory_0_empty;
assign        status[`STATUS_MEMORY_1_EMPTY]  = w_memory_1_empty;
assign        status[31:2]          = 0;

//assign        debug[1:0]            = wfifo_ready;
//assign        debug[3:2]            = wfifo_activate;
//assign        debug[4]              = wfifo_strobe;
//assign        debug[5]              = wfifo_data[31];
//assign        debug[31:16]          = wfifo_data[23:8];

//blocks
always @ (posedge clk) begin
  if (rst) begin
    o_wbs_dat       <=  32'h0;
    o_wbs_ack       <=  0;
    timeout_enable  <=  0;
    timeout_value   <=  `DEFAULT_MEMORY_TIMEOUT;

    control         <=  0;

    //Default base, user can change this from the API
    r_memory_0_base <=  w_default_mem_0_base;
    r_memory_1_base <=  w_default_mem_1_base;

    //Nothing in the memory initially
    r_memory_0_size <=  0;
    r_memory_1_size <=  0;

    r_memory_0_new_data <=  0;
    r_memory_1_new_data <=  0;


    clock_divider   <=  `DEFAULT_CLOCK_DIVISOR;
  end

  else begin

    r_memory_0_new_data <=  0;
    r_memory_1_new_data <=  0;


    //when the master acks our ack, then put our ack down
    if (o_wbs_ack & ~ i_wbs_stb)begin
      o_wbs_ack <= 0;
    end

    if (i_wbs_stb & i_wbs_cyc) begin
      //master is requesting somethign
      if (i_wbs_we) begin
        //write request
        case (i_wbs_adr)
          REG_CONTROL: begin
            control           <=  i_wbs_dat;
            if (i_wbs_dat[`CONTROL_ENABLE]) begin
              $display ("-----------------------------------------------------------");
              $display ("WB_I2S: Core Enable");
              $display ("-----------------------------------------------------------");
            end
          end
          REG_CLOCK_DIVIDER: begin
            clock_divider     <=  i_wbs_dat;
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
        //read request
        case (i_wbs_adr)
          REG_CONTROL: begin
            o_wbs_dat <= control;
          end
          REG_STATUS: begin
            o_wbs_dat <= status;
          end
          REG_CLOCK_RATE: begin
            o_wbs_dat <= `CLOCK_RATE;
          end
          REG_CLOCK_DIVIDER: begin
            o_wbs_dat <=  clock_divider;
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
          //add as many ADDR_X you need here
          default: begin
            o_wbs_dat <=  32'h00;
          end
        endcase
      end
      o_wbs_ack <= 1;
    end
  end
end

//initerrupt controller
always @ (posedge clk) begin
  if (rst) begin
    o_wbs_int <=  0;
  end
  else if (enable) begin
    if (!w_memory_0_empty && !w_memory_1_empty) begin
      o_wbs_int <=  0;
    end
    if (i_wbs_stb) begin
      //de-assert the interrupt on wbs transactions so I can launch another
      //interrupt when the wbs is de-asserted
      o_wbs_int <=  0;
    end
    else if (w_memory_0_empty || w_memory_1_empty) begin
      o_wbs_int <=  1;
    end
  end
  else begin
    //if we're not enable de-assert interrupt
    o_wbs_int <=  0;
  end
end

always @ (posedge clk) begin
  if (wfifo_strobe) begin
    $display ("\tI2S MEM CONTROLLER: Wrote: %h: Request: %h", wfifo_data, wfifo_size);
  end
end
endmodule
