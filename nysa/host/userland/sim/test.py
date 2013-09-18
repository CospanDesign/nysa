import cocotb
import threading
from cocotb.triggers import Timer, Join, RisingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
from cocotb.result import ReturnValue, TestFailure
from cocotb.binary import BinaryValue
from cocotb.decorators import external

from nysa.host.userland.sim.sim_host import NysaSim
from nysa.cbuilder.drt import drt
from array import array as Array

@cocotb.test()
def test_hello(dut):
    clk_gen = cocotb.fork(Clock(dut.clk, 10).start())
    nysa = NysaSim(dut)
    yield Join(cocotb.fork(nysa.reset()))
    yield ClockCycles(dut.clk, 100)
    yield Join(cocotb.fork(nysa.ping()))
    yield ClockCycles(dut.clk, 100)
    yield Join(cocotb.fork(nysa.write(device_id = 0, address = 0, data = Array('B', [0, 1, 2, 3]))))
    yield ClockCycles(dut.clk, 100)
    value = yield Join(cocotb.fork(nysa.read(device_id = 0, address = 0, length=8)))
    dut.log.info("Read value: %s" % str(value.retval))
    device_count = drt.get_number_of_devices(value.retval)
    dut.log.info("Number of devices %d" % drt.get_number_of_devices(value.retval))

    len_to_read = (device_count * 8) + 8
    value = yield Join(cocotb.fork(nysa.read(device_id = 0, address = 0, length=len_to_read)))
    response = value.retval
    print "length of response: %d" % len(response)
    print "Response: %s" % str(response)
    manager = drt.DRTManager()
    manager.set_drt(response)
    manager.pretty_print_drt()

    yield ClockCycles(dut.clk, 100)


