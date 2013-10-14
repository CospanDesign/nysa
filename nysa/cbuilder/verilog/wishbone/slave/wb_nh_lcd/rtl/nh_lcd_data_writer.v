`include "nh_lcd_defines.v"

module nh_lcd_data_writer#(
  parameter           BUFFER_SIZE = 12
)(
  input               rst,
  input               clk,

  output      [7:0]   debug,

  //Control
  input               i_enable,
  input       [31:0]  i_num_pixels,

  //FIFO Signals
  output      [1:0]   o_fifo_rdy,
  input       [1:0]   i_fifo_act,
  input               i_fifo_stb,
  output      [23:0]  o_fifo_size,
  input       [31:0]  i_fifo_data,

  //Physical Signals
  input               i_tearing_effect,
  output  reg         o_data_cmd_mode,
  output  reg [7:0]   o_data,
  output  reg         o_write
);

//Local Parameters
localparam  IDLE              = 4'h0;
localparam  WRITE_ADDRESS     = 4'h1;
localparam  WRITE_RED_START   = 4'h2;
localparam  WRITE_RED         = 4'h3;
localparam  WRITE_GREEN_START = 4'h4;
localparam  WRITE_GREEN       = 4'h5;
localparam  WRITE_BLUE_START  = 4'h6;
localparam  WRITE_BLUE        = 4'h7;

//Registers/Wires
reg           [3:0]   state;

wire          [7:0]   w_red;
wire          [7:0]   w_green;
wire          [7:0]   w_blue;

reg                   r_read_stb;
wire                  w_read_rdy;
reg                   r_read_act;
wire          [23:0]  w_read_size;
wire          [31:0]  w_read_data;

reg           [23:0]  r_read_count;
reg           [31:0]  r_pixel_count;


//Submodules
//generate a Ping Pong FIFO to cross the clock domain
ppfifo #(
  .DATA_WIDTH(32),
`ifndef SIMULATION
  .ADDRESS_WIDTH(BUFFER_SIZE)
`else
  .ADDRESS_WIDTH(2)
`endif
)ping_pong (

  .reset           (rst               ),

  //write
  .write_clock     (clk               ),
  .write_ready     (o_fifo_rdy        ),
  .write_activate  (i_fifo_act        ),
  .write_fifo_size (o_fifo_size       ),
  .write_strobe    (i_fifo_stb        ),
  .write_data      (i_fifo_data       ),

  //.starved         (starved           ),

  //read
  .read_clock      (clk               ),
  .read_strobe     (r_read_stb        ),
  .read_ready      (w_read_rdy        ),
  .read_activate   (r_read_act        ),
  .read_count      (w_read_size       ),
  .read_data       (w_read_data       )
);


//Asynchronous Logic
assign  w_red   = w_read_data[23:16];
assign  w_green = w_read_data[15:8];
assign  w_blue  = w_read_data[7:0];

//Synchronous Logic
always @ (posedge clk) begin
  if (rst) begin
    o_data              <=  0;
    o_write             <=  0;
    state               <=  IDLE;
    o_data_cmd_mode     <=  0;

    r_read_count        <=  0;
    r_read_stb          <=  0;
    r_read_act          <=  0;
    r_pixel_count       <=  0;
  end
  else begin
    //Strobes
    o_write             <=  0;
    r_read_stb          <=  0;

    //Get a ping pong FIFO
    if (w_read_rdy && !r_read_act) begin
      r_read_count      <=  0;
      r_read_act        <=  1;
    end

    case (state)
      IDLE: begin
        //Is there going to be some weird behavior with the state machine
        if ((r_pixel_count >= i_num_pixels) || !i_enable) begin
          r_pixel_count     <=  0;
        end
        //Start a transaction
        if (i_enable && r_read_act) begin
          if (r_pixel_count == 0) begin
            //We are at the beginning of a Frame, need to start writing to the
            //first address
            o_data_cmd_mode <=  1;
            o_write         <=  1;
            o_data          <=  `CMD_START_MEM_WRITE;
            state           <=  WRITE_ADDRESS;
          end
          else begin
            state           <=  WRITE_RED_START;
          end
        end
      end
      WRITE_ADDRESS: begin
        state               <=  WRITE_RED_START;
      end
      WRITE_RED_START: begin
        if (i_tearing_effect) begin
          o_write             <=  1;
          o_data              <=  w_red;
          state               <=  WRITE_RED;
        end
      end
      WRITE_RED: begin
        state               <=  WRITE_GREEN_START;
      end
      WRITE_GREEN_START: begin
        if (i_tearing_effect) begin
          o_write             <=  1;
          o_data              <=  w_green;
          state               <=  WRITE_GREEN;
        end
      end
      WRITE_GREEN: begin
        state               <=  WRITE_BLUE_START;
      end
      WRITE_BLUE_START: begin
        if (i_tearing_effect) begin
          o_write             <=  1;
          o_data              <=  w_blue;
          state               <=  WRITE_BLUE;
        end
      end
      WRITE_BLUE: begin
        r_pixel_count       <=  r_pixel_count + 1;
        if (r_read_count < w_read_size - 1) begin
          r_read_count      <=  r_read_count + 1;
          r_read_stb        <=  1;
          state             <=  WRITE_RED_START;
        end
        else begin
          r_read_act        <=  0;
          state             <=  IDLE;
        end
      end
    endcase
  end
end

endmodule
