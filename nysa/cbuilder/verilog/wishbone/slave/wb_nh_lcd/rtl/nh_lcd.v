`include "project_defines.v"

module nh_lcd #(
  parameter           BUFFER_SIZE = 12
)(
  input               rst,
  input               clk,

  output      [31:0]  debug,

  //Control Signals
  input               i_enable,
  input               i_reset_display,
  input               i_data_command_mode,
  input               i_cmd_write_stb,
  input               i_cmd_read_stb,
  input       [7:0]   i_cmd_data,
  output      [7:0]   o_cmd_data,
  output              o_cmd_finished,
  input               i_backlight_enable,
  input       [31:0]  i_num_pixels,

  //FIFO Signals
  output      [1:0]   o_fifo_rdy,
  input       [1:0]   i_fifo_act,
  input               i_fifo_stb,
  output      [23:0]  o_fifo_size,
  input       [31:0]  i_fifo_data,

  //Physical Signals
  output              o_backlight_enable,
  output              o_register_data_sel,
  output              o_write_n,
  output              o_read_n,
  inout       [7:0]   io_data,
  output              o_cs_n,
  output              o_reset_n,
  input               i_tearing_effect,
  output              o_display_on
);

//Local Parameters
//Registers/Wires
wire  [7:0]           w_data_out;
wire  [7:0]           w_data_in;

wire                  w_cmd_write;
wire                  w_cmd_read;
wire  [7:0]           w_cmd_data;

wire                  w_cmd_en_write;

wire                  w_data_dir;

wire                  w_data_cmd_mode;
wire  [7:0]           w_data_data;
wire                  w_data_write;

//Submodules
nh_lcd_command lcd_commander (

  .rst                  (rst                  ),
  .clk                  (clk                  ),

//  .debug              (debug                ),

  .i_enable             (i_enable             ),
  .i_cmd_write_stb      (i_cmd_write_stb      ),
  .i_cmd_read_stb       (i_cmd_read_stb       ),
  .i_cmd_data           (i_cmd_data           ),
  .o_cmd_data           (o_cmd_data           ),

  //Control Signals
  .o_cmd_en_write       (w_cmd_en_write       ),
  .o_cmd_finished       (o_cmd_finished       ),


  .o_write              (w_cmd_write          ),
  .o_read               (w_cmd_read           ),
  .o_data_out           (w_cmd_data           ),
  .i_data_in            (w_data_in            )
);

nh_lcd_data_writer #(
  .BUFFER_SIZE          (BUFFER_SIZE          )
)lcd_data_writer(
  .rst                  (rst                  ),
  .clk                  (clk                  ),

//  .debug              (debug                ),

  .i_enable             (i_enable             ),
  .i_num_pixels         (i_num_pixels         ),

  .o_fifo_rdy           (o_fifo_rdy           ),
  .i_fifo_act           (i_fifo_act           ),
  .i_fifo_stb           (i_fifo_stb           ),
  .o_fifo_size          (o_fifo_size          ),
  .i_fifo_data          (i_fifo_data          ),

  .i_tearing_effect     (i_tearing_effect     ),
  .o_data_cmd_mode      (w_data_cmd_mode      ),
  .o_data               (w_data_data          ),
  .o_write              (w_data_write         )



);

//Asynchronous Logic
assign  o_backlight_enable  = i_backlight_enable;
assign  o_display_on        = i_enable;
assign  o_reset_n           = ~i_reset_display;

assign  o_register_data_sel = i_data_command_mode && !w_data_cmd_mode;


assign  w_data_dir          = (i_data_command_mode || w_cmd_en_write);
assign  io_data             = (w_data_dir) ? w_data_out : 8'hZZ;
assign  w_data_in           = (w_data_dir) ? 8'hZZ: io_data;

assign  w_data_out          = (i_data_command_mode) ? w_data_data   : w_cmd_data;

assign  o_write_n           = (i_data_command_mode) ? ~w_data_write : ~w_cmd_write;
assign  o_read_n            = (i_data_command_mode) ? 1             : ~w_cmd_read;

assign  o_cs_n              = ~i_enable;

//Synchronous Logic
endmodule
