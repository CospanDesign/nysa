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
  output reg          mem_o_we,
  output reg          mem_o_stb,
  output reg          mem_o_cyc,
  output reg  [3:0]   mem_o_sel,
  output      [31:0]  mem_o_adr,
  output reg  [31:0]  mem_o_dat,
  input       [31:0]  mem_i_dat,
  input               mem_i_ack,
  input               mem_i_int,

  //status
  output              writer_starved,

  //i2s signals
  output              phy_mclock,
  output              phy_clock,
  output              phy_data,
  output              phy_lr

);


localparam           REG_CONTROL        = 32'h00000000;
localparam           REG_STATUS         = 32'h00000001;
localparam           REG_CLOCK_RATE     = 32'h00000002;
localparam           REG_CLOCK_DIVIDER  = 32'h00000003;
localparam           REG_MEM_0_BASE     = 32'h00000004;
localparam           REG_MEM_0_SIZE     = 32'h00000005;
localparam           REG_MEM_1_BASE     = 32'h00000006;
localparam           REG_MEM_1_SIZE     = 32'h00000007;

//States
localparam          IDLE                = 4'h0;
localparam          GET_MEMORY_BLOCK    = 4'h1;
localparam          READ_DATA           = 4'h2;
localparam          FINISHED            = 4'h3;


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
reg                 active_bank;


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

wire        [23:0]  wfifo_size;
reg         [23:0]  write_count;
reg         [23:0]  memory_write_count;
reg         [23:0]  memory_write_size;

wire        [1:0]   wfifo_ready;
reg         [1:0]   wfifo_activate;
reg                 wfifo_strobe;
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


//Asynchronous Logic
assign        enable                = control[`CONTROL_ENABLE];
assign        enable_interrupt      = control[`CONTROL_ENABLE_INTERRUPT];
assign        post_fifo_wave_en     = control[`CONTROL_POST_FIFO_WAVE];
assign        pre_fifo_wave_en      = control[`CONTROL_PRE_FIFO_WAVE];

assign        memory_0_empty        = (memory_count[0] == 0);
assign        memory_1_empty        = (memory_count[1] == 0);

assign        status[`STATUS_MEMORY_0_EMPTY]  = memory_0_empty;
assign        status[`STATUS_MEMORY_1_EMPTY]  = memory_1_empty;
assign        status[31:2]          = 0;


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
    o_wbs_dat       <=  32'h0;
    o_wbs_ack       <=  0;
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
            memory_base[0]    <=  i_wbs_dat;
          end
          REG_MEM_0_SIZE: begin
            memory_0_size     <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              memory_0_new_data <=  1;
            end
          end
          REG_MEM_1_BASE: begin
            memory_base[1]    <=  i_wbs_dat;
          end
          REG_MEM_1_SIZE: begin
            memory_1_size     <=  i_wbs_dat;
            if (i_wbs_dat > 0) begin
              memory_1_new_data <=  1;
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
            o_wbs_dat <=  memory_0_base;
          end
          REG_MEM_0_SIZE: begin
            o_wbs_dat <=  memory_0_count;
          end
          REG_MEM_1_BASE: begin
            o_wbs_dat <=  memory_1_base;
          end
          REG_MEM_1_SIZE: begin
            o_wbs_dat <=  memory_1_count;
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
    if (!memory_0_empty && !memory_1_empty) begin
      o_wbs_int <=  0;
    end
    if (i_wbs_stb) begin
      //de-assert the interrupt on wbs transactions so I can launch another
      //interrupt when the wbs is de-asserted
      o_wbs_int <=  0;
    end
    else if (memory_0_empty || memory_1_empty) begin
      o_wbs_int <=  1;
    end
  end
  else begin
    //if we're not enable de-assert interrupt
    o_wbs_int <=  0;
  end
end
















//Memory interface


//blocks
assign  wfifo_data                    = mem_i_dat;

always @ (posedge clk) begin
  if (wfifo_strobe) begin
    $display ("\tI2S MEM CONTROLLER: Wrote: %h: Request: %h Write Count: %h", wfifo_data, wfifo_size, write_count);
  end
end

assign              mem_o_adr         = {(memory_base[active_bank] + memory_pointer[active_bank])};

//wishbone master module
always @ (posedge clk) begin
  if (rst) begin
    mem_o_we            <=  0;
    mem_o_stb           <=  0;
    mem_o_cyc           <=  0;
    mem_o_sel           <=  4'b1111;
    mem_o_dat           <=  32'h00000000;

    //strobe for the i2s memory controller
    memory_data_strobe  <=  0;

    //point to the current location in the memory to read from
    memory_pointer[0]   <=  0;
    memory_pointer[1]   <=  0;
    request_count       <=  0;
    enable_strobe       <=  0;

    wfifo_activate      <=  0;
    wfifo_strobe        <=  0;
    write_count         <=  0;

    memory_write_count  <=  0;
    memory_write_size   <=  0;

    state               <=  IDLE;

  end
  else begin
    wfifo_strobe        <=  0;

    //Grab an available FIFO if the core is activated
    if (enable) begin
      if ((wfifo_ready > 0) && (wfifo_activate == 0)) begin
        write_count         <=  0;
        if (wfifo_ready[0]) begin
          wfifo_activate[0] <=  1;
        end
        else begin
          wfifo_activate[1] <=  1;
        end
      end
    end


    case (state)
      IDLE: begin
        if (enable) begin
          state                           <=  GET_MEMORY_BLOCK;
        end
      end
      GET_MEMORY_BLOCK: begin
        mem_o_cyc                         <=  0;
        mem_o_stb                         <=  0;

        if (memory_ready) begin
          memory_write_size               <=  memory_count[active_bank];
          state                           <=  READ_DATA;
        end
        else begin
          //Memory blocks are not ready
          if (write_count > 0) begin
            //There is some data left in the write FIFO but no data from the
            //memory, release this FIFO
            write_count                   <=  0;
            wfifo_activate                <=  0;
          end
          if (!enable) begin
            state                         <=  IDLE;
          end
        end
      end
      READ_DATA: begin
        //Check to see of the Memory has space
        if (memory_pointer[active_bank] < memory_write_size) begin
          //Check if the FIFO has room
          if (wfifo_activate) begin
            if (write_count < wfifo_size) begin
              mem_o_cyc                     <=  1;
              mem_o_stb                     <=  1;
            
              //Ping Pong FIFO has room
              //if we received data from the memory bus, read them in
              if (mem_i_ack && mem_o_stb) begin
            
                memory_write_count          <=  memory_write_count + 1;
                memory_pointer[active_bank] <=  memory_pointer[active_bank] + 1;
                write_count                 <=  write_count + 1;
                wfifo_strobe                <=  1;
                mem_o_stb                   <=  0;
              end
            end
            else begin
              //Release the Activate
              //Release the Wishbone Cycle so the host has a chance to write some data
              mem_o_cyc                     <=  0;
              mem_o_stb                     <=  0;
              wfifo_activate                <=  0;
            end
          end
          else begin
            mem_o_cyc                       <=  0;
            mem_o_stb                       <=  0;
          end
        end
        else begin
          //Memory Doesn't have room, release it
          state                             <=  GET_MEMORY_BLOCK;
        end
      end
      FINISHED: begin
      end
    endcase

    //If there more data from the host
    if (memory_0_new_data) begin
      memory_pointer[0] <=  0;
    end
    if (memory_1_new_data) begin
      memory_pointer[1] <=  0;
    end
  end
end




//active block logic
always @ (posedge clk) begin
  if (rst) begin
    active_bank  <=  0;
    memory_ready  <=  0;
  end
  else begin
    //active memory logic
    if (!memory_ready) begin
      //if there is any memory at all in the memory chunks
      if (memory_count[0] > 0) begin
        memory_ready    <=  1;
        active_bank    <=  0;
      end
      else if (memory_count[1] > 0) begin
        memory_ready    <=  1;
        active_bank    <=  1;
      end
    end
    else begin
      //if we're are currently active and a the active block
      //is empty then disable the block
      if      ((active_bank == 0) && (memory_count[0] == 0)) begin
        memory_ready    <=  0;
      end
      else if ((active_bank == 1) && (memory_count[1] == 0)) begin
        memory_ready    <=  0;
      end
    end
  end
end

endmodule
