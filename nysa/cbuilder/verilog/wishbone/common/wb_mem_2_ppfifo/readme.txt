Wishbone Memory to Ping Pong FIFO

Utility Module that can be put into a slave to allow it to read data from
a wishbone memory interface and write it into a Ping Pong FIFO


How to use:



1. Pass the o_mem.* and i_mem.* out through the top of the slave module
2. Attach the Ping Pong FIFO write side to i_ppfifo.* and o_ppfifo.*
3. Attach the i_memory_0_base to an address in the wishbone slave
4. Attach the i_memory_0_size and i_memory_0_new_data to an address in the
   wishbone slave and strobe i_memory_0_new_data when i_memory_0_size is
   written to
5. Repeat for i_memory_1.*
6. Either use the o_default_mem_*_base as the initial value of the memory
   bases or fill in your own
7. When o_read_finished goes high enable the interrupt to indicate to the
   host that a memory buffer is now empty
8. attach i_enable to either '1' or when the slave core is enabled



