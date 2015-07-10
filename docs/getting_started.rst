.. include global.rst

Getting Started
================================

Requirements
------------

Python
^^^^^^

Pip
^^^

You can test if you have pip installed by openning up a terminal and typing: ``pip --version``

If you do not see a version number here's how to get it:

#. Download `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_
#. Run the download script: ``python ./get-pip.py``

Installation
------------
From a terminal install nysa from the github repo using pip

.. code-block:: bash

    pip install git+https://github.com/CospanDesign/nysa

Nysa Command Line Tool
----------------------
A Nysa command line tool is available to the user, to view all the commands type:

.. code-block:: bash

    $> nysa --help
    usage: nysa [-h] [-v] [-d]
                {image-builder,generate-slave,install-platform,boards,install-examples,utils,ping,upload,devices,reset,platforms,init,program,status,install-verilog-repo,board-programmed,sdb-viewer}
                ...

    Nysa Tool

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Output verbose information
      -d, --debug           Output test debug information

    Tools:
      Nysa Tools

      {image-builder,generate-slave,install-platform,boards,install-examples,utils,ping,upload,devices,reset,platforms,init,program,status,install-verilog-repo,board-programmed,sdb-viewer}

    Enter the toolname with a -h to find help about that specific tool

    Tools:

    cbuilder                 Functions to help create code to go into platforms

         generate-slave      Create a project to generate a nysa compatible core
         devices             Manage/View devices IDs and descriptions

    ibuilder                 Functions to generate an entire image (or binary) to be downloaded into a platform

         image-builder       Create a project to generate an image for a platform

    host                     Functions to view and control boards

         boards              List connected boards
         ping                performs a board ping, this is the simplest level of communicatio If a board responds to a ping it has been reset and the clock is running correctly
         upload              Upload a program file to the specified board
         reset               performs a soft reset the specified board
         program             Initiate a program sequence
         board-programmed    Reads the status of the FPGA 'Done' pin to determine if the FPGA is programmed
         sdb-viewer          Display the contents of the SDB of the specified board

    utility                  Functions to update and/or upgrade the nysa tool including adding new platforms and verilog packages

         install-platform    Install a platform to the local system
         install-examples    Install examples to the local system
         utils               Utility functions
         platforms           List platforms (installed and remotely available)
         init                Creates the local nysa_projects directory, initializes the configuration files To see the status of the current nysa setup run 'nysa status'
         status              Print the status of nysa tools
         install-verilog-repoInstall a verilog repository to the local system



We will be using some of the utility functions and all of the host functions here

Initializing Nysa
-----------------

In a hurry? Copy and paste the following into a terminal otherwise skip below to find out what this means

.. code-block:: bash

    nysa init
    nysa install-verilog-repo all
    nysa install-platform all
    nysa install-examples all


Nysa needs to do the following things in order to be set up correctly

1. Create a directory where users can create projects (both core projects and image projects), by default it creates a directory in <home>/Projects/nysa_base

.. code-block:: bash

    nysa init

2. Retrieve the default verilog repositories that is used to build FPGA images. This repository also has a number of useful wishbone slaves that the users can use.

.. code-block:: bash

    nysa install-verilog-repo all

3. Install one or more board support packages.

.. code-block:: bash

    nysa install-platform all

4. Install examples of FPGA projects

.. code-block:: bash

    nysa install-examples all



Talking to an FPGA
------------------

Run the following command:

.. code-block:: bash

    nysa boards

You should get an output that looks something like this:

.. code-block:: bash

    Scanning artemis_usb2... Found 1 board(s)
        Board ID: FTYNUFY9
    Scanning dionysus... No boards found
    Scanning sim... Found 11 board(s)
        Board ID: dionysus_spi_pmod
        Board ID: dionysus_sf_camera
        Board ID: dionysus_i2c_pmod
        Board ID: dionysus_dma_test
        Board ID: dionysus_stepper_pmod
        Board ID: dionysus_dma_controller_test
        Board ID: dionysus_nes
        Board ID: dionysus_i2s
        Board ID: dionysus_pmod_oled
        Board ID: dionysus_uart_pmod
        Board ID: dionysus_pmod_tft
    Scanning artemis... No boards found

Nysa will query the host computer for any boards attached. It even queried simulated boards. Any of the above boards can be used in the following examples.


**Note About Unique Names**
Nysa will always prioritize a physical board over a simulated board. For example if I ran the command ``nysa ping`` Nysa will look for a physical board, in my case **artemis_usb2**, and ping the board. If there was no physical board attached the ``nysa ping`` command would return an error because there is more than one possible board to ping like the following:

.. code-block:: bash

    Error: ping_board: Serial number (ID) required because there are multiple platforms availble
    Available IDs:
        dionysus_spi_pmod
        dionysus_sf_camera
        dionysus_i2c_pmod
        dionysus_dma_test
        dionysus_stepper_pmod
        dionysus_dma_controller_test
        dionysus_nes
        dionysus_i2s
        dionysus_pmod_oled
        dionysus_uart_pmod
        dionysus_pmod_tft

To resove this, you must specify the id of the board using '-s <board ID>' on any command where the solution is not obvious to the tool. For example. To 'ping' the simulated board 'dionysus_spi_pmod' the following command would be used ``nysa ping sim -s dionysus_spi_pmod``

.. code-block:: bash

    $> nysa ping sim -s dionysus_spi_pmod
    Pinging board... Received a Response!


Ping a board
^^^^^^^^^^^^
Ping is the simplest form of communication, the purpose of the command is to verify that the communciation scheme is working, it does not test out any higher level features of the board.

**Simulation Example, pinging the simulated board 'dionysus_spi_pmod'**

.. code-block:: bash

    $> nysa ping sim -s dionysus_spi_pmod
    Pinging board... Received a Response!

**Physical Board Example** (in this case artemis_usb2)

.. code-block:: bash

    $> nysa ping
    Pinging board... Received a Response!


SDB Viewer
^^^^^^^^^^
The SDB (Self Defined Bus) Viewer. When the Nysa image build tool creates an FPGA image it also generates a ROM that is embedded in that image. That ROM can be read and parsed to determine the behavior of the FPGA by the user.

**Simulation Example, read/parse the SDB and display it on the command line**

.. code-block:: bash

    $> nysa sdb-viewer sim -s dionysus_spi_pmod
    Important: NysaSDBManager:read_sdb: Parsing Top Interconnect Buffer
    SDB
    Bus: top        @ 0x0000000000000000 : Size: 0x200000000
    Number of components: 2
         Bus: peripheral @ 0x0000000000000000 : Size: 0x04000000
         Number of components: 4
             SDB                  Type (Major:Minor) (01:00): SDB
             Address:        0x0000000000000000-0x0000000000000380 : Size: 0x00000380
             Vendor:Product: 8000000000000000:00000000

             wb_spi_0             Type (Major:Minor) (05:01): SPI
             Address:        0x0000000001000000-0x000000000100000C : Size: 0x0000000C
             Vendor:Product: 800000000000C594:00000005

             gpio1                Type (Major:Minor) (02:01): GPIO
             Address:        0x0000000002000000-0x0000000002000008 : Size: 0x00000008
             Vendor:Product: 800000000000C594:00000002

             1:2                  Type (Major:Minor) (00:00): Nothing
             Address:        0x0000000003000000-0x0000000003000000 : Size: 0x00000000
             Vendor:Product: 8000000000000000:00000000

         Bus: memory     @ 0x0000000100000000 : Size: 0x00800000
         Number of components: 1
             mem1                 Type (Major:Minor) (06:02): Memory
             Address:        0x0000000000000000-0x0000000000800000 : Size: 0x00800000
             Vendor:Product: 800000000000C594:00000000

**Physical Board Example** (in this case artemis_usb2)

.. code-block:: bash

    $> nysa sdb-viewer
    Important: NysaSDBManager:read_sdb: Parsing Top Interconnect Buffer
    SDB
    Bus: top        @ 0x0000000000000000 : Size: 0x200000000
    Number of components: 2
         Bus: peripheral @ 0x0000000000000000 : Size: 0x06000000
         Number of components: 6
             SDB                  Type (Major:Minor) (01:00): SDB
             Address:        0x0000000000000000-0x0000000000000440 : Size: 0x00000440
             Vendor:Product: 8000000000000000:00000000

             artemis_usb2         Type (Major:Minor) (22:03): Platform
             Address:        0x0000000001000000-0x0000000001000004 : Size: 0x00000004
             Vendor:Product: 800000000000C594:00000000

             gpio1                Type (Major:Minor) (02:01): GPIO
             Address:        0x0000000002000000-0x0000000002000008 : Size: 0x00000008
             Vendor:Product: 800000000000C594:00000002

             sata                 Type (Major:Minor) (14:01): Storage Manager
             Address:        0x0000000003000000-0x0000000003001000 : Size: 0x00001000
             Vendor:Product: 800000000000C594:00000010

             dma                  Type (Major:Minor) (13:01): DMA
             Address:        0x0000000004000000-0x0000000004000095 : Size: 0x00000095
             Vendor:Product: 800000000000C594:0000C594

             artemis              Type (Major:Minor) (22:02): Platform
             Address:        0x0000000005000000-0x0000000005000003 : Size: 0x00000003
             Vendor:Product: 800000000000C594:00000000

         Bus: memory     @ 0x0000000100000000 : Size: 0x08000000
         Number of components: 1
             ddr3_mem             Type (Major:Minor) (06:03): Memory
             Address:        0x0000000000000000-0x0000000008000000 : Size: 0x08000000
             Vendor:Product: 800000000000C594:00000000


Other Host Commands
^^^^^^^^^^^^^^^^^^^

upload
""""""
Upload an image file to a board. The format of the files is platform specific. For Artemis USB2 and Dionysus the format is a 'bin' file that is generated from the Xilinx tools using the bitgen tool.

Uploading a binary to artemis USB2

.. code-block:: bash

    $> nysa upload top.bin
    Info: upload: Found: Numonyx 2048 KB, 32 sectors each 65536 bytes
    Info: upload: Erasing the SPI flash device, this can take a minute or two...
    Info: upload: Flash erased, writing binary image to PROM
    addr: 00000000, len data: 0016A674, len self: 00200000
    Info: upload: Reading back the binary flash
    Info: upload: Verifying the data read back is correct
    Info: upload: Verification passed!

program
"""""""
Issue a signal that will reprogram the FPGA. This is platform dependent. For Artemis USB2 and Dionysus the command will pull the 'PROGRAM_N' pin low on the FPGA which tells the FPGA to read in the data from the SPI Flash ROM.

Issuing a program command

.. code-block:: bash

    $> nysa program
    Wait for board to finish programming...........................Done!

reset
"""""
Many times FPGA images have a reset signals, this command will pusle the reset signal which resets internal state machines within the FPGA

.. code-block:: bash

    $> nysa reset


Conclusion
----------

This is all the high level utility functions of Nysa to learn more about how to:

* Easily build an FPGA image that will interact with all the Nysa tools
* Create a Wishbone slave core you can use to interface with your custom hardware and that can be used to create an FPGA image with a configuration file
* Interact with Nysa graphically using the Nysa GUI (nui)
