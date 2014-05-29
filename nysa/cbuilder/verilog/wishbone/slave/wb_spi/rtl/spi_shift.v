//////////////////////////////////////////////////////////////////////
////                                                              ////
////  spi_shift.v                                                 ////
////                                                              ////
////  This file is part of the SPI IP core project                ////
////  http://www.opencores.org/projects/spi/                      ////
////                                                              ////
////  Author(s):                                                  ////
////      - Simon Srot (simons@opencores.org)                     ////
////                                                              ////
////  All additional information is avaliable in the Readme.txt   ////
////  file.                                                       ////
////                                                              ////
//////////////////////////////////////////////////////////////////////
////                                                              ////
//// Copyright (C) 2002 Authors                                   ////
////                                                              ////
//// This source file may be used and distributed without         ////
//// restriction provided that this copyright statement is not    ////
//// removed from the file and that any derivative work contains  ////
//// the original copyright notice and the associated disclaimer. ////
////                                                              ////
//// This source file is free software; you can redistribute it   ////
//// and/or modify it under the terms of the GNU Lesser General   ////
//// Public License as published by the Free Software Foundation; ////
//// either version 2.1 of the License, or (at your option) any   ////
//// later version.                                               ////
////                                                              ////
//// This source is distributed in the hope that it will be       ////
//// useful, but WITHOUT ANY WARRANTY; without even the implied   ////
//// warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR      ////
//// PURPOSE.  See the GNU Lesser General Public License for more ////
//// details.                                                     ////
////                                                              ////
//// You should have received a copy of the GNU Lesser General    ////
//// Public License along with this source; if not, download it   ////
//// from http://www.opencores.org/lgpl.shtml                     ////
////                                                              ////
//////////////////////////////////////////////////////////////////////

`include "spi_defines.v"
`include "timescale.v"

module spi_shift (

  input                          clk,          // system clock
  input                          rst,          // reset
  input                    [3:0] latch,        // latch signal for storing the data in shift register
  input [`SPI_CHAR_LEN_BITS-1:0] len,          // data len in bits (minus one)
  input                          lsb,          // lbs first on the line
  input                          go,           // start stansfer
  input                          pos_edge,     // recognize posedge of sclk
  input                          neg_edge,     // recognize negedge of sclk
  input                          rx_negedge,   // s_in is sampled on negative edge
  input                          tx_negedge,   // s_out is driven on negative edge
  output                         tip,          // transfer in progress
  output                         last,         // last bit
  input                   [31:0] p_in,         // parallel in
  output  reg[`SPI_MAX_CHAR-1:0] p_out,        // parallel out
  input                          s_clk,        // serial clock
  input                          s_in,         // serial in
  output                         s_out,        // serial out
  input       [127:0]            mosi_data
);

//Local Parameters

//Registers/Wires
reg                             s_out;
reg                             tip;

reg     [`SPI_CHAR_LEN_BITS:0]  cnt;          // data bit count
reg     [`SPI_MAX_CHAR-1:0]     data;         // shift register
wire    [`SPI_CHAR_LEN_BITS:0]  rx_bit_pos;   // next bit position
wire                            rx_clk;       // rx clock enable
wire                            tx_clk;       // tx clock enable

//Submodules

//Asynchronous Logic
assign tx_bit_pos = lsb ? len - cnt : cnt;
assign rx_bit_pos = lsb ? len - (rx_negedge ? cnt + {{`SPI_CHAR_LEN_BITS{1'b0}},1'b1} : cnt) :
                          (rx_negedge ? cnt : cnt - {{`SPI_CHAR_LEN_BITS{1'b0}},1'b1});

assign last = !(|cnt);

assign rx_clk = (rx_negedge ? neg_edge : pos_edge) && (!last || s_clk);
assign tx_clk = (tx_negedge ? neg_edge : pos_edge) && !last;

//Synchronous Logic

// Character bit counter
always @(posedge clk) begin
  if(rst) begin
    cnt <=  0;
  end
  else begin
    if(tip) begin
      cnt <=  pos_edge ? (cnt - 1) : cnt;
    end
    else begin
      //if len is zero then we put in the max
      //else put in the number specified
      cnt <=  !(|len) ? {1'b1, {`SPI_CHAR_LEN_BITS{1'b0}}} : {1'b0, len};
    end
  end
end

// Transfer in progress
always @(posedge clk) begin
  if(rst) begin
    tip <=  1'b0;
  end
  else begin
    if(go && ~tip) begin
      tip <=  1'b1;
    end
    else if(tip && last && pos_edge) begin
      tip <=  1'b0;
    end
  end
end

// Sending bits to the line
always @(posedge clk) begin
  if (rst) begin
    s_out   <=  1'b0;
    data    <=  0;
  end
  else begin
    if (tx_clk && tip) begin
      if (!lsb) begin
        s_out         <=  data[127];
        data     <=  {data[126:0], 1'b1};
      end
      else begin
        s_out         <=  data[0];
        data     <=  {1'b1, data[127:1]};
      end
    end
    if (!tip) begin
      data            <=  mosi_data;
    end
  end
end

// Receiving bits from the line
always @(posedge clk) begin
  if (rst) begin
    p_out     <=  0;
  end
  else begin
    if (rx_clk) begin
      //Clock data in on the receive clock
      p_out <=  {p_out[126:0], s_in};
    end
  end
end

endmodule

