module sf_camera (
input                 clk,
input                 rst,

//Core Configuration Signals
input       [31:0]    i_control,
output                o_captured,

//Memory FIFO Interface
output                o_enable_dma,

output                o_rfifo_ready,
input                 i_rfifo_activate,
input                 i_rfifo_strobe,
output      [31:0]    o_rfifo_data,
output      [23:0]    o_rfifo_size,

//Physical Interface
output                o_cam_rst,
output                o_flash,
output                o_status,

output                o_cam_in_clk,
input                 i_pix_clk,
input                 i_flash_strobe,
input                 i_vsync,
input                 i_hsync,
input       [7:0]     i_pix_data
);

//Local Parameters
//Registers/Wires
wire                w_enable_reader;

//Ping Pong FIFO Write Side
sf_camera_controller controller(
  .clk                  (clk                      ),
  .rst                  (rst                      ),

  //Physical Interface
  .o_cam_rst            (o_cam_rst                ),
  .o_flash              (o_flash                  ),
  .o_status             (o_status                 ),

  //Camera Controlled Flash Signal
  .i_flash_strobe       (i_flash_strobe           ),

  .o_cam_in_clk         (o_cam_in_clk             ),

  //Configuration Registers
  .i_control            (i_control                ),
  .i_captured           (o_captured               ),


  //Core Controller
  .o_enable_dma         (o_enable_dma             ),
  .o_enable_reader      (w_enable_reader          )
);

sf_camera_reader reader(
  .clk                  (clk                      ),
  .rst                  (rst                      ),

  .i_enable             (w_enable_reader          ),

  //Physical Interface
  .i_pix_clk            (i_pix_clk                ),
  .i_vsync              (i_vsync                  ),
  .i_hsync              (i_hsync                  ),
  .i_pix_data           (i_pix_data               ),

  //read
  .i_rfifo_strobe       (i_rfifo_strobe           ),
  .o_rfifo_ready        (o_rfifo_ready            ),
  .i_rfifo_activate     (i_rfifo_activate         ),
  .o_rfifo_size         (o_rfifo_size             ),
  .o_rfifo_data         (o_rfifo_data             )
);

//Asynchronous Logic
//Synchronous Logic

endmodule
