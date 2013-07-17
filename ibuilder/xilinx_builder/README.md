#Xilinx Builder

##Description: sCons based command line tools to interface with Xilinx tools

##How to use:

+ Edit the config.json file to setup a build environment, the keywords are as
    follows:
  * name: Name of the project to be created ex: "project"
  * build\_dir: Output directory of the project ex: "build"
  * device: Device part number ex: "xc6slx9-tqg144-3"
  * verilog: A list of verilog files or paths
      - If the entry is a directory then all items in the diretory will be added
      - If the "recursive" flag is set to true then it will also be recusively
        searched
  * top\_module: Top verilog module in the project
  * constraint\_files: List of constraint files to be used
  * coregen: Settings for coregen
      - flags: Flags that can be set for the coregen, any flag specified by
    the user will override the default values set in
  * xst: Setting for xst synthesizer
      - flags: Flags that can be set for the synthesizer, any flag specified
        by the user will override the default values set in
        site_scons/xst_default_flags.json
  * ngd: Settings for ngdbuild translator
      - flags: Flags that can be set for the translator, any flag specified
        by the user will override the default values set in
        site_scons/ngd_default_flags.json
  * map: Settings for map
      - flags: Flags that can be set for the translator, any flag specified
        by the user will override the default values set in
        site_scons/map_default_flags.json
  * par: Settings for place and route
      - flags: Flags that can be set for the translator, any flag specified
        by the user will override the default values set in
        site_scons/par_default_flags.json
  * trace: Settings for trace timing analysis
      - flags: Flags that can be set for the translator, any flag specified
        by the user will override the default values set in
        site_scons/trace_default_flags.json
  * bitgen: Settings for bitgen
      - flags: Flags that can be set for the translator, any flag specified
        by the user will override the default values set in
        site_scons/bitgen_default_flags.json
      - configuration: Override the default configuration, any value set in
        this block will override the default vlues set in
        site_scons/bitgen_configuration.json  
  
  

  * ***NOTE:*** by setting a flag to "\_true" then the flag will be inserted as 
  a standalone flag: eg "-my\_flag":"\_true" will show up as: 
  ...-my\_flag... for the tool, NOT ...-my\_flag \_true...
  * ***NOTE:*** Do not specify a flag to allow the default flags to override 
  (the default flags can be viewed in site\_scons/??\_default\_flags.json)
  * ***NOTE:*** Setting a flag to blank will override the default flag with 
  nothing  

+ Build the project by typing either 'scons' to build all targets or scons
  plus a Target (listed below)
  

##Command Line Options:

###Targets:
  * cores: generate cores in the cores directory (cores -> .ngc)
  * xst: synthesize (verilog, [cores]) -> .ncd
  * ngd\_build: netlist translation (from abstract constructs to Xilinx 
      specific constructs)
      (.ngc -> .ngd)
  * map: mapping the xilinx specific netlist (logical design) into the
      specified xilinx component (using slices, BRAMs, and I/Os) 
      (.ngd -> .ncd)
  * par: place and route the component within the FPGA
      (.ncd -> _par.ncd)
  * bitgen: generating a bit file that can be downloaded to the FPGA
      (_par.ncd -> .bit)
  * trace: analyzing the design for timing violations
      (_par.ncd -> .twr)

###Flags:
  * --debug\_build: view debug messages helpful to debug the builder 
  * --config\_file: specify a different configuration file than 'config.json' 
  * --clean\_build: remove all directories create by the build process 
                    config["build\_dir"] directory 
                    _xmsgs directory 
  * --clean\_cores: clean the cores, cores take a long time to build so it 
                    doesn't make sense to rebuild them every run so unless 
                    explicitly declared the default clean (scons -c) scons 
                    will not remove the generated cores 



* * *
##Notes About Cores:
Cores are very useful and can add a lot of functionality to code here is how
to use them in this build environment.

Use Coregen GUI to generate your core. It's alright if the part number/family
doesn't match up with the final build the build tool will fix this (Just make
sure that your device can accomodate the core, i.e. don't put a PCIE core
on a spartan 3)

After coregen generates your core copy the (core\_name).xco (as is) to the 
'cores' directory. copy the (core\_name).v file to the rtl directory. This is
the interface to your core. It looks strange becaus the sythesis implementation
only declares ports and parameters but this is like a header file in c where
the synthesizer will know to look for an NGC file created by coregen to
attach the backend of that module to.

For example if you generated a complex multiplier for use with a
xc6slx4-tgq144-2 part and you are currently building for a xc6slx9-tqg144-3
part the tool will fix the necessary project settings and generate your core.

###Example:
If you named the complex multiplier cm in coregen, it will output
a lot of files two of them being cm.xco and cm.v. Put cm.xco in the 'cores'
directory and cm.v in the 'rtl' directory.


* * *

##To Do:

  [\_] Add support for vhdl  
  [x] Add Support for SmartGuide (reusing previous builds to speed up new
      builds)  
  [\_] Add support for multiple verilog/VHDL libraries  
  [x] Add support for cores  
  [\_] Add support for bmm  
  [\_] Test build environment on 32-bit Linux Box  
  [\_] Test build environment on 32-bit Windows Box  
  [\_] Test build environemnt on 64-bit Windows Box  


