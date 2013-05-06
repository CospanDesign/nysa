//mg_defines.v
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

`ifndef __MG_DEFINES__
`define __MG_DEFINES__

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

`endif //__MG_DEFINES__
