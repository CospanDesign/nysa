#Project: Nysa
NOTE: Nysa is a remake of Olympus, Olympus is depreciated and will be removed soon

##Goal: Simplifiy both generation of HDL and interactions with FPGAs.

##Problem:

FPGA are extremely flexible.
They can be used to:
* Communicate with sensors that employ a variety of protocols including I2C, UART, SPI etc...
* Read images from cameras and write to LCD screens
* Interface with memory devices
* Exchange data with a processor


Unfortunately FPGA require a lot of resources and knowledge before one can
get the coveted initial "blinky" analogy up and running. Not only does one
need to know about the physical constraints of an FPGA but understand how it
interacts with a hardware description language.

##What Nysa is:

* A flexible I/O peripheral expansion for a host.
  * This host can be a desktop computer a laptop an Android tablet or even a microcontroller
* A platform to build interfaces to complex sensors and algorithms.
  * Cameras
  * LCD screens
  * Process data

##What Nysa is NOT:

* A general FPGA development environment
* A platform for soft core processors. There are may projects that already do that including OpenCores and Papilion.
* Used to develop stand alone FPGA platforms, independent of the host


##Description:

The suite is split into three subgroups: cbuilder (generates verilog modules), ibuilder (generates FPGA images) and host (host side software used to interface with an FPGA)

###cbuilder (Core Builder): Generates individual cores to interface with a sensor, IC, or process an algorithm.
* Utilities to create Wishbone slave modules that can be used within a Nysa image.
  * The created module includes.
    * An actual verilog module the user edits.
    * Software tools to build, simulate and view the waveform of the simulations using gtkwave.
    * A simple mechanism that allows users to easily introduce different stimulus on the core.
* The verilog modules generated here are fed into ibuilder to be used within an actual FPGA image.

###ibuilder (Image Builder): Generates FPGA images to go onto a board
* Using only a configuration file users can generate an FPGA image specifying the behavior they want from the FPGA.
* Generates PlanAhead projects and associated scripts to build a bit or binary file that can be used to program an FPGA.

###Host: Host side software
* Interface with an FPGA image using Python or c. An simple low level API is defined to detect and interact with an FPGA board.
* Users can simply plug in an FPGA board, such as Dionysus, and the host computer can query the FPGA for it's behavior.
* Writing drivers for a module is as simple as creating a Python module or a C library.
* Writing applications for Nysa based FPGAs are simpler than writing software to control native components on a desktop, laptop or an embedded device.


