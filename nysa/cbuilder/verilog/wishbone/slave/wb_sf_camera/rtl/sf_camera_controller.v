module sf_camera_controller (
input                 clk,
input                 rst,

//Physical Interface
output                o_cam_rst,
output                o_flash,
output                o_status,

output                o_cam_in_clk,
input                 i_pix_clk,
input                 i_flag_strobe,
input                 i_vsync,
input                 i_hsync,
input       [7:0]     i_pix_data,

//Memory FIFO Interface
output                o_fifo_ready,
input                 o_fifo_activate,
input                 i_fifo_strobe,
output      [31:0]    o_fifo_data,
output      [23:0]    o_fifo_size,


//Configuration Registers
input       [31:0]    i_control,
output  reg           o_captured,
input       [31:0]    i_hcount

);

//Local Parameters
localparam  IDLE            = 0;
localparam  CAPTURE         = 1;
localparam  READ_HORIZONTAL = 2;
localparam  SEND_TO_MEM     = 3;
localparam  IMAGE_CAPTURED  = 4;

//Registers/Wires
reg   [3:0]           state;
reg   [3:0]           next_state;


wire                  w_locked;

//20MHz Clock Genertors
sf_camera_clk_gen clk_gen(
  .clk              (clk                ),
  .rst              (rst                ),
  .locked           (w_locked           ),
  .phy_out_clk      (o_cam_in_clk       )
);


endmodule
