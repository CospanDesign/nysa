import cocotb
import threading
from cocotb.triggers import Timer, Join, RisingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
from cocotb.result import ReturnValue, TestFailure
from cocotb.binary import BinaryValue

from sim import NysaSim

@cocotb.test()
def test_hello(dut):
    nysa = NysaSim(dut)
    dut.log.info("Activate FIFO 0")

