//wishbone master interconnect testbench
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

/* Log
  08/30/2012
    -Major overhall of the testbench
    -modfied the way reads and writes happen, now each write requires the
    number of 32-bit data packets even if the user sends only 1
    -there is no more streaming as the data_count will implicity declare
    that a read/write is streaming
    -added the ih_reset which has not been formally defined within the
    system, but will more than likely reset the entire statemachine
  11/12/2011
    -overhauled the design to behave more similar to a real I/O handler
    -changed the timeout to 40 seconds to allow the wishbone master to catch
    nacks
  11/08/2011
    -added interrupt support
*/

`timescale 1 ns/1 ps

`define TIMEOUT_COUNT 40
`define INPUT_FILE "master_input_test_data.txt"
`define OUTPUT_FILE "master_output_test_data.txt"


`define CLK_HALF_PERIOD 1
`define CLK_PERIOD (2 * `CLK_HALF_PERIOD)

`define SLEEP_HALF_CLK #(`CLK_HALF_PERIOD)
`define SLEEP_FULL_CLK #(`CLK_PERIOD)

//Sleep a number of clock cycles
`define SLEEP_CLK(x)  #(x * `CLK_PERIOD)

module wishbone_master_tb (
);

//Virtual Host Interface Signals
reg               clk           = 0;
reg               rst           = 0;
wire              master_ready;
reg               in_ready      = 0;
reg   [31:0]      in_command    = 32'h00000000;
reg   [31:0]      in_address    = 32'h00000000;
reg   [31:0]      in_data       = 32'h00000000;
reg   [27:0]      in_data_count = 0;
reg               out_ready     = 0;
wire              out_en;
wire  [31:0]      out_status;
wire  [31:0]      out_address;
wire  [31:0]      out_data;
wire  [27:0]      out_data_count;
reg               ih_reset      = 0;

//wishbone signals
wire              wbm_we_o;
wire              wbm_cyc_o;
wire              wbm_stb_o;
wire [3:0]        wbm_sel_o;
wire [31:0]       wbm_adr_o;
wire [31:0]       wbm_dat_i;
wire [31:0]       wbm_dat_o;
wire              wbm_ack_o;
wire              wbm_int_i;



//Wishbone Slave 0 (DRT) signals
wire              wbs0_we_o;
wire              wbs0_cyc_o;
wire  [31:0]      wbs0_dat_o;
wire              wbs0_stb_o;
wire  [3:0]       wbs0_sel_o;
wire              wbs0_ack_i;
wire  [31:0]      wbs0_dat_i;
wire  [31:0]      wbs0_adr_o;
wire              wbs0_int_i;


//wishbone slave 1 (Unit Under Test) signals
wire              wbs1_we_o;
wire              wbs1_cyc_o;
wire  [31:0]      wbs1_dat_o;
wire              wbs1_stb_o;
wire  [3:0]       wbs1_sel_o;
wire              wbs1_ack_i;
wire  [31:0]      wbs1_dat_i;
wire  [31:0]      wbs1_adr_o;
wire              wbs1_int_i;

//Local Parameters

localparam        IDLE            = 4'h0;
localparam        EXECUTE         = 4'h1;
localparam        RESET           = 4'h2;
localparam        PING_RESPONSE   = 4'h3;
localparam        WRITE_DATA      = 4'h4;
localparam        WRITE_RESPONSE  = 4'h5;
localparam        GET_WRITE_DATA  = 4'h6;
localparam        READ_RESPONSE   = 4'h7;
localparam        READ_MORE_DATA  = 4'h8;

//Registers/Wires/Simulation Integers
integer           fd_in;
integer           fd_out;
integer           read_count;
integer           timeout_count;
integer           ch;

integer           data_count;

reg [3:0]         state           =   IDLE;
reg               prev_int        = 0;


reg               execute_command;
reg               command_finished;
reg               request_more_data;
reg               request_more_data_ack;
reg     [27:0]    data_write_count;

//Submodules
wishbone_master wm (
  .clk(clk),
  .rst(rst),
  .ih_reset(ih_reset),
  .in_ready(in_ready),
  .in_command(in_command),
  .in_address(in_address),
  .in_data(in_data),
  .in_data_count(in_data_count),
  .out_ready(out_ready),
  .out_en(out_en),
  .out_status(out_status),
  .out_address(out_address),
  .out_data(out_data),
  .out_data_count(out_data_count),
  .master_ready(master_ready),

  .wb_adr_o(wbm_adr_o),
  .wb_dat_o(wbm_dat_o),
  .wb_dat_i(wbm_dat_i),
  .wb_stb_o(wbm_stb_o),
  .wb_cyc_o(wbm_cyc_o),
  .wb_we_o(wbm_we_o),
  .wb_msk_o(wbm_msk_o),
  .wb_sel_o(wbm_sel_o),
  .wb_ack_i(wbm_ack_i),
  .wb_int_i(wbm_int_i)
);

//slave 1
USER_SLAVE s1 (

  .clk(clk),
  .rst(rst),

  .wbs_we_i(wbs1_we_o),
  .wbs_cyc_i(wbs1_cyc_o),
  .wbs_dat_i(wbs1_dat_o),
  .wbs_stb_i(wbs1_stb_o),
  .wbs_ack_o(wbs1_ack_i),
  .wbs_dat_o(wbs1_dat_i),
  .wbs_adr_i(wbs1_adr_o),
  .wbs_int_o(wbs1_int_i)

);

wishbone_interconnect wi (
    .clk(clk),
    .rst(rst),

    .m_we_i(wbm_we_o),
    .m_cyc_i(wbm_cyc_o),
    .m_stb_i(wbm_stb_o),
    .m_ack_o(wbm_ack_i),
    .m_dat_i(wbm_dat_o),
    .m_dat_o(wbm_dat_i),
    .m_adr_i(wbm_adr_o),
    .m_int_o(wbm_int_i),

    .s0_we_o(wbs0_we_o),
    .s0_cyc_o(wbs0_cyc_o),
    .s0_stb_o(wbs0_stb_o),
    .s0_ack_i(wbs0_ack_i),
    .s0_dat_o(wbs0_dat_o),
    .s0_dat_i(wbs0_dat_i),
    .s0_adr_o(wbs0_adr_o),
    .s0_int_i(wbs0_int_i),

    .s1_we_o(wbs1_we_o),
    .s1_cyc_o(wbs1_cyc_o),
    .s1_stb_o(wbs1_stb_o),
    .s1_ack_i(wbs1_ack_i),
    .s1_dat_o(wbs1_dat_o),
    .s1_dat_i(wbs1_dat_i),
    .s1_adr_o(wbs1_adr_o),
    .s1_int_i(wbs1_int_i)
);








always #`CLK_HALF_PERIOD      clk = ~clk;

initial begin
  fd_out                      = 0;
  read_count                  = 0;
  data_count                  = 0;
  timeout_count               = 0;
  request_more_data_ack       <=  0;
  execute_command             <=  0;

  $dumpfile ("design.vcd");
  $dumpvars (0, wishbone_master_tb);
  fd_in                       = $fopen(`INPUT_FILE, "r");
  fd_out                      = $fopen(`OUTPUT_FILE, "w");
  `SLEEP_HALF_CLK;

  rst                         <= 0;
  `SLEEP_CLK(2);
  rst                         <= 1;

  //clear the handler signals
  in_ready                    <= 0;
  in_command                  <= 0;
  in_address                  <= 32'h0;
  in_data                     <= 32'h0;
  in_data_count               <= 0;
  out_ready                   <= 0;
  //clear wishbone signals
  `SLEEP_CLK(10);
  rst                         <= 0;
  out_ready                   <= 1;

  if (fd_in == 0) begin
    $display ("TB: input stimulus file was not found");
  end
  else begin
    //while there is still data to be read from the file
    while (!$feof(fd_in)) begin
      //read in a command
      read_count              = $fscanf (fd_in, "%h:%h:%h:%h\n", in_data_count, in_command, in_address, in_data);

      if (read_count != 4) begin
        ch = $fgetc(fd_in);
        if (read_count == 1) begin
          $display ("Sleep for %h Clock cycles" % in_data_count);
          `SLEEP_CLK(in_data_count);
        end
        else begin
          $display ("Error: read_count = %h != 4", read_count);
          $display ("Character: %h", ch);
        end
      end
      else begin
        case (in_command)
          0: $display ("TB: Executing PING commad");
          1: $display ("TB: Executing WRITE command");
          2: $display ("TB: Executing READ command");
          3: $display ("TB: Executing RESET command");
        endcase
        execute_command                 <= 1;
        `SLEEP_CLK(1);
        while (~command_finished) begin
          request_more_data_ack         <= 0;

          if ((in_command & 32'h0000FFFF) == 1) begin
            if (request_more_data && ~request_more_data_ack) begin
              read_count      = $fscanf(fd_in, "%h\n", in_data);
              $display ("TB: reading a new double word: %h", in_data);
              request_more_data_ack     <= 1;
            end
          end

          //so time porgresses wait a tick
          `SLEEP_CLK(1);
          //this doesn't need to be here, but there is a weird behavior in iverilog
          //that wont allow me to put a delay in right before an 'end' statement
          execute_command <= 1;
        end //while command is not finished
        while (command_finished) begin
          `SLEEP_CLK(1);
          execute_command <= 0;
        end
        `SLEEP_CLK(50);
        $display ("TB: finished command");
      end //end read_count == 4
    end //end while ! eof
  end //end not reset
  `SLEEP_CLK(50);
  $fclose (fd_in);
  $fclose (fd_out);
  $finish();
end
//initial begin
//    $monitor("%t, state: %h", $time, state);
//end

always @ (posedge clk) begin
  if (rst) begin
    state                     <= IDLE;
    request_more_data         <= 0;
    timeout_count             <= 0;
    prev_int                  <= 0;
    ih_reset                  <= 0;
    data_write_count          <=  0;
  end
  else begin
    ih_reset                  <= 0;
    in_ready                  <= 0;
    out_ready                 <= 1;
    command_finished          <= 0;

    //Countdown the NACK timeout
    if (execute_command && timeout_count > 0) begin
      timeout_count           <= timeout_count - 1;
    end

    if (execute_command && timeout_count == 0) begin
      case (in_command)
        0: $display ("TB: Master timed out while executing PING commad");
        1: $display ("TB: Master timed out while executing WRITE command");
        2: $display ("TB: Master timed out while executing READ command");
        3: $display ("TB: Master timed out while executing RESET command");
      endcase

      state                   <= IDLE;
      command_finished        <= 1;
      timeout_count           <= `TIMEOUT_COUNT;
      data_write_count        <= 1;
    end //end reached the end of a timeout

    case (state)
      IDLE: begin
        if (execute_command & ~command_finished) begin
          $display ("TB: #:C:A:D = %h:%h:%h:%h", in_data_count, in_command, in_address, in_data);
          timeout_count       <= `TIMEOUT_COUNT;
          state               <= EXECUTE;
        end
      end
      EXECUTE: begin
        if (master_ready) begin
          //send the command over
          in_ready            <= 1;
          case (in_command & 32'h0000FFFF)
            0: begin
              //ping
              state           <=  PING_RESPONSE;
            end
            1: begin
              //write
              if (in_data_count > 1) begin
                $display ("TB: \tWrote double word %d: %h", data_write_count, in_data);
                state                   <=  WRITE_DATA;
                timeout_count           <= `TIMEOUT_COUNT;
                data_write_count        <=  data_write_count + 1;
              end
              else begin
                if (data_write_count > 1) begin
                  $display ("TB: \tWrote double word %d: %h", data_write_count, in_data);
                end
                state                   <=  WRITE_RESPONSE;
              end
            end
            2: begin
              //read
              state           <=  READ_RESPONSE;
            end
            3: begin
              //reset
              state           <=  RESET;
            end
          endcase
        end
      end
      RESET: begin
        //reset the system
        ih_reset                    <=  1;
        command_finished            <=  1;
        state                       <=  IDLE;
      end
      PING_RESPONSE: begin
        if (out_en) begin
          if (out_status == (~(32'h00000000))) begin
            $display ("TB: Read a successful ping reponse");
          end
          else begin
            $display ("TB: Ping response is incorrect!");
          end
          $display ("TB: \tS:A:D = %h:%h:%h\n", out_status, out_address, out_data);
          command_finished  <= 1;
          state                     <=  IDLE;
        end
      end
      WRITE_DATA: begin
        if (!in_ready && master_ready) begin
          state                     <=  GET_WRITE_DATA;
          request_more_data         <=  1;
        end
      end
      WRITE_RESPONSE: begin
        if (out_en) begin
         if (out_status == (~(32'h00000001))) begin
            $display ("TB: Read a successful write reponse");
          end
          else begin
            $display ("TB: Write response is incorrect!");
          end
          $display ("TB: \tS:A:D = %h:%h:%h\n", out_status, out_address, out_data);
          state                   <=  IDLE;
          command_finished  <= 1;
        end
      end
      GET_WRITE_DATA: begin
        if (request_more_data_ack) begin
//XXX: should request more data be a strobe?
          request_more_data   <=  0;
          in_ready            <=  1;
          in_data_count       <=  in_data_count -1;
          state               <=  EXECUTE;
        end
      end
      READ_RESPONSE: begin
        if (out_en) begin
          if (out_status == (~(32'h00000002))) begin
            $display ("TB: Read a successful read response");
            if (out_data_count > 0) begin
              state             <=  READ_MORE_DATA;
              //reset the NACK timeout
              timeout_count     <=  `TIMEOUT_COUNT;
            end
            else begin
              state             <=  IDLE;
              command_finished  <= 1;
            end
          end
          else begin
            $display ("TB: Read response is incorrect");
            command_finished  <= 1;
          end
          $display ("TB: \tS:A:D = %h:%h:%h\n", out_status, out_address, out_data);
        end
      end
      READ_MORE_DATA: begin
        if (out_en) begin
          out_ready             <=  0;
          if (out_status == (~(32'h00000002))) begin
            $display ("TB: Read a 32bit data packet");
            $display ("Tb: \tRead Data: %h", out_data);
          end
          else begin
            $display ("TB: Read reponse is incorrect");
          end

          //read the output data count to determine if there is more data
          if (out_data_count == 0) begin
            state             <=  IDLE;
            command_finished  <=  1;
          end
        end
      end
      default: begin
        $display ("TB: state is wrong");
        state <= IDLE;
      end //somethine wrong here
    endcase //state machine
    if (out_en && out_status == `PERIPH_INTERRUPT) begin
      $display("TB: Output Handler Recieved interrupt");
      $display("TB:\tcommand: %h", out_status);
      $display("TB:\taddress: %h", out_address);
      $display("TB:\tdata: %h", out_data);
    end
  end//not reset
end

endmodule
