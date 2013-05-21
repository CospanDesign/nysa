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
  Use this to tell sycamore how to populate the Device ROM table
  so that users can interact with your slave

  META DATA

  identification of your device 0 - 65536
  DRT_ID:  11

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:  1

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:  3

*/

`define DEFAULT_MEMORY_TIMEOUT  300

`include "project_defines.v"
`include "i2s_defines.v"
`timescale 1 ns/1 ps

module wb_i2s (
  clk,
  rst,

  //Add signals to control your device here

  wbs_we_i,
  wbs_cyc_i,
  wbs_sel_i,
  wbs_dat_i,
  wbs_stb_i,
  wbs_ack_o,
  wbs_dat_o,
  wbs_adr_i,
  wbs_int_o,

  mem_we_o,
  mem_stb_o,
  mem_cyc_o,
  mem_sel_o,
  mem_adr_o,
  mem_dat_o,
  mem_dat_i,
  mem_ack_i,
  mem_int_i,

  writer_starved,

  phy_mclock,
  phy_clock,
  phy_data,
  phy_lr
);

`define DEFAULT_CLOCK_DIVISOR (`CLOCK_RATE / (`AUDIO_RATE * `AUDIO_BITS * `AUDIO_CHANNELS)) / 2

input         clk;
input         rst;

//wishbone slave signals
input               wbs_we_i;
input               wbs_stb_i;
input               wbs_cyc_i;
input       [3:0]   wbs_sel_i;
input       [31:0]  wbs_adr_i;
input       [31:0]  wbs_dat_i;
output reg  [31:0]  wbs_dat_o;
output reg          wbs_ack_o;
output reg          wbs_int_o;

//master control signal for memory arbitration
output reg          mem_we_o;
output reg          mem_stb_o;
output reg          mem_cyc_o;
output reg  [3:0]   mem_sel_o;
output reg  [31:0]  mem_adr_o;
output reg  [31:0]  mem_dat_o;
input       [31:0]  mem_dat_i;
input               mem_ack_i;
input               mem_int_i;

//status
output              writer_starved;

//i2s signals
output              phy_mclock;
output              phy_clock;
output              phy_data;
output              phy_lr;


parameter           REG_CONTROL       = 32'h00000000;
parameter           REG_STATUS        = 32'h00000001;
parameter           REG_CLOCK_RATE    = 32'h00000002;
parameter           REG_CLOCK_DIVIDER = 32'h00000003;
parameter           REG_MEM_0_BASE    = 32'h00000004;
parameter           REG_MEM_0_SIZE    = 32'h00000005;
parameter           REG_MEM_1_BASE    = 32'h00000006;
parameter           REG_MEM_1_SIZE    = 32'h00000007;


//Reg/Wire
wire                timeout_elapsed;
reg                 timeout_enable;
reg         [31:0]  timeout_count;
reg         [31:0]  timeout_value;

reg                 enable_mem_read;

wire                request_data;
reg                 prev_request_data;
wire                request_data_pos_edge;

reg                 prev_mem_ack;
wire                mem_ack_pos_edge;

wire        [23:0]  request_size;
reg                 request_finished;
//wire        [31:0]  memory_data;
reg         [31:0]  memory_data;
reg                 memory_data_strobe;
reg                 enable_strobe;


reg         [31:0]  control;
wire        [31:0]  status;
reg         [31:0]  clock_divider;


reg         [23:0]  request_count;

reg         [31:0]  memory_0_size;
reg                 memory_0_new_data;
reg         [31:0]  memory_1_size;
reg                 memory_1_new_data;

wire        [31:0]  memory_count[1:0];
wire        [31:0]  memory_0_count;
wire        [31:0]  memory_1_count;
reg         [31:0]  memory_pointer[1:0];
wire        [31:0]  memory_0_pointer;
wire        [31:0]  memory_1_pointer;

reg                 memory_ready;
reg                 active_block;


reg         [31:0]  memory_base[1:0];
wire        [31:0]  memory_0_base;
wire        [31:0]  memory_1_base;

//control
wire                enable;
wire                enable_interrupt;
wire                post_fifo_wave_en;
wire                pre_fifo_wave_en;

//status  
wire                memory_0_empty;
wire                memory_1_empty;




i2s_controller controller (
  .rst(rst),
  .clk(clk),

  .enable(enable),
  .post_fifo_wave_en(post_fifo_wave_en),
  .pre_fifo_wave_en(pre_fifo_wave_en),

  .clock_divider(clock_divider),

  .request_data(request_data),
  .request_size(request_size),
  .request_finished(request_finished),
  .memory_data(memory_data),
  .memory_data_strobe(memory_data_strobe),

  .starved(writer_starved),

  .i2s_mclock(phy_mclock),
  .i2s_clock(phy_clock),
  .i2s_data(phy_data),
  .i2s_lr(phy_lr)
);


//Asynchronous Logic
//assign        memory_data           = mem_dat_i;

assign        enable                = control[`CONTROL_ENABLE];
assign        enable_interrupt      = control[`CONTROL_ENABLE_INTERRUPT];
assign        post_fifo_wave_en     = control[`CONTROL_POST_FIFO_WAVE];
assign        pre_fifo_wave_en      = control[`CONTROL_PRE_FIFO_WAVE];

assign        memory_0_empty        = (memory_count[0] == 0);
assign        memory_1_empty        = (memory_count[1] == 0);

assign        status[`STATUS_MEMORY_0_EMPTY]  = memory_0_empty;
assign        status[`STATUS_MEMORY_1_EMPTY]  = memory_1_empty;
assign        status[31:2]          = 0;

assign        request_data_pos_edge = request_data && ~prev_request_data;
assign        mem_ack_pos_edge      = mem_ack_i && ~prev_mem_ack;

assign        memory_count[0]       = memory_0_size - memory_pointer[0];
assign        memory_count[1]       = memory_1_size - memory_pointer[1];

assign        memory_0_count        = memory_count[0];
assign        memory_1_count        = memory_count[1];

assign        memory_0_pointer      = memory_pointer[0];
assign        memory_1_pointer      = memory_pointer[1];

assign        memory_0_base         = memory_base[0];
assign        memory_1_base         = memory_base[1];


//blocks
always @ (posedge clk) begin
  if (rst) begin
    wbs_dat_o       <=  32'h0;
    wbs_ack_o       <=  0;
    timeout_enable  <=  0;
    timeout_value   <=  `DEFAULT_MEMORY_TIMEOUT;

    control         <=  0;

    memory_base[0]  <=  `DEFAULT_MEM_0_BASE;
    memory_base[1]  <=  `DEFAULT_MEM_1_BASE;

    //memory_0_base   <=  `DEFAULT_MEM_0_BASE;
    //memory_1_base   <=  `DEFAULT_MEM_1_BASE;

    memory_0_new_data <=  0;
    memory_1_new_data <=  0;

    clock_divider   <=  `DEFAULT_CLOCK_DIVISOR;
  end

  else begin

    memory_0_new_data <=  0;
    memory_1_new_data <=  0;


    //when the master acks our ack, then put our ack down
    if (wbs_ack_o & ~ wbs_stb_i)begin
      wbs_ack_o <= 0;
    end

    if (wbs_stb_i & wbs_cyc_i) begin
      //master is requesting somethign
      if (wbs_we_i) begin
        //write request
        case (wbs_adr_i) 
          REG_CONTROL: begin
            control           <=  wbs_dat_i;
          end
          REG_CLOCK_DIVIDER: begin
            clock_divider     <=  wbs_dat_i;
          end
          REG_MEM_0_BASE: begin
            memory_base[0]    <=  wbs_dat_i;
          end
          REG_MEM_0_SIZE: begin
            memory_0_size     <=  wbs_dat_i;
            if (wbs_dat_i > 0) begin
              memory_0_new_data <=  1;
            end
          end
          REG_MEM_1_BASE: begin
            memory_base[1]    <=  wbs_dat_i;
          end
          REG_MEM_1_SIZE: begin
            memory_1_size     <=  wbs_dat_i;
            if (wbs_dat_i > 0) begin
              memory_1_new_data <=  1;
            end
          end
          default: begin
          end
        endcase
      end

      else begin 
        //read request
        case (wbs_adr_i)
          REG_CONTROL: begin
            wbs_dat_o <= control;
          end
          REG_STATUS: begin
            wbs_dat_o <= status;
          end
          REG_CLOCK_RATE: begin
            wbs_dat_o <= `CLOCK_RATE;
          end
          REG_CLOCK_DIVIDER: begin
            wbs_dat_o <=  clock_divider;
          end
          REG_MEM_0_BASE: begin
            wbs_dat_o <=  memory_0_base;
          end
          REG_MEM_0_SIZE: begin
            wbs_dat_o <=  memory_0_count;
          end
          REG_MEM_1_BASE: begin
            wbs_dat_o <=  memory_1_base;
          end
          REG_MEM_1_SIZE: begin
            wbs_dat_o <=  memory_1_count;
          end
          //add as many ADDR_X you need here
          default: begin
            wbs_dat_o <=  32'h00;
          end
        endcase
      end
      wbs_ack_o <= 1;
    end
  end
end

//detect the positive edge of request data
always @ (posedge clk) begin
  if (rst) begin
    prev_request_data   <=  0;
    prev_mem_ack        <=  0;
  end
  else begin
    prev_request_data   <=  request_data;
    prev_mem_ack        <=  mem_ack_i;
  end
end


//wishbone master module
always @ (posedge clk) begin
  if (rst) begin
    mem_we_o            <=  0;
    mem_stb_o           <=  0;
    mem_cyc_o           <=  0;
    mem_sel_o           <=  4'h0;
    mem_adr_o           <=  32'h00000000;
    mem_dat_o           <=  32'h00000000;

    //strobe for the i2s memory controller
    memory_data_strobe  <=  0;

    //point to the current location in the memory to read from
    memory_pointer[0]   <=  0;
    memory_pointer[1]   <=  0;

    request_count       <=  0;

    enable_strobe       <=  0;

  end
  else begin

    request_finished    <=  0;

    if (memory_0_new_data) begin
      memory_pointer[0] <=  0;
    end
    if (memory_1_new_data) begin
      memory_pointer[1] <=  0;
    end

    //a delay for the strobe so the data can be registered
    if (enable_strobe) begin
      enable_strobe     <=  0;
      memory_data_strobe<=  1;
    end
    //memory strobe
    if (memory_data_strobe) begin
      memory_data_strobe  <=  0;
      if (request_count == 0) begin
        request_finished            <=  1;
      end
    end


    //check to see if the i2s_mem_controller has requested data
    if (request_data_pos_edge) begin
      request_count     <=  request_size - 1;
    end
    //postvie edge of the ack, send the data to the mem controller
    if (mem_ack_pos_edge) begin
      $display ("got an ack!");
      if (request_count == 1) begin
        mem_cyc_o                   <=  0;
      end
      memory_data                   <=  mem_dat_i;
      enable_strobe                 <=  1;
      request_count                 <=  request_count - 1;
      memory_pointer[active_block]  <=  memory_pointer[active_block] + 4;
      mem_stb_o                       <=  0;
    end
    if (memory_ready) begin
      if ((request_count > 0) && (memory_count[active_block] > 0) && ~mem_stb_o && ~mem_ack_i) begin
        //need to request data from the memory
        $display("get some data from the memory");
        mem_cyc_o                     <=  1;
        mem_stb_o                     <=  1;
        mem_sel_o                     <=  4'b1111;
        mem_we_o                      <=  0;
        mem_dat_o                     <=  0;  
        mem_adr_o                     <=  memory_base[active_block] + memory_pointer[active_block];
      end
    end
    else begin
      //the memory is not ready
      mem_stb_o                       <=  0;
      mem_cyc_o                       <=  0;
    end
/*
    if (request_count == 0) begin
      //finished filling up the internal buffer
      mem_stb_o                       <=  0;
      mem_cyc_o                       <=  0;
    end
*/
  end
end

//active block logic
always @ (posedge clk) begin
  if (rst) begin
    active_block  <=  0;
    memory_ready  <=  0;
  end
  else begin
    //active memory logic
    if (!memory_ready) begin
      //if there is any memory at all in the memory chunks
      if (memory_count[0] > 0) begin
        memory_ready    <=  1;
        active_block    <=  0;
      end
      else if (memory_count[1] > 0) begin
        memory_ready    <=  1;
        active_block    <=  1;
      end
    end
    else begin
      //if we're are currently active and a the active block
      //is empty then disable the block
      if      ((active_block == 0) && (memory_count[0] == 0)) begin
        memory_ready    <=  0;
      end
      else if ((active_block == 1) && (memory_count[1] == 0)) begin
        memory_ready    <=  0;
      end
    end
  end
end

//initerrupt controller
always @ (posedge clk) begin
  if (rst) begin
    wbs_int_o <=  0;
  end
  else if (enable) begin
    if (!memory_0_empty && !memory_1_empty) begin
      wbs_int_o <=  0;
    end
    if (wbs_stb_i) begin
      //de-assert the interrupt on wbs transactions so I can launch another
      //interrupt when the wbs is de-asserted
      wbs_int_o <=  0;
    end
    else if (memory_0_empty || memory_1_empty) begin
      wbs_int_o <=  1;
    end
  end
  else begin
    //if we're not enable de-assert interrupt
    wbs_int_o <=  0;
  end
end


endmodule
