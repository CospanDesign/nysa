//i2s_controllerv
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

`include "project_defines.v"
`include "i2s_defines.v"


`timescale 1 ns/1 ps
module i2s_controller (
  rst,
  clk,

  enable,
  post_fifo_wave_en,
  pre_fifo_wave_en,

  clock_divider,

  request_data,
  request_size,
  request_finished,
  memory_data,
  memory_data_strobe,

  starved,

  i2s_mclock,
  i2s_clock,
  i2s_data,
  i2s_lr
);

`define DEFAULT_MCLOCK_DIVISOR `CLOCK_RATE / (`AUDIO_RATE) / 256

input               rst;
input               clk;

input               enable;
input               post_fifo_wave_en;
input               pre_fifo_wave_en;
output              starved;


input       [31:0]  clock_divider;


output              request_data;
output      [23:0]  request_size;
input               request_finished;
input       [31:0]  memory_data;
input               memory_data_strobe;

output  reg         i2s_mclock = 0;
output  reg         i2s_clock = 0;
output              i2s_data;
output              i2s_lr;

//registers/wires
reg         [2:0]   clock_count = 0;
reg                 mclock_count = 0;

wire                audio_data_request;
wire                audio_data_ack;
wire        [23:0]  audio_data;
wire                audio_lr_bit;

//sub modules
i2s_mem_controller mcontroller (
  .rst(rst),
  .clk(clk),

  //control
  .enable(enable),
  .post_fifo_wave_en(post_fifo_wave_en),
  .pre_fifo_wave_en(pre_fifo_wave_en),

  //clock
  .i2s_clock(i2s_clock),

  //memory interface
  .request_data(request_data),
  .request_size(request_size),
  .request_finished(request_finished),
  .memory_data(memory_data),
  .memory_data_strobe(memory_data_strobe),

  //i2s writer
  .audio_data_request(audio_data_request),
  .audio_data_ack(audio_data_ack),
  .audio_data(audio_data),
  .audio_lr_bit(audio_lr_bit)
);

i2s_writer writer(
  .rst(rst),
  .clk(clk),

  //control/clock
  .enable(enable),
  .starved(starved),

  //i2s clock
  .i2s_clock(i2s_clock),

  //i2s writer
  .audio_data_request(audio_data_request),
  .audio_data_ack(audio_data_ack),
  .audio_data(audio_data),
  .audio_lr_bit(audio_lr_bit),

  //i2s audio interface
  .i2s_data(i2s_data),
  .i2s_lr(i2s_lr)
);

//asynchronous logic
//`define DEFAULT_MCLOCK_DIVISOR (`CLOCK_RATE / (`AUDIO_RATE * 256)) / 2
`define DEFAULT_MCLOCK_DIVISOR 1

//synchronous logic
//clock generator
always @(posedge clk) begin
//  if (rst) begin
//    i2s_clock   <=  0;
//    clock_count <=  0;
//  end
//  else begin
    if (clock_count == 0) begin
      i2s_clock <=  ~i2s_clock;
    end
    clock_count <=  clock_count + 1;
//    if (clock_count == clock_divider) begin
//      i2s_clock     <=  ~i2s_clock;
//      clock_count   <= 0;
//    end
//    else begin
//      clock_count   <=  clock_count + 1;
//    end


//  end
end


always @(posedge clk) begin
//  if (rst) begin
//    i2s_mclock  <=  0;
//    mclock_count  <=  0;
//  end
//  else begin
    if (mclock_count == 0) begin
      i2s_mclock     <=  ~i2s_mclock;
    end
    mclock_count  <=  mclock_count + 1;
    /*
    if (mclock_count == `DEFAULT_MCLOCK_DIVISOR) begin
      i2s_mclock     <=  ~i2s_mclock;
      mclock_count   <= 1;
    end
    else begin
      mclock_count   <=  mclock_count + 1;
    end
  */
//  end
end


endmodule
