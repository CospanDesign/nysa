.. _getting-started:

Getting Started With Nysa
=========================

This document has the following three parts:

* Installing Nysa on your system
* Set up Nysa
* Explore some of the features and commands available

Requirements
------------

**Python**

Currently Nysa is built for Python 2 you can download it `here <https://www.python.org/downloads>`_

**Pip**

Pip simplifies the process of installing Python modules. You can test if you have pip installed by openning up a terminal and typing: ``pip --version``

If you do not see a version number here's how to get it:

#. Download `get-pip.py <https://bootstrap.pypa.io/get-pip.py>`_
#. Run the downloaded script in a terminal: ``python ./get-pip.py``
#. Using apt-get install git, iverilog and gtkwave

.. code-block:: bash

    sudo apt-get install git verilog gtkwave

Installation
------------
From a terminal install nysa from the github repo using pip

**Ubuntu**

.. code-block:: bash

    sudo pip install git+https://github.com/CospanDesign/nysa


Pip will install the nysa module as well as the command line tool

Nysa Command Line Tool
----------------------
The Nysa command line tool is available to the user, to view all the commands type:

.. code-block:: bash

    $> nysa --help
    usage: nysa [-h] [-v] [-d]
                {generate-slave,devices,image-builder,reset,ping,board-programmed,program,upload,sdb-viewer,init,utils,boards,platforms,install-platform,install-verilog-repo,install-examples,status}
                ...

    Nysa Tool

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         Output verbose information
      -d, --debug           Output test debug information

    Tools:
      Nysa Tools

      {generate-slave,devices,image-builder,reset,ping,board-programmed,program,upload,sdb-viewer,init,utils,boards,platforms,install-platform,install-verilog-repo,install-examples,status}

    Enter the toolname with a -h to find help about that specific tool

    Tools:

    cbuilder                 Functions to help create code to go into platforms

         generate-slave      create a project to generate a nysa compatible core
         devices             manage/view devices IDs and descriptions

    ibuilder                 Functions to generate an entire image (or binary) to be downloaded into a platform

         image-builder       create a vendor specific project to generate an image for a platform

    host                     Functions to view and control boards

         reset               performs a soft reset the specified board
         ping                performs a board ping, this is the simplest level of communicatio If a board responds to a ping it has been reset and the clock is running correctly
         board-programmed    reads the status of the FPGA 'Done' pin to determine if the FPGA is programmed
         program             Initiate a program sequence
         upload              upload a program file to the specified board
         sdb-viewer          display the contents of the SDB of the specified board

    utility                  Functions to update and/or upgrade the nysa tool including adding new platforms and verilog packages

         init                creates the local nysa_projects directory, initializes the configuration files. To see the status of the current nysa setup run 'nysa status'
         utils               utility functions
         boards              list connected boards
         platforms           list platforms (installed and remotely available)
         install-platform    install a platform to the local system
         install-verilog-repoinstall a verilog repository to the local system
         install-examples    install FPGA Project examples to the local system
         status              print the status of the nysa tools

We will be using some of these functions to configure Nysa and communicate with either a physical or simulated FPGA board.

Initializing Nysa
-----------------

In a hurry? Copy and paste the following into a terminal otherwise skip below to find out what this means.

.. code-block:: bash

    nysa init
    nysa install-verilog-repo all
    nysa install-platform all
    nysa install-examples all


Nysa needs to do the following things in order to be set up correctly

1. Create a directory where users can create projects (both core projects and image projects), by default it creates a directory in <home>/Projects/nysa_base on Ubuntu.

.. code-block:: bash

    nysa init

2. Retrieve the default verilog repositories that is used to build FPGA images. This repository also has a number of useful wishbone slaves that the users can use.

.. code-block:: bash

    nysa install-verilog-repo all

3. Install one or more board support packages.

.. code-block:: bash

    nysa install-platform all

4. Install examples of FPGA projects.

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


**Note about implicit names**
When executing a command that interfaces with a board Nysa will attempt to determine which board the user is refering to. For example, if the 'artemis_usb2' board was the only board attached to my computer and I types ``nysa ping`` Nysa will send a ping down to artemis_usb2. The command ``nysa ping`` would be the same as typing ``nysa ping artemis_usb2 -s FTYNUFY9`` (Assuming FTYNUFY9 was the board's serial number). If there are multiple boards for a single platform the user will need to explicitly write the entire command.

As an example, if there were no physical boards attached and the ``nysa ping`` was issued, the following would occur:

.. code-block:: bash

    $> nysa ping
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

The following variation to the command would resolve this: ``nysa ping sim -s dionysus_spi_pmod``

.. code-block:: bash

    $> nysa ping sim -s dionysus_spi_pmod
    Pinging board... Received a Response!


Ping a board
^^^^^^^^^^^^
Ping is the simplest form of communication, the purpose of the command is to verify that the

#. The communication medium is working (UART, USB, PCIE, etc...).
#. The clock is working correctly.
#. The FPGA is programmed.
#. The most basic functionality is working.

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
Upload an image file to a board. The format of the files is platform specific. For Artemis USB2 and Dionysus the format is a 'bin' file that is generated from the Xilinx bitgen tool.

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
Issue a signal that will reprogram the FPGA. This is platform dependent. For Artemis USB2 and Dionysus the command will pull the 'PROGRAM_N' pin low FPGA which tells the FPGA to read in the data from the SPI Flash ROM.

Issuing a program command

.. code-block:: bash

    $> nysa program
    Wait for board to finish programming...........................Done!

reset
"""""
Many times FPGA images have a reset signals, this command will pusle the reset signal which resets FPGA's internal state machines

.. code-block:: bash

    $> nysa reset


Conclusion
----------

This is all the high level utility functions of Nysa to learn more about how to:

* Create a Wishbone slave core you can use to interface with your custom hardware and that can be used within an FPGA image: :ref:`Getting started with CBuilder <getting-started-cbuilder>`
* Build FPGA images with a configuration file: :ref:`Getting started with IBuilder <getting-started-ibuilder>`
* Interact with Nysa graphically using the Nysa GUI (nui)
