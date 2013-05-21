#! /bin/bash

echo "Fixing FTDI Interface"
sed -i 's/\"ftdi_clk/\"i_ftdi_clk/g' *.json
sed -i 's/\"ftdi_data/\"io_ftdi_data/g' *.json
sed -i 's/\"ftdi_txe/\"i_ftdi_txe/g' *.json
sed -i 's/\"ftdi_wr_n/\"o_ftdi_wr_n/g' *.json
sed -i 's/\"ftdi_rde_n/\"i_ftdi_rde_n/g' *.json
sed -i 's/\"ftdi_rd_n/\"o_ftdi_rd_n/g' *.json
sed -i 's/\"ftdi_oe_n/\"o_ftdi_oe_n/g' *.json
sed -i 's/\"ftdi_siwu/\"o_ftdi_siwu/g' *.json
sed -i 's/\"ftdi_suspend_n/\"o_ftdi_suspend_n/g' *.json


echo "Changing UART Interface"
sed -i 's/\"phy_uart_in/\"i_phy_uart_in/g' *.json
sed -i 's/\"phy_uart_out/\"o_phy_uart_out/g' *.json


