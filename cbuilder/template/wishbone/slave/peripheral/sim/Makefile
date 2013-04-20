all:
	python fix_verilog_paths.py
	iverilog -I../ -o design -ctemp.txt -DSIMULATION
strict:
	python fix_verilog_paths.py
	iverilog -I../ -o design -Wall -ccmd_file.txt -DSIMULATION
clean:
	rm design
	rm *.vcd
sim:
	vvp design
wave:
	vvp design
	gtkwave design.vcd -T wave_script.tcl &

