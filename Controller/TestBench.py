from myhdl import *
from Simulator import *
from SdramCntl import *
from host_intf import host_intf

def test_readWrite(host_intf,sd_intf):

    @instance
    def test():
        yield delay(140)
    #    yield host_intf.write(120,23)
        host_intf.addr_i.next = 120
        host_intf.data_i.next = 23
        yield delay(5)
        host_intf.wr_i.next   = 1
    #
        yield host_intf.done_o.posedge
        yield host_intf.nop()
        yield delay(20)
    #    yield host_intf.read(120)
        host_intf.addr_i.next = 120
        host_intf.rd_i.next   = 1
        yield delay(2)
        host_intf.rd_i.next   = 0
        yield sd_intf.clk.posedge
    #
        yield host_intf.done_o.posedge

        print "Data Value : ",host_intf.data_o," clk : ",now()
    return test

clk_i = Signal(bool(0))
rst_i = ResetSignal(0,active=1,async=True)

clkDriver_Inst      = clkDriver(clk_i)
sd_intf_Inst        = sd_intf(clk_i)
host_intf_Inst      = host_intf(clk_i)

sdram_Inst = sdram(sd_intf_Inst,show_command=False)
sdramCntl_Inst = SdramCntl(host_intf_Inst,sd_intf_Inst,rst_i)

test_readWrite_Inst = traceSignals(test_readWrite,host_intf_Inst,sd_intf_Inst)

sim = Simulation(clkDriver_Inst,sdram_Inst,sdramCntl_Inst,test_readWrite_Inst)
sim.run(7500)
