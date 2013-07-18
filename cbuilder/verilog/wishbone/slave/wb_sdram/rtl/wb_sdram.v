//wb_sdram.v
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
  DRT_ID:  5

  flags (read drt.txt in the slave/device_rom_table directory 1 means
  a standard device
  DRT_FLAGS:  3

  number of registers this should be equal to the nubmer of ADDR_???
  parameters
  DRT_SIZE:  8388607

*/
`timescale 1 ns/1 ps


module wb_sdram (
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

  output  reg         o_wbs_int,

  //SDRAM signals
  output              o_sdram_clk,
  output              o_sdram_cke,
  output              o_sdram_cs_n,
  output              o_sdram_ras,
  output              o_sdram_cas,
  output              o_sdram_we,

  output    [11:0]    o_sdram_addr,
  output    [1:0]     o_sdram_bank,
  inout     [15:0]    io_sdram_data,
  output    [1:0]     o_sdram_data_mask,
  output              o_sdram_ready,

  output              o_ext_sdram_clk


);

//Local Parameters

//Registers/Wires
reg               if_write_strobe;
wire      [1:0]   if_write_ready;
reg       [1:0]   if_write_activate;
wire      [23:0]  if_write_fifo_size;
reg       [23:0]  if_count;
wire              if_starved;

reg               of_read_strobe;
wire              of_read_ready;
reg               of_read_activate;
wire      [23:0]  of_read_count;
wire      [31:0]  of_read_data;
reg       [23:0]  of_count;

//wire              wr_fifo_full;
//wire              rd_fifo_empty;

reg       [3:0]   delay;
reg               wb_reading;

reg               writing;
reg               reading;
reg       [21:0]  ram_address;
reg               first_exchange;


//Submoduels

sdram ram (
  .clk                (clk                ),
  .rst                (rst                ),

  //write path
  .if_write_strobe    (if_write_strobe    ),
  .if_write_data      (i_wbs_dat          ),
  .if_write_mask      (~i_wbs_sel         ),
  .if_write_ready     (if_write_ready     ),
  .if_write_activate  (if_write_activate  ),
  .if_write_fifo_size (if_write_fifo_size ),
  .if_starved         (if_starved         ),

  //read path
  .of_read_strobe     (of_read_strobe     ),
  .of_read_data       (of_read_data       ),
  .of_read_ready      (of_read_ready      ),
  .of_read_activate   (of_read_activate   ),
  .of_read_count      (of_read_count      ),

  .sdram_write_enable (writing            ),
  .sdram_read_enable  (reading            ),
  .sdram_ready        (o_sdram_ready      ),
  //.app_address      (i_wbs_adr[23:2]    ),
  .app_address        (ram_address        ),

  .sd_clk             (o_sdram_clk        ),
  .cke                (o_sdram_cke        ),
  .cs_n               (o_sdram_cs_n       ),
  .ras                (o_sdram_ras        ),
  .cas                (o_sdram_cas        ),
  .we                 (o_sdram_we         ),

  .address            (o_sdram_addr       ),
  .bank               (o_sdram_bank       ),
  .data               (io_sdram_data      ),
  .data_mask          (o_sdram_data_mask  ),

  .ext_sdram_clk      (o_ext_sdram_clk    )

);

//blocks
always @ (posedge clk) begin
  if (rst) begin
    o_wbs_ack                         <= 0;
    o_wbs_int                         <= 0;
    if_write_strobe                   <= 0;
    of_read_strobe                    <= 0;
    delay                             <= 0;
    wb_reading                        <= 0;
    writing                           <= 0;
    reading                           <= 0;
    if_count                          <= 0;
    of_count                          <= 0;
    if_write_activate                 <= 0;
    ram_address                       <= 0;
    first_exchange                    <= 0;
    o_wbs_dat                         <= 0;
  end
  else begin
    if_write_strobe                   <= 0;
    of_read_strobe                    <= 0;

    //when the master acks our ack, then put our ack down
    if (~i_wbs_cyc) begin
      writing                         <= 0;
      reading                         <= 0;
      of_read_activate                <= 0;
      first_exchange                  <= 1;
    end

    if (o_wbs_ack & ~i_wbs_stb)begin
      o_wbs_ack                       <= 0;
      if ((if_write_activate > 0) && if_starved) begin
        //release any previously held FIFOs
        if_count                      <= 0;
        if_write_activate             <= 0;
      end
    end

    else if (!o_wbs_ack && i_wbs_stb && i_wbs_cyc) begin
      if (first_exchange) begin
        ram_address                   <=  i_wbs_adr[22:1];
        first_exchange                <=  0;
      end
      //master is requesting something
      if (i_wbs_we) begin
        writing <=  1;
        if (if_write_activate == 0) begin
          //try and get a FIFO
          if (if_write_ready > 0) begin
            if_count                  <= if_write_fifo_size - 1;
            if (if_write_ready[0]) begin
              $display ("Getting FIFO 0");
              if_write_activate[0]    <=  1;
            end
            else begin
              $display ("Getting FIFO 1");
              if_write_activate[1]    <=  1;
            end
          end
        end
        else begin
          $display ("Writing");
          //write request
          if (~o_wbs_ack) begin
            if (if_count > 0) begin
              $display("user wrote %h to address %h", i_wbs_dat, i_wbs_adr);
              o_wbs_ack               <= 1;
              if_write_strobe         <= 1;
              if_count                <= if_count - 1;

            end
            else begin
              if_write_activate       <=  0;
            end
          end
        end
      end

      //Reading
      else if (~writing) begin
        reading                       <=  1;
        if (of_read_ready && !of_read_activate) begin
          of_count                    <=  of_read_count;
          of_read_activate            <=  1;
        end
        else if (of_read_activate) begin
          if (of_count > 0) begin
            if (~o_wbs_ack) begin
              o_wbs_dat               <=  of_read_data;
              of_count                <=  of_count - 1;
              of_read_strobe          <=  1;
              o_wbs_ack               <=  1;
              $display("user wb_reading %h", o_wbs_dat);
            end
          end
          else begin
            //release the FIFO
            of_read_activate          <=  0;
          end
        end
      end
    end
  end
end


endmodule
