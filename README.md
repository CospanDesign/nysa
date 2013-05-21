#Project: Nysa
##NOTE: Nysa is a remake of Nysa, Nysa is depreciated and will be removed soon

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
* A platform to build interfaces to complex sensors.
  * Cameras
  * LCD screens

##What Nysa is NOT:

* A general FPGA development environment
* A platform for soft core processors. There are may projects that already do that including OpenCores and Papilion.
* Used to develop stand alone FPGA platforms, independent of the host


##Description: 

The suite is split into three subgroups, although Nysa can be run entirely from the command line Nysa was designed to be used as a GUI plugin for IDE. (Specifically Ninja-IDE)

###cbuilder (Core Builder): Generates individual cores to interface with a sensor, IC, or process an algorithm.
* there are tools and scripts provided to simplify the process of synthesizing and simulating a verilog module
* the cores are used by ibuilder to generate FPGA images that will call on a 
    created core in a predefined manner.
  * For example: perhaps a sensor simply requires an I2C interface. The user
    can specify this in the metadata and the host will read this metadata and 
    use either a python script or even a kernel driver to interface with this
    device

###ibuilder (Image Builder): Generates FPGA images to go onto a board
* Generates PlanAhead projects and associated scripts to build a bit or 
  binary file that can be used to program an FPGA
* users can use either the command line interface or the graphical user 
  interface (GUI) called "Image Builder"

###Host: Host side software
* this section is split up into two sections
  * kernelland: low level code designed to facilitate communication between 
    the FPGA and the kernel itself
    * the benefit of this model is that end-users will interact with devices
      in the same way they would interact
      with other devices on their computer
      * For example: When you attach a usb->serial device on your computer 
        a new device appears in the /dev directory. When an Nysa based 
        design is attached to a Linux box the kernel will behave in a similar
        fashion and generate devices 
        inside the /dev directory.
  * userland: the end user will use the scripts and libraries here to interact
    with their script
    * interaction can be accomplished by communicating directly with the FPGA
      or by means of a standard linux device
      using the procedure described in the kernelland portion


