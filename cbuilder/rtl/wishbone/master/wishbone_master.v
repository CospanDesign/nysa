//wishbone_master
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
    -added the ih_reset port to indicate that the input handler is resetting
    the incomming data state machine
  02/02/2012
    -changed the read state machine to use local_data_count instead of out_data_count
  11/12/2011
    -added support for burst read and writes
    -added support for nacks when the slave doesn't respond in time
  11/07/2011
    -added interrupt handling to the master
    -when the master is idle the interconnect will output the interrupt 
      on the wbs data
  10/30/2011
    -fixed the memory bus issue where that master was not responding 
      to a slave ack
    -changed the READ and WRITE command to call either the memory 
      bus depending on the
    flags in the command sent from the user
  10/25/2011
    -added the interrupt input pin for both busses
  10/23/2011
    -commented out the debug message "GOT AN ACK!!", we're passed this
  10/26/2011
    -removed the stream commands, future versions will use flags instead of separate commands
*/
`include "mg_defines.v"

module wishbone_master (
  clk,
  rst,

  //indicate to the input that we are ready
  master_ready,

  //input handler interface
  in_ready,
  ih_reset,
  in_command,
  in_address,
  in_data,
  in_data_count,

  //output handler interface
  out_ready,
  out_en,
  out_status,
  out_address,
  out_data,
  out_data_count,

  //stimulus input
  //debug output
  debug_out,

  //wishbone signals
  wb_adr_o,
  wb_dat_o,
  wb_dat_i,
  wb_stb_o,
  wb_cyc_o,
  wb_we_o,
  wb_msk_o,
  wb_sel_o,
  wb_ack_i,
  wb_int_i,

  //wishbone memory signals
  mem_adr_o,
  mem_dat_o,
  mem_dat_i,
  mem_stb_o,
  mem_cyc_o,
  mem_we_o,
  mem_msk_o,
  mem_sel_o,
  mem_ack_i,
  mem_int_i
  );

  input               clk;
  input               rst;

  output reg          master_ready;
  input               in_ready;
  input               ih_reset;
  input       [31:0]  in_command;
  input       [31:0]  in_address;
  input       [31:0]  in_data;
  input       [27:0]  in_data_count;

  input               out_ready;
  output reg          out_en      = 0;
  output reg  [31:0]  out_status    = 32'h0;
  output reg  [31:0]  out_address   = 32'h0;
  output reg  [31:0]  out_data    = 32'h0;
  output wire [27:0]  out_data_count;

  //debug output
  output reg  [31:0]  debug_out;
  
  //wishbone
  output reg  [31:0]  wb_adr_o;
  output reg  [31:0]  wb_dat_o;
  input       [31:0]  wb_dat_i;
  output reg          wb_stb_o;
  output reg          wb_cyc_o;
  output reg          wb_we_o;
  output reg          wb_msk_o;
  output reg  [3:0]   wb_sel_o;
  input               wb_ack_i;
  input               wb_int_i;

  //wishbone memory bus
  output reg  [31:0]  mem_adr_o;
  output reg  [31:0]  mem_dat_o;
  input       [31:0]  mem_dat_i;
  output reg          mem_stb_o;
  output reg          mem_cyc_o;
  output reg          mem_we_o;
  output reg          mem_msk_o;
  output reg  [3:0]   mem_sel_o;
  input               mem_ack_i;
  input               mem_int_i;


  //parameters
  parameter       IDLE                  = 32'h00000000;
  parameter       WRITE                 = 32'h00000001;
  parameter       READ                  = 32'h00000002;
  parameter       DUMP_CORE             = 32'h00000003;

  parameter       S_PING_RESP           = 32'h0000C594;

  parameter       DUMP_COUNT            = 14;


  // registers

  reg [31:0]          state             = IDLE;
  reg [31:0]          local_address     = 32'h0;
  reg [31:0]          local_data        = 32'h0;
  reg [27:0]          local_data_count  = 27'h0;
  reg                 mem_bus_select;

  reg [31:0]          master_flags      = 32'h0;
  reg [31:0]          rw_count          = 32'h0;
  reg                 wait_for_slave    = 0;


  reg                 prev_int          = 0;


  reg                 interrupt_mask    = 32'h00000000;

  reg [31:0]          nack_timeout      = `DEF_NACK_TIMEOUT; 
  reg [31:0]          nack_count        = 0;

  //core dump
  reg [31:0]          dump_count        = 0;

  reg [31:0]          dump_state        = 0;
  reg [31:0]          dump_status       = 0;
  reg [31:0]          dump_flags        = 0;
  reg [31:0]          dump_nack_count   = 0;
  reg [31:0]          dump_lcommand     = 0;
  reg [31:0]          dump_laddress     = 0;
  reg [31:0]          dump_ldata_count  = 0;
  reg [31:0]          dump_wb_state     = 0;
  reg [31:0]          dump_wb_p_addr    = 0;
  reg [31:0]          dump_wb_p_dat_in  = 0;
  reg [31:0]          dump_wb_p_dat_out = 0;
  reg [31:0]          dump_wb_m_addr    = 0;
  reg [31:0]          dump_wb_m_dat_in  = 0;
  reg [31:0]          dump_wb_m_dat_out = 0;

  reg                 prev_reset        = 0;

  // wires
  wire [15:0]         command_flags;
  wire                enable_nack;

  wire [15:0]         real_command;

  wire                pos_edge_reset;

  // assigns
  assign              out_data_count    = ((state == READ) || (state == DUMP_CORE)) ? local_data_count : 0;
  assign              command_flags     = in_command[31:16];
  assign              real_command      = in_command[15:0];

  assign              enable_nack       = master_flags[0];

  assign              pos_edge_reset    = rst & ~prev_reset;


initial begin
    //$monitor("%t, int: %h, ih_ready: %h, ack: %h, stb: %h, cyc: %h", $time, wb_int_i, in_ready, wb_ack_i, wb_stb_o, wb_cyc_o);
    //$monitor("%t, cyc: %h, stb: %h, ack: %h, in_ready: %h, out_en: %h, master_ready: %h", $time, wb_cyc_o, wb_stb_o, wb_ack_i, in_ready, out_en, master_ready);
end


//blocks
always @ (posedge clk) begin
    
  out_en              <= 0;

//master ready should be used as a flow control, for now its being reset every
//clock cycle, but in the future this should be used to regulate data comming in so that the master can send data to the slaves without overflowing any buffers
  //master_ready  <= 1;
  if (pos_edge_reset) begin
    dump_state        <=  state;
    dump_status       <=  {26'h0, ih_reset, out_ready, out_en, in_ready, master_ready, mem_bus_select};
    dump_flags        <=  master_flags;
    dump_nack_count   <=  nack_count;
    dump_lcommand     <=  {command_flags, real_command};
    dump_laddress     <=  in_address;
    dump_ldata_count  <=  local_data_count;
    dump_wb_state     <=  {11'h0, wb_cyc_o, wb_stb_o, wb_we_o, wb_ack_i, wb_int_i,  12'h0, mem_cyc_o, mem_stb_o, mem_we_o, mem_ack_i};
    dump_wb_p_addr    <=  wb_adr_o;
    dump_wb_p_dat_in  <=  wb_dat_i;
    dump_wb_p_dat_out <=  wb_dat_o;
    dump_wb_m_addr    <=  mem_adr_o;
    dump_wb_m_dat_in  <=  mem_dat_i;
    dump_wb_m_dat_out <=  mem_dat_o;



  end

  if (rst || ih_reset) begin



    out_status        <= 32'h0;
    out_address       <= 32'h0;
    out_data          <= 32'h0;
    //out_data_count  <= 28'h0;
    local_address     <= 32'h0;
    local_data        <= 32'h0;
    local_data_count  <= 27'h0;
    master_flags      <= 32'h0;
    rw_count          <= 0;
    state             <= IDLE;
    mem_bus_select    <= 0;
    prev_int          <= 0;

    wait_for_slave    <= 0;

    debug_out         <= 32'h00000000;

    //wishbone reset
    wb_adr_o          <= 32'h0;
    wb_dat_o          <= 32'h0;
    wb_stb_o          <= 0;
    wb_cyc_o          <= 0;
    wb_we_o           <= 0;
    wb_msk_o          <= 0;

    //select is always on
    wb_sel_o          <= 4'hF;

    //wishbone memory reset
    mem_adr_o         <= 32'h0;
    mem_dat_o         <= 32'h0;
    mem_stb_o         <= 0;
    mem_cyc_o         <= 0;
    mem_we_o          <= 0;
    mem_msk_o         <= 0;

    //select is always on
    mem_sel_o         <= 4'hF;

    //interrupts
    interrupt_mask    <= 32'h00000000;
    nack_timeout      <= `DEF_NACK_TIMEOUT;
    nack_count        <= 0;


  end

  else begin 
    
    //check for timeout conditions
    if (nack_count == 0) begin
      if (state != IDLE && enable_nack) begin
        debug_out[4]  <= ~debug_out[4];
        $display ("WBM: Timed out");
        //timeout occured, send a nack and go back to IDLE
        state         <= IDLE;
        out_status    <= `NACK_TIMEOUT;
        out_address   <= 32'h00000000;
        out_data      <= 32'h00000000;
        out_en        <= 1;
      end
    end
    else begin
      nack_count <= nack_count - 1;
    end

    //check if the input handler reset us
    case (state)
      READ: begin
        if (mem_bus_select) begin
          if (mem_ack_i) begin
            //put the strobe down to say we got that double word
            mem_stb_o <= 0;
          end
          else if (~mem_stb_o && out_ready) begin
            $display("WBM: local_data_count = %h", local_data_count);
            out_data    <= mem_dat_i;
            out_en      <= 1; 
            if (local_data_count > 1) begin
              debug_out[9]  <=  ~debug_out[9];
              //finished the next double word
              nack_count    <= nack_timeout;
              local_data_count  <= local_data_count -1;
              mem_adr_o   <= mem_adr_o + 4;
              mem_stb_o   <= 1;
              //initiate an output transfer
            end
            else begin
              //finished all the reads de-assert the cycle
              debug_out[10]  <=  ~debug_out[10];
              mem_cyc_o   <=  0;
              state       <=  IDLE;
            end
          end
        end
        else begin
          //Peripheral BUS
          if (wb_ack_i) begin
            wb_stb_o    <= 0;
          end
          else if (~wb_stb_o && out_ready) begin
            $display("WBM: local_data_count = %h", local_data_count);
           //put the data in the otput
           out_data    <= wb_dat_i;
           //tell the io_handler to send data
           out_en    <= 1; 

            if (local_data_count > 1) begin
              debug_out[8]  <=  ~debug_out[8];
//the nack count might need to be reset outside of these conditionals becuase
//at this point we are waiting on the io handler
              nack_count    <= nack_timeout;
              local_data_count  <= local_data_count - 1;
              wb_adr_o    <= wb_adr_o + 1;
              wb_stb_o    <= 1;
            end
            else begin
              //finished all the reads, put de-assert the cycle
              debug_out[7]  <= ~debug_out[7];
              wb_cyc_o    <= 0;
              state       <= IDLE;
            end
          end
        end
      end
      WRITE: begin
        if (mem_bus_select) begin
          if (mem_ack_i) begin
            mem_stb_o    <= 0;
            if (local_data_count <= 1) begin
              //finished all writes 
              $display ("WBM: in_data_count == 0");
              debug_out[12] <=  ~debug_out[12];
              mem_cyc_o <= 0;
              state   <= IDLE;
              out_en    <= 1;
              mem_we_o  <= 0;
            end
            //tell the IO handler were ready for the next one
            master_ready  <=  1;
          end
          else if ((local_data_count > 1) && in_ready && (mem_stb_o == 0)) begin
            local_data_count  <= local_data_count - 1;
            $display ("WBM: (burst mode) writing another double word");
            master_ready  <=  0;
            mem_stb_o   <= 1;
            mem_adr_o   <= mem_adr_o + 4;
            mem_dat_o   <= in_data;
            nack_count    <= nack_timeout;
            debug_out[13] <=  ~debug_out[13];
          end
        end //end working with mem_bus
        else begin //peripheral bus
          if (wb_ack_i) begin
            wb_stb_o              <= 0;
            if (local_data_count  <= 1) begin
              $display ("WBM: in_data_count == 0");
              wb_cyc_o            <= 0;
              state               <= IDLE;
              out_en              <= 1;
              wb_we_o             <= 0;
            end
            //tell the IO handler were ready for the next one
            master_ready  <= 1;
          end
          else if ((local_data_count > 1) && in_ready && (wb_stb_o == 0)) begin 
            local_data_count <= local_data_count - 1;
            debug_out[5]  <= ~debug_out[5];
            $display ("WBM: (burst mode) writing another double word");
            master_ready  <=  0;
            wb_stb_o    <= 1;
            wb_adr_o    <= wb_adr_o + 1;
            wb_dat_o    <= in_data;
            nack_count    <= nack_timeout;
          end
        end
      end
      DUMP_CORE: begin
        if (out_ready && !out_en) begin
          case (dump_count)
            0:  begin
              out_data          <=  dump_state;
            end
            1:  begin
              out_data          <=  dump_status;
            end
            2:  begin
              out_data          <=  dump_flags;
            end
            3:  begin
              out_data          <=  dump_nack_count;
            end
            4:  begin
              out_data          <=  dump_lcommand;
            end
            5:  begin
              out_data          <=  dump_laddress;
            end
            6:  begin
              out_data          <=  dump_ldata_count;
            end
            7:  begin
              out_data          <=  dump_wb_state;
            end
            8:  begin
              out_data          <=  dump_wb_p_addr;
            end
            9:  begin
              out_data          <=  dump_wb_p_dat_in;
            end
            10: begin
              out_data          <=  dump_wb_p_dat_out;
            end
            11: begin
              out_data          <=  dump_wb_m_addr;
            end
            12: begin
              out_data          <=  dump_wb_m_dat_in;
            end
            13: begin
              out_data          <=  dump_wb_m_dat_out;
            end
            default: begin
              out_data            <=  32'hFFFFFFFF;
            end
          endcase
          if (local_data_count > 0) begin
             local_data_count <= local_data_count - 1;
           end
           else begin
            state                 <=  IDLE;
           end
           out_status              <=  ~in_command;
           out_address             <=  0;
           out_en                  <=  1; 
           dump_count              <=  dump_count + 1;
        end
      end
      IDLE: begin
        //handle input
        master_ready            <= 1;
        mem_bus_select          <= 0;
        if (in_ready) begin
          debug_out[6]          <= ~debug_out[6];
          mem_bus_select        <= 0;
          nack_count            <= nack_timeout;

          local_address         <= in_address;
          local_data            <= in_data;
          //out_data_count  <= 0;

          case (real_command)

            `COMMAND_PING: begin
              $display ("WBM: ping");
              debug_out[0]    <= ~debug_out[0];
              out_status      <= ~in_command;
              out_address     <= 32'h00000000;
              out_data        <= S_PING_RESP;
              out_en          <= 1;
              state           <= IDLE;
            end
            `COMMAND_WRITE: begin
              out_status      <= ~in_command;
              debug_out[1]    <= ~debug_out[1];
              local_data_count    <=  in_data_count;
              if (command_flags & `FLAG_MEM_BUS) begin
                mem_bus_select  <= 1; 
                mem_adr_o     <= in_address;
                mem_stb_o     <= 1;
                mem_cyc_o     <= 1;
                mem_we_o      <= 1;
                mem_dat_o     <= in_data;
              end
              else begin
                mem_bus_select  <= 0;
                wb_adr_o      <= in_address;
                wb_stb_o      <= 1;
                wb_cyc_o      <= 1;
                wb_we_o       <= 1;
                wb_dat_o      <= in_data;
              end 
              out_address     <= in_address;
              out_data        <= in_data;
              master_ready    <= 0;
              state           <= WRITE;
            end
            `COMMAND_READ:  begin
              local_data_count  <=  in_data_count;
              debug_out[2]    <= ~debug_out[2];
              if (command_flags & `FLAG_MEM_BUS) begin
                mem_bus_select  <= 1; 
                mem_adr_o     <= in_address;
                mem_stb_o     <= 1;
                mem_cyc_o     <= 1;
                mem_we_o      <= 0;
                out_status    <= ~in_command;
              end
              else begin
                mem_bus_select  <= 0;
                wb_adr_o      <= in_address;
                wb_stb_o      <= 1;
                wb_cyc_o      <= 1;
                wb_we_o       <= 0;
                out_status    <= ~in_command;
              end
              master_ready    <= 0;
              out_address     <= in_address;
              state           <= READ;
            end 
            `COMMAND_MASTER_ADDR: begin
              out_address     <=  in_address;
              out_status      <= ~in_command;
              case (in_address)
                `MADDR_WR_FLAGS: begin
                  master_flags  <= in_data;
                end
                `MADDR_RD_FLAGS: begin
                  out_data      <= master_flags;
                end
                `MADDR_WR_INT_EN: begin
                  interrupt_mask  <= in_data;
                  out_data      <=  in_data;
                  $display("WBM: setting interrupt enable to: %h", in_data); 
                end
                `MADDR_RD_INT_EN: begin
                  out_data      <= interrupt_mask;
                end
                `MADDR_NACK_TO_WR: begin
                  nack_timeout  <= in_data;
                end
                `MADDR_NACK_TO_RD: begin
                  out_data      <= nack_timeout;
                end
                default: begin
                  //unrecognized command
                  out_status      <=  32'h00000000;
               end
              endcase
              out_en          <=  1;
              state           <=  IDLE;
            end
            `COMMAND_CORE_DUMP: begin
              local_data_count        <=  DUMP_COUNT + 1;
              dump_count              <=  0;
              state                   <=  DUMP_CORE;
            end
            default:    begin
            end
          endcase
        end
        //not handling an input, if there is an interrupt send it to the user
        else if (wb_ack_i == 0 & wb_stb_o == 0 & wb_cyc_o == 0) begin
          //hack for getting the in_data_count before the io_handler decrements it
            //local_data_count  <= in_data_count;
            //work around to add a delay
            wb_adr_o              <= local_address;
            //handle input
            local_address         <= 32'hFFFFFFFF;        
          //check if there is an interrupt
          //if the wb_int_i goes positive then send a nortifiction to the user
          if ((~prev_int) & wb_int_i) begin 
            debug_out[11]          <= ~debug_out[11];
            $display("WBM: found an interrupt!");
            out_status            <= `PERIPH_INTERRUPT; 
            //only supporting interrupts on slave 0 - 31
            out_address           <= 32'h00000000;
            out_data              <= wb_dat_i;
            out_en                <= 1;
          end
          prev_int  <= wb_int_i;
        end
      end
      default: begin
      state <= IDLE;
      end
    endcase
  end
  //handle output
  prev_reset  <=  rst;
end

endmodule
