//i2s_mem_controllerv
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
`timescale 1 ns/1 ps

module i2s_mem_controller (
  rst,
  clk,

  //control
  enable,
  post_fifo_wave_en,
  pre_fifo_wave_en,

  //clock divider
  i2s_clock,
  
  //memory interface
  request_data,
  request_size,
  request_finished,
  memory_data_strobe,
  memory_data,

  //i2s writer
  audio_data_request,
  audio_data_ack,
  audio_data,
  audio_lr_bit
);

input               rst;
input               clk;

input               enable;
input               post_fifo_wave_en;
input               pre_fifo_wave_en;

input               i2s_clock;

output  reg         request_data = 0;
output      [23:0]  request_size;
input               request_finished;
input       [31:0]  memory_data;
input               memory_data_strobe;

input               audio_data_request;
output  reg         audio_data_ack = 0;
output  reg [23:0]  audio_data = 0;
output  reg         audio_lr_bit = 0;



//registers/wires

//input side
wire        [1:0]   write_ready;
reg         [1:0]   write_activate = 0;
wire        [23:0]  write_fifo_size;
wire                starved;

//output side
reg                 read_strobe = 0;
wire                read_ready;
reg                 read_activate = 0;
wire        [23:0]  read_size;
wire        [31:0]  read_data;


//i2s writer interface
reg         [23:0]  read_count = 0;
reg         [3:0]   state = 0;


//waveform
reg         [31:0]  write_count = 0;
reg         [7:0]   test_pre_pos = 0;
wire        [7:0]   test_pre_wavelength;
wire        [15:0]  test_pre_value;
reg         [31:0]  test_pre_data;
reg                 test_pre_write_strobe;
wire        [31:0]  fifo_data;
wire                fifo_write_strobe;

reg         [7:0]   test_pos = 0;
wire        [7:0]   test_wavelength;
wire        [15:0]  test_value;

assign              fifo_data         = (pre_fifo_wave_en) ? test_pre_data : memory_data;
assign              fifo_write_strobe = (pre_fifo_wave_en) ? test_pre_write_strobe : memory_data_strobe;

//parameters
parameter   READ_STROBE     = 4'h0;
parameter   DELAY           = 4'h1;
parameter   READ            = 4'h2; 

//generate a Ping Pong FIFO to cross the clock domain
ppfifo #(
  .DATA_WIDTH(32),
`ifndef SIMULATION
  .ADDRESS_WIDTH(12)
`else
  .ADDRESS_WIDTH(4)
`endif
)ping_pong (

  .reset(rst),

  //write
  .write_clock(clk),
  .write_ready(write_ready),
  .write_activate(write_activate),
  .write_fifo_size(write_fifo_size),
  .write_strobe(fifo_write_strobe),
  .write_data(fifo_data),

  .starved(starved),

  //read
  .read_clock(i2s_clock),
  .read_strobe(read_strobe),
  .read_ready(read_ready),
  .read_activate(read_activate),
  .read_count(read_size),
  .read_data(read_data)
);

waveform wave_pre (
  .clk(clk),
  .rst(rst),
  .wavelength(test_pre_wavelength),
  .pos(test_pre_pos),
  .value(test_pre_value)
);


waveform wave_post (
  .clk(clk),
  .rst(rst),
  .wavelength(test_wavelength),
  .pos(test_pos),
  .value(test_value)
);

//asynchronous logic

//XXX: the request data may need to be controlled within a block
assign  request_size  = write_fifo_size;


//blocks

//data flow and control
always @(posedge clk) begin
  if (rst) begin
    request_data          <=  0;
    write_activate        <=  0;
    test_pre_pos          <=  0;
    test_pre_data         <=  0;
    test_pre_data[31]     <=  1;
    test_pre_write_strobe <=  0;
    write_count           <=  0;
  end
  else begin
    request_data          <=  0;
    test_pre_write_strobe     <=  0;
    if (enable) begin
      if (pre_fifo_wave_en) begin
        if ((write_ready > 0) && (write_activate == 0)) begin
          //find a buffer that is empty
          if (write_ready[0]) begin
            //activate that buffer
            write_activate[0] <=  1;
          end
          else if (write_ready[1]) begin
            //activate that buffer
            write_activate[1] <=  1;
          end
          write_count       <=  request_size - 1;
        end
        else if (write_activate > 0) begin
          if (write_count > 0) begin
            if (test_pre_pos      >= test_pre_wavelength - 1) begin 
              test_pre_pos        <=  0;
            end
            else begin
              test_pre_pos        <=  test_pre_pos + 1;
            end
            write_count           <=  write_count - 1;
            test_pre_data[31]     <= ~test_pre_data[31];
            test_pre_data[30:24]  <=  0;
            test_pre_data[23:8]   <=  test_pre_value;
            test_pre_data[7:0]    <=  0;
            test_pre_write_strobe <=  1;
          end
          else begin
            write_activate        <=  0;
          end
        end
      end
      else begin
        if ((write_ready > 0) && (write_activate == 0)) begin
          //find a buffer that is empty
          if (write_ready[0]) begin
            //activate that buffer
            write_activate[0] <=  1;
          end
          else if (write_ready[1]) begin
            //activate that buffer
            write_activate[1] <=  1;
          end
          //request data from the memory
          request_data        <=  1;
        end
        //wait for request finished to pusle high
        if (request_finished) begin
          write_activate <= 0;
        end
      end
    end
  end
end


//prepare the data for the i2s writer
`ifdef SIMULATION
always @(posedge i2s_clock or posedge rst) begin
`else
always @(posedge i2s_clock) begin
`endif
  read_strobe     <=  0;
  if (rst) begin
    audio_data_ack  <=  0;
    audio_data      <=  0;
    audio_lr_bit    <=  0;
    read_count      <=  0;
    read_activate   <=  0;
    state           <=  READ_STROBE;
    test_pos        <=  0;
  end
  else if (enable) begin

    //got an ack from the writer
    if (~audio_data_request && audio_data_ack) begin
      //de-assert the ack
      audio_data_ack      <=  0;
    end

    if (post_fifo_wave_en) begin
      if (audio_data_request && ~audio_data_ack) begin
        audio_lr_bit    <=  ~audio_lr_bit;

        if (test_pos >= test_wavelength - 1) begin 
          test_pos  <=  0;
        end
        else begin
          test_pos  <=  test_pos + 1;
        end
        
        audio_data        <=  {test_value, 8'h0};
        audio_data_ack    <=  1;
      end
    end
    else begin
      if (audio_data_request && ~audio_data_ack) begin
       if (read_count > 0) begin
          //more than 0 in the read count
          case (state)
            READ_STROBE: begin
              //if the i2s writer request a dword
              //more data to be read
              read_count          <=  read_count - 1;
              read_strobe         <=  1;
              state               <=  DELAY;
            end
            DELAY: begin
              state               <=  READ;
            end
            READ: begin
              //get data from the ping pong
              //put it into the dword_data
              audio_data          <=  read_data[23:0];
              audio_lr_bit        <=  read_data[31];
              //raise the ACK to indicate there is new data
              audio_data_ack      <=  1;
              state               <=  READ_STROBE;
            end
            default: begin
            end
          endcase
        end
        else begin
          if (read_activate) begin
            read_activate       <=  0;
          end
          //get a new FIFO if it is available
          else if (read_ready) begin
            //activate the PPFIFO
            read_count        <=  read_size;
            read_activate     <=  1;
          end
        end
      end
    end
  end
end
 


endmodule
