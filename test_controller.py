from clk_driver import clk_driver
from sdram import *
from sdram_cntl import sdram_cntl
from host_intf import HostIntf
from sd_intf import *


def test_readwrite(host_intf):

    @instance
    def test():
        yield delay(140)
        yield host_intf.write(120, 23)
        yield host_intf.done_o.posedge
        yield host_intf.nop()
        yield delay(5)
        yield host_intf.read(120)
        yield host_intf.done_o.posedge

        print "Data Value : ", host_intf.data_o, " clk : ", now()
    return test

clk_i = Signal(bool(0))
rst_i = ResetSignal(0, active=1, async=True)

clkDriver_Inst = clk_driver(clk_i)
sd_intf_Inst = SdramIntf()
host_intf_Inst = HostIntf()

sdram_Inst = sdram(clk_i, sd_intf_Inst, show_command=False)
sdramCntl_Inst = sdram_cntl(clk_i, host_intf_Inst, sd_intf_Inst)
# sdramCntl_Inst = traceSignals(MySdramCntl,host_intf_Inst,sd_intf_Inst)

test_readWrite_Inst = test_readwrite(host_intf_Inst)

sim = Simulation(clkDriver_Inst, sdram_Inst, sdramCntl_Inst, test_readWrite_Inst)
sim.run(7500)
