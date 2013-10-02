module sf_camera_controller (
input                 clk,
input                 rst,

//Physical Interface
output                o_cam_rst,
output                o_flash,
output                o_status,
input                 i_flash_strobe,

output                o_cam_in_clk,

//Configuration Registers
input       [31:0]    i_control,
input                 i_captured,

//Core Controller
output  reg           o_enable_dma,
output  reg           o_enable_reader

);

//Local Parameters

//Registers/Wires
reg   [3:0]           state;
reg   [3:0]           next_state;


wire                  w_locked;

//Submodules
//20MHz Clock Genertors
sf_camera_clk_gen clk_gen(
  .clk              (clk                ),
  .rst              (rst                ),
  .locked           (w_locked           ),
  .phy_out_clk      (o_cam_in_clk       )
);

//Asynchronous Logic
//Synchronous Logic
always @ (posedge clk) begin
  if (rst) begin
    o_enable_dma    <=  0;
    o_enable_reader <=  0;
  end
  else begin
  end
end

endmodule
