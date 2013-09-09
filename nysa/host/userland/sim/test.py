import cocotb
import threading
from cocotb.triggers import Timer, Join, RisingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
from cocotb.result import ReturnValue, TestFailure
from cocotb.binary import BinaryValue

from nysa.host.userland.sim.sim_host import NysaSim
from array import array as Array

@cocotb.test()
def test_hello(dut):
    in_clk    = Clock(dut.clk, 10)
    in_clk.start()
    nysa = NysaSim(dut)
    yield Join(cocotb.fork(nysa.reset()))
    yield ClockCycles(dut.clk, 100)
    yield Join(cocotb.fork(nysa.ping()))
    yield ClockCycles(dut.clk, 100)
    yield Join(cocotb.fork(nysa.write(device_id = 0, address = 0, data = Array('B', [0, 1, 2, 3]))))
    yield ClockCycles(dut.clk, 100)
    yield nysa.read(device_id = 0, address = 0, length=8)
    yield ClockCycles(dut.clk, 100)

    in_clk.stop()

