/*
	Use this to tell sycamore how to populate the Device ROM table
	so that users can interact with your slave

	META DATA

	identification of your device 0 - 65536
	DRT_ID:  1

	flags (read drt.txt in the slave/device_rom_table directory 1 means
	a standard device
	DRT_FLAGS:  1

	number of registers this should be equal to the nubmer of ???
	parameters
	DRT_SIZE:  5

	USER_PARAMETER: DEFAULT_INTERRUPT_MASK
	USER_PARAMETER: DEFAULT_INTERRUPT_EDGE

*/

module wb_gpio#(
  parameter DEFAULT_INTERRUPT_MASK = 0,
  parameter DEFAULT_INTERRUPT_EDGE = 0
  )(
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

  //This interrupt can be controlled from this module or a submodule
  output  reg         o_wbs_int,

  output      [34:32] gpio_out,
  input       [31:0]  gpio_in

);



localparam			GPIO			            =	32'h00000000;
localparam			GPIO_OUTPUT_ENABLE		=	32'h00000001;
localparam			INTERRUPTS		        =	32'h00000002;
localparam			INTERRUPT_ENABLE	    =	32'h00000003;
localparam			INTERRUPT_EDGE        =	32'h00000004;


//gpio registers
reg			[31:0]	gpio_direction;
wire    [31:0]  gpio;

//interrupt registers
reg			[31:0]	interrupts;
reg			[31:0]	interrupt_mask;
reg			[31:0]	interrupt_edge;
reg					    clear_interrupts;


endmodule
