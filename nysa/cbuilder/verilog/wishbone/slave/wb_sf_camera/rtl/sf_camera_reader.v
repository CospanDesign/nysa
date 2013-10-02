module sf_camera_reader (
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


//ppfifo interface
wire  [1:0]           w_write_ready;
reg   [1:0]           r_write_activate;
wire  [23:0]          w_write_fifo_size;
reg                   r_write_strobe;
reg   [23:0]          r_write_count;
reg   [1:0]           r_byte_index;
wire  [7:0]           w_write_data;
wire                  w_locked;

reg   [31:0]          r_pix_count;
reg   [31:0]          r_pix_per_line;
reg   [31:0]          r_hcount;

wire  [31:0]          w_dword_pixel;

reg   [7:0]           r_dword_pixel [3:0];




//Submodules
ppfifo # (
  .DATA_WIDTH       (32                 ),
  .ADDRESS_WIDTH    (10                 )
)camera_fifo        (

  //universal input
  .reset            (rst                ),

  //write side
  .write_clock      (i_pix_clk          ),
  .write_ready      (w_write_ready      ),
  .write_activate   (r_write_activate   ),
  .write_fifo_size  (w_write_fifo_size  ),
  .write_strobe     (r_write_strobe     ),
  .write_data       (w_write_data       ),

  //read side
  .read_clock       (clk                ),
  .read_strobe      (i_fifo_strobe      ),
  .read_ready       (o_fifo_ready       ),
  .read_activate    (o_fifo_activate    ),
  .read_count       (o_fifo_size        ),
  .read_data        (o_fifo_data        )
);


//Asynchronous Logic
always @ (*) begin
  if (rst) begin
    next_state      = IDLE;
  end
  else begin
    case (state)
      IDLE: begin
        next_state  = IDLE;
      end
      CAPTURE: begin
      end
      default: begin
      end
    endcase
  end
end
//Synchronous Logic
always @ (posedge i_pix_clk) begin
  if (rst) begin
    state         <=  IDLE;
  end
  else begin
    state         <=  next_state;
  end
end

always @ (posedge i_pix_clk) begin
  if (rst) begin
    r_write_activate              <=  0;
    r_write_strobe                <=  0;
    r_write_count                 <=  0;
    r_byte_index                  <=  0;
                                 
    r_dword_pixel[0]              <=  0;
    r_dword_pixel[1]              <=  0;
    r_dword_pixel[2]              <=  0;
    r_dword_pixel[3]              <=  0;
                                 
    r_hcount                      <=  0;
    o_captured                    <=  0;
  end                            
  else begin                     
    //Strobes                    
    r_write_strobe                <=  0;
    o_captured                    <=  0;

    //Get an empty FIFO
    if ((w_write_ready > 0) && (r_write_activate == 0)) begin
      r_byte_index                <=  0;
      r_write_count               <=  0;
                                  
      r_dword_pixel[0]            <=  0;
      r_dword_pixel[1]            <=  0;
      r_dword_pixel[2]            <=  0;
      r_dword_pixel[3]            <=  0;

      if (w_write_ready[0] == 1) begin
        r_write_activate[0]       <=  1;
      end
      else begin
        r_write_activate[1]       <=  1;
      end
    end

    if (r_hcount > i_hcount) begin
      o_captured                  <=  0;
      r_hcount                    <=  0;
    end

    //Capture Pixels when hsync is high
    if (i_hsync) begin
      r_dword_pixel[r_byte_index] <=  i_pix_data;
      if (r_byte_index == 3) begin
        //if we hit the double word boundary send this peice of data to the
        //FIFO
        r_write_strobe            <=  1;
        r_write_count             <=  r_write_count + 1;
      end
      r_byte_index                <=  r_byte_index + 1;
    end
    else begin
      //if the hsync line is low we are done with a line capture
      if (r_write_count > 0) begin
        r_byte_index              <=  0;
        r_write_activate          <=  0;
        r_hcount                  <=  r_hcount + 1;
      end
    end
  end
end

endmodule
