//uart_io_handler.v
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

/*
  06/24/2012
    -Added host interface reset to reset the state machine
  12/16/2011
    -fixed a bug in the data output count where it was sending
    5 bits instead of 4
*/

//generalize the uart handler
`include "cbuilder_defines.v"

module uart_io_handler (
  //input/output signals
  input               clk,
  input               rst,
  
  //input handler
  output reg          o_ih_ready,
  output              o_ih_reset,
  input               i_master_ready,
  
  output reg [31:0]   o_in_command,
  output reg [31:0]   o_in_address,
  output reg [31:0]   o_in_data,
  output reg [27:0]   o_in_data_count,
  
  
  //output handler
  output  reg         o_oh_ready,
  input               i_oh_en,
  
  input [31:0]        i_out_status,
  input [31:0]        i_out_address,
  input [31:0]        i_out_data,
  input [27:0]        i_out_data_count,
  
  //these are the only thing that are different between xxx_io_handler
  input               i_phy_uart_in,
  output              o_phy_uart_out
);


//STATES
localparam IDLE             = 8'h0;
localparam READ_ID          = 8'h1;
localparam READ_DATA_COUNT  = 8'h2;
localparam READ_CONTROL     = 8'h3;
localparam READ_ADDRESS     = 8'h4;
localparam READ_DATA        = 8'h5;

localparam WRITE_DATA_COUNT = 8'h1;
localparam WRITE_STATUS     = 8'h2;
localparam WRITE_ADDRESS    = 8'h3;
localparam WRITE_DATA       = 8'h4;

localparam CHAR_L           = 8'h4C;

localparam CHAR_0           = 8'h30;
localparam CHAR_HEX_OFFSET  = 8'h37;
localparam CHAR_A           = 8'h41;
localparam CHAR_F           = 8'h46;
localparam CHAR_S           = 8'h53;

//Registers/Wires
reg     [7:0]       in_state;
reg     [7:0]       out_state;
                   
reg     [3:0]       in_nibble_count;
reg     [3:0]       out_nibble_count;
reg     [15:0]      r_count;


reg                 send_first_data;

wire    [15:0]      user_command;
wire                is_writing;

reg     [7:0]       out_byte;
wire                in_byte_available;
wire    [7:0]       in_byte;
wire                uart_in_busy;
                   
wire                uart_out_busy;
wire                uart_tx_ready;
reg                 uart_out_byte_en;
reg                 oh_finished;
reg                 uart_wait_for_tx;

reg     [27:0]      li_out_data_count;
reg     [27:0]      li_out_data_count_buf;
reg     [31:0]      li_out_data;
reg     [31:0]      li_out_status;
reg     [31:0]      li_out_address;



//REAL UART use this when actually implementing on a board
//Submodules
uart uart_dev (
  .clk             (clk               ),
  .rst             (rst               ),
  .rx              (i_phy_uart_in     ),
  .tx              (o_phy_uart_out    ),
  .transmit        (uart_out_byte_en  ),
  .tx_byte         (out_byte          ),
  .received        (in_byte_available ),
  .rx_byte         (in_byte           ),
  .is_receiving    (uart_in_busy      ),
  .is_transmitting (uart_out_busy     )
//  .recv_error    (                  ),
);

//Asynchronous Logic
assign          user_command   =  o_in_command[15:0];
assign          is_writing     =  (user_command == `COMMAND_WRITE);
assign          o_ih_reset     =  0;
assign          uart_tx_ready  =  ~uart_out_busy;

//Synchronous Logic
//input handler
always @ (posedge clk) begin

  o_ih_ready                <= 0;

  if (rst) begin
    o_in_command            <= 32'h0000;
    o_in_address            <= 32'h0000;
    o_in_data               <= 32'h0000;
    in_state                <= IDLE;
    in_nibble_count         <= 4'h0;
    o_in_data_count         <= 27'h0;
    send_first_data         <= 0;
  end
  else begin
    //main state machine goes here
    case (in_state)
      IDLE: begin
        if (in_byte_available) begin
          in_state     <= READ_ID;
        end
      end
      READ_ID: begin
        //putting this here lets master hold onto the data for
        //a longer time
        o_in_command      <= 32'h0000;
        o_in_address      <= 32'h0000;
        o_in_data       <= 32'h0000;
        o_in_data_count   <= 27'h000;
        send_first_data   <= 1;
        if (in_byte == CHAR_L) begin
        //read the first of in_byte
          in_state      <= READ_DATA_COUNT;
          in_nibble_count <= 4'h0;
        end
        else begin
          in_state    <= IDLE;
        end
      end

      READ_DATA_COUNT: begin
        if (in_byte_available) begin
          if ((in_byte < CHAR_0) ||
              (( in_byte > CHAR_0 + 10) && (in_byte < CHAR_A)) ||
              (in_byte > CHAR_F)) begin
            //invalid character go back to READ_ID
            in_state     <= READ_ID;
          end
          else begin
            //valid character
            if (in_byte >= CHAR_A) begin
              //A - F
              o_in_data_count  <= (o_in_data_count[23:0]) + (in_byte - CHAR_HEX_OFFSET); 
            end
            else begin
              o_in_data_count  <= (o_in_data_count[23:0]) + (in_byte - CHAR_0);
            end
            if (in_nibble_count >= 6) begin
              in_nibble_count   <= 4'h0;
              in_state      <= READ_CONTROL;
            end
            else begin
              in_nibble_count <= in_nibble_count + 1;
            end
          end
        end
      end
      READ_CONTROL: begin
      if (in_byte_available) begin
        if ((in_byte < CHAR_0) || 
          ((in_byte > CHAR_0 + 10) && (in_byte < CHAR_A)) || 
          (in_byte > CHAR_F)) begin
          /*
          something went wrong reset... this code could be put
          outside all of the states, but within the state its
          easier to understand the code
          */
          in_state    <=    READ_ID;
        end
        else begin
          /*
          read a in_byte, increment the count and put data into the
          command register MSB first
          */
          if (in_byte >= CHAR_A) begin
            //A - F value
            o_in_command    <= (o_in_command[31:0] << 4) + (in_byte - CHAR_HEX_OFFSET);
          end
          else begin
            //0-9 value
            o_in_command    <= (o_in_command[31:0] << 4) + (in_byte - CHAR_0);
          end

          if (in_nibble_count >= 7) begin
           in_state      <= READ_ADDRESS;
           in_nibble_count   <= 4'h0;
         end
         else begin
           in_nibble_count   <= in_nibble_count + 1; 
         end
  
                 end
             end
         end
         READ_ADDRESS: begin
             //read the size
             if (in_byte_available) begin
                 if ((in_byte < CHAR_0) || 
         ((in_byte > CHAR_0 + 10) && (in_byte < CHAR_A)) || 
         (in_byte > CHAR_F)) begin
         /*
         something went wront reset... this code could be put
         outside all of the states, but within the state its
         easier to understand the code
         */
                     in_state    <=    READ_ID;
                 end
                 else begin
         if (in_byte >= CHAR_A) begin
           //A - F value
           o_in_address    <= (o_in_address[31:0] << 4) + (in_byte - CHAR_HEX_OFFSET);
         end
         else begin
           //0-9 value
           o_in_address    <= (o_in_address[31:0] << 4) + (in_byte - CHAR_0);
         end
     
       
         if (in_nibble_count >= 7) begin
           in_state      <= READ_DATA;
           in_nibble_count   <= 4'h0;
         end
         else begin
           in_nibble_count   <= in_nibble_count + 1;
         end
                 end                
             end
         end
         READ_DATA : begin
             if (in_byte_available) begin

       if ((in_byte < CHAR_0) || 
         ((in_byte > CHAR_0 + 10) && (in_byte < CHAR_A)) || 
         (in_byte > CHAR_F)) begin
         /*
         something went wrong reset... this code could be put
         outside all of the states, but within the state its
         easier to understand the code
         */
                     in_state    <=    READ_ID;
                 end
                 else begin
         if (in_nibble_count <= 7) begin
           if (in_byte >= CHAR_A) begin
             //A - F value
             o_in_data     <= (o_in_data[31:0] << 4 | (in_byte - CHAR_HEX_OFFSET));
           end
           else begin
             //0-9 value
             o_in_data     <= (o_in_data[31:0] << 4 |  (in_byte - CHAR_0));
           end
             in_nibble_count <= in_nibble_count + 1;
         end
       end
             end //if in byte available
     if (in_nibble_count > 7) begin
       if (i_master_ready) begin
         if (is_writing && o_in_data_count > 0) begin
           o_in_data_count <= o_in_data_count - 1;
         end
         else begin
           in_state      <= IDLE;
         end
         o_ih_ready        <= 1;
         in_nibble_count         <= 4'h0;
       end
     end
   end
         default: begin
             o_in_command         <= 8'h0;
             in_state         <= IDLE;
         end
     endcase
  nd
end





//output handler
always @ (posedge clk) begin

  //uart_out_byte_en should only be high for one clock cycle

  oh_finished               <= 0;
  uart_out_byte_en      <= 0;

  if (rst) begin
    out_state       <=  IDLE;
    out_nibble_count    <=  4'h0;
    out_byte        <=  8'h0;
        li_out_data_count     <= 27'h0;
    li_out_data_count_buf   <= 27'h0;
    li_out_data       <= 32'h0;
    li_out_status       <= 32'h0;
    li_out_address      <= 32'h0;
    uart_wait_for_tx    <= 0;
    o_oh_ready        <= 0;
  end

  else begin
    //don't do anything until the UART is ready
    if (~uart_wait_for_tx & uart_tx_ready) begin
    case (out_state)
      IDLE: begin
        out_byte        <=  8'h0;
        out_nibble_count    <=  4'h0;
        o_oh_ready        <=  1'h1;
        if (i_oh_en) begin
//moved this outside because by the time it reaches this part, the out data_count is
//changed
          li_out_status     <= i_out_status;
          li_out_address    <= i_out_address;
          li_out_data     <= i_out_data;

          out_byte      <= CHAR_S;  
          out_state     <= WRITE_DATA_COUNT; 
          o_oh_ready      <= 0;
          uart_out_byte_en  <= 1;
          uart_wait_for_tx  <= 1;
        end 
        else begin
          li_out_data_count   <= i_out_data_count;
          li_out_data_count_buf <= i_out_data_count;
        end
      end
      WRITE_DATA_COUNT: begin
        if (li_out_data_count_buf[27:24] < 10)begin
          //send character number
          out_byte      <= li_out_data_count_buf[27:24] + CHAR_0;
        end
        else begin
          //send  character hex value
          out_byte      <= li_out_data_count_buf[27:24] + CHAR_HEX_OFFSET;
        end
        li_out_data_count_buf   <= li_out_data_count_buf[27:0] << 4;
        uart_out_byte_en    <= 1;
        uart_wait_for_tx    <= 1;
        if (out_nibble_count >= 6) begin
          out_state     <= WRITE_STATUS;
          out_nibble_count  <= 4'h0;
        end
        else begin
          out_nibble_count    <= out_nibble_count + 1;
        end
      end
      WRITE_STATUS: begin
        //shift the data into the output out_byte one at a time
        if (li_out_status[31:28] < 10)begin
          //send character number
          out_byte      <= li_out_status[31:28] + CHAR_0;
        end
        else begin
          //send  character hex value
          out_byte      <= li_out_status[31:28] + CHAR_HEX_OFFSET;
        end
        li_out_status       <= (li_out_status[31:0] << 4);
        uart_out_byte_en    <= 1;
        uart_wait_for_tx    <= 1;
        if (out_nibble_count >= 7) begin
          out_state     <= WRITE_ADDRESS;
          out_nibble_count  <= 4'h0;
        end
        else begin
          out_nibble_count    <= out_nibble_count + 1;
        end

      end
      WRITE_ADDRESS: begin
        //shift the data into the output out_byte one at a time
        if (li_out_address[31:28] < 10)begin
          //send character number
          out_byte  <= li_out_address[31:28] + CHAR_0;
        end
        else begin
          //send character hex value
          out_byte  <= li_out_address[31:28] + CHAR_HEX_OFFSET;
        end

        li_out_address      <= (li_out_address[31:0] << 4);
        uart_out_byte_en    <= 1;
        uart_wait_for_tx    <= 1;

          if (out_nibble_count >= 7) begin
          out_state     <= WRITE_DATA;
          out_nibble_count  <= 4'h0;
        end
        else begin
          out_nibble_count    <= out_nibble_count + 1;
        end

      end
      WRITE_DATA: begin
        if (out_nibble_count <= 7) begin
          //shift the data into the output out_byte one at a time
          if (li_out_data[31:28] < 10)begin
            //send character number
            out_byte  <= li_out_data[31:28] + CHAR_0;
          end
          else begin
            //send  character hex value
            out_byte  <= li_out_data[31:28] + CHAR_HEX_OFFSET;
          end

          li_out_data         <= (li_out_data[28:0] << 4);
          uart_out_byte_en    <= 1;
          uart_wait_for_tx    <= 1;
          out_nibble_count    <= out_nibble_count + 1;
        end
        //nibble count >= 7
        else begin
                    if (li_out_data_count > 0) begin
            o_oh_ready        <= 1;
            if (i_oh_en) begin
              o_oh_ready      <= 0;
                          li_out_data_count   <= li_out_data_count - 1;
              li_out_data     <= i_out_data;
              out_nibble_count  <= 4'h0;
            end
                    end
                    else begin
              oh_finished   <= 1;
              out_state   <= IDLE;
            out_nibble_count  <= 4'h0;
                    end
        end
      end
      default: begin
          out_state <=  IDLE;
      end
    endcase
    end
  end
  
  if (~uart_tx_ready) begin
    uart_wait_for_tx    <= 0;
  end
end


endmodule
