#execute in windows with <path to planAhead>/PlanAhead -mode batch -source project_gen.tcl
#execute in windows with gui <path to planahead>/PlanAhead -source project_gen.tcl

#this project looks for things in the /src directory

#11/07/2011 fixed glob from not crashing when there is an empty directory like "arbitor"

proc findVerilogFiles { dir } {
	set vSources [list]
	set contents [glob -nocomplain -directory $dir *] 
	
	foreach item $contents {
		#puts $item
		# recurse - go into the sub directory
		if { [file isdirectory $item] } {
			set innerItems [findVerilogFiles $item] 
			foreach f $innerItems {
				lappend vSources $f
			}
		} elseif {[regexp {\.v$} $item]} {
			#puts $item
			lappend vSources $item
		}
	}
	return $vSources
}

proc findUCFFiles { dir } {
	set contents [glob -nocomplain -directory $dir *]
	set ucfSources [list]

	foreach item $contents {
		#puts $item
		# recursively go into the sub directories
		if { [file isdirectory $item] } {
			set innerItems [findUCFFiles $item]
			foreach f $innerItems {
				lappend ucfSources $f
			}
		} elseif {[regexp {\.ucf$} $item]} {
			#puts $item
			lappend ucfSources $item
		}
	}
	return $ucfSources
}



set projDir [file dirname [info script]]
set srcDir $projDir
set projName test_project
set topName top
set device xc3s500efg320-4


if {[file exists $projDir/$projName]} {
# if the project directory exists, delete it and create a new clean one
file delete -force $projDir/$projName
}

#if {[file exists $projDir/$projName]}{
#	#If the project directory exists, delte it and create a new clean one
#	file delete -force $projDir/$projName
#}

create_project $projName $projDir/$projName -part $device

set_property design_mode RTL [get_filesets sources_1]

#Define the RTL sources to add to the project
#set verilogSources [list] 
#[glob $srcDir/*.v]
#need to start in the base directory because there is a 'dependency' dir
set verilogSources [findVerilogFiles $srcDir/rtl]
#lappend verilogSources [findVerilogFiles $srcDir/dependencies]
set contents [glob -nocomplain -directory $srcDir/dependencies *]
foreach item $contents {
	if {[regexp {\.v$} $item]} {
		lappend verilogSources $item
	}
}

set contents [glob -directory $srcDir *]
foreach item $contents {
	if {[regexp {\.v$} $item]} {
		lappend verilogSources $item
	}
}
lappend verilogSources $srcDir/rtl/bus/slave/device_rom_table.txt

#set verilog_dir_read [glob -directory $srcDir *]
#foreach item $verilog_dir_read {
#	if {[regexp {\.v$} $item]} {
#		lappend verilogSources $item
#    }
#	
#}
	
foreach f $verilogSources {
	puts $f
}
	

#imports the individual files into the project and put those files in a "container" called fileset
import_files -fileset [get_filesets sources_1] -force -norecurse $verilogSources
	#-force overwrites any previous sources by the same name
	#-norecurse tells PlanAhead not to recursively search every subdirectory and add any additional files it finds
	
#add the device_rom_table file
#add_files -norecurse -scan_for_includes $srcDir/rtl/bus/slave/device_rom_table.txt
#import_files -norecurse $srcDir/rtl/bus/slave/device_rom_table.txt	
	
#set the library name, work is default, so this is really optional
#set_property library work [get_filesets sources_1]
set_property TOP_LIB work [get_filesets sources_1]

#set the UCF constraint
set ucfSources [findUCFFiles $srcDir/constraints]
import_files -fileset [get_filesets constrs_1] -force -norecurse $ucfSources

#set the name of the top-level module or entity, so the synthesis engine knows what the top-level to synthesize is
set_property top $topName [get_filesets sources_1]


set flist [get_files -of_objects {sources_1} *.v]
foreach item $flist {
#	puts "checking: "
#	puts $item
	if {[regexp {project_defines.v} $item]} {
#		puts "found Project Defines"
		set_property is_global_include true $item
	}
	if {[regexp {cbuilder_defines.v} $item]} {
#		puts "found Project Defines"
		set_property is_global_include true $item
	}
}


#set different strategies... power optimization, speed etc..
#set_property strategy PowerOptimization [get_runs synth_1]
#now launch the project
launch_runs -runs synth_1


#the above step runs in another thread, so wait for it
wait_on_run synth_1


#now run the implementation
#can set different implementation strategies set the propertly like in synthesis
#set_property strategy MapTiming[get_runs impl_1]
set_property add_step Bitgen [get_runs impl_1]
#generate a bin file
config_run impl_1 -program bitgen -option {More Options} -value {-g Binary:yes}
launch_runs -runs impl_1
wait_on_run impl_1

#now we can open the design for editing in the TCL script
#open_impl_design


#launch_impact



