/*
Distributed under the MIT licesnse.
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

`timescale 1ns/1ps

//XXX: NOTE: All counts are 24bits long, this could be a parameter in the future


module ppfifo
  #(parameter   DATA_WIDTH    = 8,
                ADDRESS_WIDTH = 4
)(

  reset,

  //write
  write_clock,
  write_ready,
  write_activate,
  write_fifo_size,
  write_strobe,
  write_data,

  starved,

  //read
  read_clock,
  read_strobe,
  read_ready,
  read_activate,
  read_count,
  read_data
);

parameter FIFO_DEPTH = (1 << ADDRESS_WIDTH);
//universal input
input                       reset;

//write side
input                       write_clock;
output [1:0]                write_ready;
input  [1:0]                write_activate;
output wire [23:0]          write_fifo_size;
input                       write_strobe;
input [DATA_WIDTH - 1: 0]   write_data;
output                      starved;

//read side
input                       read_clock;
input                       read_strobe;
output reg                  read_ready;
input                       read_activate;
output reg [23:0]           read_count;
output [DATA_WIDTH - 1: 0]  read_data;




//Local Registers/Wires
reg    [23:0]               fifo0_write_count;
reg    [23:0]               fifo1_write_count;

wire  [DATA_WIDTH - 1: 0]   fifo0_read_data;
wire                        fifo0_read_strobe;
wire                        fifo0_empty;

wire  [DATA_WIDTH - 1: 0]   fifo0_write_data;
wire                        fifo0_write_strobe;
wire                        fifo0_full;


wire  [DATA_WIDTH - 1: 0]   fifo1_read_data;
wire                        fifo1_read_strobe;
wire                        fifo1_empty;

wire  [DATA_WIDTH - 1: 0]   fifo1_write_data;
wire                        fifo1_write_strobe;
wire                        fifo1_full;

reg   [1:0]                 read_fifo_select;

reg   [DATA_WIDTH - 1: 0]   last_read_data;
reg                         pre_read_strobe0;
reg                         pre_read_strobe1;

reg                         first_read0;
reg                         first_read1;


//Cross clock status
reg   [1:0]                 fifo0_ready_history;
wire                        fifo0_ready;
reg   [1:0]                 fifo1_ready_history;
wire                        fifo1_ready;


wire                        write_clock_pulse_empty0_valid;
reg   [2:0]                 write_clock_pulse_empty0_valid_sync;

wire                        write_clock_pulse_empty1_valid;
reg   [2:0]                 write_clock_pulse_empty1_valid_sync;

reg   [1:0]                 read_pre_select;

wire                        read_pre_select0;
wire                        read_pre_select1;

wire                        pos_edge_fifo0_ready;
wire                        pos_edge_fifo1_ready;

reg                         prev_fifo0_ready;
reg                         prev_fifo1_ready;



afifo 
  #(
  .DATA_WIDTH(DATA_WIDTH),
  .ADDRESS_WIDTH(ADDRESS_WIDTH)
  )
  fifo0(
    .rst(reset),

    //read
    .dout_clk(read_clock),
    .data_out(fifo0_read_data),
    .rd_en(fifo0_read_strobe),
    .empty(fifo0_empty),

    //write
    .din_clk(write_clock),
    .data_in(fifo0_write_data),
    .wr_en(fifo0_write_strobe),
    .full(fifo0_full)
);

afifo #(
  .DATA_WIDTH(DATA_WIDTH),
  .ADDRESS_WIDTH(ADDRESS_WIDTH)
  )
  fifo1(
    .rst(reset),

    //read
    .dout_clk(read_clock),
    .data_out(fifo1_read_data),
    .rd_en(fifo1_read_strobe),
    .empty(fifo1_empty),

    //write
    .din_clk(write_clock),
    .data_in(fifo1_write_data),
    .wr_en(fifo1_write_strobe),
    .full(fifo1_full)
);

//asynchronous logic
assign  write_fifo_size = FIFO_DEPTH;

assign fifo0_write_data     = (write_activate[0]) ? write_data : 0; 
assign fifo1_write_data     = (write_activate[1]) ? write_data : 0;

assign fifo0_write_strobe   = (write_activate[0]) ? write_strobe : 0;
assign fifo1_write_strobe   = (write_activate[1]) ? write_strobe : 0;

assign write_ready          = {fifo1_empty && (fifo1_write_count == 0) , fifo0_empty && (fifo0_write_count == 0)};

assign starved              = ((write_activate[0] == 1) && fifo1_empty) || 
                              ((write_activate[1] == 1) && fifo0_empty) ||
                              (fifo0_empty && fifo1_empty);

//assign the read output
assign read_data            = (read_fifo_select[0] == 1) ? fifo0_read_data :
                              (read_fifo_select[1] == 1) ? fifo1_read_data :
                              last_read_data;

assign fifo0_read_strobe    = ((read_fifo_select[0] == 1) ? read_strobe : 0) | pre_read_strobe0;
assign fifo1_read_strobe    = ((read_fifo_select[1] == 1) ? read_strobe : 0) | pre_read_strobe1;

assign  write_clock_pulse_empty0_valid  = (~write_clock_pulse_empty0_valid_sync[2] && write_clock_pulse_empty0_valid_sync[1]);
assign  write_clock_pulse_empty1_valid  = (~write_clock_pulse_empty1_valid_sync[2] && write_clock_pulse_empty1_valid_sync[1]);


//debug signals so the simulator can view it
assign read_pre_select0     = read_pre_select[0];
assign read_pre_select1     = read_pre_select[1];
//synchronous logic

always @(posedge write_clock or posedge reset) begin
  if (reset) begin
    write_clock_pulse_empty0_valid_sync <=  0;
    write_clock_pulse_empty1_valid_sync <=  0;
  end
  else begin
    write_clock_pulse_empty0_valid_sync <=  {write_clock_pulse_empty0_valid_sync[1:0], fifo0_empty};
    write_clock_pulse_empty1_valid_sync <=  {write_clock_pulse_empty1_valid_sync[1:0], fifo1_empty};
  end
end

//FIFO write counts
always @ (posedge write_clock or posedge reset) begin
  if (reset) begin
    fifo0_write_count   <=  0;
  end
  else begin
    if (write_clock_pulse_empty0_valid && ~write_activate[0]) begin
      fifo0_write_count <=  0;
    end
    if (fifo0_write_strobe) begin
      fifo0_write_count <=  fifo0_write_count + 1;
    end
  end
end

//FIFO1 write counts
always @ (posedge write_clock or posedge reset) begin
  if (reset) begin
    fifo1_write_count   <=  0;
  end
  else begin
    if (write_clock_pulse_empty1_valid && ~write_activate[1]) begin
      fifo1_write_count <=  0;
    end
    if (fifo1_write_strobe) begin
      fifo1_write_count <=  fifo1_write_count + 1;
    end
  end
end


//Read side synchronization of write side status
assign  fifo0_ready = (fifo0_ready_history[1] & fifo0_ready_history[0]);
assign  fifo1_ready = (fifo1_ready_history[1] & fifo1_ready_history[0]);

assign  pos_edge_fifo0_ready  = fifo0_ready & ~prev_fifo0_ready;
assign  pos_edge_fifo1_ready  = fifo1_ready & ~prev_fifo1_ready;

always @ (posedge read_clock or posedge reset) begin
  if (reset) begin
    fifo0_ready_history <=  0;
    fifo1_ready_history <=  0;
  end
  else begin
    if (fifo0_empty) begin
      fifo0_ready_history <=  0;
    end
    else begin
      fifo0_ready_history[1] <=  fifo0_ready_history[0];
      fifo0_ready_history[0] <= (!write_activate[0] && (fifo0_write_count != 0));
    end

    if (fifo1_empty) begin
      fifo1_ready_history <=  0;
    end
    else begin
      fifo1_ready_history[1] <=  fifo1_ready_history[0];
      fifo1_ready_history[0] <= (!write_activate[1] && (fifo1_write_count != 0));
    end

    prev_fifo0_ready         <=  fifo0_ready;
    prev_fifo1_ready         <=  fifo1_ready;

  end
end

//selecting and activating read side data
always @ (posedge read_clock or posedge reset) begin
  if (reset) begin
    read_ready              <=  0;
    read_count              <=  0;
    read_fifo_select        <=  0;
    last_read_data          <=  0;
    pre_read_strobe0        <=  0;
    pre_read_strobe1        <=  0;
    read_pre_select         <=  0;
    first_read0             <=  1;
    first_read1             <=  1;
  end
  else begin
    pre_read_strobe0        <=  0;
    pre_read_strobe1        <=  0;
    if ((read_fifo_select == 0) && !read_activate) begin
      if (read_pre_select[0] && fifo0_ready) begin
          read_count          <=  fifo0_write_count;
          read_ready          <=  1;
          read_fifo_select[0] <=  1;
          read_pre_select     <=  0;
      end
      else if (read_pre_select[1] && fifo1_ready) begin
          read_count          <=  fifo1_write_count; 
          read_ready          <=  1;
          read_fifo_select[1] <=  1;
          read_pre_select     <=  0;
      end
      else begin
        if (fifo0_ready) begin
          //although this signal is asynchronous due to the synchronization of fifo0_redy I know that
          //the fifoX_write_count is stable
          read_count          <=  fifo0_write_count;
          read_ready          <=  1;
          read_fifo_select[0] <=  1;
        end
        else if (fifo1_ready) begin
          read_count          <=  fifo1_write_count; 
          read_ready          <=  1;
          read_fifo_select[1] <=  1;
        end
        else begin
          read_ready          <=  0;
          read_count          <=  0;
        end
      end
    end

    //if (pos_edge_fifo0_ready && first_read0) begin
    if (pos_edge_fifo0_ready) begin
      pre_read_strobe0        <=  1;
      first_read0             <=  0;
    end
    //if (pos_edge_fifo1_ready && first_read1) begin
    if (pos_edge_fifo1_ready) begin
      pre_read_strobe1        <=  1;
      first_read1             <=  0;
    end
    
    if (read_activate && read_ready) begin
      read_ready            <=  0;
    end
    //keep the last peice of data around
    if (read_fifo_select[0]) begin
      last_read_data          <=  fifo0_read_data; 
    end
    if (read_fifo_select[1]) begin
      last_read_data           <=  fifo1_read_data; 
    end

    //reset select
    //reset FIFO 0 select
    if (read_fifo_select[0] && fifo0_empty) begin
      read_fifo_select[0]     <=  0;
      read_ready              <=  0;
      //gives the other buffer priority (this is useful for very slow read clocks)
      //fifo0 can be re-filled before the block can select the other FIFO
      read_pre_select[1]      <=  1;
    end

    //reset FIFO 1 select 
    if (read_fifo_select[1] && fifo1_empty) begin
      read_fifo_select[1]     <=  0;
      read_ready              <=  0;
      //gives the other buffer priroity (this is useful for very slow read clocks)
      read_pre_select[0]      <=  1;
    end

  end
end
endmodule

