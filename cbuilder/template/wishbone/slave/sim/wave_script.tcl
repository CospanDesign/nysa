
set signals [list]


lappend signals "__HI__"
lappend signals "wishbone_master_tb.clk"
lappend	signals "wishbone_master_tb.rst"
#uncomment the below line for debug
#lappend signals "wishbone_master_tb.state"
lappend signals "wishbone_master_tb.execute_command"
lappend signals "wishbone_master_tb.command_finished"
lappend signals "wishbone_master_tb.in_command"
lappend signals "wishbone_master_tb.in_address"
lappend signals "wishbone_master_tb.in_data_count"
lappend signals "wishbone_master_tb.in_data"
lappend signals "wishbone_master_tb.out_data_count"
lappend signals "wishbone_master_tb.out_status"
lappend signals "wishbone_master_tb.out_data"
lappend signals "wishbone_master_tb.master_ready"
lappend signals "wishbone_master_tb.in_ready"
lappend signals "wishbone_master_tb.out_ready"
lappend signals "wishbone_master_tb.out_en"

#master signals
lappend signals "wishbone_master_tb.wm.wb_adr_o"
lappend signals "wishbone_master_tb.wm.wb_dat_o"
lappend signals "wishbone_master_tb.wm.wb_dat_i"
lappend signals "wishbone_master_tb.wm.wb_cyc_o"
lappend signals "wishbone_master_tb.wm.wb_stb_o"
lappend signals "wishbone_master_tb.wm.wb_we_o"
lappend signals "wishbone_master_tb.wm.wb_ack_i"

#add the DUT signals, add your own signals by following the format
#lappend signals "wishbone_master_tb.s1.wbs_we_i"
#lappend signals "wishbone_master_tb.s1.wbs_cyc_i"
#lappend signals "wishbone_master_tb.s1.wbs_ack_i"
#lappend signals "wishbone_master_tb.s1.wbs_stb_o"

set num_added [gtkwave::addSignalsFromList $signals]
set min_time [gtkwave::getMinTime]
set max_time [gtkwave::getMaxTime]
gtkwave::setZoomRangeTimes $min_time $max_time
gtkwave::setLeftJustifySigs on
