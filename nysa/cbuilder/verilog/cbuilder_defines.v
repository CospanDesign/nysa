//cbuilder_defines.v
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
  09/21/2012
    -changed the master command interface to use the address for single read
    and write
    -added core dump feature so users can find out the state of the master
    before the system was reset
  06/24/2012
    -Added the Reset command that will reset the state machine from
    the host interface
  11/12/2011
    -Added NACK support
      commands
        COMMAND_NACK_TO_WR: set the NACK timeout
        COMMAND_NACK_TO_RD: read the NACK timeout

      status codes
        NACK_TIMEOUT: a NACK timeout occured

      default values:
        DEF_NACK_TIMEOUT: currently  set to 20 hex or 32 ticks
  11/06/2011
    -Added PERIPH_INTERRUPT to notify users of a peripheral
      slave interrupt
    -Changed COMMAND_INTERRUPT to COMMAND_WR_INT_EN and
    COMMAND_RD_INT_EN
*/

// defines for the miracle grow project

`ifndef __CBUILDER_DEFINES__
`define __CBUILDER_DEFINES__

`define COMMAND_PING        32'h00000000
`define COMMAND_WRITE       32'h00000001
`define COMMAND_READ        32'h00000002
`define COMMAND_RESET       32'h00000003
`define COMMAND_MASTER_ADDR 32'h00000004
`define COMMAND_CORE_DUMP   32'h0000000F

//master address space
`define MADDR_WR_FLAGS      32'h00000000
`define MADDR_RD_FLAGS      32'h00000001
`define MADDR_WR_INT_EN     32'h00000002
`define MADDR_RD_INT_EN     32'h00000003
`define MADDR_NACK_TO_WR    32'h00000004
`define MADDR_NACK_TO_RD    32'h00000005
`define MADDR_CORE_DUMP     32'h00000006

//conditions
`define PERIPH_INTERRUPT    32'h00000001
`define NACK_TIMEOUT        32'h00000002

//flags
`define FLAG_MEM_BUS        16'h0001

//default variables
`define DEF_NACK_TIMEOUT    32'h00000100


//AXI Defines

//--Burst
`define AXI_BURST_FIXED     2'b00
`define AXI_BURST_INCR      2'b01
`define AXI_BURST_WRAP      2'b10

//--Burst Size
`define AXI_BURST_SIZE_1    3'b000
`define AXI_BURST_SIZE_2    3'b001
`define AXI_BURST_SIZE_4    3'b010
`define AXI_BURST_SIZE_8    3'b011
`define AXI_BURST_SIZE_16   3'b100
`define AXI_BURST_SIZE_32   3'b101
`define AXI_BURST_SIZE_64   3'b110
`define AXI_BURST_SIZE_128  3'b111

//--Response
`define AXI_RESP_OKAY       2'b00
`define AXI_RESP_EXOKAY     2'b01
`define AXI_RESP_SLVERR     2'b10
`define AXI_RESP_DECERR     2'b11

//--Lock
`define AXI_LOCK_NORMAL     2'b00
`define AXI_LOCK_EXCLUSIVE  2'b01
`define AXI_LOCK_LOCKED     2'b10

//--cache
//----Bufferable
`define AXI_CACHE_NON_BUF   1'b0
`define AXI_CACHE_BUF       1'b1
//----Cachable
`define AXI_CACHE_NON_CACHE 1'b0
`define AXI_CACHE_CACHE     1'b1
//----Read Allocate
`define AXI_CACHE_NON_RA    1'b0
`define AXI_CACHE_RA        1'b1
//----Write Allocate
`define AXI_CACHE_NON_WA    1'b0
`define AXI_CACHE_WA        1'b1
//----Unused
`define AXI_CACHE_UNUSED    4'b0000

//--Protection
//----ARPROT[0]
`define AXI_PROT_NORMAL     1'b0
`define AXI_PROT_PRIVLEDGE  1'b1

//----ARPROT[1]
`define AXI_PROT_SECURE     1'b0
`define AXI_PROT_NON_SECURE 1'b1

//----ARPROT[2]
`define AXI_PROT_DATA       1'b0
`define AXI_PROT_INST       1'b1

//----Unused:
`define AXI_PROT_UNUSED     {`AXI_PROT_NORMAL, `AXI_PROT_NON_SECURE, `AXI_PROT_DATA}

//--Low Power Mode
`define AXI_POWER_LOW       1'b0
`define AXI_POWER_NORMAL    1'b1

`endif //__CBUILDER_DEFINES__
